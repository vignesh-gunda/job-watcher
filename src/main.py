from __future__ import annotations
import os, re, sys, yaml, requests
from typing import List, Dict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from config import EMAIL_TO, EMAIL_FROM, SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, REPO_STATE_PATH
from storage import SeenStore
from emailer import send_email, format_email_payload

from parsers import greenhouse as gh
from parsers import lever as lv
from parsers import workday as wd
from parsers import html as htmlp

def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def normalize_text(s: str) -> str:
    return (s or "").strip()

def matches_filters(job: Dict, global_cfg: dict, company_cfg: dict) -> bool:
    title = normalize_text(job.get("title", "")).lower()
    loc = normalize_text(job.get("location", "")).lower()

    # keywords
    include_any = [k.lower() for k in (company_cfg.get("include_keywords") or global_cfg.get("keywords_any") or [])]
    exclude_any = [k.lower() for k in (company_cfg.get("exclude_keywords") or global_cfg.get("exclude_keywords") or [])]

    if include_any and not any(k in title for k in include_any):
        return False
    if any(k in title for k in exclude_any):
        return False

    # locations (optional, string contains)
    loc_filters = [l.lower() for l in (company_cfg.get("locations_any") or global_cfg.get("locations_any") or [])]
    if loc_filters:
        if not any(lf in loc for lf in loc_filters):
            # allow empty location to pass (many APIs don't include it)
            if loc:
                return False

    return True

def fetch_company(company: dict) -> List[Dict]:
    ctype = company.get("type")
    name = company.get("name", "Unknown")
    try:
        if ctype == "greenhouse":
            return gh.fetch(company["board"], name)
        elif ctype == "lever":
            return lv.fetch(company["board"], name)
        elif ctype == "workday_json":
            return wd.fetch(company["url"], name)
        elif ctype == "html":
            return htmlp.fetch(company["url"], name)
        else:
            print(f"[WARN] Unsupported type for {name}: {ctype}", file=sys.stderr)
            return []
    except requests.HTTPError as e:
        print(f"[ERROR] HTTP for {name}: {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[ERROR] {name}: {e}", file=sys.stderr)
        return []

def main() -> int:
    cfg = load_yaml("companies.yaml")
    global_cfg = cfg.get("global", {})
    companies = cfg.get("companies", [])

    all_jobs: List[Dict] = []
    for c in companies:
        jobs = fetch_company(c)
        # filter per company
        jobs = [j for j in jobs if matches_filters(j, global_cfg, c)]
        all_jobs.extend(jobs)

    # Dedup by id
    uniq = {}
    for j in all_jobs:
        uniq[j["id"]] = j
    jobs = list(uniq.values())

    # Check "seen" store
    store = SeenStore(REPO_STATE_PATH)
    new_ids = store.mark_and_filter_new([j["id"] for j in jobs])
    new_jobs = [j for j in jobs if j["id"] in new_ids]

    # Save state regardless
    store.save()

    if not new_jobs:
        print("No new jobs.")
        return 0

    subject, payloads = format_email_payload(new_jobs)
    if not subject:
        print("No subject; skipping email.")
        return 0

    html_body, text_body = payloads

    # ensure SMTP envs exist
    required = [SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO]
    if any(x in (None, "", []) for x in required):
        print("[WARN] Missing SMTP or email env vars; printing message instead of sending.")
        print(subject)
        print(text_body)
        return 0

    send_email(SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO, subject, html_body, text_body)
    print(f"Emailed {len(new_jobs)} new jobs to {EMAIL_TO}.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
