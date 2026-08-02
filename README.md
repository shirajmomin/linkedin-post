# LinkedIn Post Agent

Generates one USA healthcare / FHIR / CMS LinkedIn draft (text + premium infographic) and **emails** it to you.

You copy from email → post on LinkedIn. **Nothing is kept on disk** (no drafts/, no data/, no history).

## Run

```powershell
cd D:\ShirajMomin\cursor\Agents\linkedin-post
.\.venv\Scripts\Activate.ps1
python run_agent.py
```

Flags: `--no-ai` · `--no-email` · `--topic "CMS-0057-F PAS"`

## Schedule

GitHub’s built-in `schedule` cron **may not fire** for this repo (history shows only manual runs).

**Reliable options:**
1. **Actions → Run workflow** (manual — always works)
2. **External cron → `workflow_dispatch`** — see [docs/SCHEDULE.md](docs/SCHEDULE.md)
3. Local helper: `.\scripts\trigger_workflow.ps1` (needs `gh auth login`)

YAML still lists 9:00 / 14:00 / 19:00 IST as a backup cron.

Secrets: `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_TO` (optional AI keys + `AI_PROVIDER`).

## Layout

```
run_agent.py          # main agent (temp image → email → delete)
linkedin_image.py     # premium USA healthcare infographic (AI + Pillow)
ai.py / send_email.py / common.py
profile.json / config.yaml / prompts/   # post + image designer prompts
.github/workflows/    # Actions
docs/SCHEDULE.md      # reliable auto-schedule setup
scripts/              # gh trigger helper
```
