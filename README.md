# J.A.R.V.I.S — Voice AI Assistant

> Just A Rather Very Intelligent System

A hands-free voice bot powered by Gemini AI with a stunning Iron Man-inspired UI.
Say **"JARVIS"** to activate, speak your command, and get a spoken + text response.

---

## 🛠️ Setup

### 1. Backend (Flask)

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The Flask server runs on **http://localhost:5000**

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

The UI runs on **http://localhost:3000**

---

## 🔑 Get Your Free Gemini API Key

1. Go to [https://aistudio.google.com/apikey](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy and paste it into the JARVIS interface

---

## 🎙️ How to Use

1. Open **http://localhost:3000** in Chrome
2. Enter your Gemini API key and click **INITIALIZE**
3. Allow microphone access when the browser asks
4. Say **"JARVIS"** out loud → you'll hear a beep
5. Speak your command within **7 seconds**
6. JARVIS replies with voice + displays the text

**Examples:**
- "JARVIS, what's the weather like today?"
- "JARVIS, tell me a joke"
- "JARVIS, explain quantum computing in simple terms"
- "JARVIS, what time is it in Tokyo?"

---

## 🔧 Requirements

- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **Google Chrome** (for Web Speech API support)
- **Microphone** access

---

## 📁 Project Structure

```
jarvis/
├── backend/
│   ├── app.py          # Flask API server
│   └── requirements.txt
└── frontend/
    ├── app/
    │   ├── page.tsx    # Main JARVIS UI
    │   ├── layout.tsx
    │   └── globals.css
    ├── package.json
    └── next.config.js
```

---

## ⚡ Quick Start Script

```bash
# Terminal 1 — Backend
cd backend && pip install -r requirements.txt && python app.py

# Terminal 2 — Frontend
cd frontend && npm install && npm run dev
```

Then open Chrome at **http://localhost:3000** 🚀
