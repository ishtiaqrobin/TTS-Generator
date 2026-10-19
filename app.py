"""
Flask Web Application for Storytelling TTS Generator
Serves Hybrid Engine (Edge-TTS & Kokoro-82M) and the ShadcnUI-inspired minimalist frontend.
"""

import os
import uuid
import threading
import asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from engine import (
    EDGE_VOICES,
    KOKORO_VOICES,
    OUTPUT_DIR,
    generate_full_story,
    synthesize_edge_chunk,
    synthesize_kokoro_chunk
)

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)

# In-memory task tracking
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
    Returns curated voices for both Edge-TTS and Kokoro-82M.
    """
    return jsonify({
        "success": True,
        "edge_voices": EDGE_VOICES,
        "kokoro_voices": KOKORO_VOICES
    })


@app.route("/api/preview", methods=["POST"])
def preview_voice():
    """
    Generates a quick 3-5 second audition sample using the chosen engine and voice.
    """
    data = request.json or {}
    engine = data.get("engine", "edge")
    voice_id = data.get("voice_id", "en-US-GuyNeural")
    style = data.get("style", "narration-relaxed")
    style_degree = float(data.get("style_degree", 1.0))
    rate = int(data.get("rate", 0))
    pitch = int(data.get("pitch", 0))
    text = data.get("text", "The silent corridor stretched endlessly into the shadows of the old manor.")

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
        else:
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
    """
    Starts long-form story generation asynchronously.
    """
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
    """
    Serves the output audio and subtitle files for streaming and preview.
    """
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)


@app.route("/download/<path:filename>")
def download_output(filename):
    """
    Direct file download attachment.
    """
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    print("\n" + "="*60)
    print(" 🎙️ Storyteller Studio — Hybrid TTS Server")
    print(" Engine 1: Edge-TTS (Neural Cloud + SSML Emotions)")
    print(" Engine 2: Kokoro-82M (Local AI Studio Model)")
    print(" Access Web Interface at: http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
