from typing import Any
import wmill

VERIFY_TOKEN_PATH = "u/shamlahtanai/whatsapp_verify_token"


def main(
    body: dict[str, Any] | None = None,
    query: dict[str, Any] | None = None,
    verify_token: str | None = None,
) -> Any:
    body = body or {}
    query = query or {}

    # Windmill HTTP route may put request data in body
    if not query and isinstance(body, dict):
        query = body.get("query", {}) or body.get("args", {}) or {}

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
            "query": query,
        }

    message = messages[0]

    return {
        "received": True,
        "message_found": True,
        "patient_phone": message.get("from"),
        "message_text": message.get("text", {}).get("body"),
        "raw_message": message,
    }