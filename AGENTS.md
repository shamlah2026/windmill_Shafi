# Agent Guidance

This repository is for a Windmill-based WhatsApp dentist appointment assistant.

## Goals

- Keep scripts small and Windmill-friendly.
- Expose one `main(...)` function per script.
- Never commit API tokens, webhook verify tokens, phone numbers, patient data, or calendar credentials.
- Prefer Windmill secrets/resources for credentials.
- Make scripts independently testable before wiring them into a flow.

## Expected flow

1. `extract_appointment.py` parses incoming WhatsApp webhook payloads.
2. `check_calendar_availability.py` checks the requested time range.
3. `create_calendar_event.py` creates a confirmed event.
4. `generate_reply.py` creates the patient-facing WhatsApp message.
5. `send_whatsapp.py` sends the reply with Meta WhatsApp Cloud API.

## Coding style

- Python 3.11+.
- Use `requests` for HTTP calls.
- Return dictionaries from `main(...)` so Windmill can pass data between steps.
- Raise clear `ValueError` messages for missing required input.
- Keep secrets as function arguments supplied by Windmill, not module constants.
