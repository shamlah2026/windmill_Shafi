from datetime import datetime, timedelta
from typing import Any

import requests

try:
    import wmill
except Exception:  # pragma: no cover
    wmill = None


GOOGLE_FREEBUSY_URL = "https://www.googleapis.com/calendar/v3/freeBusy"


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


def _end_time(start_iso: str, duration_minutes: int) -> str:
    start = datetime.fromisoformat(start_iso)
    return (start + timedelta(minutes=duration_minutes)).isoformat()


def main(
    appointment: dict[str, Any],
    google_calendar: dict[str, Any] | None = None,
    google_access_token: str | None = None,
    calendar_id: str | None = None,
) -> dict[str, Any]:
    """Check whether the requested appointment slot is free in Google Calendar."""
    requested_start = appointment.get("requested_start")
    if not requested_start:
        return {**appointment, "available": False, "availability_reason": "missing_requested_start"}

    calendar_id = calendar_id or _get_variable("u/google/calendar_id", "primary")
    duration = int(appointment.get("duration_minutes") or 30)
    requested_end = _end_time(requested_start, duration)

    response = requests.post(
        GOOGLE_FREEBUSY_URL,
        headers={"Authorization": f"Bearer {_google_token(google_calendar, google_access_token)}"},
        json={"timeMin": requested_start, "timeMax": requested_end, "items": [{"id": calendar_id}]},
        timeout=20,
    )
    response.raise_for_status()

    busy = response.json().get("calendars", {}).get(calendar_id, {}).get("busy", [])
    return {
        **appointment,
        "calendar_id": calendar_id,
        "requested_end": requested_end,
        "available": len(busy) == 0,
        "busy": busy,
    }
