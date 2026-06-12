from typing import Any
from datetime import datetime


def format_datetime(dt: str | None) -> str:
    if not dt:
        return "the requested time"

    try:
        return datetime.fromisoformat(dt).strftime("%d/%m/%Y at %H:%M")
    except Exception:
        return dt


def main(appointment: dict[str, Any] | None = None) -> dict[str, Any]:

    if appointment is None:
        return {
            "patient_phone": "",
            "reply_text": "An unexpected error occurred."
        }

    patient_name = appointment.get("patient_name", "Patient")
    patient_phone = appointment.get("patient_phone", "")
    doctor = appointment.get("doctor", "our dentist")
    requested_start = format_datetime(appointment.get("requested_start"))

    if appointment.get("needs_clarification"):
        reply = (
            f"Hello {patient_name}, thank you for contacting our clinic. "
            f"Could you please specify your preferred appointment date and time?"
        )

    elif appointment.get("event_created"):

        reply = (
            f"Hello {patient_name}, your appointment with {doctor} "
            f"has been confirmed for {requested_start}. "
            f"We look forward to seeing you."
        )

    elif appointment.get("available") is False:

        reply = (
            f"Hello {patient_name}, unfortunately the requested time is not available. "
            f"Please send another preferred date or time."
        )

    else:

        reply = (
            f"Hello {patient_name}, we have received your appointment request "
            f"and will confirm it shortly."
        )

    return {
        **appointment,
        "patient_phone": patient_phone,
        "reply_text": reply
    }