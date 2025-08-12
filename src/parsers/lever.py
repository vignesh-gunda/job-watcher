from __future__ import annotations
import requests
from typing import List, Dict

def fetch(board: str, company_name: str) -> List[Dict]:
    # Lever postings API
    url = f"https://api.lever.co/v0/postings/{board}?mode=json"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    jobs = []
    for item in data:
        job_id = str(item.get("id"))
        title = item.get("text", "")
        abs_url = item.get("hostedUrl") or item.get("applyUrl") or item.get("url") or ""
        loc = ", ".join([l.get("name","") for l in item.get("categories", {}).get("location", [])]) if isinstance(item.get("categories",{}).get("location", []), list) else (item.get("categories", {}).get("location") or "")
        created = item.get("createdAt")
        posted_at = ""
        if created:
            try:
                posted_at = created
            except Exception:
                posted_at = ""
        jobs.append({
            "id": f"lever:{board}:{job_id}",
            "title": title,
            "company": company_name,
            "location": loc,
            "url": abs_url,
            "posted_at": posted_at,
            "source": "lever",
        })
    return jobs
