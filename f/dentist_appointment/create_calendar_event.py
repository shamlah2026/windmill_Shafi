from typing import Any

import requests

try:
    import wmill
except Exception:  # pragma: no cover
    wmill = None


GOOGLE_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"


def _get_variable(path: str, default: Any = None) -> Any:
    if wmill is None:
        return default
    try:
        value = wmill.get_variable(path)
        return value if value not in (None, "") else default
    except Exception:
        return default


def _get_resource(path: str) -> dict[str, Any]:
    if wmill is None:
        return {}
    try:
        value = wmill.get_resource(path)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _google_token(google_calendar: dict[str, Any] | None, google_access_token: str | None) -> str:
    resource = google_calendar or _get_resource("u/google/calendar")
    token = google_access_token or resource.get("access_token") or resource.get("token")
    token = token or _get_variable("u/google/calendar_access_token")
    if not token:
        raise ValueError("Missing Google Calendar access token. Configure u/google/calendar resource or u/google/calendar_access_token variable.")
    return token


def main(
    appointment: dict[str, Any],
    google_calendar: dict[str, Any] | None = None,
    google_access_token: str | None = None,
    calendar_id: str | None = None,
    clinic_timezone: str | None = None,
) -> dict[str, Any]:
    """Create a Google Calendar event for an available appointment."""
    if not appointment.get("available"):
        return {**appointment, "event_created": False, "event_reason": "slot_not_available"}

    requested_start = appointment.get("requested_start")
    requested_end = appointment.get("requested_end")
    if not requested_start or not requested_end:
        raise ValueError("requested_start and requested_end are required to create an event")

    calendar_id = calendar_id or appointment.get("calendar_id") or _get_variable("u/google/calendar_id", "primary")
    clinic_timezone = clinic_timezone or appointment.get("clinic_timezone") or _get_variable("u/clinic/timezone", "Europe/Berlin")
    patient_name = appointment.get("patient_name") or "Patient"
    patient_phone = appointment.get("patient_phone") or "unknown"

    response = requests.post(
        GOOGLE_EVENTS_URL.format(calendar_id=calendar_id),
        headers={"Authorization": f"Bearer {_google_token(google_calendar, google_access_token)}"},
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
