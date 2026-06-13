"""Konfiguration für den Malbuch-Generator.

Werte können über Umgebungsvariablen (oder eine .env-Datei) überschrieben
werden. Für den normalen Betrieb reicht es meistens, FOOOCUS_API_URL
anzupassen, falls die Fooocus-API nicht unter dem Standard-Port läuft.
"""
import os
from pathlib import Path

# .env optional einlesen (ohne Zusatz-Abhängigkeit)
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#") or "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        os.environ.setdefault(_k.strip(), _v.strip())

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Port, auf dem die Malbuch-App läuft.
APP_PORT = int(os.environ.get("APP_PORT", "5010"))

# Adresse der Fooocus-API (REST-Wrapper für Fooocus). Standard-Port: 8888.
FOOOCUS_API_URL = os.environ.get("FOOOCUS_API_URL", "http://127.0.0.1:8888")

# Wie lange (Sekunden) auf ein einzelnes Bild gewartet wird, bevor abgebrochen wird.
GENERATION_TIMEOUT = int(os.environ.get("GENERATION_TIMEOUT", "600"))

# Maximale Bildanzahl pro Auftrag (Sicherheitsgrenze).
MAX_IMAGES = int(os.environ.get("MAX_IMAGES", "60"))

# Fooocus-Performance: "Speed", "Quality" oder "Extreme Speed".
PERFORMANCE = os.environ.get("FOOOCUS_PERFORMANCE", "Speed")

# Seitenverhältnis im Fooocus-Format "Breite*Höhe" (Hochformat für Buchseiten).
ASPECT_RATIO = os.environ.get("FOOOCUS_ASPECT_RATIO", "896*1152")


# Stil-Vorlagen. Jede Vorlage beschreibt, wie aus dem Thema ein Prompt wird.
# "prompt_suffix" wird an das Thema angehängt, "negative" hält unerwünschte
# Dinge fern, "styles" sind Fooocus-Stilnamen.
STYLE_PRESETS = {
    "lineart": {
        "label": "Malbuch – klare Linien (Standard)",
        "prompt_suffix": (
            "black and white line art, coloring book page, clean bold outlines, "
            "no shading, no color, no grayscale, pure white background, simple, cute"
        ),
        "negative": (
            "color, colored, shading, gradient, grayscale, gray, photo, realistic, "
            "3d, complex background, text, watermark, signature, blurry, noisy"
        ),
        "styles": ["Fooocus V2"],
    },
    "kawaii": {
        "label": "Malbuch – niedlich / Kawaii",
        "prompt_suffix": (
            "cute kawaii style, black and white line art, coloring book page for kids, "
            "thick clean outlines, big friendly shapes, no shading, white background"
        ),
        "negative": (
            "color, shading, gradient, grayscale, scary, realistic, photo, text, "
            "watermark, blurry, complex details"
        ),
        "styles": ["Fooocus V2"],
    },
    "mandala": {
        "label": "Mandala / Muster",
        "prompt_suffix": (
            "symmetrical mandala, black and white line art, intricate decorative outlines, "
            "coloring page, no shading, no color, white background, centered"
        ),
        "negative": (
            "color, shading, grayscale, photo, realistic, text, watermark, asymmetrical, blurry"
        ),
        "styles": ["Fooocus V2"],
    },
    "detailed": {
        "label": "Malbuch – detailliert (Erwachsene)",
        "prompt_suffix": (
            "detailed black and white line art, intricate coloring book page for adults, "
            "fine clean outlines, no shading, no color, white background"
        ),
        "negative": (
            "color, shading, gradient, grayscale, photo, realistic, text, watermark, blurry"
        ),
        "styles": ["Fooocus V2"],
    },
}

DEFAULT_STYLE = "lineart"
