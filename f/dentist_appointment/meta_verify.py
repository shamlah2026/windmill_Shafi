from typing import Any
import wmill

VERIFY_TOKEN_PATH = "u/shamlahtanai/whatsapp_verify_token"


def preprocessor(event: dict[str, Any]) -> dict[str, Any]:
    if event.get("kind") == "http" and event.get("method", "").lower() == "get":
        query = event.get("query") or {}
        return {
            "hub_mode": query.get("hub.mode", ""),
            "hub_verify_token": query.get("hub.verify_token", ""),
            "hub_challenge": query.get("hub.challenge", ""),
            "event": event,
        }

    return {"event": event}


def main(
    event: dict[str, Any] | None = None,
    hub_mode: str = "",
    hub_verify_token: str = "",
    hub_challenge: str = "",
) -> dict[str, Any]:
    event = event or {}

    if hub_mode:
        expected = wmill.get_variable(VERIFY_TOKEN_PATH)
        if hub_mode == "subscribe" and hub_verify_token == expected and hub_challenge:
            return {
                "wm_status_code": 200,
                "wm_content_type": "text/plain; charset=utf-8",
                "result": str(hub_challenge),
            }
        return {"wm_status_code": 403, "result": "Invalid verification"}

    body = event.get("body") or {}
    value = body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
    messages = value.get("messages", [])

    if not messages:
        return {"received": True, "message_found": False, "body": body}

    if not messages:
        return {"received": True, "message_found": False, "body": body}

    msg = messages[0]
    text = msg.get("text", {}).get("body", "")
    phone = msg.get("from", "")

    job_id = wmill.run_flow_async(
        "f/dentist_appointment/dentist_appointment_flow",
        args={
            "patient_phone": phone,
            "message_text": text,
        },
    )

    return {
        "received": True,
        "message_found": True,
        "patient_phone": phone,
        "message_text": text,
        "flow_job_id": job_id,
    }