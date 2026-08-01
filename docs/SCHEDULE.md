# Reliable schedule (GitHub cron may not fire)

Your Actions history shows **only** `workflow_dispatch` runs — **zero** `schedule` runs,
even with a public repo and `*/5 * * * *`. That means GitHub’s built-in cron is not
triggering for this workflow. Manual runs + email are fine.

Use an **external cron** that calls GitHub’s API. That is reliable.

## Option A — cron-job.org (recommended, no PC needed)

### 1. Create a GitHub Personal Access Token
1. GitHub → **Settings → Developer settings → Personal access tokens**
2. Prefer **Fine-grained token**:
   - Resource owner: `shirajmomin`
   - Repository access: only `linkedin-post`
   - Permissions → **Actions: Read and write**
   - Permissions → **Contents: Read** (sometimes required)
3. Copy the token (you won’t see it again)

### 2. Create jobs on [cron-job.org](https://cron-job.org) (free)
Create **3 jobs** (or one job with 3 schedules if the UI allows):

| Job | Schedule (your local IST) | Cron if site uses UTC |
|-----|---------------------------|------------------------|
| Morning | 09:00 IST | `30 3 * * *` |
| Afternoon | 14:00 IST | `30 8 * * *` |
| Evening | 19:00 IST | `30 13 * * *` |

For each job:

- **URL:**  
  `https://api.github.com/repos/shirajmomin/linkedin-post/actions/workflows/linkedin-agent.yml/dispatches`
- **Method:** `POST`
- **Headers:**
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer YOUR_GITHUB_TOKEN`
  - `X-GitHub-Api-Version: 2022-11-28`
- **Body (raw JSON):**
  ```json
  {"ref":"main"}
  ```

### 3. Test
Save the job → **Run now** (if available) → check Actions for a new run → check email.

## Option B — trigger from your PC (`gh`)

If [GitHub CLI](https://cli.github.com/) is logged in:

```powershell
cd D:\ShirajMomin\cursor\Agents\linkedin-post
gh workflow run "LinkedIn Post Agent" --ref main
```

Or:

```powershell
.\scripts\trigger_workflow.ps1
```

You can point Windows Task Scheduler at that script for 09:00 / 14:00 / 19:00 IST
(only runs when the PC is on).

## Option C — repository_dispatch

Same as Option A, but URL:

`https://api.github.com/repos/shirajmomin/linkedin-post/dispatches`

Body:

```json
{"event_type":"linkedin-post","client_payload":{}}
```

## What we keep in the repo
GitHub `schedule` (9 / 14 / 19 IST) stays in the YAML as a backup.
If GitHub ever starts firing it, you’ll get extra runs — then you can remove
either the GitHub cron or the external cron.
