from typing import Any


def main(appointment: dict[str, Any] | None = None) -> dict[str, Any]:
    if appointment is None:
        return {
            "event_created": False,
            "event_reason": "missing_appointment_input",
        }

    if not appointment.get("available"):
        return {
            **appointment,
            "event_created": False,
            "event_reason": "slot_not_available",
        }

    return {
        **appointment,
        "event_created": True,
        "event_reason": "temporary_fake_event_created",
        "event_id": "fake_event_001",
        "event_link": None,
    }