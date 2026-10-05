/**
 * api.js
 * ------
 * ONLY job of this file: send the image to the Python backend and
 * return the parsed JSON. No DOM manipulation, no camera logic here.
 */

const Api = (() => {
  // Change this if your backend runs on a different host/port,
  // e.g. when testing from a phone: "http://192.168.1.5:5000"
  const BACKEND_URL = window.MEDIHELP_BACKEND_URL || "http://localhost:5000";

  async function analyzeImage(imageBlob) {
    const formData = new FormData();
    formData.append("image", imageBlob, "prescription.jpg");

    const response = await fetch(`${BACKEND_URL}/api/analyze`, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || `Request failed with status ${response.status}`);
    }
    return data; // { medicines: [...], notes: "" }
  }

  return { analyzeImage };
})();
