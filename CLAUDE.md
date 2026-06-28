# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RSS-to-Email subscription notification system. A single Python script fetches an Atom/RSS feed daily, generates an HTML email with the latest post, and BCC-delivers it to subscribers via SMTP. Runs on a GitHub Actions cron schedule (daily 12:00 CST).

## Commands

```bash
# Install dependencies
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# Run locally (requires env vars set)
python send_update.py

# Run with test data (use the local atom.xml fixture)
RSS_URL="https://090909.top/atom.xml" \
SMTP_SERVER="smtp.resend.com" \
SMTP_PORT="465" \
SMTP_USER="resend" \
SMTP_PASS="<key>" \
SMTP_FROM_NAME="他说" \
SMTP_FROM_ADDR="subscribe@090909.top" \
SMTP_SUBJECT="他说，你收到了新的订阅" \
EMAIL_LIST="me@upxuu.com" \
python send_update.py

# Manually trigger the workflow from CLI
gh workflow run send.yml
```

## Architecture

### Script: `send_update.py` (191 lines)

Single-file Python script with no framework. The flow is:

1. **Parse config** — 14 env vars (SMTP, RSS URL, email list, customizable HTML tags)
2. **Fetch RSS** — `feedparser.parse(RSS_URL)`, take `feed.entries[0]`
3. **Deduplicate** — compare latest entry's link against `link.txt` (cache file)
4. **Build email** — `build_html_content()` + `build_plain_content()`, combined as `multipart/alternative`
5. **Send SMTP** — `smtplib.SMTP_SSL` with the sender as To and subscribers as BCC
6. **Persist** — save the sent link to `link.txt`

Key design decisions:
- **BCC-only delivery**: subscribers never see each other's addresses
- **Plain-text fallback**: `strip_html_tags()` strips the RSS summary HTML for the plaintext part
- **Customizable template tags**: `TAG_TITLE`, `TAG_SUMMARY`, `TAG_LINK`, `LINK_TEXT` env vars let users change `<h1>`/`<p>`/`<a>` without modifying code
- **No state DB**: a single-line text file (`link.txt`) cached via `actions/cache@v4` serves as state

### CI/CD: `.github/workflows/send.yml`

- **Trigger**: Daily at `0 4 * * *` (UTC) = 12:00 CST, plus `workflow_dispatch`
- **Runner**: `ubuntu-latest`, 5-minute timeout
- **Cache**: `link.txt` cached across runs via `actions/cache@v4` (restore key `rss-sent-link-`)
- **Secrets**: 14 GitHub Secrets mapped directly to env vars
- **No build/test/lint steps** — deploy-and-run pattern

### Key Files

| File | Purpose |
|---|---|
| `send_update.py` | Sole script — all logic |
| `requirements.txt` | `feedparser==6.0.12`, `sgmllib3k==1.0.0` |
| `.github/workflows/send.yml` | GitHub Actions scheduled job |
| `link.txt` | Durable state: last-sent article URL (gitignored) |
| `atom.xml` | Local RSS feed fixture (gitignored, not needed for CI) |
| `demo.html` | Reference HTML email template (gitignored) |
| `smtp.txt` / `serects.txt` | Local dev notes for SMTP/email config (gitignored) |

## Environment Variables

14 env vars — all required except 4 with defaults:

| Variable | Default | Description |
|---|---|---|
| `SMTP_SERVER` | — | SMTP hostname |
| `SMTP_PORT` | `465` | SMTP port |
| `SMTP_USER` | — | SMTP username |
| `SMTP_PASS` | — | SMTP password / API key |
| `SMTP_FROM_NAME` | — | Sender display name |
| `SMTP_FROM_ADDR` | — | Sender email address |
| `SMTP_SUBJECT` | — | Email subject line |
| `RSS_URL` | — | Atom/RSS feed URL |
| `EMAIL_LIST` | — | Space-separated BCC recipient emails |
| `TAG_TITLE` | `h1` | HTML tag for email title |
| `TAG_SUMMARY` | `p` | HTML tag for email summary |
| `TAG_LINK` | `a` | HTML tag for email link |
| `LINK_TEXT` | `阅读详情` | Link anchor text |

Notable: the script exits with code 1 if any required var is missing, and with code 0 for "no new articles" (normal skip).

## No Tests

The project has zero tests. If adding tests, use Python's `unittest` or `pytest` — either fits the codebase's simplicity.
