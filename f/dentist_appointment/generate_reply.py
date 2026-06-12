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
            "reply_text": "⚠️ Sorry, something went wrong while processing your appointment request."
        }

    patient_name = appointment.get("patient_name") or "Patient"
    patient_phone = appointment.get("patient_phone", "")
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

    elif appointment.get("event_created"):
        reply = (
            f"✅ Appointment confirmed!\n\n"
            f"👤 Patient: {patient_name}\n"
            f"🦷 Doctor: {doctor}\n"
            f"📅 Date & Time: {requested_start}\n"
            f"📍 Address: {clinic_address}\n\n"
            f"Thank you for choosing {clinic_name}. See you soon!"
        )

    elif appointment.get("available") is False:
        reply = (
            f"❌ Sorry {patient_name}, that time is not available.\n\n"
            f"📅 Requested time: {requested_start}\n"
            f"🦷 Doctor: {doctor}\n\n"
            f"Please send another date or time."
        )

    else:
        reply = (
            f"👋 Hello {patient_name}, we received your appointment request.\n\n"
            f"🦷 Doctor: {doctor}\n"
            f"📅 Requested time: {requested_start}\n\n"
            f"We will confirm it shortly."
        )

    return {
        **appointment,
        "patient_phone": patient_phone,
        "reply_text": reply
    }