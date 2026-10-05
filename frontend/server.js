/**
 * server.js
 * ---------
 * ONLY job of this file: serve the static frontend (HTML/CSS/JS) on
 * Windows or Android (via browser). It does NOT talk to Gemini —
 * that happens in the Python backend (backend/app.py).
 */

const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.static(path.join(__dirname, "public")));

app.listen(PORT, "0.0.0.0", () => {
  console.log(`MediHelp frontend running:`);
  console.log(`  On this computer:  http://localhost:${PORT}`);
  console.log(`  On your phone (same Wi-Fi): http://<this-PC's-LAN-IP>:${PORT}`);
});
