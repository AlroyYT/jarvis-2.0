import asyncio
import base64
import io
import json
import os
import re

import edge_tts
import google.generativeai as genai
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── API Key ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ── Voice map ──────────────────────────────────────────────────────────────────
JARVIS_VOICE_MAP = {
    "en": "en-GB-RyanNeural",
    "hi": "hi-IN-MadhurNeural",
    "kn": "kn-IN-GaganNeural",
    "ta": "ta-IN-ValluvarNeural",
    "te": "te-IN-MohanNeural",
    "ml": "ml-IN-MidhunNeural",
    "mr": "mr-IN-ManoharNeural",
}

# ── Language config ────────────────────────────────────────────────────────────
JARVIS_LANGUAGE_CONFIG = {
    "en": {
        "system_prompt": """You are JARVIS, an advanced AI assistant for engineering students. Be witty and helpful. Be concise - give essential information directly.

FORMATTING RULES:
- Use numbered lists for steps/procedures (1. 2. 3.)
- Use **bold** for key terms
- Use LaTeX for equations: inline $equation$ or display $$equation$$
- No tables, no code blocks unless absolutely necessary
- Keep responses under 200 words
- Address user as "sir"

EQUATION RULE: Always include LaTeX equations when explaining formulas.
Example: Ohm's law: $$V = IR$$""",
    },
    "hi": {
        "system_prompt": """आप JARVIS हैं, इंजीनियरिंग छात्रों के लिए उन्नत AI सहायक। संक्षिप्त रहें - सीधे आवश्यक जानकारी दें।

फ़ॉर्मेटिंग नियम:
- चरणों/प्रक्रियाओं के लिए क्रमांकित सूची (1. 2. 3.)
- मुख्य शब्दों के लिए **bold**
- समीकरणों के लिए LaTeX: inline $equation$ या display $$equation$$
- जवाब 200 शब्दों से कम रखें
- उपयोगकर्ता को 'सर' कहें

समीकरण नियम: सूत्र समझाते समय LaTeX equation ज़रूर शामिल करें।""",
    },
    "kn": {
        "system_prompt": """ನೀವು JARVIS, ಇಂಜಿನಿಯರಿಂಗ್ ವಿದ್ಯಾರ್ಥಿಗಳಿಗೆ ಸುಧಾರಿತ AI ಸಹಾಯಕ. ಸಂಕ್ಷಿಪ್ತವಾಗಿರಿ - ನೇರವಾಗಿ ಅಗತ್ಯ ಮಾಹಿತಿ ನೀಡಿ.

ಫಾರ್ಮ್ಯಾಟಿಂಗ್ ನಿಯಮಗಳು:
- ಹಂತಗಳಿಗೆ ಸಂಖ್ಯಾ ಪಟ್ಟಿ (1. 2. 3.)
- ಮುಖ್ಯ ಪದಗಳಿಗೆ **bold**
- ಸಮೀಕರಣಗಳಿಗೆ LaTeX: inline $equation$ ಅಥವಾ display $$equation$$
- 200 ಪದಗಳಿಗಿಂತ ಕಡಿಮೆ ಇರಿಸಿ
- ಬಳಕೆದಾರರನ್ನು 'ಸರ್' ಎಂದು ಸಂಬೋಧಿಸಿ

ಸಮೀಕರಣ ನಿಯಮ: ಸೂತ್ರ ವಿವರಿಸುವಾಗ LaTeX equation ಸೇರಿಸಿ.""",
    },
    "ta": {
        "system_prompt": """நீங்கள் JARVIS, இஞ்சினியரிங் மாணவர்களுக்கான மேம்பட்ட AI உதவியாளர். சுருக்கமாக இருங்கள் - நேரடியாக தேவையான தகவல்களை கொடுங்கள்.

வடிவமைப்பு விதிகள்:
- படிகளுக்கு எண் பட்டியல் (1. 2. 3.)
- முக்கிய சொற்களுக்கு **bold**
- சமன்பாடுகளுக்கு LaTeX: inline $equation$ அல்லது display $$equation$$
- 200 வார்த்தைகளுக்குக் குறைவாக வைத்திருங்கள்
- பயனரை 'சார்' என்று அழையுங்கள்

சமன்பாடு விதி: சூத்திரத்தை விளக்கும்போது LaTeX equation சேர்க்கவும்.""",
    },
    "te": {
        "system_prompt": """మీరు JARVIS, ఇంజినీరింగ్ విద్యార్థులకు అధునాతన AI సహాయకుడు. క్లుప్తంగా ఉండండి - నేరుగా అవసరమైన సమాచారం ఇవ్వండి.

ఫార్మాటింగ్ నియమాలు:
- దశలకు సంఖ్యా జాబితా (1. 2. 3.)
- కీలక పదాలకు **bold**
- సమీకరణాలకు LaTeX: inline $equation$ లేదా display $$equation$$
- 200 పదాల కంటే తక్కువగా ఉంచండి
- వినియోగదారుని 'సార్' అని సంబోధించండి

సమీకరణ నియమం: సూత్రం వివరించేటప్పుడు LaTeX equation తప్పకుండా చేర్చండి.""",
    },
    "ml": {
        "system_prompt": """നിങ്ങൾ JARVIS, ഇൻജിനീയറിംഗ് വിദ്യാർഥികൾക്കായുള്ള നൂതന AI സഹായി. സംക്ഷിപ്തമായിരിക്കുക - ആവശ്യമായ വിവരങ്ങൾ നേരിട്ട് നൽകുക.

ഫോർമാറ്റിംഗ് നിയമങ്ങൾ:
- ഘട്ടങ്ങൾക്ക് ക്രമ പട്ടിക (1. 2. 3.)
- പ്രധാന പദങ്ങൾക്ക് **bold**
- സമവാക്യങ്ങൾക്ക് LaTeX: inline $equation$ അല്ലെങ്കിൽ display $$equation$$
- 200 വാക്കുകളിൽ താഴെ നിലനിർത്തുക
- ഉപയോക്താവിനെ 'സർ' എന്ന് അഭിസംബോധന ചെയ്യുക

സമവാക്യ നിയമം: ഫോർമുല വിശദീകരിക്കുമ്പോൾ LaTeX equation ഉൾപ്പെടുത്തുക.""",
    },
    "mr": {
        "system_prompt": """तुम्ही JARVIS, इंजिनिअरिंग विद्यार्थ्यांसाठी प्रगत AI सहाय्यक. संक्षिप्त रहा - थेट आवश्यक माहिती द्या.

फॉरमॅटिंग नियम:
- पायऱ्यांसाठी क्रमांकित यादी (1. 2. 3.)
- मुख्य शब्दांसाठी **bold**
- समीकरणांसाठी LaTeX: inline $equation$ किंवा display $$equation$$
- 200 शब्दांपेक्षा कमी ठेवा
- वापरकर्त्याला 'सर' म्हणून संबोधित करा

समीकरण नियम: सूत्र समजावताना LaTeX equation आवश्यक आहे.""",
    },
}

# ── Conversation state ─────────────────────────────────────────────────────────
_jarvis_conversation_history = []
_jarvis_current_language = "en"


# ── TTS cleaner ────────────────────────────────────────────────────────────────
def _strip_for_tts(text: str) -> str:
    """Remove markdown/LaTeX for speech while keeping all content."""

    def clean_display_math(m):
        inner = m.group(1)
        inner = re.sub(r"\\[a-zA-Z]+", " ", inner)
        inner = re.sub(r"[{}^_]", " ", inner)
        inner = re.sub(r"\s+", " ", inner).strip()
        return f" जहाँ {inner} " if inner else " समीकरण "

    text = re.sub(r"\$\$([\s\S]+?)\$\$", clean_display_math, text)

    def clean_inline_math(m):
        inner = m.group(1)
        inner = re.sub(r"\\[a-zA-Z]+", " ", inner)
        inner = re.sub(r"[{}^_]", " ", inner)
        inner = re.sub(r"\s+", " ", inner).strip()
        return f" {inner} " if inner else " समीकरण "

    text = re.sub(r"\$([^$\n]+?)\$", clean_inline_math, text)
    text = re.sub(r"```[\s\S]*?```", " कोड ब्लॉक ", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"^(\d+)\.\s+", r"\1. ", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


# ── TTS async generator ────────────────────────────────────────────────────────
async def _generate_tts(text: str, voice: str) -> bytes:
    audio_buffer = io.BytesIO()
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])
    audio_buffer.seek(0)
    return audio_buffer.read()


# ── Health check ───────────────────────────────────────────────────────────────
@app.route("/api/health/", methods=["GET"])
def jarvis_health():
    return jsonify({"status": "online", "jarvis": "ready"})


# ── Configure ──────────────────────────────────────────────────────────────────
@app.route("/api/configure/", methods=["POST"])
def jarvis_configure():
    return jsonify({"success": True, "message": "API key pre-configured"})


# ── Main chat endpoint ─────────────────────────────────────────────────────────
@app.route("/api/chat/", methods=["POST"])
def jarvis_chat():
    global _jarvis_conversation_history, _jarvis_current_language

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    user_text = data.get("text", "")
    language = data.get("language", "en")

    if not user_text:
        return jsonify({"error": "No text provided"}), 400

    # Reset history on language switch
    if language != _jarvis_current_language:
        _jarvis_conversation_history = []
        _jarvis_current_language = language

    lang_cfg = JARVIS_LANGUAGE_CONFIG.get(language, JARVIS_LANGUAGE_CONFIG["en"])
    voice = JARVIS_VOICE_MAP.get(language, "en-GB-RyanNeural")

    try:
        # ── 1. Gemini with minimal history ─────────────────────────────────
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=lang_cfg["system_prompt"],
        )

        _jarvis_conversation_history.append({"role": "user", "parts": [user_text]})
        history_to_send = _jarvis_conversation_history[-4:]

        chat_session = model.start_chat(
            history=history_to_send[:-1] if len(history_to_send) > 1 else []
        )
        response = chat_session.send_message(user_text)
        reply_text = response.text
        _jarvis_conversation_history.append({"role": "model", "parts": [reply_text]})

        if len(_jarvis_conversation_history) > 8:
            _jarvis_conversation_history = _jarvis_conversation_history[-8:]

        # ── 2. TTS cleaning ─────────────────────────────────────────────────
        tts_text = _strip_for_tts(reply_text)

        # ── 3. Async TTS generation ─────────────────────────────────────────
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                raise RuntimeError("closed")
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        audio_bytes = loop.run_until_complete(_generate_tts(tts_text, voice))
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        return jsonify(
            {
                "reply": reply_text,
                "audio": audio_base64,
                "audio_format": "mp3",
                "language": language,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Reset conversation ─────────────────────────────────────────────────────────
@app.route("/api/reset/", methods=["POST"])
def jarvis_reset():
    global _jarvis_conversation_history
    _jarvis_conversation_history = []
    return jsonify({"success": True, "message": "Conversation reset"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)