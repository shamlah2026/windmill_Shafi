# Meta WhatsApp Webhook Verification Route

Use this for the Windmill Cloud HTTP route:

```text
GET https://app.windmill.dev/api/r/shamlah/meta-verify
```

Meta calls it with dotted query parameters:

```text
?hub.mode=subscribe&hub.verify_token=...&hub.challenge=123456
```

## Runnable

- Script: `f/dentist_appointment/meta_verify`
- Request type: `Sync`
- Auth: `No Auth`
- Method: `GET`

## Body Processing

- Wrap body: `Off`
- Raw body: `Off`

The verification request is a GET request with query parameters, so body processing is not needed.

## Preprocessor

Do not look for a separate preprocessor field in the HTTP route UI.

The script itself defines a Python `preprocessor(event)` function. Windmill calls that function for HTTP route events before it calls `main()`. The preprocessor reads these exact Meta query names:

- `hub.mode`
- `hub.verify_token`
- `hub.challenge`

Then it maps them into normal Python arguments:

- `hub_mode`
- `hub_verify_token`
- `hub_challenge`

This is why the exact Meta URL works without changing the query string.

## Windmill variable

Create this Windmill variable/secret:

```text
u/shamlahtanai/whatsapp_verify_token = ShafiDentistWebhook2026!
```

## Test

Open this exact URL in the browser:

```text
https://app.windmill.dev/api/r/shamlah/meta-verify?hub.mode=subscribe&hub.verify_token=ShafiDentistWebhook2026!&hub.challenge=123456
```

Expected response body:

```text
123456
```
