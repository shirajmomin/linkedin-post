"""Email drafts via SMTP (Gmail App Password, M365, or SendGrid SMTP)."""

from __future__ import annotations

import mimetypes
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from common import env, load_config, load_profile


def _smtp_creds() -> tuple[str, str, str] | None:
    config = load_config()
    email_cfg = config.get("email", {})
    if not email_cfg.get("enabled", True):
        print("[email] Disabled in config.yaml")
        return None

    user = env("SMTP_USER")
    password = env("SMTP_PASSWORD")
    to_addr = env("EMAIL_TO") or (load_profile().get("email") or {}).get("to", "")

    if not user or not password or not to_addr or to_addr.startswith("YOUR_"):
        print("[email] Skipping — set SMTP_USER, SMTP_PASSWORD, and EMAIL_TO in .env")
        return None
    return user, password, to_addr


def _send_message(msg: MIMEMultipart, user: str, password: str, to_addr: str) -> bool:
    config = load_config()
    email_cfg = config.get("email", {})
    host = email_cfg.get("smtp_host", "smtp.gmail.com")
    port = int(email_cfg.get("smtp_port", 587))

    try:
        with smtplib.SMTP(host, port, timeout=45) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.sendmail(user, [to_addr], msg.as_string())
    except smtplib.SMTPAuthenticationError:
        print(
            "[email] Gmail rejected the password. Use a Google App Password "
            "(not your normal Gmail password), with spaces removed, in SMTP_PASSWORD."
        )
        return False
    except Exception as exc:  # noqa: BLE001
        print(f"[email] Failed to send: {exc}")
        return False
    return True


def _attach_file(msg: MIMEMultipart, path: Path) -> None:
    if not path.exists():
        return
    ctype, encoding = mimetypes.guess_type(str(path))
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    with open(path, "rb") as f:
        part = MIMEBase(maintype, subtype)
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", "attachment", filename=path.name)
    msg.attach(part)


def send_text(subject: str, body: str, attachments: list[Path] | None = None) -> bool:
    creds = _smtp_creds()
    if not creds:
        return False
    user, password, to_addr = creds

    prefix = load_config().get("email", {}).get("subject_prefix", "[LinkedIn Agent]")
    msg = MIMEMultipart("mixed" if attachments else "alternative")
    msg["Subject"] = f"{prefix} {subject}".strip()
    msg["From"] = user
    msg["To"] = to_addr
    msg.attach(MIMEText(body, "plain", "utf-8"))

    for path in attachments or []:
        _attach_file(msg, Path(path))

    if not _send_message(msg, user, password, to_addr):
        return False

    print(f"[email] Sent '{subject}' to {to_addr}")
    return True
