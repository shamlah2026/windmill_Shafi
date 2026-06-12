# Meta WhatsApp Webhook Verification Route

Use this for the Windmill Cloud HTTP route:

```text
GET https://app.windmill.dev/api/r/shamlah/meta-verify
```

Meta will call it with dotted query parameters:

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

Add this preprocessor to the HTTP route:

```ts
export async function preprocessor(event: {
  kind: "http";
  query: Record<string, string>;
}) {
  if (event.kind !== "http") {
    throw new Error(`Expected HTTP route event, got ${event.kind}`);
  }

  return {
    hub_mode: event.query["hub.mode"] ?? event.query["hub_mode"] ?? event.query["mode"] ?? "",
    hub_verify_token:
      event.query["hub.verify_token"] ??
      event.query["hub_verify_token"] ??
      event.query["verify_token"] ??
      "",
    hub_challenge:
      event.query["hub.challenge"] ??
      event.query["hub_challenge"] ??
      event.query["challenge"] ??
      "",
  };
}
```

## Windmill variable

Create this Windmill variable/secret:

```text
u/shamlahtanai/whatsapp_verify_token = ShafiDentistWebhook2026!
```

## Test

Open this URL in the browser:

```text
https://app.windmill.dev/api/r/shamlah/meta-verify?hub.mode=subscribe&hub.verify_token=ShafiDentistWebhook2026!&hub.challenge=123456
```

Expected response body:

```text
123456
```
