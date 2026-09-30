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
    
api_view(["POST"])
def discord_interactions(request):
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    if not signature or not timestamp:
        return Response(
            {"error": "Missing Discord signature headers"},
            status=401,
        )

    public_key = os.getenv("DISCORD_PUBLIC_KEY")

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

    if interaction.get("type") == 1:
        return Response({
            "type": 1
        })

    return Response({
        "message": "Interaction received"
    })