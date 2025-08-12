from __future__ import annotations
import requests
from typing import List, Dict

def fetch(url: str, company_name: str) -> List[Dict]:
    # Expects a Workday JSON search endpoint URL (customer-specific)
    # You must place a valid endpoint in companies.yaml for this to work.
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    jobs = []
    # Heuristic extraction (structure varies by tenant)
    # Try common path: data['jobPostings'] or data['body']['children'][0]['children']...
    postings = []
    if isinstance(data, dict):
        if "jobPostings" in data:
            postings = data["jobPostings"]
        elif "items" in data:
            postings = data["items"]
        else:
            # best-effort collect any list of dicts having 'title' and 'externalPath'
            for v in data.values():
                if isinstance(v, list) and v and isinstance(v[0], dict) and ("title" in v[0] or "title" in v[0].get("jobPosting", {})):
                    postings = v
                    break
    for p in postings:
        jp = p.get("jobPosting", p)
        title = jp.get("title") or p.get("title") or ""
        loc = jp.get("locationsText") or jp.get("locations", "") or ""
        # Try to build URL
        url_path = jp.get("externalPath") or jp.get("externalUrl") or ""
        abs_url = url_path if url_path.startswith("http") else ""
        jid = str(jp.get("externalId") or jp.get("id") or abs_url or title)
        jobs.append({
            "id": f"workday:{company_name}:{jid}",
            "title": title,
            "company": company_name,
            "location": loc,
            "url": abs_url,
            "posted_at": jp.get("postedOn") or "",
            "source": "workday",
        })
    return jobs
