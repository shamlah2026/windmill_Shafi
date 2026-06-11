import json
import re
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    import wmill
except Exception:  # pragma: no cover - lets the script run outside Windmill too.
    wmill = None


ISO_DATETIME_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})(?:[ T](\d{1,2}:\d{2}))?\b")
TIME_RE = re.compile(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", re.IGNORECASE)


def _as_dict(payload: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(payload, str):
        return json.loads(payload)
    if isinstance(payload, dict) and isinstance(payload.get("body"), str):
        try:
            return json.loads(payload["body"])
        except json.JSONDecodeError:
            return payload
    return payload


def _first_text_message(payload: dict[str, Any]) -> dict[str, Any]:
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            contacts = value.get("contacts", [])
            for message in value.get("messages", []):
                text = message.get("text", {}).get("body", "").strip()
                if not text:
                    continue
                return {
                    "patient_phone": message.get("from"),
                    "message_id": message.get("id"),
                    "message_text": text,
                    "patient_name": contacts[0].get("profile", {}).get("name") if contacts else None,
                    "raw_message": message,
                }
    raise ValueError("No WhatsApp text message found in payload")


def _parse_requested_datetime(text: str, now_iso: str | None, clinic_timezone: str) -> str | None:
    if now_iso:
        now = datetime.fromisoformat(now_iso)
    else:
        now = datetime.now(timezone.utc)

    lowered = text.lower()
    iso_match = ISO_DATETIME_RE.search(text)
    if iso_match:
        date_part, time_part = iso_match.groups()
        time_part = time_part or "09:00"
        return f"{date_part}T{time_part}:00"

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

    return datetime.combine(target_date, datetime.min.time()).replace(hour=hour, minute=minute).isoformat()


def main(
    payload: dict[str, Any] | str,
    default_duration_minutes: int = 30,
    now_iso: str | None = None,
    clinic_timezone: str = "Europe/Berlin",
) -> dict[str, Any]:
    """Extract appointment request details from a Meta WhatsApp webhook payload."""
    message = _first_text_message(_as_dict(payload))
    requested_start = _parse_requested_datetime(message["message_text"], now_iso, clinic_timezone)

    return {
        "patient_name": message.get("patient_name") or "Patient",
        "patient_phone": message["patient_phone"],
        "message_id": message.get("message_id"),
        "message_text": message["message_text"],
        "requested_start": requested_start,
        "duration_minutes": int(default_duration_minutes),
        "clinic_timezone": clinic_timezone,
        "needs_clarification": requested_start is None,
    }
