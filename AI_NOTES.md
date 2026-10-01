# AI_NOTES.md

## Tools and split of work
- AI: [Claude / Chatgpt/ Copilot], used in chat for debugging hypotheses, code suggestions, and test ideas.
- From Me: architecture, service choices, all deployment and env config, running and testing every change, and reading logs to find root causes.

## Key decisions I made
1. Django + DRF. It gives me the ORM, auth, migrations, and admin, so the interaction endpoint, the log, and the login-protected dashboard all fit in one small app.
2. Postgres on Neon. The dashboard needs queryable command and mirror-attempt history, and Neon's free tier needs no card.

## Hardest bug
`/report` was stuck on "Slash Bot is thinking…" and the dashboard showed `failed ×1` for every mirror.
- Cause 1: a duplicated `status = ... if ok else ... block in process_report(). ok`= is only defined when a mirror is attempted, so non-mirrored reports raised "UnboundLocalError". The background thread died silently and Discord never got a follow-up.
- **Cause 2: send_followup() swallowed all errors. It also could fire before Discord had registered the deferred reply, which would 404 invisibly.
- Cause 3: MIRROR_WEBHOOK_URL was not set on the host, so every attempt failed with "not configured".
- How I found it: the code looked correct, so I stopped reading it and checked the dashboard's per-attempt errors and the Render logs.
- Fix: Still strugging; a few parts are remaining so I am working on it I'll update the gitlog asap it done

## Status (honest)
Signature verification, deduplication, command logging, and the dashboard work. **The mirror to the second channel is [not fully verified / verified on <date>] on the live URL.** [Update this line after your last test.]

## With more time
- Automated tests for signature checks, duplicate interactions, and webhook failure and retry.
- A real background queue and retry worker, because daemon threads can be killed on free hosts and nothing retries failed mirrors yet.
- Structured logging and dashboard filtering and pagination.
