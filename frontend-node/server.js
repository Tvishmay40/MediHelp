/**
 * Medi Help - Minimal Node.js Server
 * Serves the Neumorphic Progressive Web App (PWA) for desktop & smartphone
 * and proxies /api/* calls to the Python FastAPI Backend (http://127.0.0.1:8000).
 */
const express = require('express');
const path = require('path');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.FRONTEND_PORT || 3000;
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://127.0.0.1:8000';

// Proxy all /api requests to Python FastAPI server
app.use('/api', createProxyMiddleware({
  target: PYTHON_BACKEND_URL,
  changeOrigin: true
}));

// Serve static Neumorphic UI and PWA assets
app.use(express.static(path.join(__dirname, 'public')));

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Medi Help Node.js Neumorphic UI running at http://localhost:${PORT}`);
  console.log(`Connected to Python FastAPI Backend at ${PYTHON_BACKEND_URL}`);
});
