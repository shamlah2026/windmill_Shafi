# Windmill Dentist Appointment Assistant

End-to-end starter for handling WhatsApp dentist appointment requests with Windmill.

The target flow is:

1. Receive a WhatsApp webhook payload from Meta.
2. Extract the patient message, phone number, requested date/time, and appointment details.
3. Check calendar availability.
4. Create a calendar event when the slot is available.
5. Generate a patient-friendly reply.
6. Send the reply through the WhatsApp Cloud API.

## Repository layout

```text
windmill-dentist-appointment/
├── scripts/
│   ├── extract_appointment.py
│   ├── check_calendar_availability.py
│   ├── create_calendar_event.py
│   ├── generate_reply.py
│   └── send_whatsapp.py
├── flows/
│   └── dentist_appointment_flow.yaml
├── AGENTS.md
└── README.md
```

## Windmill Cloud setup

Use your empty GitHub repository with Windmill Git Sync.

1. Open Windmill Cloud.
2. Go to Workspace settings -> Git Sync.
3. Add a Git repository connection for:
   `https://github.com/shamlah2026/windmill_Shafi.git`
4. Prefer the Windmill GitHub App connection if available.
5. If you use a Personal Access Token instead, it needs read/write access to repository contents.
6. Save the connection.
7. If Windmill asks to initialize the repository, skip initialization if these files already exist. Otherwise let Windmill create `wmill.yaml`, then pull/merge this code.

Windmill's Git Sync docs say an empty repo is the recommended starting point, and Windmill can create `wmill.yaml` and push workspace content during initialization.

## Windmill variables and secrets

Create these in Windmill as secrets or resources. Do not commit them to Git.

### WhatsApp / Meta

- `u/meta/whatsapp_access_token`: permanent or long-lived WhatsApp Cloud API token.
- `u/meta/whatsapp_phone_number_id`: Phone Number ID from Meta.
- `u/meta/whatsapp_verify_token`: token you choose for webhook verification.
- `u/meta/whatsapp_api_version`: optional, for example `v23.0`.

### Calendar

- `u/google/calendar_access_token`: Google OAuth access token or resource-backed token.
- `u/google/calendar_id`: calendar id, usually `primary` or the clinic calendar email.

For production, prefer a proper Windmill resource/OAuth connection over copying access tokens manually.

## Meta WhatsApp setup checklist

1. Go to Meta for Developers.
2. Create or open an app.
3. Add WhatsApp product.
4. Add or connect a WhatsApp Business phone number.
5. Copy the Phone Number ID.
6. Generate a token for the WhatsApp Cloud API.
7. Configure a webhook callback URL from Windmill.
8. Subscribe to WhatsApp `messages` webhook events.
9. Store token, phone number id, and verify token in Windmill secrets.

## Development order

1. Deploy `scripts/extract_appointment.py` first and test it with a sample WhatsApp webhook payload.
2. Deploy `scripts/generate_reply.py` second so you can test the response text without external APIs.
3. Add `scripts/send_whatsapp.py` after Meta token and phone number id are ready.
4. Add calendar availability and event creation after Google Calendar auth is ready.
5. Wire everything into a Windmill flow.

## Notes

The scripts are written with Windmill-friendly `main(...)` functions. The flow YAML is a blueprint for the intended orchestration; if Windmill generates its own exported flow schema, use the Windmill-generated YAML as the source of truth and keep this flow updated from Windmill Git Sync.
