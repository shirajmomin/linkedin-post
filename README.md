# LinkedIn Post Agent

Daily agent that drafts **one LinkedIn post** on **HL7 FHIR**, **CMS interoperability**, and related health tech — with a ready-to-upload image — and emails both to you.

Profile: [linkedin.com/in/shiraj-momin-25610232](https://www.linkedin.com/in/shiraj-momin-25610232/)

## What you get each day

1. AI-written post text (copy-paste ready) — practitioner voice on FHIR / CMS interop
2. PNG **infographic** (1200×1200) — LinkedIn-style designed graphic (split compare, workflow, title card, etc.). **No author name on the image.**
3. Email with text + image attachment

LinkedIn does **not** allow auto-posting from this agent; you publish manually.

**Images** are rendered as Health IT infographics (like common FHIR/CMS LinkedIn posts), not stock-photo overlays.

**Posts** need a working `OPENAI_API_KEY` (with quota) or `ANTHROPIC_API_KEY`. If the LLM is unavailable, curated practitioner templates + matching infographic fields are used.

## Layout

```
linkedin-post/
├── profile.json              # Author voice + LinkedIn URL
├── config.yaml               # Email + schedule
├── .env.example              # → copy to .env
├── requirements.txt
├── run_agent.py              # Main daily runner
├── schedule_daily.py         # Optional in-process scheduler
├── linkedin_image.py         # Post card PNG
├── ai.py / common.py / send_email.py
├── prompts/linkedin_post_prompt.txt
├── data/post_history.json    # Topic rotation (created on first run)
└── drafts/                   # YYYY-MM-DD.md + .png
```

## Quick start

```powershell
cd D:\ShirajMomin\cursor\Agents\linkedin-post
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Fill `.env` with the same SMTP settings you use for the job agent (`SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_TO`). Optionally set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.

### Run once

```powershell
python run_agent.py
python run_agent.py --no-ai          # template only
python run_agent.py --no-email       # local files only
python run_agent.py --topic "CMS-0057-F PAS"
```

### Schedule 3× daily with GitHub Actions (recommended — no PC needed)

Yes — you can run this on **GitHub Actions** so your Windows machine can stay off.

1. Create a new GitHub repo and push this project (do **not** commit `.env`).
2. In the repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Required | Example |
|---|---|---|
| `SMTP_USER` | yes | your Gmail |
| `SMTP_PASSWORD` | yes | Gmail App Password |
| `EMAIL_TO` | yes | where drafts are sent |
| `OPENAI_API_KEY` | optional | for AI-written posts |
| `AI_PROVIDER` | optional | `openai` or `anthropic` |
| `ANTHROPIC_API_KEY` | optional | if using Anthropic |

3. Push includes `.github/workflows/linkedin-agent.yml`, which runs **3 times/day**:
   - **09:00 IST**
   - **14:00 IST**
   - **19:00 IST**

4. Test immediately: **Actions → LinkedIn Post Agent → Run workflow**

Each run emails you the post + image (same as `python run_agent.py`). Topic history is saved back to the repo so topics rotate.

To change times, edit the `cron:` lines in `.github/workflows/linkedin-agent.yml` (cron uses **UTC**).

### Schedule on this PC (optional)

- Windows Task Scheduler, or `python schedule_daily.py`
## Topics

Rotates ~15 topics (Patient Access, Provider Directory, CMS-0057-F CRD/DTR/PAS, Azure/APIM, leadership, etc.) so drafts do not repeat for about two weeks.

## Separate from job-post

This project is independent of `job-post` (job search). Schedule them separately if you use both.
