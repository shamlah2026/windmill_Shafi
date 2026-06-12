from typing import Any
from datetime import datetime


def format_datetime(dt: str | None) -> str:
    if not dt:
        return "your requested time"
    try:
        return datetime.fromisoformat(dt).strftime("%d/%m/%Y at %H:%M")
    except Exception:
        return dt


def main(appointment: dict[str, Any] | None = None) -> dict[str, Any]:
    if appointment is None:
        appointment = {}

    patient_name = appointment.get("patient_name") or "Patient"
    patient_phone = appointment.get("patient_phone") or ""
    doctor = appointment.get("doctor") or "our dentist"
    requested_start = format_datetime(appointment.get("requested_start"))

    clinic_name = "Pavia Smile Dental Clinic"
    clinic_address = "Via Roma 25, 27100 Pavia, Italy"

    if appointment.get("needs_clarification"):
        reply = (
            f"👋 Hello {patient_name}, thank you for contacting {clinic_name}.\n\n"
            f"🦷 Please send your preferred appointment date and time.\n"
            f"Example: tomorrow at 10:00 with Dr Ali."
        )
    else:
        reply = (
            f"✅ Appointment confirmed!\n\n"
            f"👤 Patient: {patient_name}\n"
            f"🦷 Doctor: {doctor}\n"
            f"📅 Date & Time: {requested_start}\n"
            f"📍 Address: {clinic_address}\n\n"
            f"Thank you for choosing {clinic_name}. See you soon! 😊"
        )

    return {
        **appointment,
        "patient_phone": patient_phone,
        "reply_text": reply,
        "event_created": True,
        "event_reason": "temporary_confirmation_without_calendar",
    }