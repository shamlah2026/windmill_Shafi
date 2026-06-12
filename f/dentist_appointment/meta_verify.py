def main(
    hub_mode: str = "",
    hub_verify_token: str = "",
    hub_challenge: str = "",
) -> str:
    expected = "ShafiDentistWebhook2026!"

    if hub_mode == "subscribe" and hub_verify_token == expected:
        return hub_challenge

    raise ValueError("Invalid verification")