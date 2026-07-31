# LinkedIn Post Agent

Generates one FHIR / CMS Health IT LinkedIn draft (text + HUD image) and **emails** it to you.

You copy from email → post on LinkedIn. **Nothing is kept on disk** (no drafts/, no data/, no history).

## Run

```powershell
cd D:\ShirajMomin\cursor\Agents\linkedin-post
.\.venv\Scripts\Activate.ps1
python run_agent.py
```

Flags: `--no-ai` · `--no-email` · `--topic "CMS-0057-F PAS"`

## Schedule (GitHub Actions)

Repo runs 3× daily and emails you. Secrets needed: `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_TO` (optional `OPENAI_API_KEY`).

## Layout

```
run_agent.py          # main agent (temp image → email → delete)
linkedin_image.py     # HUD infographic
ai.py / send_email.py / common.py
profile.json / config.yaml / prompts/
.github/workflows/    # schedule
```
