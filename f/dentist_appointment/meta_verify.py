from typing import Any

import wmill


VERIFY_TOKEN_PATH = "u/shamlahtanai/whatsapp_verify_token"


def _plain_response(value: str, status_code: int = 200) -> dict[str, Any]:
    return {
        "wm_status_code": status_code,
        "wm_content_type": "text/plain; charset=utf-8",
        "result": value,
    }


def main(
    hub_mode: str = "",
    hub_verify_token: str = "",
    hub_challenge: str = "",
    verify_token: str | None = None,
) -> dict[str, Any]:
    """Verify Meta WhatsApp webhook setup and return the challenge as plain text."""
    expected = verify_token or wmill.get_variable(VERIFY_TOKEN_PATH)

    if hub_mode == "subscribe" and hub_verify_token == expected and hub_challenge:
        return _plain_response(str(hub_challenge))

    return _plain_response("Invalid verification", status_code=403)
