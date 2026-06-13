"""Baut aus den generierten Bildern ein druckfertiges PDF-Malbuch.

Pro Seite: optionaler Text (Überschrift) oben, darunter das Bild zentriert.
Zusätzlich eine einfache Titelseite mit dem Thema.
"""
from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def _draw_centered_text(c, text, x_center, y, font, size, max_width):
    """Zeichnet Text zentriert; verkleinert die Schrift, falls zu breit."""
    c.setFont(font, size)
    while size > 8 and c.stringWidth(text, font, size) > max_width:
        size -= 1
        c.setFont(font, size)
    c.drawCentredString(x_center, y, text)


def build_coloring_book(
    images: list[dict],
    output_path: Path,
    title: str = "Malbuch",
    max_pixels: int = 2000,
) -> Path:
    """Erzeugt das PDF.

    images: Liste von Dicts mit "file" (Pfad zum Bild) und optional "caption".
    max_pixels: längste Bildkante; größere Bilder werden sanft verkleinert
        (für den Druck bleibt das mehr als ausreichend scharf).

    Die Bilder werden in Graustufen eingebettet und verlustfrei (Flate)
    komprimiert. Bei schwarz-weißer Malbuch-Linienkunst spart das viel Platz,
    ohne sichtbaren Qualitätsverlust.
    """
    page_w, page_h = A4
    margin = 15 * mm
    c = canvas.Canvas(str(output_path), pagesize=A4)
    c.setPageCompression(1)

    # --- Titelseite ---
    c.setFillColorRGB(0, 0, 0)
    _draw_centered_text(
        c, title, page_w / 2, page_h * 0.6, "Helvetica-Bold", 32, page_w - 2 * margin
    )
    _draw_centered_text(
        c, "Mein Malbuch", page_w / 2, page_h * 0.5, "Helvetica", 16, page_w - 2 * margin
    )
    c.showPage()

    # --- Bildseiten ---
    for item in images:
        img_path = Path(item["file"])
        if not img_path.exists():
            continue
        caption = (item.get("caption") or "").strip()

        top = page_h - margin
        if caption:
            _draw_centered_text(
                c, caption, page_w / 2, top - 6 * mm,
                "Helvetica-Bold", 20, page_w - 2 * margin,
            )
            image_top = top - 18 * mm
        else:
            image_top = top

        # Verfügbaren Bereich für das Bild bestimmen und Seitenverhältnis wahren.
        avail_w = page_w - 2 * margin
        avail_h = image_top - margin
        with Image.open(img_path) as im:
            # Graustufen: schwarz-weiße Linien brauchen keine Farbkanäle ->
            # rund 1/3 der Bilddaten, ohne sichtbaren Qualitätsverlust.
            im = im.convert("L")
            if max_pixels and max(im.size) > max_pixels:
                im.thumbnail((max_pixels, max_pixels), Image.LANCZOS)
            iw, ih = im.size
            reader = ImageReader(im)
            scale = min(avail_w / iw, avail_h / ih)
            draw_w = iw * scale
            draw_h = ih * scale
            x = (page_w - draw_w) / 2
            y = margin + (avail_h - draw_h) / 2

            c.drawImage(
                reader, x, y, width=draw_w, height=draw_h,
                preserveAspectRatio=True, mask="auto",
            )
        c.showPage()

    c.save()
    return output_path
