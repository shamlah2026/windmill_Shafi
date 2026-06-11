# Windmill Dentist Appointment Assistant

End-to-end Windmill Cloud project for a dentist appointment assistant:

```text
WhatsApp webhook -> extract appointment -> check calendar -> create event if free -> generate reply -> send WhatsApp reply
```

## Windmill Cloud layout

Windmill Git Sync is configured through `wmill.yaml` and currently syncs `f/**`. The Cloud-ready scripts are therefore under:

```text
f/dentist_appointment/
├── extract_appointment.py
├── verify_whatsapp_webhook.py
├── check_calendar_availability.py
├── create_calendar_event.py
├── generate_reply.py
└── send_whatsapp.py
```

The same scripts are mirrored under `scripts/` for local editing, notebook experiments, and readability:

```text
scripts/
├── extract_appointment.py
├── verify_whatsapp_webhook.py
├── check_calendar_availability.py
├── create_calendar_event.py
├── generate_reply.py
└── send_whatsapp.py
```

## Windmill resources and variables

Do not commit secrets. Create these in Windmill Cloud.

### Preferred resources

Create these as Windmill resources when possible:

- `u/meta/whatsapp`
  - `access_token`
  - `phone_number_id`
  - `api_version`, for example `v23.0`
- `u/openai/default`
  - `api_key`
  - `model`, for example `gpt-4.1-mini`
- `u/google/calendar`
  - `access_token`

### Supported fallback variables

The scripts also support these variables/secrets:

- `u/clinic/name`
- `u/clinic/timezone`, for example `Europe/Berlin`
- `u/meta/whatsapp_verify_token`
- `u/meta/whatsapp_access_token`
- `u/meta/whatsapp_phone_number_id`
- `u/meta/whatsapp_api_version`
- `u/openai/api_key`
- `u/openai/model`
- `u/google/calendar_access_token`
- `u/google/calendar_id`, usually `primary` or the clinic calendar email

## Scripts

Every Python script exposes a Windmill-compatible `main()` function.

- `extract_appointment.py`: parses Meta WhatsApp webhook payloads and extracts patient phone, message text, requested start time, duration, and clarification status.
- `verify_whatsapp_webhook.py`: returns Meta's challenge when the webhook verify token matches.
- `check_calendar_availability.py`: calls Google Calendar FreeBusy and returns whether the requested slot is available.
- `create_calendar_event.py`: creates a Google Calendar event only when the slot is free.
- `generate_reply.py`: uses OpenAI when configured and falls back to a deterministic template when not configured.
- `send_whatsapp.py`: sends the final text message with the Meta WhatsApp Cloud API.

## Build the Windmill flow

Use `flows/dentist_appointment_flow.yaml` as the wiring map. In Windmill Cloud, create a flow with these steps:

1. `extract_appointment`: `f/dentist_appointment/extract_appointment.py`
2. If `needs_clarification` is false: `check_calendar_availability`
3. If `available` is true: `create_calendar_event`
4. `generate_reply` using either the booking result, unavailable result, or clarification result
5. `send_whatsapp`

For Meta webhook verification, use `f/dentist_appointment/verify_whatsapp_webhook.py` with the verify token stored in `u/meta/whatsapp_verify_token`.

## Meta WhatsApp setup checklist

1. In Meta for Developers, create or open an app.
2. Add the WhatsApp product.
3. Add or connect your WhatsApp Business phone number.
4. Copy the Phone Number ID into Windmill.
5. Create a long-lived/permanent access token and store it as a Windmill secret/resource.
6. Configure the Windmill webhook URL in Meta.
7. Subscribe to WhatsApp `messages` webhook events.
8. Test with a simple message such as `I need a dentist appointment tomorrow at 10:30`.

## Local notebook use

Your `windmill_Whatsapp.ipynb` can import or copy from `scripts/` for local experiments. The production Windmill source of truth is `f/dentist_appointment/` because that is what Git Sync includes.
