from typing import Any

import wmill


VERIFY_TOKEN_PATH = "u/shamlahtanai/whatsapp_verify_token"


def main(
    query: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
    verify_token: str | None = None,
) -> Any:
    """
    Meta WhatsApp webhook endpoint.

    1. GET verification:
       Meta sends hub.mode, hub.verify_token, hub.challenge.
       We return hub.challenge.

    2. POST incoming messages:
       Meta sends WhatsApp message payload.
       We return parsed sender and text for testing.
    """

    query = query or {}
    body = body or {}

    expected_token = verify_token or wmill.get_variable(VERIFY_TOKEN_PATH)

    mode = query.get("hub.mode") or query.get("mode")
    token = query.get("hub.verify_token") or query.get("verify_token")
    challenge = query.get("hub.challenge") or query.get("challenge")

    if mode == "subscribe":
        if token == expected_token and challenge:
            return str(challenge)
        raise ValueError("Invalid WhatsApp webhook verification token.")

    messages = (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("messages", [])
    )

    if not messages:
        return {
            "received": True,
            "message_found": False,
            "body": body,
        }

    message = messages[0]
    sender_phone = message.get("from")
    text = message.get("text", {}).get("body")

    return {
        "received": True,
        "message_found": True,
        "patient_phone": sender_phone,
        "message_text": text,
        "raw_message": message,
    }