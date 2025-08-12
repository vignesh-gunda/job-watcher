from __future__ import annotations
import requests
from datetime import datetime
from typing import List, Dict

def fetch(board: str, company_name: str) -> List[Dict]:
    # Greenhouse Job Board API
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    data = r.json()
    jobs = []
    for item in data.get("jobs", []):
        job_id = str(item.get("id"))
        title = item.get("title", "")
        abs_url = item.get("absolute_url", "")
        loc = (item.get("location") or {}).get("name", "")
        updated = item.get("updated_at") or item.get("created_at")
        jobs.append({
            "id": f"greenhouse:{board}:{job_id}",
            "title": title,
            "company": company_name,
            "location": loc,
            "url": abs_url,
            "posted_at": updated or "",
            "source": "greenhouse",
        })
    return jobs
