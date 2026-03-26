# Jeena's Command Center Bot — Setup Guide

## What This Does
One Telegram bot that sends you:
- **5:00am PT daily** — News briefing (Web3, AI, tech, world) + Today's GMAT mission + Morning fuel
- **7:00pm PT daily** — Evening motivation + Remember your why + Push harder
- **5x per workday (weekdays)** — Sneaky GMAT facts disguised as pop culture updates

All powered by Claude AI. Runs 100% in the cloud — your computer never needs to be on.

---

## Step 1 — Create Your GitHub Repo

1. Go to [github.com](https://github.com) → click **New** (top left)
2. Name it something like `jeena-command-center` (keep it private!)
3. Leave everything else default → click **Create repository**

---

## Step 2 — Upload These Files

Drag and drop the entire contents of this folder into your new GitHub repo:
- `main.py`
- `schedule.json`
- `requirements.txt`
- `.github/` folder (with all the workflow files inside)

**Important:** Make sure the `.github/workflows/` folder structure is preserved.

To upload via the GitHub web interface:
1. Click **uploading an existing file** on the repo page
2. Drag in all the files above
3. Commit them

Or if you have Git installed:
```bash
cd jeena-command-center
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/jeena-command-center.git
git push -u origin main
```

---

## Step 3 — Add Your Secrets

This is where you give GitHub your API keys (stored securely — never visible after saving).

1. In your GitHub repo, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add these three:

| Secret Name | Value |
|-------------|-------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID (see below) |
| `ANTHROPIC_API_KEY` | Your Anthropic API key |

### How to get your Telegram Chat ID:
1. Open Telegram and send any message to your bot
2. Visit this URL in your browser (replace YOUR_TOKEN):
   `https://api.telegram.org/botYOUR_TOKEN/getUpdates`
3. Find `"id"` inside the `"chat"` object — that number is your Chat ID

---

## Step 4 — Test It

Once everything is uploaded and secrets are set:
1. Go to your repo → **Actions** tab
2. Click on any workflow (e.g., "Morning Briefing")
3. Click **Run workflow** → **Run workflow** (green button)
4. Check your Telegram — the message should arrive within ~30 seconds

---

## Schedule Reference (Pacific Time)

| Time | Message |
|------|---------|
| 5:00am PT (daily) | Morning briefing |
| 7:00pm PT (daily) | Evening push |
| 9:17am PT (weekdays) | Sneak message 1 |
| 11:03am PT (weekdays) | Sneak message 2 |
| 12:44pm PT (weekdays) | Sneak message 3 |
| 2:28pm PT (weekdays) | Sneak message 4 |
| 4:11pm PT (weekdays) | Sneak message 5 |

Note: GitHub Actions cron uses UTC. All times above are converted correctly for PDT (UTC-7).
When daylight saving ends in November, update the cron times by adding 1 hour to the UTC values.

---

## Updating Your TTP Schedule

When you move past May 2, open `schedule.json` and add new entries in this format:
```json
"2026-05-03": "What you're studying that day — with a tip or focus area."
```

---

## Troubleshooting

- **No message received?** Check the Actions tab for errors. Most common issue: secrets not set correctly.
- **Wrong time?** Remember cron uses UTC. PDT = UTC-7, PST = UTC-8.
- **Rate limit errors?** Anthropic API has generous limits — unlikely to hit them.
