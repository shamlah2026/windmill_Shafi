import re
from datetime import datetime, timedelta, timezone
from typing import Any


ISO_DATETIME_RE = re.compile(
    r"\b(\d{4}-\d{2}-\d{2})(?:[ T](\d{1,2}:\d{2}))?\b"
)
TIME_RE = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", re.IGNORECASE)


def _first_text_message(payload: dict[str, Any]) -> dict[str, Any]:
    entries = payload.get("entry", [])
    for entry in entries:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = value.get("contacts", [])
            messages = value.get("messages", [])
            if not messages:
                continue
            message = messages[0]
            text = message.get("text", {}).get("body", "")
            return {
                "from_phone": message.get("from"),
                "message_id": message.get("id"),
                "message_text": text.strip(),
                "patient_name": contacts[0].get("profile", {}).get("name") if contacts else None,
                "raw_message": message,
            }
    raise ValueError("No WhatsApp text message found in payload")


def _parse_requested_datetime(text: str, now_iso: str | None = None) -> str | None:
    now = datetime.fromisoformat(now_iso) if now_iso else datetime.now(timezone.utc)
    lowered = text.lower()

    iso_match = ISO_DATETIME_RE.search(text)
    if iso_match:
        date_part, time_part = iso_match.groups()
        time_part = time_part or "09:00"
        parsed = datetime.fromisoformat(f"{date_part}T{time_part}:00")
        return parsed.isoformat()

    target_date = None
    if "tomorrow" in lowered:
        target_date = (now + timedelta(days=1)).date()
    elif "today" in lowered:
        target_date = now.date()

    if not target_date:
        return None

    time_match = TIME_RE.search(lowered)
    hour = 9
    minute = 0
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        suffix = time_match.group(3)
        if suffix and suffix.lower() == "pm" and hour < 12:
            hour += 12
        if suffix and suffix.lower() == "am" and hour == 12:
            hour = 0

    return datetime.combine(target_date, datetime.min.time()).replace(
        hour=hour,
        minute=minute,
    ).isoformat()


def main(payload: dict[str, Any], default_duration_minutes: int = 30, now_iso: str | None = None) -> dict[str, Any]:
    """Extract appointment request details from a Meta WhatsApp webhook payload."""
    message = _first_text_message(payload)
    requested_start = _parse_requested_datetime(message["message_text"], now_iso=now_iso)

    return {
        "patient_name": message.get("patient_name") or "Patient",
        "patient_phone": message["from_phone"],
        "message_id": message.get("message_id"),
        "message_text": message["message_text"],
        "requested_start": requested_start,
        "duration_minutes": default_duration_minutes,
        "needs_clarification": requested_start is None,
    }
