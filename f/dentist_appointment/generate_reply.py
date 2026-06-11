import json
from datetime import datetime
from typing import Any

import requests

try:
    import wmill
except Exception:  # pragma: no cover
    wmill = None


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


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


def _format_time(value: str | None) -> str:
    if not value:
        return "the requested time"
    try:
        return datetime.fromisoformat(value).strftime("%A, %d %B at %H:%M")
    except ValueError:
        return value


def _template_reply(appointment: dict[str, Any], clinic_name: str) -> str:
    patient_name = appointment.get("patient_name") or "there"
    if appointment.get("needs_clarification"):
        return (
            f"Hi {patient_name}, thanks for contacting {clinic_name}. "
            "What day and time would you like for your dentist appointment? "
            "You can reply like: tomorrow 10:30 or 2026-06-15 14:00."
        )
    if appointment.get("event_created"):
        return f"Hi {patient_name}, your dentist appointment is confirmed for {_format_time(appointment.get('requested_start'))}. See you soon."
    if appointment.get("available") is False:
        return f"Hi {patient_name}, sorry, {_format_time(appointment.get('requested_start'))} is not available. Please send another day and time."
    return f"Hi {patient_name}, thanks for your message. We received your appointment request and will confirm the time shortly."


def _openai_config(openai: dict[str, Any] | None, openai_api_key: str | None, openai_model: str | None) -> tuple[str | None, str]:
    resource = openai or _get_resource("u/openai/default")
    api_key = openai_api_key or resource.get("api_key") or resource.get("token") or _get_variable("u/openai/api_key")
    model = openai_model or resource.get("model") or _get_variable("u/openai/model", "gpt-4.1-mini")
    return api_key, model


def _extract_output_text(response_body: dict[str, Any]) -> str | None:
    if response_body.get("output_text"):
        return response_body["output_text"].strip()
    for item in response_body.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                return content["text"].strip()
    return None


def main(
    appointment: dict[str, Any],
    clinic_name: str | None = None,
    openai: dict[str, Any] | None = None,
    openai_api_key: str | None = None,
    openai_model: str | None = None,
    use_openai: bool = True,
) -> dict[str, Any]:
    """Generate a patient-facing WhatsApp reply, using OpenAI when configured."""
    clinic_name = clinic_name or _get_variable("u/clinic/name", "the dental clinic")
    fallback = _template_reply(appointment, clinic_name)

    api_key, model = _openai_config(openai, openai_api_key, openai_model)
    if not use_openai or not api_key:
        return {**appointment, "reply_text": fallback, "reply_generated_by": "template"}

    prompt = {
        "clinic_name": clinic_name,
        "appointment": appointment,
        "required_style": "Warm, concise WhatsApp reply. Do not mention internal systems, APIs, or uncertainty. Keep under 500 characters.",
        "fallback_reply": fallback,
    }
    response = requests.post(
        OPENAI_RESPONSES_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "input": [
                {"role": "system", "content": "You write short, safe, professional dentist appointment WhatsApp replies."},
                {"role": "user", "content": json.dumps(prompt, ensure_ascii=False)},
            ],
            "max_output_tokens": 180,
        },
        timeout=30,
    )
    response.raise_for_status()
    reply_text = _extract_output_text(response.json()) or fallback

    return {**appointment, "reply_text": reply_text, "reply_generated_by": "openai", "openai_model": model}
