const input = document.querySelector("#file");
const drop = document.querySelector("#drop");
const result = document.querySelector("#result");
const sourceImg = document.querySelector("#source");
const outputImg = document.querySelector("#output");
const skeleton = document.querySelector("#skeleton");
const stats = document.querySelector("#stats");
const detections = document.querySelector("#detections");
const errorEl = document.querySelector("#error");
const statusEl = document.querySelector("#status");
const again = document.querySelector("#again");

let objectUrl = null;

function setBusy(busy) {
  drop.classList.toggle("busy", busy);
  statusEl.textContent = busy ? "Reading the water…" : "Drop a coastal photo";
  input.disabled = busy;
}

function labelFor(name) {
  return name.replace(/_/g, " ");
}

function showError(message) {
  errorEl.hidden = false;
  errorEl.textContent = message;
}

function clearError() {
  errorEl.hidden = true;
  errorEl.textContent = "";
}

function renderStats(data) {
  stats.replaceChildren();
  const chips = [];
  if (!data.count) {
    chips.push("No rip current found");
  } else {
    const counts = new Map();
    for (const item of data.detections) {
      const name = labelFor(item.class);
      counts.set(name, (counts.get(name) || 0) + 1);
    }
    chips.push([...counts].map(([name, count]) => `${count} ${name}`).join(" · "));
    const top = data.detections[0];
    chips.push(`${Math.round(top.confidence * 100)}% top confidence`);
  }
  chips.push(`${data.elapsed_ms} ms`);
  for (const text of chips) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = text;
    stats.append(chip);
  }

  detections.replaceChildren();
  for (const item of data.detections) {
    const row = document.createElement("li");
    const name = document.createElement("strong");
    name.textContent = labelFor(item.class);
    const score = document.createElement("span");
    score.textContent = `${Math.round(item.confidence * 100)}%`;
    row.append(name, score);
    detections.append(row);
  }
}

async function segment(file) {
  clearError();
  if (objectUrl) URL.revokeObjectURL(objectUrl);
  objectUrl = URL.createObjectURL(file);
  sourceImg.src = objectUrl;
  outputImg.hidden = true;
  outputImg.removeAttribute("src");
  skeleton.hidden = false;
  result.hidden = false;
  stats.replaceChildren();
  detections.replaceChildren();
  setBusy(true);

  const body = new FormData();
  body.append("image", file);
  try {
    const response = await fetch("/segment", { method: "POST", body });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || "Segmentation failed.");
    outputImg.onload = () => {
      skeleton.hidden = true;
    };
    outputImg.onerror = () => {
      skeleton.hidden = true;
      showError("Could not display the result.");
    };
    outputImg.src = data.image;
    outputImg.hidden = false;
    if (outputImg.complete) skeleton.hidden = true;
    renderStats(data);
  } catch (err) {
    skeleton.hidden = true;
    showError(err.message || "Segmentation failed.");
  } finally {
    setBusy(false);
  }
}

drop.addEventListener("dragover", (event) => {
  event.preventDefault();
  drop.classList.add("drag");
});

drop.addEventListener("dragleave", () => drop.classList.remove("drag"));

drop.addEventListener("drop", (event) => {
  event.preventDefault();
  drop.classList.remove("drag");
  const file = event.dataTransfer.files[0];
  if (file) segment(file);
});

input.addEventListener("change", () => {
  const file = input.files[0];
  if (file) segment(file);
});

again.addEventListener("click", () => {
  result.hidden = true;
  input.value = "";
  clearError();
  drop.scrollIntoView({ behavior: "smooth", block: "center" });
});
