from typing import Any


def main(appointment: dict[str, Any] | None = None) -> dict[str, Any]:
    if appointment is None:
        return {
            "available": False,
            "availability_reason": "missing_appointment_input",
            "requested_end": None,
            "busy": [],
        }

    requested_start = appointment.get("requested_start")

    if not requested_start:
        return {
            **appointment,
            "available": False,
            "availability_reason": "missing_requested_start",
            "requested_end": None,
            "busy": [],
        }

    return {
        **appointment,
        "calendar_id": "fake_calendar",
        "requested_end": None,
        "available": True,
        "availability_reason": "temporary_fake_available",
        "busy": [],
    }