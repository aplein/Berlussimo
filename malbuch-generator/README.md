# 🎨 Malbuch-Generator

Eine kleine, eigenständige Web-App, mit der du aus einem Thema (z. B. „niedliche
Dinosaurier") per **Fooocus** eine ganze Serie von Malbuch-Seiten (Line Art)
erzeugst, jede Seite mit eigenem Text versiehst und am Ende ein **druckfertiges
PDF-Malbuch** herunterlädst.

Kein Bauschritt, keine Cloud, keine laufenden Kosten – die Bilder entstehen
lokal auf deiner Fooocus-Installation.

---

## Wie es funktioniert

```
Browser (UI)  ──►  Flask-App (diese App)  ──►  Fooocus-API  ──►  Fooocus / GPU
                         │
                         └──►  PDF-Malbuch (reportlab)
```

Du gibst Thema, Stil, Anzahl und Seitentext ein. Die App erzeugt die Bilder
im Hintergrund Stück für Stück, zeigt sie in einer Galerie (mit „neu
generieren" je Bild) und baut auf Knopfdruck das PDF.

---

## Voraussetzungen

1. **Python 3.10+**
2. **Fooocus mit aktivierter REST-API.** Fooocus selbst hat keine fertige
   REST-Schnittstelle – dafür gibt es das Projekt **Fooocus-API**, das Fooocus
   kapselt und Endpunkte wie `POST /v1/generation/text-to-image` bereitstellt.

### Fooocus-API starten

```bash
# einmalig holen
git clone https://github.com/mrhan1993/Fooocus-API.git
cd Fooocus-API
pip install -r requirements.txt

# starten (lädt beim ersten Mal die Modelle, Standard-Port 8888)
python main.py
```

> Tipp: Wenn du bereits Fooocus mit heruntergeladenen Modellen hast, kann
> Fooocus-API auf dieselben Modell-Ordner zeigen, damit nichts doppelt
> geladen wird (siehe Fooocus-API README, Option `--config` /
> Pfad-Einstellungen).

Prüfe im Browser: `http://127.0.0.1:8888/docs` – wenn die OpenAPI-Doku
erscheint, läuft die API.

---

## Diese App starten

```bash
cd malbuch-generator
python -m venv .venv && source .venv/bin/activate   # optional, empfohlen
pip install -r requirements.txt

# optional: Einstellungen anpassen
cp .env.example .env        # z. B. anderen Fooocus-Port eintragen

python app.py
```

Dann im Browser öffnen: **http://127.0.0.1:5000**

Oben rechts siehst du, ob Fooocus verbunden ist (grün = bereit).

---

## Bedienung

1. **Thema** eingeben, z. B. `niedliche Dinosaurier`.
2. **Stil** wählen (Standard = klare Linien / Line Art, dazu Kawaii, Mandala,
   detailliert für Erwachsene).
3. **Anzahl** der Bilder (z. B. 30) und optional einen **Text pro Seite**.
4. **„Bilder erstellen"** – der Fortschritt läuft live mit.
5. In der **Galerie** einzelne Bilder neu generieren oder Seitentexte anpassen.
6. **„PDF-Malbuch erstellen"** → Download des fertigen PDFs (A4, Titelseite +
   eine Malseite pro Bild).

> 30 Bilder dauern je nach GPU eine Weile (oft 15–40 Min). Die App generiert
> bewusst Bild für Bild, damit du den Fortschritt siehst und einzelne Seiten
> gezielt neu würfeln kannst.

---

## Konfiguration

Alles über `.env` bzw. Umgebungsvariablen (siehe `.env.example`):

| Variable | Bedeutung | Standard |
|---|---|---|
| `FOOOCUS_API_URL` | Adresse der Fooocus-API | `http://127.0.0.1:8888` |
| `FOOOCUS_PERFORMANCE` | `Speed`, `Quality`, `Extreme Speed` | `Speed` |
| `FOOOCUS_ASPECT_RATIO` | Seitenverhältnis `B*H` | `896*1152` |
| `MAX_IMAGES` | Obergrenze pro Auftrag | `60` |
| `GENERATION_TIMEOUT` | Timeout pro Bild (Sek.) | `600` |

**Eigene Stile** legst du in `config.py` unter `STYLE_PRESETS` an – jeweils
mit Prompt-Zusatz, Negativ-Prompt und Fooocus-Stilnamen.

---

## Dateien

| Datei | Zweck |
|---|---|
| `app.py` | Flask-App, Auftrags-/Hintergrundlogik, Endpunkte |
| `fooocus_client.py` | Aufruf der Fooocus-API |
| `pdf_builder.py` | Zusammenbau des PDF-Malbuchs |
| `config.py` | Einstellungen & Stil-Vorlagen |
| `templates/`, `static/` | Web-Oberfläche |
| `output/` | erzeugte Bilder & PDFs (nicht im Git) |

---

## Hinweise

- **Midjourney** wurde bewusst nicht eingebunden: Es hat keine offizielle API.
  Fooocus läuft lokal, kostenlos und ist für Line-Art/Malbücher bestens
  geeignet. Falls später doch ein anderer Anbieter dazukommen soll, lässt sich
  `fooocus_client.py` durch einen analogen Client ersetzen.
- Die App ist als lokales Einzelplatz-Werkzeug gedacht (kein Login, kein
  Mehrbenutzerbetrieb).
