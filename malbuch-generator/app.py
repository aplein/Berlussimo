"""Malbuch-Generator – kleine Flask-App.

Ablauf:
  1. Nutzer gibt Thema, Stil, Anzahl und Seitentext ein.
  2. Im Hintergrund werden über Fooocus Bild für Bild Line-Art-Seiten erzeugt.
  3. In der Galerie können einzelne Bilder neu generiert und Texte angepasst werden.
  4. Zum Schluss wird ein druckfertiges PDF-Malbuch gebaut.
"""
import json
import threading
import uuid
from datetime import datetime
from pathlib import Path

from flask import (
    Flask, jsonify, request, render_template, send_file, abort, url_for,
)

import config
from fooocus_client import FooocusClient, FooocusError
from pdf_builder import build_coloring_book

app = Flask(__name__)
client = FooocusClient()

# In-Memory-Auftragsspeicher. Für ein lokales Einzelplatz-Tool ausreichend;
# Bilder/Metadaten liegen zusätzlich auf der Platte (output/<job_id>/).
jobs: dict[str, dict] = {}
jobs_lock = threading.Lock()


def _job_dir(job_id: str) -> Path:
    d = config.OUTPUT_DIR / job_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def _save_job_meta(job: dict):
    meta = {k: v for k, v in job.items() if k != "thread"}
    (_job_dir(job["id"]) / "job.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _build_prompt(theme: str, suffix: str) -> str:
    theme = theme.strip().rstrip(",")
    suffix = (suffix or "").strip()
    return f"{theme}, {suffix}" if suffix else theme


def _scene_for(job: dict, index: int) -> str:
    """Szene/Aktivität für eine Seite (für den Geschichte-Modus), sonst ''."""
    scenes = job.get("scenes") or []
    return scenes[index] if index < len(scenes) else ""


def _caption_for(job: dict, index: int) -> str:
    """Seitentext: im Geschichte-Modus die Szene, sonst der globale Text."""
    return _scene_for(job, index) or job["page_text"]


def _generate_one(job: dict, index: int, seed: int = -1) -> dict:
    """Erzeugt ein einzelnes Bild und legt es auf der Platte ab."""
    scene = _scene_for(job, index)
    subject = f'{job["theme"]} {scene}'.strip() if scene else job["theme"]
    prompt = _build_prompt(subject, job["prompt_suffix"])
    png = client.text_to_image(
        prompt=prompt,
        negative_prompt=job["negative_prompt"],
        styles=job["styles"],
        seed=seed,
    )
    filename = f"img_{index:03d}.png"
    path = _job_dir(job["id"]) / filename
    path.write_bytes(png)
    return {
        "index": index,
        "file": str(path),
        "filename": filename,
        "caption": _caption_for(job, index),
        "error": None,
    }


def _run_job(job_id: str):
    with jobs_lock:
        job = jobs[job_id]
        job["state"] = "running"
    for i in range(job["count"]):
        with jobs_lock:
            if job["state"] == "cancelled":
                break
        try:
            img = _generate_one(job, i)
        except FooocusError as exc:
            img = {"index": i, "file": None, "filename": None,
                   "caption": _caption_for(job, i), "error": str(exc)}
        with jobs_lock:
            job["images"].append(img)
            job["done"] = len(job["images"])
            _save_job_meta(job)
    with jobs_lock:
        if job["state"] != "cancelled":
            job["state"] = "done"
        _save_job_meta(job)


@app.route("/")
def index():
    presets = [
        {
            "key": k,
            "label": v["label"],
            "prompt_suffix": v["prompt_suffix"],
            "negative": v["negative"],
        }
        for k, v in config.STYLE_PRESETS.items()
    ]
    return render_template(
        "index.html",
        presets=presets,
        default_style=config.DEFAULT_STYLE,
        max_images=config.MAX_IMAGES,
    )


@app.route("/api/health")
def health():
    return jsonify({
        "fooocus_url": config.FOOOCUS_API_URL,
        "fooocus_available": client.is_available(),
    })


@app.route("/api/jobs", methods=["POST"])
def create_job():
    data = request.get_json(force=True) or {}
    theme = (data.get("theme") or "").strip()
    style = data.get("style") or config.DEFAULT_STYLE
    page_text = (data.get("page_text") or "").strip()
    title = (data.get("title") or theme or "Malbuch").strip()
    try:
        count = int(data.get("count") or 1)
    except (TypeError, ValueError):
        return jsonify({"error": "Ungültige Anzahl."}), 400

    if not theme:
        return jsonify({"error": "Bitte ein Thema angeben."}), 400
    if style not in config.STYLE_PRESETS:
        return jsonify({"error": "Unbekannter Stil."}), 400
    count = max(1, min(count, config.MAX_IMAGES))

    # Stil: aus dem Formular angepasste Werte bevorzugen, sonst die Vorlage.
    preset = config.STYLE_PRESETS[style]
    prompt_suffix = data.get("prompt_suffix")
    if prompt_suffix is None or not prompt_suffix.strip():
        prompt_suffix = preset["prompt_suffix"]
    negative_prompt = data.get("negative_prompt")
    if negative_prompt is None:
        negative_prompt = preset["negative"]
    # "Fooocus V2" sorgt fuer mehr Variation/Details; abschaltbar fuer puren Prompt.
    fooocus_v2 = data.get("fooocus_v2", True)
    styles = ["Fooocus V2"] if fooocus_v2 else []

    # Geschichte-Modus: eine Szene pro Zeile. Dann entsteht pro Szene ein Bild
    # und die Zeile wird zum Seitentext. Die Bildanzahl ergibt sich aus den Szenen.
    scenes = [s.strip() for s in (data.get("scenes") or "").splitlines() if s.strip()]
    scenes = scenes[:config.MAX_IMAGES]
    if scenes:
        count = len(scenes)

    job_id = uuid.uuid4().hex[:12]
    job = {
        "id": job_id,
        "theme": theme,
        "style": style,
        "prompt_suffix": prompt_suffix.strip(),
        "negative_prompt": negative_prompt.strip(),
        "styles": styles,
        "scenes": scenes,
        "page_text": page_text,
        "title": title,
        "count": count,
        "done": 0,
        "state": "queued",
        "images": [],
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    with jobs_lock:
        jobs[job_id] = job
        _save_job_meta(job)

    t = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    job["thread"] = t
    t.start()
    return jsonify({"id": job_id})


def _public_job(job: dict) -> dict:
    images = []
    for img in job["images"]:
        images.append({
            "index": img["index"],
            "caption": img.get("caption", ""),
            "error": img.get("error"),
            "url": (url_for("job_image", job_id=job["id"], filename=img["filename"])
                    if img.get("filename") else None),
        })
    return {
        "id": job["id"],
        "theme": job["theme"],
        "style": job["style"],
        "title": job["title"],
        "page_text": job["page_text"],
        "count": job["count"],
        "done": job["done"],
        "state": job["state"],
        "images": images,
    }


@app.route("/api/jobs/<job_id>")
def get_job(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            abort(404)
        return jsonify(_public_job(job))


@app.route("/api/jobs/<job_id>/cancel", methods=["POST"])
def cancel_job(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            abort(404)
        if job["state"] in ("queued", "running"):
            job["state"] = "cancelled"
    return jsonify({"ok": True})


@app.route("/api/jobs/<job_id>/regenerate/<int:index>", methods=["POST"])
def regenerate(job_id, index):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            abort(404)
        if job["state"] == "running":
            return jsonify({"error": "Bitte warten, bis der Auftrag fertig ist."}), 409
    try:
        img = _generate_one(job, index)
    except FooocusError as exc:
        return jsonify({"error": str(exc)}), 502
    with jobs_lock:
        # vorhandenen Eintrag ersetzen, sonst anhängen
        for i, existing in enumerate(job["images"]):
            if existing["index"] == index:
                img["caption"] = existing.get("caption", job["page_text"])
                job["images"][i] = img
                break
        else:
            job["images"].append(img)
        _save_job_meta(job)
    return jsonify(_public_job(job))


@app.route("/api/jobs/<job_id>/captions", methods=["POST"])
def update_captions(job_id):
    data = request.get_json(force=True) or {}
    captions = data.get("captions") or {}
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            abort(404)
        for img in job["images"]:
            key = str(img["index"])
            if key in captions:
                img["caption"] = captions[key]
        _save_job_meta(job)
    return jsonify({"ok": True})


@app.route("/api/jobs/<job_id>/pdf", methods=["POST"])
def make_pdf(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            abort(404)
        valid = [img for img in job["images"] if img.get("file") and not img.get("error")]
        title = job["title"]
    if not valid:
        return jsonify({"error": "Keine fertigen Bilder vorhanden."}), 400
    valid.sort(key=lambda x: x["index"])
    pdf_path = _job_dir(job_id) / "malbuch.pdf"
    build_coloring_book(valid, pdf_path, title=title)
    return jsonify({"url": url_for("download_pdf", job_id=job_id)})


@app.route("/jobs/<job_id>/images/<filename>")
def job_image(job_id, filename):
    path = _job_dir(job_id) / filename
    if not path.exists() or not filename.startswith("img_"):
        abort(404)
    return send_file(path, mimetype="image/png")


@app.route("/jobs/<job_id>/malbuch.pdf")
def download_pdf(job_id):
    path = _job_dir(job_id) / "malbuch.pdf"
    if not path.exists():
        abort(404)
    return send_file(
        path, mimetype="application/pdf",
        as_attachment=True, download_name="malbuch.pdf",
    )


if __name__ == "__main__":
    print(f"Malbuch-Generator läuft auf http://127.0.0.1:{config.APP_PORT}")
    print(f"Fooocus-API erwartet unter: {config.FOOOCUS_API_URL}")
    app.run(host="127.0.0.1", port=config.APP_PORT, debug=False, threaded=True)
