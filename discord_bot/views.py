from django.shortcuts import render
import os
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def health(request):
    return Response({
        "status": "ok"
    })
    
@api_view(["POST"])
def discord_interactions(request):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")
    print("----------------------------------------------")
    print("Signature exists:", bool(signature))
    print("Timestamp exists:", bool(timestamp))
    print("Header names:", list(request.headers.keys()))
    if not signature or not timestamp:
        return Response(
            {"error": "Missing Discord signature headers"},
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

    except (BadSignatureError, ValueError):
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
        data = interaction.get("data", {})
        command_name = data.get("name")

        # /status
        if command_name == "status":
            return Response({
                "type": 4,
                "data": {
                    "content": "Bot is online and healthy."
                }
            })

        # /report
        if command_name == "report":
            options = data.get("options", [])

            report_text = ""

            for option in options:
                if option.get("name") == "text":
                    report_text = option.get("value", "")
                    break

            return Response({
                "type": 4,
                "data": {
                    "content": f"Report received: {report_text}"
                }
            })

        # Unknown command
        return Response({
            "type": 4,
            "data": {
                "content": "Unknown command."
            }
        })

    return Response({
        "message": "Interaction received"
    })