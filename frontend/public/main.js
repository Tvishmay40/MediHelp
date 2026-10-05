/**
 * main.js
 * -------
 * ONLY job of this file: wire up button clicks, show the preview image,
 * and render the results list. Delegates actual work to Camera (camera.js)
 * and Api (api.js).
 */

const fileInput = document.getElementById("fileInput");
const chooseBtn = document.getElementById("chooseBtn");
const webcamBtn = document.getElementById("webcamBtn");
const webcamWrap = document.getElementById("webcamWrap");
const webcamVideo = document.getElementById("webcamVideo");
const captureBtn = document.getElementById("captureBtn");
const closeWebcamBtn = document.getElementById("closeWebcamBtn");
const canvas = document.getElementById("canvas");
const previewWrap = document.getElementById("previewWrap");
const previewImg = document.getElementById("previewImg");
const analyzeBtn = document.getElementById("analyzeBtn");
const statusEl = document.getElementById("status");
const resultsWrap = document.getElementById("resultsWrap");
const resultsList = document.getElementById("resultsList");
const notesText = document.getElementById("notesText");

let currentImageBlob = null;

function setStatus(msg) {
  statusEl.textContent = msg || "";
}

function showPreview(blob) {
  currentImageBlob = blob;
  previewImg.src = URL.createObjectURL(blob);
  previewWrap.classList.remove("hidden");
  resultsWrap.classList.add("hidden");
  setStatus("");
}

// --- Option 1: file picker / Android native camera ---
chooseBtn.addEventListener("click", () => Camera.openFilePicker(fileInput));

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) showPreview(file);
});

// --- Option 2: live desktop webcam ---
webcamBtn.addEventListener("click", async () => {
  try {
    webcamWrap.classList.remove("hidden");
    await Camera.startWebcam(webcamVideo);
  } catch (err) {
    setStatus("Could not access webcam: " + err.message);
    webcamWrap.classList.add("hidden");
  }
});

closeWebcamBtn.addEventListener("click", () => {
  Camera.stopWebcam();
  webcamWrap.classList.add("hidden");
});

captureBtn.addEventListener("click", async () => {
  const blob = await Camera.captureFrame(webcamVideo, canvas);
  Camera.stopWebcam();
  webcamWrap.classList.add("hidden");
  showPreview(blob);
});

// --- Analyze ---
analyzeBtn.addEventListener("click", async () => {
  if (!currentImageBlob) return;
  setStatus("Analyzing prescription… this can take a few seconds.");
  analyzeBtn.disabled = true;
  resultsWrap.classList.add("hidden");

  try {
    const data = await Api.analyzeImage(currentImageBlob);
    renderResults(data);
    setStatus("");
  } catch (err) {
    setStatus("Error: " + err.message);
  } finally {
    analyzeBtn.disabled = false;
  }
});

function renderResults(data) {
  resultsList.innerHTML = "";

  if (!data.medicines || data.medicines.length === 0) {
    resultsList.innerHTML = "<li>No medicines could be detected.</li>";
  } else {
    data.medicines.forEach((med) => {
      const li = document.createElement("li");
      const details = [med.dose, med.frequency, med.duration]
        .filter(Boolean)
        .join(" · ");
      li.innerHTML = `
        <span class="med-name">${escapeHtml(med.name || "Unknown")}</span>
        <span class="med-detail">${escapeHtml(details)}${
        med.confidence ? ` (confidence: ${escapeHtml(med.confidence)})` : ""
      }</span>
      `;
      resultsList.appendChild(li);
    });
  }

  notesText.textContent = data.notes || "";
  notesText.classList.toggle("hidden", !data.notes);
  resultsWrap.classList.remove("hidden");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str || "";
  return div.innerHTML;
}
