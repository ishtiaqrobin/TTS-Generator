# TTS-Generator

🎙️ **Storyteller Studio** — A modern, hybrid Text-to-Speech (TTS) web application specifically engineered for long-form narrative and storytelling. Runs 100% locally on your machine with zero cloud subscription fees.

---

## ✨ Features

- **Hybrid Engine Switcher**:
  - ⚡ **Edge-TTS (Neural Cloud)**: Lightning-fast rendering powered by Microsoft's neural voices. Supports expressive SSML emotion styles (`whispering`, `terrified`, `sad`, `cheerful`, `empathetic`, `angry`, `narration-relaxed`).
  - 🤖 **Kokoro-82M (Local AI Model)**: State-of-the-art open-source 82M parameter model running locally on CPU/GPU. Delivers studio-grade human cadence, natural rhythm, and breath dynamics.
- **Long-Form Narrative Engine (30+ Minutes Ready)**:
  - Smart paragraph & sentence chunker that prevents timeouts and disconnections.
  - Asynchronous background batch synthesis with real-time percentage and section progress.
  - Seamless FFmpeg audio stitching with zero pops, clicks, or cuts.
- **Narrative Fine-Tuning**:
  - **Dramatic Pause Slider**: Add customizable dramatic pauses (`100ms` – `1500ms`) at paragraph breaks.
  - **Emotion Intensity Slider**: Adjust expressive emotional degree (`0.5x` – `2.0x`).
  - **Speed & Pitch Controls**: Modulate voice rate and pitch (deep bass to high pitch).
- **Subtitles & Export**:
  - Synchronized `.SRT` subtitle generation ready for YouTube or video editing.
  - Direct `.MP3` master audio download.
- **Modern Minimal UI**:
  - ShadcnUI-inspired minimalist dark theme (Deep Zinc `#09090b`).
  - Instant 3-second audition preview before generating full audio.
  - Persistent bottom master audio player with scrubber and variable speed controls (`1x`, `1.25x`, `1.5x`).

---

## 🎭 Featured Character Archetypes

### Edge-TTS Voices
- **Guy** — The Master Storyteller (Expressive with 8 emotion styles)
- **Christopher** — Deep Baritone & Audiobook Narrator (Documentaries, Sci-Fi)
- **Aria** — Emotional Protagonist (Drama, Psychological Thrillers)
- **Davis** — Noir, Crime & Dark Horror Narrator
- **Ryan** — Classic British Gentleman
- **Sonia** — Enchanting & Literary British Narrator
- **Jenny** — Soothing Bedtime Storyteller

### Kokoro-82M Voices
- **Heart (`af_heart`)** — Ranked #1 open-source voice for warm, human-like narration
- **Michael (`am_michael`)** — Natural, rich American male baritone
- **Adam (`am_adam`)** — Deep, commanding, and grounded storyteller
- **George (`bm_george`)** — Prestigious British audiobook reader
- **Lewis (`bm_lewis`)** — Refined British fantasy & lore narrator
- **Emma (`bf_emma`)** — Victorian, gothic, and literary female delivery

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, Flask-CORS
- **Audio Synthesis**: `edge-tts` (7.3.1+), `kokoro` (0.9.4+), `soundfile`, `torch`
- **Audio Processing**: FFmpeg & FFprobe (concatenation & metadata)
- **Frontend**: HTML5, Modern Vanilla CSS (ShadcnUI Dark tokens), ES6+ JavaScript

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
