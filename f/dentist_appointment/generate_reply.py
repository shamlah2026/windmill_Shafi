from datetime import datetime
from typing import Any


def _format_time(value: str | None) -> str:
    if not value:
        return "the requested time"
    try:
        return datetime.fromisoformat(value).strftime("%A, %d %B at %H:%M")
    except ValueError:
        return value


def main(appointment: dict[str, Any], clinic_name: str = "the dental clinic") -> dict[str, Any]:
    """Generate a patient-facing WhatsApp reply for the appointment flow."""
    patient_name = appointment.get("patient_name") or "there"

    if appointment.get("needs_clarification"):
        reply = (
            f"Hi {patient_name}, thanks for contacting {clinic_name}. "
            "What day and time would you like for your dentist appointment? "
            "You can reply like: tomorrow 10:30 or 2026-06-15 14:00."
        )
    elif appointment.get("event_created"):
        reply = (
            f"Hi {patient_name}, your dentist appointment is confirmed for "
            f"{_format_time(appointment.get('requested_start'))}. See you soon."
        )
    elif appointment.get("available") is False:
        reply = (
            f"Hi {patient_name}, sorry, {_format_time(appointment.get('requested_start'))} "
            "is not available. Please send another day and time."
        )
    else:
        reply = (
            f"Hi {patient_name}, thanks for your message. We received your appointment request "
            "and will confirm the time shortly."
        )

    return {
        **appointment,
        "reply_text": reply,
    }
