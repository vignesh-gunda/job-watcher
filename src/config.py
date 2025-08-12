from __future__ import annotations
import os

EMAIL_TO = os.getenv("EMAIL_TO", "vgunda.work@gmail.com")
EMAIL_FROM = os.getenv("EMAIL_FROM", "alerts@example.com")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

REPO_STATE_PATH = os.getenv("REPO_STATE_PATH", "state/seen.json")
