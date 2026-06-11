import requests
import wmill


ACCESS_TOKEN_PATH = "u/shamlahtanai/whatsapp_access_token"
PHONE_NUMBER_ID_PATH = "u/shamlahtanai/whatsapp_phone_number_id"
API_VERSION_PATH = "u/shamlahtanai/whatsapp_api_version"

print(wmill.get_variable("u/shamlahtanai/whatsapp_access_token"))
def main(
    patient_phone: str,
    reply_text: str,
) -> dict:
    """
    Send a WhatsApp text message using Meta WhatsApp Cloud API.
    """

    access_token = wmill.get_variable(ACCESS_TOKEN_PATH)
    phone_number_id = wmill.get_variable(PHONE_NUMBER_ID_PATH)
    api_version = wmill.get_variable(API_VERSION_PATH) or "v25.0"

    if not access_token:
        raise ValueError("WhatsApp access token is missing.")

    if not phone_number_id:
        raise ValueError("WhatsApp phone number ID is missing.")

    if not patient_phone:
        raise ValueError("Patient phone number is missing.")

    if not reply_text:
        raise ValueError("Reply text is missing.")

    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": patient_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": reply_text,
        },
    }

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    try:
        meta_response = response.json()
    except Exception:
        meta_response = {"raw_response": response.text}

    if response.status_code >= 400:
        raise Exception(
            {
                "status_code": response.status_code,
                "meta_response": meta_response,
            }
        )

    return {
        "success": True,
        "sent_to": patient_phone,
        "message": reply_text,
        "status_code": response.status_code,
        "meta_response": meta_response,
    }