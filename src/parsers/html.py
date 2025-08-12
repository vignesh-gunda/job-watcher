from __future__ import annotations
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def fetch(url: str, company_name: str) -> List[Dict]:
    # Basic HTML scraping fallback (update selectors per site as needed)
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    jobs = []
    # Example: look for <a> tags with job titles in a list
    for a in soup.select("a"):
        title = a.get_text(strip=True)
        href = a.get("href") or ""
        if not title or not href:
            continue
        if href.startswith("/"):
            # cannot reliably resolve without base; leave as relative
            abs_url = href
        else:
            abs_url = href
        jid = f"{company_name}:{abs_url}"
        jobs.append({
            "id": f"html:{jid}",
            "title": title,
            "company": company_name,
            "location": "",
            "url": abs_url,
            "posted_at": "",
            "source": "html",
        })
    return jobs
