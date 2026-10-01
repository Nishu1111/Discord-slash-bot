import os
import requests
import threading
from django.db import connection
from .models import CommandLog, MirrorAttempt


TIMEOUT = 5
MAX_ATTEMPTS = 5


# Build the message we send to the mirror
def main_body(log, url):
    prefix = (
        "URGENT"
        if log.action == "flagged_urgent"
        else "The Report"
    )

    text = (
        f"{prefix} from "
        f"{log.username or 'unknown'}: "
        f"{log.options.get('text', '')}"
    )[:1800]

    # Discord needs this format
    if "discord.com" in url or "discordapp.com" in url:
        return {
            "content": text,
            "allowed_mentions": {
                "parse": []
            },
        }

    return {
        "text": text
    }


# Send the report to the mirror
def send_mirror(log):
    url = os.getenv("MIRROR_WEBHOOK_URL")

    n = log.mirror_attempts + 1

    ok = False
    http_status = None
    error = ""

    # Check if the webhook URL exists
    if not url:
        error = "MIRROR_WEBHOOK_URL not configured"

    else:
        try:
            response = requests.post(
                url,
                json=main_body(log, url),
                timeout=TIMEOUT,
            )

            http_status = response.status_code

            # Status codes below 300 mean successfor all 2XX
            ok = response.status_code < 300

            if not ok:
                error = f"HTTP {response.status_code}"

        except requests.RequestException as exc:
            # Do not store the webhook URL in the error
            error = type(exc).__name__

    # Save this attempt
    MirrorAttempt.objects.create(
        log=log,
        attempt_no=n,
        ok=ok,
        http_status=http_status,
        error=error,
    )

    # Update the main log
    log.mirror_attempts = n
    log.mirror_last_error = error

    log.mirror_status = (
        CommandLog.MirrorStatus.SENT
        if ok
        else CommandLog.MirrorStatus.FAILED
    )

    log.save(
        update_fields=[
            "mirror_attempts",
            "mirror_last_error",
            "mirror_status",
        ]
    )

    return ok


# Send the final response to Discord
def send_followup(app_id, token, content):
    url = (
        f"https://discord.com/api/v10/webhooks/"
        f"{app_id}/{token}/messages/@original"
    )

    try:
        requests.patch(
            url,
            json={
                "content": content,
                "allowed_mentions": {
                    "parse": []
                },
            },
            timeout=TIMEOUT,
        )

    except requests.RequestException:
        # to ignore follow-up errors
        pass


def process_report(log_id, app_id, token):
    try:
        log = CommandLog.objects.get(pk=log_id)

        ok = send_mirror(log)

        text = log.options.get("text", "")

        flag = (
            "🚨 Flagged as urgent. "
            if log.action == "flagged_urgent"
            else ""
        )

        status = (
            "Mirrored to the team channel."
            if ok
            else "Saved. Mirroring will be retried automatically."
        )

        send_followup(
            app_id,
            token,
            f"Report received: {text}\n"
            f"{flag}{status}",
        )

    finally:
        connection.close()


def start_report_task(log_id, app_id, token):
    threading.Thread(
        target=process_report,
        args=(log_id, app_id, token),
        daemon=True,
    ).start()
