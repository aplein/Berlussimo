"use strict";

let currentJob = null;
let pollTimer = null;
const renderedTiles = new Map(); // Bild-Index -> { el, imgEl } für inkrementelles Rendern

const $ = (id) => document.getElementById(id);

// Stil-Vorlagen für die editierbaren Felder
const PRESETS = {};
(window.PRESETS || []).forEach((p) => { PRESETS[p.key] = p; });

function applyPreset() {
  const p = PRESETS[$("style").value];
  if (!p) return;
  $("style_prompt").value = p.prompt_suffix || "";
  $("negative_prompt").value = p.negative || "";
}
$("style").addEventListener("change", applyPreset);
$("resetStyle").addEventListener("click", applyPreset);
applyPreset(); // Felder beim Laden vorbelegen

// Geschichte-/Szenen-Modus
function sceneLines() {
  return $("scenes").value.split("\n").map((s) => s.trim()).filter(Boolean);
}
function updateSceneCount() {
  const n = sceneLines().length;
  $("sceneCount").textContent = n
    ? `→ ${n} Szenen = ${n} Bilder (die Anzahl oben wird dann ignoriert)`
    : "";
}
$("scenes").addEventListener("input", updateSceneCount);
$("exampleScenes").addEventListener("click", () => {
  $("scenes").value = [
    "bei der Jagd",
    "beim Fischen",
    "beim Holz machen",
    "am Lagerfeuer",
    "beim Bootsbau",
    "auf großer Fahrt",
  ].join("\n");
  $("storyEditor").open = true;
  updateSceneCount();
});

// Beispielbild (Image Prompt)
let referenceDataUrl = null;
$("reference_file").addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    referenceDataUrl = reader.result;
    $("refImg").src = referenceDataUrl;
    $("refPreview").classList.remove("hidden");
    $("refEditor").open = true;
  };
  reader.readAsDataURL(file);
});
$("refClear").addEventListener("click", () => {
  referenceDataUrl = null;
  $("reference_file").value = "";
  $("refPreview").classList.add("hidden");
});

async function checkHealth() {
  const el = $("status");
  try {
    const r = await fetch("/api/health");
    const d = await r.json();
    if (d.fooocus_available) {
      el.textContent = "Fooocus verbunden ✓";
      el.className = "status ok";
    } else {
      el.textContent = "Fooocus nicht erreichbar (" + d.fooocus_url + ")";
      el.className = "status err";
    }
  } catch (e) {
    el.textContent = "Server nicht erreichbar";
    el.className = "status err";
  }
}

$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = {
    theme: $("theme").value,
    style: $("style").value,
    count: parseInt($("count").value, 10),
    page_text: $("page_text").value,
    title: $("title").value,
    prompt_suffix: $("style_prompt").value,
    negative_prompt: $("negative_prompt").value,
    fooocus_v2: $("fooocus_v2").checked,
    comic: $("comic").checked,
    scenes: $("scenes").value,
    reference_image: referenceDataUrl,
    reference_type: $("reference_type").value,
    reference_strength: $("reference_strength").value,
  };
  if (!body.theme.trim()) return;

  $("startBtn").disabled = true;
  const r = await fetch("/api/jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const d = await r.json();
  $("startBtn").disabled = false;
  if (!r.ok) { alert(d.error || "Fehler beim Starten."); return; }

  currentJob = d.id;
  localStorage.setItem("malbuch_job", currentJob);
  renderedTiles.clear();
  $("gallery").innerHTML = "";
  $("progress").classList.remove("hidden");
  $("gallerySection").classList.remove("hidden");
  $("pdfLink").innerHTML = "";
  poll();
});

$("cancelBtn").addEventListener("click", async () => {
  if (!currentJob) return;
  await fetch(`/api/jobs/${currentJob}/cancel`, { method: "POST" });
});

function poll() {
  clearTimeout(pollTimer);
  fetchJob().then((job) => {
    if (!job) return;
    if (job.state === "running" || job.state === "queued") {
      // Bei großen Aufträgen seltener pollen (weniger Last über Nacht).
      const interval = job.count > 100 ? 5000 : 2000;
      pollTimer = setTimeout(poll, interval);
    }
  });
}

async function fetchJob() {
  if (!currentJob) return null;
  const r = await fetch(`/api/jobs/${currentJob}`);
  if (!r.ok) return null;
  const job = await r.json();
  render(job);
  return job;
}

function render(job) {
  const pct = job.count ? Math.round((job.done / job.count) * 100) : 0;
  $("bar").style.width = pct + "%";
  let label = `${job.done} / ${job.count} Bildern fertig`;
  if (job.state === "done") label += " – fertig ✓";
  if (job.state === "cancelled") label += " – abgebrochen";
  $("progressText").textContent = label;
  $("cancelBtn").style.display =
    (job.state === "running" || job.state === "queued") ? "" : "none";

  // Inkrementell: nur NEUE Bilder anhängen (kein Neuaufbau, kein Neuladen,
  // vom Nutzer getippte Seitentexte bleiben erhalten).
  const g = $("gallery");
  job.images
    .slice()
    .sort((a, b) => a.index - b.index)
    .forEach((img) => {
      if (!renderedTiles.has(img.index)) {
        const t = tile(img);
        renderedTiles.set(img.index, t);
        g.appendChild(t.el);
      }
    });
}

function tile(img) {
  const div = document.createElement("div");
  if (img.error) {
    div.className = "tile error";
    div.textContent = "Fehler: " + img.error;
    return { el: div, imgEl: null };
  }
  div.className = "tile";

  const image = document.createElement("img");
  image.loading = "lazy"; // bei vielen Bildern: nur Sichtbares wird geladen
  image.src = img.url;
  div.appendChild(image);

  const cap = document.createElement("input");
  cap.className = "cap";
  cap.value = img.caption || "";
  cap.placeholder = "Seitentext …";
  cap.dataset.index = img.index;
  div.appendChild(cap);

  const regen = document.createElement("button");
  regen.className = "regen";
  regen.textContent = "🔄 neu generieren";
  regen.onclick = async () => {
    regen.disabled = true;
    regen.textContent = "…";
    const r = await fetch(`/api/jobs/${currentJob}/regenerate/${img.index}`, {
      method: "POST",
    });
    const d = await r.json();
    regen.disabled = false;
    regen.textContent = "🔄 neu generieren";
    if (r.ok) {
      // nur dieses eine Bild aktualisieren (Cache-Buster erzwingt Neuladen)
      const updated = (d.images || []).find((i) => i.index === img.index);
      if (updated && updated.url) image.src = updated.url + "?t=" + Date.now();
    } else {
      alert(d.error || "Fehler");
    }
  };
  div.appendChild(regen);

  return { el: div, imgEl: image };
}

$("saveCaptionsBtn").addEventListener("click", async () => {
  const captions = {};
  document.querySelectorAll(".tile .cap").forEach((el) => {
    captions[el.dataset.index] = el.value;
  });
  await fetch(`/api/jobs/${currentJob}/captions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ captions }),
  });
  alert("Texte gespeichert.");
});

$("pdfBtn").addEventListener("click", async () => {
  if (!currentJob) return;
  // Texte vorher mitspeichern, damit sie im PDF landen.
  const captions = {};
  document.querySelectorAll(".tile .cap").forEach((el) => {
    captions[el.dataset.index] = el.value;
  });
  await fetch(`/api/jobs/${currentJob}/captions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ captions }),
  });

  $("pdfBtn").disabled = true;
  $("pdfBtn").textContent = "Erstelle PDF …";
  const r = await fetch(`/api/jobs/${currentJob}/pdf`, { method: "POST" });
  const d = await r.json();
  $("pdfBtn").disabled = false;
  $("pdfBtn").textContent = "📕 PDF-Malbuch erstellen";
  if (r.ok) {
    $("pdfLink").innerHTML =
      `<a href="${d.url}" target="_blank">⬇️ Malbuch herunterladen (PDF)</a>`;
  } else {
    alert(d.error || "Fehler beim PDF.");
  }
});

// Nach einem Browser-Neustart wieder mit dem laufenden/letzten Auftrag
// verbinden – so geht ein Nacht-Lauf nicht verloren (solange die App läuft).
function resumeStoredJob() {
  const stored = localStorage.getItem("malbuch_job");
  if (!stored) return;
  fetch(`/api/jobs/${stored}`)
    .then((r) => (r.ok ? r.json() : null))
    .then((job) => {
      if (!job) { localStorage.removeItem("malbuch_job"); return; }
      currentJob = stored;
      renderedTiles.clear();
      $("gallery").innerHTML = "";
      $("progress").classList.remove("hidden");
      $("gallerySection").classList.remove("hidden");
      render(job);
      if (job.state === "running" || job.state === "queued") poll();
    })
    .catch(() => {});
}

resumeStoredJob();
checkHealth();
setInterval(checkHealth, 15000);
