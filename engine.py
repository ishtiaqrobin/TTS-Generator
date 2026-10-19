"""
Storytelling TTS Hybrid Engine (Edge-TTS & Kokoro-82M)
Supports:
- Edge-TTS Cloud Neural Voices with SSML Expressive Emotion Styles
- Kokoro-82M Local AI Pipeline with human-grade rhythm and cadence
- Long-form narrative splitting (30+ minutes / 10,000+ words)
- Concurrency-safe batch generation with progress tracking
- Seamless FFmpeg concatenation (zero pops, clicks, or cuts)
- Synchronized Subtitle (.SRT) generation
"""

import os
import re
import html
import asyncio
import subprocess
import soundfile as sf
import numpy as np
import edge_tts
from typing import List, Dict, Any, Optional

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Curated Edge-TTS Storyteller Voices
EDGE_VOICES = [
    {
        "id": "en-US-GuyNeural",
        "name": "Guy",
        "title": "The Master Storyteller",
        "gender": "Male",
        "locale": "en-US",
        "accent": "American",
        "description": "Deeply expressive, dynamic narrator ideal for mystery, thrillers, and dramatic storytelling.",
        "sample_text": "The fog rolled over the cobblestone streets as the distant clock tower struck midnight.",
        "supported_styles": [
            {"id": "narration-relaxed", "label": "Storyteller (Relaxed)"},
            {"id": "whispering", "label": "Whisper (Suspense)"},
            {"id": "terrified", "label": "Terrified (Horror)"},
            {"id": "sad", "label": "Sad (Tragic)"},
            {"id": "cheerful", "label": "Cheerful (Upbeat)"},
            {"id": "hopeful", "label": "Hopeful"},
            {"id": "empathetic", "label": "Empathetic"},
            {"id": "angry", "label": "Intense (Angry)"}
        ],
        "default_style": "narration-relaxed",
        "tag": "Most Expressive"
    },
    {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher",
        "title": "The Deep Audiobook Narrator",
        "gender": "Male",
        "locale": "en-US",
        "accent": "American",
        "description": "Deep, authoritative, cinematic baritone voice. Perfect for epic fantasy, sci-fi, and documentaries.",
        "sample_text": "In the beginning, long before the stars grew cold, an ancient civilization watched the skies.",
        "supported_styles": [
            {"id": "default", "label": "Authoritative Narrative"}
        ],
        "default_style": "default",
        "tag": "Deep Baritone"
    },
    {
        "id": "en-US-AriaNeural",
        "name": "Aria",
        "title": "The Emotional Protagonist",
        "gender": "Female",
        "locale": "en-US",
        "accent": "American",
        "description": "Rich emotional range, breath control, and nuance. Ideal for psychological thrillers and emotional drama.",
        "sample_text": "She looked out into the rain, wondering if the secret she had kept for twenty years was finally unraveling.",
        "supported_styles": [
            {"id": "narration-relaxed", "label": "Storyteller (Relaxed)"},
            {"id": "whispering", "label": "Whisper (Secretive)"},
            {"id": "sad", "label": "Sad (Melancholy)"},
            {"id": "empathetic", "label": "Empathetic"},
            {"id": "cheerful", "label": "Cheerful"}
        ],
        "default_style": "narration-relaxed",
        "tag": "Emotional Nuance"
    },
    {
        "id": "en-US-DavisNeural",
        "name": "Davis",
        "title": "The Dark & Gritty Narrator",
        "gender": "Male",
        "locale": "en-US",
        "accent": "American",
        "description": "Gruff, suspenseful, gritty tone. Exceptional for noir crime, detective mysteries, and dark horror.",
        "sample_text": "The city has a way of swallowing the truth. You don't ask questions unless you're ready for the answer.",
        "supported_styles": [
            {"id": "narration-relaxed", "label": "Noir Narrative"},
            {"id": "whispering", "label": "Whisper (Eerie)"},
            {"id": "angry", "label": "Gritty / Angry"},
            {"id": "sad", "label": "Gloomy (Sad)"}
        ],
        "default_style": "narration-relaxed",
        "tag": "Noir & Horror"
    },
    {
        "id": "en-GB-RyanNeural",
        "name": "Ryan",
        "title": "The British Gentleman",
        "gender": "Male",
        "locale": "en-GB",
        "accent": "British (UK)",
        "description": "Sophisticated, articulate British male. The hallmark voice for historical fiction, classic literature, and royal sagas.",
        "sample_text": "Beneath the vaulted ceilings of the cathedral, shadows danced upon centuries of forgotten history.",
        "supported_styles": [
            {"id": "default", "label": "Classic British Narrative"}
        ],
        "default_style": "default",
        "tag": "Classic British"
    },
    {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia",
        "title": "The Cinematic British Narrator",
        "gender": "Female",
        "locale": "en-GB",
        "accent": "British (UK)",
        "description": "Elegant, enchanting British female delivery. Wonderful for fairy tales, folklore, and gothic mysteries.",
        "sample_text": "The wind carried whispered secrets through the ancient heather moorlands of the north.",
        "supported_styles": [
            {"id": "default", "label": "Elegant British Narrative"}
        ],
        "default_style": "default",
        "tag": "Enchanting Tone"
    },
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny",
        "title": "The Soothing Bedtime Storyteller",
        "gender": "Female",
        "locale": "en-US",
        "accent": "American",
        "description": "Warm, gentle, reassuring voice. Perfect for soothing sleep stories, meditation, and gentle fables.",
        "sample_text": "As the evening settled, the stars gently appeared one by one, watching over the quiet forest.",
        "supported_styles": [
            {"id": "whispering", "label": "Gentle Whisper"},
            {"id": "cheerful", "label": "Warm & Cheerful"},
            {"id": "sad", "label": "Soft & Melancholic"}
        ],
        "default_style": "whispering",
        "tag": "Calming & Warm"
    },
    {
        "id": "en-US-BrianMultilingualNeural",
        "name": "Brian",
        "title": "The Contemporary Narrator",
        "gender": "Male",
        "locale": "en-US",
        "accent": "American",
        "description": "Crisp, modern, high-definition neural voice. Great for contemporary fiction, podcasts, and audiobooks.",
        "sample_text": "Every discovery begins with a single question that nobody dared to ask before.",
        "supported_styles": [
            {"id": "default", "label": "Modern Narrative"}
        ],
        "default_style": "default",
        "tag": "Modern Crisp"
    }
]

# Curated Kokoro-82M Voices
KOKORO_VOICES = [
    {
        "id": "af_heart",
        "name": "Heart",
        "title": "The Masterpiece Narrator",
        "gender": "Female",
        "locale": "en-US",
        "accent": "American",
        "description": "Ranked #1 for natural human storytelling. Stunning breath, rhythm, and warm audiobook delivery.",
        "sample_text": "The autumn leaves drifted softly across the cobblestones, whispering memories of summers long forgotten.",
        "supported_styles": [
            {"id": "default", "label": "Studio Natural Cadence"}
        ],
        "default_style": "default",
        "tag": "Top Quality"
    },
    {
        "id": "am_michael",
        "name": "Michael",
        "title": "The Classic American Storyteller",
        "gender": "Male",
        "locale": "en-US",
        "accent": "American",
        "description": "Natural, rich, resonant American male voice. Excellent pacing for novels, audiobooks, and biographies.",
        "sample_text": "Behind every locked door in the old city lies a history waiting for someone brave enough to uncover it.",
        "supported_styles": [
            {"id": "default", "label": "Studio Natural Cadence"}
        ],
        "default_style": "default",
        "tag": "Rich Baritone"
    },
    {
        "id": "am_adam",
        "name": "Adam",
        "title": "The Deep Dramatic Voice",
        "gender": "Male",
        "locale": "en-US",
        "accent": "American",
        "description": "Deep, commanding, and grounded. Perfect for suspense, thrillers, and dramatic monologues.",
        "sample_text": "The storm broke just before dawn, washing away the traces of what had transpired in the shadows.",
        "supported_styles": [
            {"id": "default", "label": "Studio Natural Cadence"}
        ],
        "default_style": "default",
        "tag": "Deep & Grounded"
    },
    {
        "id": "bm_george",
        "name": "George",
        "title": "The Royal British Narrator",
        "gender": "Male",
        "locale": "en-GB",
        "accent": "British (UK)",
        "description": "Prestigious British narrator with theatrical poise. Ideal for classic literature, epic fantasy, and lore.",
        "sample_text": "Upon the windswept cliffs of Dover, the old lighthouse kept its solitary vigil against the raging sea.",
        "supported_styles": [
            {"id": "default", "label": "Studio Natural Cadence"}
        ],
        "default_style": "default",
        "tag": "Prestigious British"
    },
    {
        "id": "bm_lewis",
        "name": "Lewis",
        "title": "The Refined Fantasy Narrator",
        "gender": "Male",
        "locale": "en-GB",
        "accent": "British (UK)",
        "description": "Crisp, articulate, captivating British male voice. Superb for intricate storytelling and historical drama.",
        "sample_text": "The manuscript was written in a dialect that had not been spoken in the realm for three centuries.",
        "supported_styles": [
            {"id": "default", "label": "Studio Natural Cadence"}
        ],
        "default_style": "default",
        "tag": "Refined British"
    },
    {
        "id": "bf_emma",
        "name": "Emma",
        "title": "The Victorian Storyteller",
        "gender": "Female",
        "locale": "en-GB",
        "accent": "British (UK)",
        "description": "Gentle, cultured British female voice. Evocative of Victorian novels, gothic mysteries, and poetry.",
        "sample_text": "The garden was asleep beneath a veil of silver frost, silent save for the rustle of the weeping willow.",
        "supported_styles": [
            {"id": "default", "label": "Studio Natural Cadence"}
        ],
        "default_style": "default",
        "tag": "Gothic & Literary"
    },
    {
        "id": "af_bella",
        "name": "Bella",
        "title": "The Expressive Protagonist",
        "gender": "Female",
        "locale": "en-US",
        "accent": "American",
        "description": "Lively, emotive, contemporary American female voice. Wonderful for fast-paced fiction and adventure.",
        "sample_text": "She glanced at the map one last time, took a deep breath, and stepped into the uncharted valley.",
        "supported_styles": [
            {"id": "default", "label": "Studio Natural Cadence"}
        ],
        "default_style": "default",
        "tag": "Vibrant Tone"
    },
    {
        "id": "af_nicole",
        "name": "Nicole",
        "title": "The Soft & Mystery Voice",
        "gender": "Female",
        "locale": "en-US",
        "accent": "American",
        "description": "Intimate, whisper-close delivery with subtle texture. Ideal for psychological fiction and bedtime tales.",
        "sample_text": "Listen closely to the silence, for that is where the most profound truths are whispered.",
        "supported_styles": [
            {"id": "default", "label": "Studio Natural Cadence"}
        ],
        "default_style": "default",
        "tag": "Intimate & Soft"
    }
]

# Lazy-loaded Kokoro pipelines cache
_KOKORO_PIPELINES = {}

def get_kokoro_pipeline(lang_code: str = 'a'):
    """
    Returns cached Kokoro KPipeline for the requested language code ('a' = American, 'b' = British).
    """
    global _KOKORO_PIPELINES
    if lang_code not in _KOKORO_PIPELINES:
        from kokoro import KPipeline
        print(f"[Kokoro] Initializing KPipeline with lang_code='{lang_code}'...")
        _KOKORO_PIPELINES[lang_code] = KPipeline(lang_code=lang_code)
    return _KOKORO_PIPELINES[lang_code]


def build_ssml(
    text: str,
    voice_id: str,
    style: Optional[str] = None,
    style_degree: float = 1.0,
    rate: int = 0,
    pitch: int = 0,
    pause_ms: int = 400
) -> str:
    """
    Constructs well-formed SSML for Edge-TTS with XML escaping, prosody, and emotion styles.
    """
    escaped_text = html.escape(text.strip())

    rate_str = f"{'+' if rate > 0 else ''}{rate}%" if rate != 0 else "+0%"
    pitch_str = f"{'+' if pitch > 0 else ''}{pitch}Hz" if pitch != 0 else "+0Hz"

    inner_content = f'<prosody rate="{rate_str}" pitch="{pitch_str}">{escaped_text}</prosody>'

    if style and style != "default":
        degree_str = f"{style_degree:.1f}"
        inner_content = f'<mstts:express-as style="{style}" styledegree="{degree_str}">{inner_content}</mstts:express-as>'

    if pause_ms > 0:
        inner_content += f'<break time="{pause_ms}ms"/>'

    return (
        f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
        f'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">'
        f'<voice name="{voice_id}">'
        f'{inner_content}'
        f'</voice>'
        f'</speak>'
    )


def split_text_into_chunks(text: str, max_words_per_chunk: int = 120) -> List[str]:
    """
    Splits long text (even 10,000+ words) into natural narrative chunks.
    Respects paragraph and sentence boundaries so that each chunk sounds natural.
    """
    paragraphs = [p.strip() for p in re.split(r'\n+', text) if p.strip()]
    chunks = []

    for paragraph in paragraphs:
        sentence_endings = re.compile(r'(?<=[.!?…])\s+')
        sentences = sentence_endings.split(paragraph)

        current_chunk = []
        current_word_count = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            words_in_sentence = len(sentence.split())

            if current_word_count + words_in_sentence > max_words_per_chunk and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_word_count = words_in_sentence
            else:
                current_chunk.append(sentence)
                current_word_count += words_in_sentence

        if current_chunk:
            chunks.append(" ".join(current_chunk))

    return chunks if chunks else [text.strip()]


async def synthesize_edge_chunk(
    chunk_text: str,
    output_path: str,
    voice_id: str,
    style: Optional[str] = None,
    style_degree: float = 1.0,
    rate: int = 0,
    pitch: int = 0,
    pause_ms: int = 400,
    retries: int = 3
) -> bool:
    """
    Synthesizes a chunk using Edge-TTS SSML.
    """
    for attempt in range(retries):
        try:
            ssml = build_ssml(
                chunk_text,
                voice_id=voice_id,
                style=style,
                style_degree=style_degree,
                rate=rate,
                pitch=pitch,
                pause_ms=pause_ms
            )
            communicate = edge_tts.Communicate(ssml, voice_id)
            await communicate.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                return True
        except Exception as e:
            if style and style != "default":
                try:
                    fallback_ssml = build_ssml(
                        chunk_text,
                        voice_id=voice_id,
                        style=None,
                        rate=rate,
                        pitch=pitch,
                        pause_ms=pause_ms
                    )
                    communicate = edge_tts.Communicate(fallback_ssml, voice_id)
                    await communicate.save(output_path)
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
                        return True
                except Exception:
                    pass
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(1.0 * (attempt + 1))
    return False


def synthesize_kokoro_chunk(
    chunk_text: str,
    output_path: str,
    voice_id: str,
    speed: float = 1.0
) -> bool:
    """
    Synthesizes a chunk using Kokoro-82M locally.
    Outputs audio at 24000 Hz.
    """
    lang_code = 'b' if voice_id.startswith('b') else 'a'
    pipeline = get_kokoro_pipeline(lang_code)

    generator = pipeline(chunk_text, voice=voice_id, speed=speed)
    audio_segments = []

    for gs, ps, audio in generator:
        if audio is not None and len(audio) > 0:
            audio_segments.append(audio)

    if not audio_segments:
        raise ValueError(f"Kokoro failed to generate audio for text: {chunk_text[:40]}")

    full_audio = np.concatenate(audio_segments)
    
    # Save as 24kHz WAV or MP3
    wav_path = output_path if output_path.endswith('.wav') else output_path.replace('.mp3', '.wav')
    sf.write(wav_path, full_audio, 24000)

    # Convert to standard MP3 if target is .mp3
    if output_path.endswith('.mp3'):
        cmd = [
            "ffmpeg", "-y",
            "-i", wav_path,
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        if os.path.exists(wav_path) and wav_path != output_path:
            try:
                os.remove(wav_path)
            except OSError:
                pass

    return True


def get_audio_duration(file_path: str) -> float:
    """
    Returns audio duration in seconds using ffprobe.
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception:
        size = os.path.getsize(file_path)
        return max(1.0, size / 16000.0)


def format_srt_timestamp(seconds: float) -> str:
    """
    Formats seconds into standard SRT timestamp: HH:MM:SS,mmm
    """
    millis = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    mins = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def concatenate_audio_files(chunk_files: List[str], final_output_path: str) -> bool:
    """
    Concatenates chunk files seamlessly into a single pristine MP3 using FFmpeg.
    """
    temp_dir = os.path.dirname(final_output_path)
    concat_list_path = os.path.join(temp_dir, f"concat_{os.path.basename(final_output_path)}.txt")

    with open(concat_list_path, "w", encoding="utf-8") as f:
        for file in chunk_files:
            safe_path = file.replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        final_output_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            reencode_cmd = [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_path,
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                final_output_path
            ]
            subprocess.run(reencode_cmd, capture_output=True, text=True, check=True)
        return True
    finally:
        if os.path.exists(concat_list_path):
            try:
                os.remove(concat_list_path)
            except OSError:
                pass


async def generate_full_story(
    task_id: str,
    engine: str,
    text: str,
    voice_id: str,
    style: Optional[str] = None,
    style_degree: float = 1.0,
    rate: int = 0,
    pitch: int = 0,
    pause_ms: int = 400,
    generate_subtitles: bool = True,
    progress_callback = None
) -> Dict[str, Any]:
    """
    Processes a complete long-form story (30+ minutes), splitting into chunks,
    synthesizing with the chosen engine (Edge or Kokoro), concatenating into final MP3,
    and generating synced SRT subtitles.
    """
    chunks = split_text_into_chunks(text)
    total_chunks = len(chunks)

    temp_chunk_dir = os.path.join(OUTPUT_DIR, f"temp_{task_id}")
    os.makedirs(temp_chunk_dir, exist_ok=True)

    chunk_files = []
    chunk_durations = []

    # Map speed parameter for Kokoro
    kokoro_speed = float(np.clip(1.0 + (rate / 100.0) * 1.2, 0.6, 1.6))

    if progress_callback:
        progress_callback(task_id, 0, total_chunks, f"Starting synthesis with {engine.upper()} engine...")

    try:
        for i, chunk in enumerate(chunks):
            chunk_file = os.path.join(temp_chunk_dir, f"chunk_{i:04d}.mp3")

            if progress_callback:
                progress_callback(
                    task_id,
                    i + 1,
                    total_chunks,
                    f"Synthesizing section {i + 1} of {total_chunks} ({engine.upper()})..."
                )

            if engine == "kokoro":
                synthesize_kokoro_chunk(
                    chunk_text=chunk,
                    output_path=chunk_file,
                    voice_id=voice_id,
                    speed=kokoro_speed
                )
            else:
                await synthesize_edge_chunk(
                    chunk_text=chunk,
                    output_path=chunk_file,
                    voice_id=voice_id,
                    style=style,
                    style_degree=style_degree,
                    rate=rate,
                    pitch=pitch,
                    pause_ms=pause_ms
                )

            chunk_files.append(chunk_file)
            dur = get_audio_duration(chunk_file)
            chunk_durations.append(dur)

        # Merge audio
        if progress_callback:
            progress_callback(task_id, total_chunks, total_chunks, "Merging audio sections into master file...")

        final_filename = f"story_{task_id}.mp3"
        final_mp3_path = os.path.join(OUTPUT_DIR, final_filename)
        concatenate_audio_files(chunk_files, final_mp3_path)

        total_duration = sum(chunk_durations)

        # Build Subtitles if requested
        srt_filename = None
        if generate_subtitles:
            srt_filename = f"story_{task_id}.srt"
            srt_path = os.path.join(OUTPUT_DIR, srt_filename)
            with open(srt_path, "w", encoding="utf-8") as srt_file:
                current_time = 0.0
                for index, (chunk, dur) in enumerate(zip(chunks, chunk_durations), start=1):
                    start_str = format_srt_timestamp(current_time)
                    end_time = current_time + dur
                    end_str = format_srt_timestamp(end_time)
                    srt_file.write(f"{index}\n{start_str} --> {end_str}\n{chunk}\n\n")
                    current_time = end_time

        return {
            "success": True,
            "filename": final_filename,
            "audio_url": f"/output/{final_filename}",
            "srt_url": f"/output/{srt_filename}" if srt_filename else None,
            "duration": round(total_duration, 2),
            "chunks_count": total_chunks,
            "word_count": len(text.split()),
            "engine": engine
        }

    finally:
        for f in chunk_files:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass
        if os.path.exists(temp_chunk_dir):
            try:
                os.rmdir(temp_chunk_dir)
            except OSError:
                pass
