from typing import Any

import requests


def main(
    appointment: dict[str, Any],
    whatsapp_access_token: str,
    whatsapp_phone_number_id: str,
    api_version: str = "v23.0",
) -> dict[str, Any]:
    """Send the generated reply through the Meta WhatsApp Cloud API."""
    to_phone = appointment.get("patient_phone")
    reply_text = appointment.get("reply_text")
    if not to_phone:
        raise ValueError("patient_phone is required")
    if not reply_text:
        raise ValueError("reply_text is required")

    url = f"https://graph.facebook.com/{api_version}/{whatsapp_phone_number_id}/messages"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {whatsapp_access_token}"},
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
