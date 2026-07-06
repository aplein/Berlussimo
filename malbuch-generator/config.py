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
MAX_IMAGES = int(os.environ.get("MAX_IMAGES", "1000"))

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
            "clean black and white line art, coloring book page, thick bold outlines, "
            "outline only, white interior, hair and fur drawn as thin line strands, "
            "minimal interior detail, large open areas to color, flat white background, "
            "no shading, no solid black, no color, no grayscale, simple"
        ),
        "negative": (
            "extra head, two heads, extra limbs, deformed, mutated, duplicate face, fused bodies, "
            "solid black areas, black fill, filled shapes, silhouette, dark areas, heavy ink, "
            "shading, shadows, hatching, cross-hatching, gray, grayscale, gradient, "
            "color, colored, realistic rendering, detailed muscles, 3d, photo, "
            "complex background, text, watermark, signature, blurry, noisy"
        ),
        "styles": ["Fooocus V2"],
    },
    "kawaii": {
        "label": "Malbuch – niedlich / Kawaii",
        "prompt_suffix": (
            "cute kawaii style, black and white line art, coloring book page for kids, "
            "thick clean outlines, outline only, white interior, hair as thin line strands, "
            "big friendly shapes, large open areas to color, no shading, no solid black, "
            "flat white background"
        ),
        "negative": (
            "extra head, two heads, extra limbs, deformed, mutated, duplicate face, fused bodies, "
            "solid black areas, black fill, filled shapes, silhouette, dark areas, "
            "shading, shadows, hatching, cross-hatching, gray, grayscale, gradient, "
            "color, scary, realistic, photo, text, watermark, blurry"
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
            "solid black areas, black fill, silhouette, "
            "shading, shadows, hatching, cross-hatching, gray, grayscale, color, "
            "photo, realistic, text, watermark, asymmetrical, blurry"
        ),
        "styles": ["Fooocus V2"],
    },
    "detailed": {
        "label": "Malbuch – detailliert (Erwachsene)",
        "prompt_suffix": (
            "detailed black and white line art, intricate coloring book page for adults, "
            "fine clean outlines, outline only, white interior, no solid black, "
            "no shading, no color, white background"
        ),
        "negative": (
            "extra head, two heads, extra limbs, deformed, mutated, duplicate face, fused bodies, "
            "solid black areas, black fill, filled shapes, silhouette, dark areas, "
            "shading, shadows, hatching, cross-hatching, gray, grayscale, gradient, "
            "color, photo, realistic rendering, text, watermark, blurry"
        ),
        "styles": ["Fooocus V2"],
    },
}

DEFAULT_STYLE = "lineart"
