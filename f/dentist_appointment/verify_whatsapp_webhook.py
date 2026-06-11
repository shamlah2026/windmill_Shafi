from typing import Any

try:
    import wmill
except Exception:  # pragma: no cover
    wmill = None


def _get_variable(path: str, default: Any = None) -> Any:
    if wmill is None:
        return default
    try:
        value = wmill.get_variable(path)
        return value if value not in (None, "") else default
    except Exception:
        return default


def main(
    query: dict[str, Any],
    verify_token: str | None = None,
) -> str:
    """Return Meta's webhook challenge when the verify token matches."""
    expected = verify_token or _get_variable("u/shamlahtanai/whatsapp_verify_token")
    mode = query.get("hub.mode") or query.get("mode")
    token = query.get("hub.verify_token") or query.get("verify_token")
    challenge = query.get("hub.challenge") or query.get("challenge")

    if mode == "subscribe" and expected and token == expected and challenge:
        return str(challenge)
    raise ValueError("Invalid WhatsApp webhook verification request")
