from __future__ import annotations
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def send_email(smtp_host: str, smtp_port: int, username: str, password: str,
               email_from: str, email_to: str, subject: str, html_body: str, text_body: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = email_to

    part1 = MIMEText(text_body, "plain", "utf-8")
    part2 = MIMEText(html_body, "html", "utf-8")
    msg.attach(part1)
    msg.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
        server.login(username, password)
        server.sendmail(email_from, [email_to], msg.as_string())

def format_email_payload(jobs: list[dict]) -> tuple[str, str]:
    if not jobs:
        return "", ""

    now_pt = datetime.now(timezone.utc).astimezone(ZoneInfo("America/Los_Angeles"))
    subject = f"New job postings ({len(jobs)}) – {now_pt.strftime('%Y-%m-%d %I:%M %p %Z')}"

    lines = []
    for j in jobs:
        lines.append(f"- {j.get('title')} @ {j.get('company')} [{j.get('location','')}]\n  {j.get('url')} (posted: {j.get('posted_at','n/a')})")
    text_body = "New roles detected:\n\n" + "\n".join(lines)

    rows = []
    for j in jobs:
        rows.append(f"""<tr>
<td style='padding:6px 10px;border-bottom:1px solid #eee'><a href="{j.get('url')}">{j.get('title')}</a></td>
<td style='padding:6px 10px;border-bottom:1px solid #eee'>{j.get('company')}</td>
<td style='padding:6px 10px;border-bottom:1px solid #eee'>{j.get('location','')}</td>
<td style='padding:6px 10px;border-bottom:1px solid #eee'>{j.get('posted_at','')}</td>
</tr>""")
    html_body = f"""<html><body>
<h3>New roles detected</h3>
<table cellspacing="0" cellpadding="0" style="border-collapse:collapse">
<tr><th align="left">Title</th><th align="left">Company</th><th align="left">Location</th><th align="left">Posted</th></tr>
{''.join(rows)}
</table>
</body></html>"""

    return subject, (html_body, text_body)
