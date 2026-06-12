from typing import Any, Literal, Optional, TypedDict

import wmill


VERIFY_TOKEN_PATH = "u/shamlahtanai/whatsapp_verify_token"


class HttpEvent(TypedDict, total=False):
    kind: Literal["http"]
    query: dict[str, str]
    params: dict[str, str]
    headers: dict[str, str]
    body: Any
    raw_string: Optional[str]
    route: str
    path: str
    method: str
    trigger_path: str


def preprocessor(event: HttpEvent) -> dict[str, str]:
    """Map Meta's dotted query parameters into normal Python main() arguments."""
    if event.get("kind") != "http":
        raise ValueError(f"Expected HTTP route event, got {event.get('kind')}")

    query = event.get("query") or {}
    return {
        "hub_mode": query.get("hub.mode") or query.get("hub_mode") or query.get("mode") or "",
        "hub_verify_token": (
            query.get("hub.verify_token")
            or query.get("hub_verify_token")
            or query.get("verify_token")
            or ""
        ),
        "hub_challenge": (
            query.get("hub.challenge")
            or query.get("hub_challenge")
            or query.get("challenge")
            or ""
        ),
    }


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
