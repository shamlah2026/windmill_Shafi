from typing import Any

import requests

try:
    import wmill
except Exception:
    wmill = None


WHATSAPP_RESOURCE = "u/shamlahtanai/whatsapp"
WHATSAPP_ACCESS_TOKEN = "u/shamlahtanai/whatsapp_access_token"
WHATSAPP_PHONE_NUMBER_ID = "u/shamlahtanai/whatsapp_phone_number_id"
WHATSAPP_API_VERSION = "u/shamlahtanai/whatsapp_api_version"


def _get_variable(path: str, default: Any = None) -> Any:
    if wmill is None:
        return default
    try:
        value = wmill.get_variable(path)
        return value if value not in (None, "") else default
    except Exception:
        return default


def _get_resource(path: str) -> dict[str, Any]:
    if wmill is None:
        return {}
    try:
        value = wmill.get_resource(path)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _whatsapp_config(
    whatsapp: dict[str, Any] | None,
    whatsapp_access_token: str | None,
    whatsapp_phone_number_id: str | None,
    api_version: str | None,
) -> tuple[str, str, str]:
    resource = whatsapp or _get_resource(WHATSAPP_RESOURCE)

    token = (
        whatsapp_access_token
        or resource.get("access_token")
        or resource.get("token")
        or _get_variable(WHATSAPP_ACCESS_TOKEN)
    )

    phone_number_id = (
        whatsapp_phone_number_id
        or resource.get("phone_number_id")
        or _get_variable(WHATSAPP_PHONE_NUMBER_ID)
    )

    version = (
        api_version
        or resource.get("api_version")
        or _get_variable(WHATSAPP_API_VERSION, "v25.0")
    )

    if not token:
        raise ValueError("Missing WhatsApp access token.")
    if not phone_number_id:
        raise ValueError("Missing WhatsApp phone number id.")

    return token, phone_number_id, version


def main(
    appointment: dict[str, Any],
    whatsapp: dict[str, Any] | None = None,
    whatsapp_access_token: str | None = None,
    whatsapp_phone_number_id: str | None = None,
    api_version: str | None = None,
) -> dict[str, Any]:
    """Send the generated reply through the Meta WhatsApp Cloud API."""

    to_phone = appointment.get("patient_phone")
    reply_text = appointment.get("reply_text")

    if not to_phone:
        raise ValueError("patient_phone is required")
    if not reply_text:
        raise ValueError("reply_text is required")

    token, phone_number_id, version = _whatsapp_config(
        whatsapp,
        whatsapp_access_token,
        whatsapp_phone_number_id,
        api_version,
    )

    response = requests.post(
        f"https://graph.facebook.com/{version}/{phone_number_id}/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_phone,
            "type": "text",
            "text": {"preview_url": False, "body": reply_text},
        },
        timeout=20,
    )

    response.raise_for_status()

    return {
        **appointment,
        "whatsapp_sent": True,
        "whatsapp_response": response.json(),
    }