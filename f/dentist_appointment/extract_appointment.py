import re
from datetime import datetime, timedelta, timezone
from typing import Any


ISO_DATETIME_RE = re.compile(
    r"\b(\d{4}-\d{2}-\d{2})(?:[ T](\d{1,2}:\d{2}))?\b"
)

TIME_RE = re.compile(
    r"\b(?:at\s*)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b",
    re.IGNORECASE,
)


def _parse_requested_datetime(
    text: str,
    now_iso: str | None = None,
    clinic_timezone: str = "Europe/Rome",
) -> str | None:
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

        if suffix:
            suffix = suffix.lower()
            if suffix == "pm" and hour < 12:
                hour += 12
            elif suffix == "am" and hour == 12:
                hour = 0

    return (
        datetime.combine(target_date, datetime.min.time())
        .replace(hour=hour, minute=minute)
        .isoformat()
    )


def _extract_doctor(message_text: str) -> str:
    lowered = message_text.lower()

    if "dr ali" in lowered or "doctor ali" in lowered or "ali" in lowered:
        return "Dr Ali"

    return "General Dentist"


def _extract_patient_name(message_text: str) -> str:
    lowered = message_text.lower()

    patterns = [
        r"my name is ([a-zA-Z\s]+)",
        r"i am ([a-zA-Z\s]+)",
        r"this is ([a-zA-Z\s]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            name = match.group(1).strip()
            return name.title()

    return "Patient"


def main(
    patient_phone: str,
    message_text: str,
    patient_name: str = "",
    default_duration_minutes: int = 30,
    now_iso: str | None = None,
    clinic_timezone: str = "Europe/Rome",
) -> dict[str, Any]:
    requested_start = _parse_requested_datetime(
        message_text,
        now_iso=now_iso,
        clinic_timezone=clinic_timezone,
    )

    extracted_name = patient_name or _extract_patient_name(message_text)
    doctor = _extract_doctor(message_text)

    return {
        "patient_name": extracted_name,
        "patient_phone": patient_phone,
        "message_text": message_text,
        "doctor": doctor,
        "service": "Dentist",
        "requested_start": requested_start,
        "duration_minutes": int(default_duration_minutes),
        "clinic_timezone": clinic_timezone,
        "needs_clarification": requested_start is None,
    }