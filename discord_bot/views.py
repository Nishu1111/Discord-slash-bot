import os
import time

from django.db import IntegrityError
from django.utils import timezone

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .handlers import HANDLERS, classify
from .models import CommandLog
from .mirror import start_report_task


def extract_user(interaction):
    member = interaction.get("member") or {}
    user = member.get("user") or interaction.get("user") or {}

    return (
        user.get("id", ""),
        user.get("username", ""),
    )


@api_view(["GET"])
def health(request):
    return Response({
        "status": "ok"
    })


@api_view(["POST"])
def discord_interactions(request):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    print("Header names:", list(request.headers.keys()))

    if not signature or not timestamp:
        return Response(
            {"error": "Missing Discord signature headers"},
            status=401,
        )

    # Check timestamp -> entire request must be under 5 minutes 
    try:
        if abs(time.time() - int(timestamp)) > 300:
            return Response(
                {"error": "Stale request"},
                status=401,
            )
    except ValueError:
        return Response(
            {"error": "Bad timestamp"},
            status=401,
        )

    public_key = os.getenv("DISCORD_PUBLIC_KEY")

    if not public_key:
        return Response(
            {"error": "Discord public key is not configured"},
            status=500,
        )

    try:
        verify_key = VerifyKey(bytes.fromhex(public_key))

        verify_key.verify(
            timestamp.encode() + request.body,
            bytes.fromhex(signature),
        )

    except (BadSignatureError, ValueError, TypeError):
        return Response(
            {"error": "Invalid request signature"},
            status=401,
        )

    interaction = request.data

    interaction_type = interaction.get("type")

    # Discord PING
    if interaction_type == 1:
        return Response({
            "type": 1
        })

    # Discord slash command
    if interaction_type == 2:
        user_id, username = extract_user(interaction)

        data = interaction.get("data", {})

        try:
            log, created = CommandLog.objects.get_or_create(
                interaction_id=interaction["id"],
                defaults={
                    "interaction_type": 2,
                    "command_name": data.get("name", ""),
                    "options": {
                        option["name"]: option["value"]
                        for option in data.get("options", [])
                    },
                    "guild_id": interaction.get("guild_id", ""),
                    "channel_id": interaction.get("channel_id", ""),
                    "user_id": user_id,
                    "username": username,
                },
            )

        except IntegrityError:
            log = CommandLog.objects.get(
                interaction_id=interaction["id"]
            )
            created = False

        # Duplicate interaction that was already processed
        if not created and log.response_payload:
            return Response(log.response_payload)

        handler = HANDLERS.get(log.command_name)

        try:
            payload = (
                handler(interaction)
                if handler
                else {
                    "type": 4,
                    "data": {
                        "content": "Unknown command.",
                        "flags": 64,
                    },
                }
            )

            log.status = CommandLog.Status.PROCESSED
            log.response_payload = payload

        except Exception as exc:
            log.status = CommandLog.Status.FAILED
            log.error = str(exc)

            payload = {
                "type": 4,
                "data": {
                    "content": "Something went wrong.",
                    "flags": 64,
                },
            }

        log.processed_at = timezone.now()
        log.save()

        # Start background mirror for /report
        if (
            log.command_name == "report"
            and log.status == CommandLog.Status.PROCESSED
        ):
            claimed = CommandLog.objects.filter(
                pk=log.pk,
                mirror_status=CommandLog.MirrorStatus.NOT_APPLICABLE,
            ).update(
                mirror_status=CommandLog.MirrorStatus.PENDING,
                action=classify(
                    log.options.get("text", "")
                ),
            )

            # Start the task only if we claimed the job
            if claimed:
                start_report_task(
                    log.pk,
                    interaction["application_id"],
                    interaction["token"],
                )

        return Response(payload)

    return Response({
        "message": "Interaction received"
    })
