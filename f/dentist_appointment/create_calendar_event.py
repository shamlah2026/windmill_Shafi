from typing import Any

import requests


GOOGLE_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"


def main(
    appointment: dict[str, Any],
    google_access_token: str,
    calendar_id: str = "primary",
    clinic_timezone: str = "Europe/Berlin",
) -> dict[str, Any]:
    """Create a Google Calendar event for an available appointment."""
    if not appointment.get("available"):
        return {
            **appointment,
            "event_created": False,
            "event_reason": "slot_not_available",
        }

    requested_start = appointment.get("requested_start")
    requested_end = appointment.get("requested_end")
    if not requested_start or not requested_end:
        raise ValueError("requested_start and requested_end are required to create an event")

    patient_name = appointment.get("patient_name") or "Patient"
    patient_phone = appointment.get("patient_phone") or "unknown"

    response = requests.post(
        GOOGLE_EVENTS_URL.format(calendar_id=calendar_id),
        headers={"Authorization": f"Bearer {google_access_token}"},
        json={
            "summary": f"Dentist appointment - {patient_name}",
            "description": f"Booked from WhatsApp. Patient phone: {patient_phone}",
            "start": {"dateTime": requested_start, "timeZone": clinic_timezone},
            "end": {"dateTime": requested_end, "timeZone": clinic_timezone},
        },
        timeout=20,
    )
    response.raise_for_status()
    event = response.json()

    return {
        **appointment,
        "event_created": True,
        "event_id": event.get("id"),
        "event_link": event.get("htmlLink"),
    }
