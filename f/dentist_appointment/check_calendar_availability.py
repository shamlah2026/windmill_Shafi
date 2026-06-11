from datetime import datetime, timedelta
from typing import Any

import requests


GOOGLE_FREEBUSY_URL = "https://www.googleapis.com/calendar/v3/freeBusy"


def _end_time(start_iso: str, duration_minutes: int) -> str:
    start = datetime.fromisoformat(start_iso)
    return (start + timedelta(minutes=duration_minutes)).isoformat()


def main(
    appointment: dict[str, Any],
    google_access_token: str,
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Check whether the requested appointment slot is free in Google Calendar."""
    requested_start = appointment.get("requested_start")
    if not requested_start:
        return {
            **appointment,
            "available": False,
            "availability_reason": "missing_requested_start",
        }

    duration = int(appointment.get("duration_minutes") or 30)
    requested_end = _end_time(requested_start, duration)

    response = requests.post(
        GOOGLE_FREEBUSY_URL,
        headers={"Authorization": f"Bearer {google_access_token}"},
        json={
            "timeMin": requested_start,
            "timeMax": requested_end,
            "items": [{"id": calendar_id}],
        },
        timeout=20,
    )
    response.raise_for_status()

    body = response.json()
    busy = body.get("calendars", {}).get(calendar_id, {}).get("busy", [])

    return {
        **appointment,
        "calendar_id": calendar_id,
        "requested_end": requested_end,
        "available": len(busy) == 0,
        "busy": busy,
    }
