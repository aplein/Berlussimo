"""Kleiner Client für die Fooocus-API (REST-Wrapper für Fooocus).

Siehe README zum Starten der Fooocus-API. Es wird der Endpunkt
`POST /v1/generation/text-to-image` synchron pro Bild aufgerufen, damit wir
den Fortschritt Bild für Bild verfolgen können.
"""
import base64
import requests

import config


class FooocusError(RuntimeError):
    """Fehler bei der Kommunikation mit der Fooocus-API."""


class FooocusClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or config.FOOOCUS_API_URL).rstrip("/")

    def is_available(self) -> bool:
        """Prüft, ob die Fooocus-API erreichbar ist."""
        try:
            # Die OpenAPI-Doku ist immer vorhanden, wenn die API läuft.
            resp = requests.get(self.base_url + "/docs", timeout=5)
            return resp.status_code < 500
        except requests.RequestException:
            return False

    def text_to_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        styles: list[str] | None = None,
        aspect_ratio: str | None = None,
        seed: int = -1,
    ) -> bytes:
        """Erzeugt ein einzelnes Bild und gibt die PNG-Bytes zurück."""
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "style_selections": styles or ["Fooocus V2"],
            "performance_selection": config.PERFORMANCE,
            "aspect_ratios_selection": aspect_ratio or config.ASPECT_RATIO,
            "image_number": 1,
            "image_seed": seed,
            "require_base64": True,
            "async_process": False,
        }
        url = self.base_url + "/v1/generation/text-to-image"
        try:
            resp = requests.post(url, json=payload, timeout=config.GENERATION_TIMEOUT)
        except requests.RequestException as exc:
            raise FooocusError(f"Fooocus-API nicht erreichbar: {exc}") from exc

        if resp.status_code != 200:
            raise FooocusError(
                f"Fooocus-API antwortete mit Status {resp.status_code}: {resp.text[:300]}"
            )

        try:
            data = resp.json()
        except ValueError as exc:
            raise FooocusError("Ungültige Antwort von der Fooocus-API.") from exc

        if not isinstance(data, list) or not data:
            raise FooocusError(f"Unerwartete Antwort von der Fooocus-API: {data}")

        item = data[0]
        if item.get("finish_reason") and item["finish_reason"] not in ("SUCCESS", None):
            raise FooocusError(f"Generierung fehlgeschlagen: {item.get('finish_reason')}")

        b64 = item.get("base64")
        if not b64:
            raise FooocusError("Antwort der Fooocus-API enthielt kein Bild.")

        return base64.b64decode(b64)
