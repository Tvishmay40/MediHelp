# MediHelp Prototype — Photo → Medicine List

Bare-minimum prototype: upload or photograph a prescription, get back a list
of medicines with dose/frequency, using the Gemini API for the image→text work.

```
medihelp-prototype/
├── backend/            Python (Flask) — talks to Gemini, exposes /api/analyze
│   ├── app.py              # ONLY routing / HTTP handling
│   ├── gemini_service.py   # ONLY Gemini API calls + JSON parsing
│   ├── requirements.txt
│   └── .env.example
└── frontend/            Node.js (Express) — serves the web page
    ├── server.js            # ONLY static file serving
    └── public/
        ├── index.html
        ├── style.css
        ├── camera.js        # ONLY getting an image (file picker / webcam)
        ├── api.js           # ONLY calling the backend
        └── main.js          # ONLY UI wiring + rendering results
```

## 1. Backend setup (Python)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # Windows: copy .env.example .env
# then edit .env and paste your Gemini API key
# get one free at https://aistudio.google.com/app/apikey

python app.py
```

Backend now runs at `http://localhost:5000`.

## 2. Frontend setup (Node.js)

In a second terminal:

```bash
cd frontend
npm install
npm start
```

Frontend now runs at `http://localhost:3000`.

## 3. Using it

- **On your Windows PC:** open `http://localhost:3000` in a browser.
  Use **"Upload / Take Photo"** to pick a file, or **"Use Webcam"** for a live
  capture from your PC's webcam.
- **On your Android phone (same Wi-Fi):**
  1. Find your PC's LAN IP (`ipconfig` on Windows, look for IPv4 address).
  2. On your phone's browser, go to `http://<that-IP>:3000`.
  3. Tap **"Upload / Take Photo"** — this opens the phone's native camera
     directly, or lets you pick an existing photo.
  4. Edit `frontend/public/api.js` and change `BACKEND_URL` to
     `http://<that-IP>:5000` so the phone can reach the backend too.

> Live webcam capture (`getUserMedia`) only works on `localhost` or over
> HTTPS — that's a browser security rule, not a bug. That's why Android uses
> the file-picker/native-camera route instead, which works over plain HTTP.

## Notes / limits (it's a prototype)

- No database, no auth, no history — a single screen: photo in, list out.
- Accuracy depends entirely on Gemini reading the prescription image; blurry
  or very messy handwriting may come back incomplete — check the `notes`
  field in the response for warnings.
- `GEMINI_MODEL` in `.env` defaults to `gemini-2.5-flash`; swap to another
  vision-capable Gemini model name there if you prefer.
