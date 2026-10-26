# Medi Help — AI Prescription Scanner, Drug Interaction RAG & Smart Stock Companion

**B.Tech V Semester Minor Project (AI)**  
**Architecture**: Python (`FastAPI` + `Google Gemini API` + `LiteLLM/Ollama` + `ChromaDB/SQLite`) for all core logic + Minimal `Node.js` (`Express`) server for the Neumorphic mobile-ready UI.

---

## Key Features Implemented

1. **Python Core Logic + Minimal Node.js Neumorphic UI**:
   - All OCR, RAG, Drug-Interaction checking, Stock depletion math, and authentication run in `backend/app.py`, `backend/rag_engine.py`, and `backend/llm_vision_router.py`.
   - `frontend-node/server.js` serves the tactile Neumorphic UI (`#e0e5ec` soft extruded shadows) and proxies `/api/*` to Python.
2. **User Login, Credentials & Medical History Profile**:
   - Stores chronic conditions (e.g., Hypertension), known drug allergies (e.g., Sulfa, Penicillin), and active symptoms in SQLite.
3. **Smart Home Medicine Stock, Days Left & Auto-Buy Date**:
   - Calculates `days_left = home_stock_qty / frequency_per_day` and highlights exact restock dates.
   - Supports both **AI Prescription Photo Upload** and **Manual Medicine Entry**.
4. **Huge Medicine Database + Clinical RAG + Side-Effect & Clash Detector**:
   - Explains **what each medicine does** and **why the doctor prescribed it** given the user's symptoms.
   - Detects dangerous **Drug-Drug Clashes** (e.g., *Zerodol-SP + Telma 40* NSAID-ARB interaction, or *Zerodol-SP + Dolo 650* duplicate Paracetamol hepatotoxicity risk) and **Patient History Contraindications**.
5. **Smartphone Ready (PWA + Mobile Preview Mode)**:
   - Installable on Android & iOS via Web App Manifest, camera capture (`accept="image/*" capture="environment"`), and Web Notification / Web Audio reminders.
6. **Gemini Primary + Pluggable Multi-API & Local Ollama/PaddleOCR**:
   - **Primary**: `gemini-2.5-flash` for both Prescription Vision OCR and RAG Chat.
   - **Testing / Local Dev**: Switch seamlessly in the UI Settings or `.env` to **Local Ollama Vision** (`llama3.2-vision:11b`, `qwen2.5-vl`), **Local PaddleOCR + Ollama** (`llama3.2:3b`), **OpenAI** (`gpt-4o-mini`), or **Anthropic Claude** (`claude-3-5-sonnet`).

---

## Quick Start Instructions

### 1. Start the Python Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Add your GEMINI_API_KEY
uvicorn app:app --reload --port 8000
```

### 2. Start the Minimal Node.js Neumorphic Server
```bash
cd frontend-node
npm install
npm start
# Open http://localhost:3000 on your laptop or smartphone on the same Wi-Fi!
```

### 3. Optional: Running Vision & LLM 100% Locally for Testing
```bash
# Install Ollama from https://ollama.com
ollama pull llama3.2-vision:11b
ollama pull llama3.2:3b
```
