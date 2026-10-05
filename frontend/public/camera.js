/**
 * camera.js
 * ---------
 * ONLY job of this file: get an image Blob from the user, either via the
 * file picker (works for Android's native camera + Windows file browser)
 * or via a live desktop webcam stream. No UI wiring, no API calls here.
 */

const Camera = (() => {
  let mediaStream = null;

  function openFilePicker(fileInputEl) {
    fileInputEl.click();
  }

  async function startWebcam(videoEl) {
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" },
      audio: false,
    });
    videoEl.srcObject = mediaStream;
  }

  function stopWebcam() {
    if (mediaStream) {
      mediaStream.getTracks().forEach((track) => track.stop());
      mediaStream = null;
    }
  }

  /** Grabs the current webcam frame and returns a JPEG Blob. */
  function captureFrame(videoEl, canvasEl) {
    canvasEl.width = videoEl.videoWidth;
    canvasEl.height = videoEl.videoHeight;
    const ctx = canvasEl.getContext("2d");
    ctx.drawImage(videoEl, 0, 0);
    return new Promise((resolve) => {
      canvasEl.toBlob((blob) => resolve(blob), "image/jpeg", 0.9);
    });
  }

  return { openFilePicker, startWebcam, stopWebcam, captureFrame };
})();
