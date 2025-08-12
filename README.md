# Job Watcher (GitHub Actions)

Watches company career portals every 5 minutes and emails you brand-new postings that match your keywords.

## What it supports (out of the box)
- Greenhouse job boards (JSON API)
- Lever job boards (JSON API)
- Basic HTML fallback (for sites without JSON)
- (Optional) Workday endpoints if you provide a valid JSON URL in `companies.yaml`

## Quick Start
1. **Create a new private repo** and upload these files.
2. **Add repository secrets** (Settings → Secrets and variables → Actions → New repository secret):
   - `SMTP_HOST` (e.g., `smtp.gmail.com` or SES host)
   - `SMTP_PORT` (e.g., `465` for SSL)
   - `SMTP_USERNAME` (your SMTP username or email)
   - `SMTP_PASSWORD` (App Password or SES SMTP password)
   - `EMAIL_FROM` (e.g., `alerts@yourdomain.com` or your email)
   - `EMAIL_TO` (e.g., `vgunda.work@gmail.com`)
3. (Optional) Edit `companies.yaml` to add/remove companies and tweak filters.
4. Commit & push. GitHub Actions will run every 5 minutes and email you when new jobs are found.

> Note: GitHub schedules are *best effort* and may occasionally run a few minutes late. This still meets the ~5–10 minute goal in practice.

## Customizing filters
- Update global `keywords_any` in `companies.yaml` (applies to all companies unless overridden per company).
- Add `include_keywords` or `exclude_keywords` under a specific company to override.
- You can also restrict by `locations_any` (string contains match).

## State file
- The file `state/seen.json` records previously-seen job IDs to avoid duplicate emails.
- The workflow commits changes to this file back to the repo (permissions: `contents: write`).

## Add Workday or custom sites
- If a company uses Workday and exposes a JSON endpoint, set `type: workday_json` and supply the full `url`.
- For purely HTML sites, keep `type: html` and give the careers page URL, then update the CSS selectors in `src/parsers/html.py` if needed.



## Using Amazon SES (recommended for high deliverability)
1. Verify your sender domain or email in SES.
2. Create (or use) SMTP credentials in SES (not your AWS IAM keys).
3. Add the following repo secrets with your SES details:
   - `SMTP_HOST` = e.g., `email-smtp.us-east-1.amazonaws.com`
   - `SMTP_PORT` = `465` (SSL) or `587` (STARTTLS; edit code to use TLS if preferred)
   - `SMTP_USERNAME` = SES SMTP username
   - `SMTP_PASSWORD` = SES SMTP password
   - `EMAIL_FROM` = verified sender (e.g., `alerts@yourdomain.com`)
   - `EMAIL_TO` = `vgunda.work@gmail.com`
4. Commit & push. You’ll receive emails from SES when new roles are detected.
