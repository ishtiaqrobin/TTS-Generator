"""
Flask Web Application for Storytelling TTS Suite
Serves 4 Engines: Edge-TTS, Kokoro-82M, ChatTTS, and F5-TTS
"""

import os
import uuid
import threading
import asyncio
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from engine import (
    EDGE_VOICES,
    KOKORO_VOICES,
    CHATTTS_VOICES,
    F5TTS_VOICES,
    OUTPUT_DIR,
    REF_AUDIO_DIR,
    generate_full_story,
    synthesize_edge_chunk,
    synthesize_kokoro_chunk,
    synthesize_chattts_chunk,
    synthesize_f5tts_chunk
)

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

TASKS = {}

def progress_callback(task_id: str, current: int, total: int, message: str):
    if task_id in TASKS:
        pct = int((current / total) * 100) if total > 0 else 0
        TASKS[task_id].update({
            "current_chunk": current,
            "total_chunks": total,
            "progress": pct,
            "message": message,
            "status": "processing"
        })


def run_story_generation_thread(task_id: str, params: dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            generate_full_story(
                task_id=task_id,
                engine=params.get("engine", "edge"),
                text=params["text"],
                voice_id=params["voice_id"],
                style=params.get("style"),
                style_degree=float(params.get("style_degree", 1.0)),
                rate=int(params.get("rate", 0)),
                pitch=int(params.get("pitch", 0)),
                pause_ms=int(params.get("pause_ms", 400)),
                chat_seed=int(params.get("chat_seed", 42)),
                chat_temp=float(params.get("chat_temp", 0.3)),
                chat_oral=int(params.get("chat_oral", 2)),
                chat_laugh=int(params.get("chat_laugh", 0)),
                f5_ref_audio=params.get("f5_ref_audio"),
                f5_ref_text=params.get("f5_ref_text"),
                f5_nfe_step=int(params.get("f5_nfe_step", 32)),
                generate_subtitles=bool(params.get("generate_subtitles", True)),
                progress_callback=progress_callback
            )
        )
        TASKS[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Story audio generated successfully!",
            "result": result
        })
    except Exception as e:
        TASKS[task_id].update({
            "status": "error",
            "message": f"Error: {str(e)}"
        })
    finally:
        loop.close()


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/voices", methods=["GET"])
def get_voices():
    """
    Returns curated voices for Edge-TTS, Kokoro-82M, ChatTTS, and F5-TTS.
    """
    return jsonify({
        "success": True,
        "edge_voices": EDGE_VOICES,
        "kokoro_voices": KOKORO_VOICES,
        "chattts_voices": CHATTTS_VOICES,
        "f5tts_voices": F5TTS_VOICES
    })


@app.route("/api/upload_reference", methods=["POST"])
def upload_reference():
    """
    Handles user uploaded reference audio for F5-TTS Voice Cloning.
    """
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No audio file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"success": False, "error": "Empty filename"}), 400

    filename = f"user_{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
    save_path = os.path.join(REF_AUDIO_DIR, filename)
    file.save(save_path)

    return jsonify({
        "success": True,
        "filename": filename,
        "audio_path": f"ref_audio/{filename}"
    })


@app.route("/api/preview", methods=["POST"])
def preview_voice():
    """
    Generates a quick 3-5 second sample using the chosen engine.
    """
    data = request.json or {}
    engine = data.get("engine", "edge")
    voice_id = data.get("voice_id", "en-US-GuyNeural")
    style = data.get("style", "narration-relaxed")
    style_degree = float(data.get("style_degree", 1.0))
    rate = int(data.get("rate", 0))
    pitch = int(data.get("pitch", 0))
    text = data.get("text", "The silent corridor stretched endlessly into the shadows.")

    preview_id = f"preview_{uuid.uuid4().hex[:8]}"
    output_filename = f"{preview_id}.mp3"
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        if engine == "kokoro":
            import numpy as np
            kokoro_speed = float(np.clip(1.0 + (rate / 100.0) * 1.2, 0.6, 1.6))
            synthesize_kokoro_chunk(
                chunk_text=text,
                output_path=output_path,
                voice_id=voice_id,
                speed=kokoro_speed
            )
        elif engine == "chattts":
            import numpy as np
            chat_seed = int(data.get("chat_seed", 42))
            chat_temp = float(data.get("chat_temp", 0.3))
            chat_oral = int(data.get("chat_oral", 2))
            chat_laugh = int(data.get("chat_laugh", 0))
            chat_speed_lvl = int(np.clip(5 + int(rate / 10), 1, 9))
            synthesize_chattts_chunk(
                chunk_text=text,
                output_path=output_path,
                seed=chat_seed,
                temperature=chat_temp,
                oral=chat_oral,
                laugh=chat_laugh,
                speed_level=chat_speed_lvl
            )
        elif engine == "f5":
            import numpy as np
            f5_speed = float(np.clip(1.0 + (rate / 100.0), 0.7, 1.5))
            f5_nfe_step = int(data.get("f5_nfe_step", 32))
            ref_audio = data.get("f5_ref_audio")
            ref_text = data.get("f5_ref_text")
            if not ref_audio or not ref_text:
                v = next((v for v in F5TTS_VOICES if v["id"] == voice_id), F5TTS_VOICES[0])
                ref_audio = v["ref_audio"]
                ref_text = v["ref_text"]
            synthesize_f5tts_chunk(
                chunk_text=text,
                output_path=output_path,
                ref_audio_path=ref_audio,
                ref_text=ref_text,
                speed=f5_speed,
                nfe_step=f5_nfe_step
            )
        else:  # edge
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    synthesize_edge_chunk(
                        chunk_text=text,
                        output_path=output_path,
                        voice_id=voice_id,
                        style=style,
                        style_degree=style_degree,
                        rate=rate,
                        pitch=pitch,
                        pause_ms=200
                    )
                )
            finally:
                loop.close()

        return jsonify({
            "success": True,
            "audio_url": f"/output/{output_filename}"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/generate", methods=["POST"])
def generate_story():
    data = request.json or {}
    text = (data.get("text") or "").strip()

    if not text:
        return jsonify({"success": False, "error": "Story text cannot be empty."}), 400

    task_id = uuid.uuid4().hex[:12]
    TASKS[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "current_chunk": 0,
        "total_chunks": 1,
        "message": f"Initializing {data.get('engine', 'edge').upper()} narrative pipeline...",
        "result": None
    }

    thread = threading.Thread(
        target=run_story_generation_thread,
        args=(task_id, data),
        daemon=True
    )
    thread.start()

    return jsonify({
        "success": True,
        "task_id": task_id
    })


@app.route("/api/progress/<task_id>", methods=["GET"])
def get_progress(task_id):
    task = TASKS.get(task_id)
    if not task:
        return jsonify({"success": False, "error": "Task not found."}), 404
    return jsonify(task)


@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)


@app.route("/download/<path:filename>")
def download_output(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" 🎙️ Storyteller Studio — 4-Engine Multi-TTS Suite")
    print(" 1: Edge-TTS (Cloud Neural + SSML Emotions)")
    print(" 2: Kokoro-82M (Local AI Studio Model)")
    print(" 3: ChatTTS (Conversational & Storytelling AI)")
    print(" 4: F5-TTS (Zero-Shot Diffusion Voice Cloning)")
    print(" Access Web Interface at: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
