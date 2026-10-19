# TTS-Generator

🎙️ **Storyteller Studio** — A modern, multi-engine AI Text-to-Speech (TTS) studio engineered specifically for long-form narrative storytelling, character dialogue, and zero-shot voice cloning. Runs 100% locally on your machine with zero subscription fees.

---

## ✨ 4 State-of-the-Art TTS Engines

Compare audio quality, rhythm, and expressive styles side-by-side across 4 distinct AI engines:

1. ⚡ **Edge-TTS (Neural Cloud)**:
   - Ultra-fast synthesis with Microsoft's neural voices.
   - Rich SSML emotion styles: `whispering`, `terrified`, `sad`, `cheerful`, `empathetic`, `angry`, `narration-relaxed`.
   - Dynamic pitch & speed modulation.
2. 🤖 **Kokoro-82M (Local Neural AI)**:
   - State-of-the-art open-weights 82M model running locally on CPU/GPU.
   - Warm, studio-grade human cadence, natural rhythm, and breath dynamics.
   - American & British literary narrative voices.
3. 💬 **ChatTTS (Conversational & Expressive Storytelling)**:
   - Specialized in conversational rhythm, laughter, sighs, and natural pauses.
   - **Interactive Story Tokens**: Click to inject `[laugh]` (laughter) and `[lbreak]` (natural dramatic breath pause) directly into the story text.
   - **Speaker Seeds**: Reproducible unique narrator voices with randomizer (`🎲 Randomize Seed`).
   - Expressiveness controls: **Oral Breath** level and **Laugh Tendency**.
4. 🎙️ **F5-TTS (Zero-Shot Voice Cloning)**:
   - Non-autoregressive Flow Matching model with continuous vocoder (Vocos).
   - Instant voice cloning from a 5–15 second audio reference without retraining.
   - Bundled preset voices (`David Nature`, `Emma British`, `Basic English`, `Basic Mandarin`) + custom file upload.
   - Customizable ODE sampling steps (`nfe_step`) for optimal balance between speed and fidelity.

---

## 🎨 Dual Theme UI
- 🌙 **Slate Dark Mode**: Warm, sleek dark theme inspired by slate-charcoal tones (`#38393a`) and pill-shaped interactive tabs.
- ☀️ **Modern Light Mode**: High-contrast, clean minimalist aesthetic in crisp white, black, and crimson red (`#dc2626`).
- Automatic theme preference persistence in browser `localStorage`.

---

## 🎭 Engine Comparison & Voices

| Engine | Architecture | Best For | Emotion / Control | Clone Support |
| :--- | :--- | :--- | :--- | :--- |
| **Edge-TTS** | Neural SSML Cloud | Fast chapters, 30+ min rendering | 8 SSML Emotions, Pitch, Speed | Preset library |
| **Kokoro-82M** | StyleTTS2 (82M) | Audiobooks & literary narratives | Human cadence, Speed modulation | Preset library |
| **ChatTTS** | Generative LLM | Dialogue, comedy, expressive pauses | `[laugh]`, `[lbreak]`, Oral breath | Seed-based |
| **F5-TTS** | Flow Matching ODE | Zero-shot voice cloning & narration | Reference audio cloning, Speed | Custom audio upload |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, Flask-CORS
- **AI Engines**:
  - `edge-tts` (7.3.1+)
  - `kokoro` (0.9.4+)
  - `ChatTTS` (0.2.5+)
  - `f5-tts` (1.1.22+)
- **Audio Processing**: FFmpeg & FFprobe (seamless concatenation & metadata), `soundfile`, `torch`
- **Frontend**: Modern Vanilla HTML5 / CSS3 / ES6+ JavaScript (zero external framework bloat)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10 or higher
- [FFmpeg](https://ffmpeg.org/) installed and available in your system `PATH`

### 2. Installation
Clone the repository:
```bash
git clone https://github.com/ishtiaqrobin/TTS-Generator.git
cd TTS-Generator
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Running the Application

#### Option A: One-Click (Windows)
Double-click `start.bat`.

#### Option B: Terminal
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📂 Project Structure

```
TTS-Generator/
├── app.py                      # Flask backend API & static server
├── engine.py                   # Core Hybrid TTS engine & chunker
├── start.bat                   # Windows one-click launcher
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── TTS_Storytelling_Guide.md   # Architectural & user guide
├── static/                     # Web Frontend
│   ├── index.html              # HTML structure
│   ├── style.css               # ShadcnUI Dark minimalist CSS
│   └── app.js                  # Frontend state & API controller
└── output/                     # Generated audio & subtitle files (.gitkeep)
```

---

## 📜 License

MIT License. Open-source and free for personal and commercial use.
