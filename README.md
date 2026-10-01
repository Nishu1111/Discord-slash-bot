# Discord Slash-Command Bot

Django + DRF bot that handles Discord slash commands, logs every command to Postgres, and mirrors `/report` messages to a second channel through a webhook. A login-protected dashboard shows the command log, actions taken, and rule configuration.

Live URL: [https://discord-slash-bot-zkxj.onrender.com]
Bot Status(working or not): https://discord-slash-bot-zkxj.onrender.com/health/
Dashboard: [https://discord-slash-bot-zkxj.onrender.com/dashboard/]
Rules creation: [https://discord-slash-bot-zkxj.onrender.com/dashboard/rules/]


## What it does
- /status replies "Bot is online and healthy."
- `/report text:<message> acks immediately (deferred reply). In the background, it classifies the text with the keyword rules (`flagged_urgent` or `logged`), mirrors it to a webhook, and edits the reply with the result.
- Verifies Discord's Ed25519 signature on every request and rejects unsigned, forged, or stale requests (401).
- Deduplicates by interaction ID, so a retried interaction never runs twice.
- Stores every mirror attempt (status, HTTP code, error) in `MirrorAttempt`.
- Dashboard: command log with detail view, mirror status, and an editable keyword-rules page.

## Mirror status
The mirror is implemented, and every attempt is logged, but it is [not fully verified/verified on <date>] end-to-end on the live URL. Failed mirrors are marked "failed" and are "not" retried automatically yet.

## Environment variables
Copy `.env.example` to `.env`:

| Variable | Purpose |
DISCORD_APP_ID=******
DISCORD_PUBLIC_KEY=********
DISCORD_BOT_TOKEN=******
MIRROR_WEBHOOK_URL=**************
DATABASE_URL=postgresql:***********************
# RETRY_SECRET=some_random_secret
DJANGO_SECRET_KEY=***************************

## Run locally
Requires Python 3.11+ and a Postgres database (a free Neon DB works).

```bash
git clone []
cd discord-slash-bot
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

cp .env.example .env           # then fill in the values
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Health check: http://127.0.0.1:8000/discord/health/
- Dashboard: http://127.0.0.1:8000/dashboard/ (log in with the superuser)

**Testing Discord against localhost:** Discord can't reach `localhost:8000`, so expose it with a tunnel:

Set the Discord **Interactions Endpoint URL** to `https://<tunnel-host>/discord/interactions/` and add the tunnel host to `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` if needed.

**Register slash commands:** [`python manage.py <command>` or `python register_commands.py`, whichever you use]

## Deployment
- **Hosting:** Render (free web service). Build command: `pip install -r requirements.txt && python manage.py migrate`. Start command: `gunicorn config.wsgi` [confirm yours].
- **Database:** Neon free Postgres. Its connection string goes in `DATABASE_URL`.
- **Env vars:** Set all of the tables above in Render, Environment tab. A `.env` file is not deployed.
- **Discord:** Interactions Endpoint URL is `https://<render-url>/discord/interactions/`.
- **Note:** The free tier sleeps when idle, so the first command after a pause can time out. Run `/status` once to wake it.

## How to test
1. Add the bot to a server: [Bot server]. Or use the test server: [link].
2. Run `/status`. The bot should reply right away.
3. Run `/report text: test urgent`. The reply should update to "Flagged as urgent…", and the message should appear in the mirror channel.
4. Log in at `/dashboard/` with `[admin username]` / `[admin password]` (throwaway account) to see the log, mirror status, and rules.

## Unhappy-path behavior
| Case | Result |
|---|---|
| Missing or bad signature | 401, nothing logged |
| Same interaction twice | Second call returns the stored response, with no duplicate work |
| Mirror webhook down | Command still succeeds, mirror marked `failed`, error stored |
| Slow work | `/report` defers, so the 3-second limit is not an issue |

## AI usage
See [AI_NOTES.md].,

Project UI
<img width="1851" height="922" alt="image" src="https://github.com/user-attachments/assets/c344d5f5-75aa-4111-9a0a-0241564dff48" />
<img width="853" height="432" alt="image" src="https://github.com/user-attachments/assets/8bc0c697-73b7-4ec1-ac95-b69d857aa19a" />
<img width="1882" height="908" alt="image" src="https://github.com/user-attachments/assets/7b092a23-4b3d-45a6-9301-61a12e5626a3" />
<img width="1785" height="1077" alt="image" src="https://github.com/user-attachments/assets/90cfbb63-c32f-41a9-b91b-8fee604144b7" />
<img width="1831" height="1080" alt="image" src="https://github.com/user-attachments/assets/d9766d02-f9d9-4fb1-817d-15d42a71153f" />
<img width="1397" height="973" alt="image" src="https://github.com/user-attachments/assets/726c1111-e95d-4029-848f-f125ff6a9412" />
<img width="1906" height="742" alt="image" src="https://github.com/user-attachments/assets/5fd239c8-7d3d-4c9d-948c-acdd66ea835f" />


