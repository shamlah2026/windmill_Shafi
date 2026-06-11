from typing import Any
import requests

try:
    import wmill
except Exception:
    wmill = None


WHATSAPP_ACCESS_TOKEN = "u/shamlahtanai/whatsapp_access_token"
WHATSAPP_PHONE_NUMBER_ID = "u/shamlahtanai/whatsapp_phone_number_id"
WHATSAPP_API_VERSION = "u/shamlahtanai/whatsapp_api_version"


def get_variable(path: str, default: Any = None) -> Any:
    if wmill is None:
        return default
    value = wmill.get_variable(path)
    return value if value not in (None, "") else default


def main(
    appointment: dict[str, Any] | None = None,
    patient_phone: str | None = None,
    reply_text: str | None = None,
    whatsapp_access_token: str | None = None,
    whatsapp_phone_number_id: str | None = None,
    api_version: str | None = None,
) -> dict[str, Any]:
    """
    Send WhatsApp text message using Meta WhatsApp Cloud API.

    You can test it in two ways:

    Option 1:
    appointment = {
        "patient_phone": "393514545383",
        "reply_text": "Hello from Windmill dentist bot."
    }

    Option 2:
    patient_phone = "393514545383"
    reply_text = "Hello from Windmill dentist bot."
    """

    appointment = appointment or {}

    final_phone = (
        patient_phone
        or appointment.get("patient_phone")
        or appointment.get("phone")
        or appointment.get("to_phone")
    )

    final_message = (
        reply_text
        or appointment.get("reply_text")
        or appointment.get("message")
        or appointment.get("text")
    )

    if not final_phone:
        raise ValueError("Missing patient phone number.")

    if not final_message:
        raise ValueError("Missing reply message text.")

    token = whatsapp_access_token or get_variable(WHATSAPP_ACCESS_TOKEN)
    phone_number_id = whatsapp_phone_number_id or get_variable(WHATSAPP_PHONE_NUMBER_ID)
    version = api_version or get_variable(WHATSAPP_API_VERSION, "v25.0")

    if not token:
        raise ValueError("Missing WhatsApp access token.")

    if not phone_number_id:
        raise ValueError("Missing WhatsApp phone number ID.")

    url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": final_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": final_message,
        },
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    try:
        response_json = response.json()
    except Exception:
        response_json = {"raw_text": response.text}

    if not response.ok:
        raise ValueError(
            {
                "status_code": response.status_code,
                "meta_error": response_json,
            }
        )

    return {
        "whatsapp_sent": True,
        "patient_phone": final_phone,
        "reply_text": final_message,
        "status_code": response.status_code,
        "meta_response": response_json,
    }