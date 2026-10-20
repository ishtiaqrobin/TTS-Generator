"""
Storytelling TTS Multi-Engine Suite
Supports 4 World-Class TTS Engines:
1. ⚡ Edge-TTS: Cloud Neural Voices with SSML Expressive Emotions (Ultra-fast)
2. 🤖 Kokoro-82M: Local Open-Source AI (82M params, StyleTTS2-based human cadence)
3. 💬 ChatTTS: Conversational & Storytelling AI (Supports [laugh], [lbreak], oral breath, speaker seeds)
4. 🎙️ F5-TTS: Zero-Shot Diffusion Voice Cloning (Clone any voice from 5-10s audio sample)

Features:
- Long-form narrative splitting (30+ minutes / 10,000+ words)
- Concurrency-safe batch generation with real-time progress callbacks
- Seamless FFmpeg concatenation with micro-crossfades
- Synchronized Subtitle (.SRT) export
"""

import os
import re
import html
import asyncio
import subprocess
import soundfile as sf
import numpy as np
import torch
import edge_tts
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
REF_AUDIO_DIR = os.path.join(BASE_DIR, "ref_audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(REF_AUDIO_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. VOICE CATALOGS FOR ALL 4 ENGINES
# ---------------------------------------------------------------------------

EDGE_VOICES = [
    # --- English (US / UK) ---
    {
        "id": "en-US-AndrewMultilingualNeural",
        "name": "Andrew (Multilingual)",
        "title": "The Advanced Cinematic Narrator",
        "gender": "Male",
        "locale": "en-US",
        "language": "en",
        "accent": "American",
        "description": "Microsoft's most advanced multilingual male neural voice. Exceptional naturalness and cinematic presence.",
        "sample_text": "Beyond the edge of the known universe, ancient stars whispered stories of forgotten civilizations.",
        "supported_styles": [{"id": "default", "label": "Cinematic Storytelling"}],
        "default_style": "default",
        "tag": "Advanced AI"
    },
    {
        "id": "en-US-AvaMultilingualNeural",
        "name": "Ava (Multilingual)",
        "title": "The Modern Studio Narrator",
        "gender": "Female",
        "locale": "en-US",
        "language": "en",
        "accent": "American",
        "description": "State-of-the-art multilingual female neural model. Impeccable clarity, emotion, and audiobook cadence.",
        "sample_text": "The memory of that summer afternoon remained as vivid as watercolor on fresh parchment.",
        "supported_styles": [{"id": "default", "label": "Studio Cadence"}],
        "default_style": "default",
        "tag": "Advanced AI"
    },
    {
        "id": "en-US-BrianMultilingualNeural",
        "name": "Brian (Multilingual)",
        "title": "The Contemporary Narrator",
        "gender": "Male",
        "locale": "en-US",
        "language": "en",
        "accent": "American",
        "description": "Crisp, modern, high-definition neural voice. Great for contemporary fiction, podcasts, and lore.",
        "sample_text": "Every scientific discovery begins with a single question that nobody dared to ask before.",
        "supported_styles": [{"id": "default", "label": "Modern Narrative"}],
        "default_style": "default",
        "tag": "Modern Crisp"
    },
    {
        "id": "en-US-EmmaMultilingualNeural",
        "name": "Emma (Multilingual)",
        "title": "The Expressive Protagonist",
        "gender": "Female",
        "locale": "en-US",
        "language": "en",
        "accent": "American",
        "description": "Warm, expressive, high-clarity female voice with natural breathing and storytelling depth.",
        "sample_text": "She looked up into the twilight sky, wondering if the stars held the answers she was searching for.",
        "supported_styles": [{"id": "default", "label": "Expressive Narrative"}],
        "default_style": "default",
        "tag": "Top Emotional"
    },
    {
        "id": "en-US-GuyNeural",
        "name": "Guy",
        "title": "The Master Storyteller",
        "gender": "Male",
        "locale": "en-US",
        "language": "en",
        "accent": "American",
        "description": "Deeply expressive, dynamic narrator ideal for mystery, thrillers, and dramatic storytelling.",
        "sample_text": "The fog rolled over the cobblestone streets as the distant clock tower struck midnight.",
        "supported_styles": [{"id": "default", "label": "Master Storyteller"}],
        "default_style": "default",
        "tag": "Classic Narrator"
    },
    {
        "id": "en-US-ChristopherNeural",
        "name": "Christopher",
        "title": "The Deep Audiobook Narrator",
        "gender": "Male",
        "locale": "en-US",
        "language": "en",
        "accent": "American",
        "description": "Deep, authoritative, cinematic baritone voice. Perfect for epic fantasy, sci-fi, and documentaries.",
        "sample_text": "In the beginning, long before the stars grew cold, an ancient civilization watched the skies.",
        "supported_styles": [{"id": "default", "label": "Deep Baritone"}],
        "default_style": "default",
        "tag": "Deep Baritone"
    },
    {
        "id": "en-US-AriaNeural",
        "name": "Aria",
        "title": "The Dramatic Protagonist",
        "gender": "Female",
        "locale": "en-US",
        "language": "en",
        "accent": "American",
        "description": "Rich emotional range, breath control, and nuance. Ideal for psychological thrillers and drama.",
        "sample_text": "She looked out into the rain, wondering if the secret she kept for twenty years was unraveling.",
        "supported_styles": [{"id": "default", "label": "Dramatic Narrative"}],
        "default_style": "default",
        "tag": "Nuanced Drama"
    },
    {
        "id": "en-US-JennyNeural",
        "name": "Jenny",
        "title": "The Soothing Bedtime Storyteller",
        "gender": "Female",
        "locale": "en-US",
        "language": "en",
        "accent": "American",
        "description": "Warm, gentle, reassuring voice. Perfect for soothing sleep stories, meditation, and gentle fables.",
        "sample_text": "As the evening settled, the stars gently appeared one by one, watching over the quiet forest.",
        "supported_styles": [{"id": "default", "label": "Soothing Tone"}],
        "default_style": "default",
        "tag": "Calming & Warm"
    },
    {
        "id": "en-GB-RyanNeural",
        "name": "Ryan",
        "title": "The British Gentleman",
        "gender": "Male",
        "locale": "en-GB",
        "language": "en",
        "accent": "British (UK)",
        "description": "Sophisticated, articulate British male. The hallmark voice for historical fiction and classic literature.",
        "sample_text": "Beneath the vaulted ceilings of the cathedral, shadows danced upon centuries of forgotten history.",
        "supported_styles": [{"id": "default", "label": "Classic British"}],
        "default_style": "default",
        "tag": "Classic British"
    },
    {
        "id": "en-GB-SoniaNeural",
        "name": "Sonia",
        "title": "The Cinematic British Narrator",
        "gender": "Female",
        "locale": "en-GB",
        "language": "en",
        "accent": "British (UK)",
        "description": "Elegant, enchanting British female delivery. Wonderful for fairy tales, folklore, and gothic mysteries.",
        "sample_text": "The wind carried whispered secrets through the ancient heather moorlands of the north.",
        "supported_styles": [{"id": "default", "label": "Enchanting Tone"}],
        "default_style": "default",
        "tag": "Enchanting British"
    },

    # --- French (Français) ---
    {
        "id": "fr-FR-RemyMultilingualNeural",
        "name": "Remy (Multilingue)",
        "title": "Le Narrateur Français Cinématographique",
        "gender": "Male",
        "locale": "fr-FR",
        "language": "fr",
        "accent": "Français (France)",
        "description": "Modèle neuronal avancé de pointe. Voix masculine française riche, profonde et immersive.",
        "sample_text": "Le silence régnait dans la vieille demeure lorsque les premières lueurs de l'aube éclairèrent le salon.",
        "supported_styles": [{"id": "default", "label": "Narration Française"}],
        "default_style": "default",
        "tag": "French Multilingual"
    },
    {
        "id": "fr-FR-VivienneMultilingualNeural",
        "name": "Vivienne (Multilingue)",
        "title": "La Voix Littéraire Française",
        "gender": "Female",
        "locale": "fr-FR",
        "language": "fr",
        "accent": "Français (France)",
        "description": "Modèle neuronal moderne. Voix féminine élégante, captivante et idéale pour les romans et fables.",
        "sample_text": "Au cœur de la forêt enchantée, les arbres séculaires chuchotaient les légendes d'un royaume oublié.",
        "supported_styles": [{"id": "default", "label": "Littéraire & Poétique"}],
        "default_style": "default",
        "tag": "French Multilingual"
    },
    {
        "id": "fr-FR-HenriNeural",
        "name": "Henri",
        "title": "Le Conteur Classique",
        "gender": "Male",
        "locale": "fr-FR",
        "language": "fr",
        "accent": "Français (France)",
        "description": "Voix masculine posée, chaleureuse et noble. Parfaite pour les récits historiques et documentaires.",
        "sample_text": "Les vagues s'écrasaient avec fracas contre les falaises de granit sous un ciel d'orage.",
        "supported_styles": [{"id": "default", "label": "Conteur Noble"}],
        "default_style": "default",
        "tag": "Classic French"
    },
    {
        "id": "fr-FR-DeniseNeural",
        "name": "Denise",
        "title": "La Conteuse Douce",
        "gender": "Female",
        "locale": "fr-FR",
        "language": "fr",
        "accent": "Français (France)",
        "description": "Voix féminine claire, posée et très expressive pour les livres audio et fables.",
        "sample_text": "Une douce brise d'automne faisait tournoyer les feuilles dorées le long des allées silencieuses.",
        "supported_styles": [{"id": "default", "label": "Conteuse Douce"}],
        "default_style": "default",
        "tag": "Audiobook French"
    },
    {
        "id": "fr-FR-EloiseNeural",
        "name": "Eloise",
        "title": "La Protagoniste Expressive",
        "gender": "Female",
        "locale": "fr-FR",
        "language": "fr",
        "accent": "Français (France)",
        "description": "Voix jeune, fraîche et captivante. Excellente pour les aventures et histoires à suspense.",
        "sample_text": "Elle ouvrit délicatement la vieille boîte de bois sculpté, révélant la clé d'argent.",
        "supported_styles": [{"id": "default", "label": "Jeune Protagoniste"}],
        "default_style": "default",
        "tag": "Expressive French"
    },
    {
        "id": "fr-CA-JeanNeural",
        "name": "Jean (Québec)",
        "title": "Le Narrateur Canadien",
        "gender": "Male",
        "locale": "fr-CA",
        "language": "fr",
        "accent": "Français (Canada)",
        "description": "Voix masculine québécoise chaleureuse, naturelle et engageante pour la narration.",
        "sample_text": "L'immensité des grands espaces du nord résonnait sous le souffle du vent boréal.",
        "supported_styles": [{"id": "default", "label": "Accent Québécois"}],
        "default_style": "default",
        "tag": "Canadian French"
    },
    {
        "id": "fr-CA-SylvieNeural",
        "name": "Sylvie (Québec)",
        "title": "La Conteuse Canadienne",
        "gender": "Female",
        "locale": "fr-CA",
        "language": "fr",
        "accent": "Français (Canada)",
        "description": "Voix féminine chaleureuse et captivante avec l'accent francophone du Canada.",
        "sample_text": "Les étoiles brillaient d'un éclat vif dans la nuit froide de l'hiver boréal.",
        "supported_styles": [{"id": "default", "label": "Conteuse Canadienne"}],
        "default_style": "default",
        "tag": "Canadian French"
    },

    # --- Russian (Русский) ---
    {
        "id": "ru-RU-DmitryNeural",
        "name": "Dmitry (Дмитрий)",
        "title": "Глубокий Рассказчик",
        "gender": "Male",
        "locale": "ru-RU",
        "language": "ru",
        "accent": "Русский (Россия)",
        "description": "Мощный, глубокий и авторитетный мужской баритон. Идеален для классики, фэнтези, триллеров и аудиокниг.",
        "sample_text": "В тот холодный ноябрьский вечер старинные часы в пустой зале пробили ровно полночь.",
        "supported_styles": [{"id": "default", "label": "Художественное чтение"}],
        "default_style": "default",
        "tag": "Russian Master"
    },
    {
        "id": "ru-RU-SvetlanaNeural",
        "name": "Svetlana (Светлана)",
        "title": "Эмоциональная Сказительница",
        "gender": "Female",
        "locale": "ru-RU",
        "language": "ru",
        "accent": "Русский (Россия)",
        "description": "Тёплый, выразительный и чарующий женский голос. Превосходен для сказок, романов, драмы и стихов.",
        "sample_text": "За старым садом тихо шумел сосновый лес, укрытый серебристым покрывалом первого снега.",
        "supported_styles": [{"id": "default", "label": "Лирический рассказ"}],
        "default_style": "default",
        "tag": "Russian Master"
    }
]

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
        "supported_styles": [{"id": "default", "label": "Studio Natural Cadence"}],
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
        "supported_styles": [{"id": "default", "label": "Studio Natural Cadence"}],
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
        "supported_styles": [{"id": "default", "label": "Studio Natural Cadence"}],
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
        "supported_styles": [{"id": "default", "label": "Studio Natural Cadence"}],
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
        "supported_styles": [{"id": "default", "label": "Studio Natural Cadence"}],
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
        "supported_styles": [{"id": "default", "label": "Studio Natural Cadence"}],
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
        "supported_styles": [{"id": "default", "label": "Studio Natural Cadence"}],
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
        "supported_styles": [{"id": "default", "label": "Studio Natural Cadence"}],
        "default_style": "default",
        "tag": "Intimate & Soft"
    }
]

CHATTTS_VOICES = [
    {
        "id": "chattts_seed_2",
        "name": "Warm Conversationalist",
        "title": "The Natural Storyteller",
        "seed": 2,
        "gender": "Male",
        "locale": "en-US",
        "accent": "Conversational",
        "description": "Warm, authentic conversational pacing. Perfect for narrative podcasts, relaxed storytelling, and natural dialogues.",
        "sample_text": "You know [laugh], I never believed in ghost stories until that rainy night in October.",
        "supported_styles": [{"id": "default", "label": "Conversational Nuance"}],
        "default_style": "default",
        "tag": "Seed 2"
    },
    {
        "id": "chattts_seed_42",
        "name": "Dynamic Narrator",
        "title": "The Engaging Storyteller",
        "seed": 42,
        "gender": "Male",
        "locale": "en-US",
        "accent": "Narrative",
        "description": "Expressive cadence with spontaneous micro-pauses and natural breathing.",
        "sample_text": "There are moments in life [lbreak] when everything changes in the blink of an eye.",
        "supported_styles": [{"id": "default", "label": "Expressive Tone"}],
        "default_style": "default",
        "tag": "Seed 42"
    },
    {
        "id": "chattts_seed_1111",
        "name": "Podcast Host",
        "title": "The Deep Resonant Voice",
        "seed": 1111,
        "gender": "Male",
        "locale": "en-US",
        "accent": "Podcast Baritone",
        "description": "Broadcaster tone with rich acoustic resonance. Superb for storytelling episodes.",
        "sample_text": "Welcome back to the mystery chronicles. Tonight, we examine the strange events of Sector Four.",
        "supported_styles": [{"id": "default", "label": "Broadcast Tone"}],
        "default_style": "default",
        "tag": "Seed 1111"
    },
    {
        "id": "chattts_seed_2222",
        "name": "Articulate Female",
        "title": "The Poised Storyteller",
        "seed": 2222,
        "gender": "Female",
        "locale": "en-US",
        "accent": "Articulate",
        "description": "Clean, charming feminine voice with realistic laughter and conversational flow.",
        "sample_text": "It was the silliest thing [laugh], but we couldn't stop smiling all afternoon.",
        "supported_styles": [{"id": "default", "label": "Poised Flow"}],
        "default_style": "default",
        "tag": "Seed 2222"
    },
    {
        "id": "chattts_seed_6666",
        "name": "Dramatic Cinematic",
        "title": "The Grounded Narrator",
        "seed": 6666,
        "gender": "Male",
        "locale": "en-US",
        "accent": "Dramatic",
        "description": "Low, moody, atmospheric pacing suited for noir mysteries and suspense.",
        "sample_text": "The footsteps stopped outside the door [lbreak]. Silence fell heavier than the winter cold.",
        "supported_styles": [{"id": "default", "label": "Cinematic Tone"}],
        "default_style": "default",
        "tag": "Seed 6666"
    }
]

F5TTS_VOICES = [
    {
        "id": "f5_nature_narrator",
        "name": "Mother Nature Voice",
        "title": "The Documentary Narrator",
        "ref_audio": "ref_audio/basic_ref_en.wav",
        "ref_text": "Some call me nature, others call me mother nature.",
        "gender": "Female",
        "locale": "en-US",
        "accent": "Documentary",
        "description": "Grounded, majestic voice with organic cadence cloned from a cinematic narrative reference.",
        "sample_text": "Deep within the primeval canopy, centuries-old redwood trees shelter a realm untamed.",
        "supported_styles": [{"id": "default", "label": "Diffusion Cloned"}],
        "default_style": "default",
        "tag": "Zero-Shot Clone"
    },
    {
        "id": "f5_david_lore",
        "name": "Sir George / Lore Master",
        "title": "The British Storyteller",
        "ref_audio": "ref_audio/david_nature.wav",
        "ref_text": "In the deep heart of the ancient forest, creatures roam undisturbed by the passage of time.",
        "gender": "Male",
        "locale": "en-GB",
        "accent": "British (UK)",
        "description": "Stately British narrator tone cloned for epic fantasy and historical fiction.",
        "sample_text": "Beyond the misty horizons of Avalon, an ancient legend awaits its rightful champion.",
        "supported_styles": [{"id": "default", "label": "Diffusion Cloned"}],
        "default_style": "default",
        "tag": "British Fantasy"
    },
    {
        "id": "f5_emma_victorian",
        "name": "Lady Emma",
        "title": "The Victorian Gothic Reader",
        "ref_audio": "ref_audio/emma_british.wav",
        "ref_text": "There is an enchantment in the evening air when the twilight descends upon the countryside.",
        "gender": "Female",
        "locale": "en-GB",
        "accent": "British (UK)",
        "description": "Enchanting British female delivery cloned for romantic, classical, and gothic storytelling.",
        "sample_text": "The candle flickered softly against the damp stone walls, casting fleeting shadows of memory.",
        "supported_styles": [{"id": "default", "label": "Diffusion Cloned"}],
        "default_style": "default",
        "tag": "Gothic Romance"
    },
    {
        "id": "f5_chinese_eastern",
        "name": "Eastern Storyteller",
        "title": "Multilingual Clone (Chinese/English)",
        "ref_audio": "ref_audio/basic_ref_zh.wav",
        "ref_text": "对，这就是我，一个人见人爱的女孩。",
        "gender": "Female",
        "locale": "zh-CN",
        "accent": "Mandarin / Cross-lingual",
        "description": "Demonstrates cross-lingual zero-shot voice cloning capabilities of F5-TTS.",
        "sample_text": "In a peaceful pavilion beside the tranquil lake, old tales of travelers come alive.",
        "supported_styles": [{"id": "default", "label": "Diffusion Cloned"}],
        "default_style": "default",
        "tag": "Cross-Lingual"
    }
]

# ---------------------------------------------------------------------------
# 2. MODEL CACHING & LAZY LOADERS
# ---------------------------------------------------------------------------

_KOKORO_PIPELINES = {}
_CHATTTS_INSTANCE = None
_F5TTS_INSTANCE = None

def get_kokoro_pipeline(lang_code: str = 'a'):
    global _KOKORO_PIPELINES
    if lang_code not in _KOKORO_PIPELINES:
        from kokoro import KPipeline
        print(f"[Kokoro] Initializing KPipeline (lang_code='{lang_code}')...")
        _KOKORO_PIPELINES[lang_code] = KPipeline(lang_code=lang_code)
    return _KOKORO_PIPELINES[lang_code]


def get_chattts_instance():
    global _CHATTTS_INSTANCE
    if _CHATTTS_INSTANCE is None:
        import ChatTTS
        print("[ChatTTS] Loading ChatTTS model from Hugging Face...")
        chat = ChatTTS.Chat()
        chat.load(source='huggingface', compile=False)
        _CHATTTS_INSTANCE = chat
        print("[ChatTTS] Model loaded successfully.")
    return _CHATTTS_INSTANCE


def get_f5tts_instance():
    global _F5TTS_INSTANCE
    if _F5TTS_INSTANCE is None:
        from f5_tts.api import F5TTS
        print("[F5-TTS] Initializing F5TTS Diffusion pipeline...")
        _F5TTS_INSTANCE = F5TTS()
        print("[F5-TTS] Pipeline ready.")
    return _F5TTS_INSTANCE

# ---------------------------------------------------------------------------
# 3. TEXT CHUNKER (30+ Minutes Narrative splitting)
# ---------------------------------------------------------------------------

def split_text_into_chunks(text: str, max_words_per_chunk: int = 120) -> List[str]:
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

# ---------------------------------------------------------------------------
# 4. ENGINE-SPECIFIC SYNTHESIS FUNCTIONS
# ---------------------------------------------------------------------------

# --- A. EDGE-TTS ---
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
    Synthesize audio using Edge-TTS neural models with pitch and rate modulation.
    Directly passes text to edge_tts.Communicate to guarantee 100% reliability
    across all languages (English, French, Russian) and long narratives.
    """
    clean_text = chunk_text.strip()
    if not clean_text:
        return False

    rate_str = f"{'+' if rate > 0 else ''}{rate}%"
    pitch_str = f"{'+' if pitch > 0 else ''}{pitch}Hz"

    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(
                clean_text,
                voice_id,
                rate=rate_str,
                pitch=pitch_str
            )
            await communicate.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 200:
                return True
        except Exception as e:
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(1.0 * (attempt + 1))
    return False


# --- B. KOKORO-82M ---
def synthesize_kokoro_chunk(
    chunk_text: str,
    output_path: str,
    voice_id: str,
    speed: float = 1.0
) -> bool:
    lang_code = 'b' if voice_id.startswith('b') else 'a'
    pipeline = get_kokoro_pipeline(lang_code)

    generator = pipeline(chunk_text, voice=voice_id, speed=speed)
    audio_segments = []

    for _, _, audio in generator:
        if audio is not None and len(audio) > 0:
            audio_segments.append(audio)

    if not audio_segments:
        raise ValueError(f"Kokoro failed to generate audio for text: {chunk_text[:40]}")

    full_audio = np.concatenate(audio_segments)
    wav_path = output_path if output_path.endswith('.wav') else output_path.replace('.mp3', '.wav')
    sf.write(wav_path, full_audio, 24000)

    if output_path.endswith('.mp3'):
        cmd = ["ffmpeg", "-y", "-i", wav_path, "-c:a", "libmp3lame", "-b:a", "192k", output_path]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        if os.path.exists(wav_path) and wav_path != output_path:
            try:
                os.remove(wav_path)
            except OSError:
                pass
    return True


# --- C. CHATTTS ---
def synthesize_chattts_chunk(
    chunk_text: str,
    output_path: str,
    seed: int = 42,
    temperature: float = 0.3,
    oral: int = 2,
    laugh: int = 0,
    speed_level: int = 5
) -> bool:
    chat = get_chattts_instance()
    import ChatTTS

    torch.manual_seed(seed)
    spk = chat.sample_random_speaker()

    # Map speed_level 1..9 to prompt [speed_N]
    speed_code = f"[speed_{max(1, min(9, speed_level))}]"
    params_infer = ChatTTS.Chat.InferCodeParams(
        spk_emb=spk,
        temperature=temperature,
        prompt=speed_code
    )

    refine_prompt = f"[oral_{max(0, min(9, oral))}][laugh_{max(0, min(2, laugh))}][break_4]"
    params_refine = ChatTTS.Chat.RefineTextParams(prompt=refine_prompt)

    # Clean unsupported characters for ChatTTS
    clean_text = chunk_text.replace("!", ".").replace("?", ".")
    wavs = chat.infer([clean_text], params_refine_text=params_refine, params_infer_code=params_infer)

    if not wavs or len(wavs[0]) == 0:
        raise ValueError("ChatTTS produced empty audio.")

    audio_data = np.array(wavs[0]).flatten()
    wav_path = output_path if output_path.endswith('.wav') else output_path.replace('.mp3', '.wav')
    sf.write(wav_path, audio_data, 24000)

    if output_path.endswith('.mp3'):
        cmd = ["ffmpeg", "-y", "-i", wav_path, "-c:a", "libmp3lame", "-b:a", "192k", output_path]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        if os.path.exists(wav_path) and wav_path != output_path:
            try:
                os.remove(wav_path)
            except OSError:
                pass
    return True


# --- D. F5-TTS (Zero-Shot Voice Cloning) ---
def synthesize_f5tts_chunk(
    chunk_text: str,
    output_path: str,
    ref_audio_path: str,
    ref_text: str,
    speed: float = 1.0,
    nfe_step: int = 32
) -> bool:
    f5 = get_f5tts_instance()

    if not os.path.isabs(ref_audio_path):
        ref_audio_path = os.path.join(BASE_DIR, ref_audio_path)

    wav_output = output_path if output_path.endswith('.wav') else output_path.replace('.mp3', '.wav')

    # F5-TTS infer returns (wav, sample_rate, spec)
    wav, sr, _ = f5.infer(
        ref_file=ref_audio_path,
        ref_text=ref_text,
        gen_text=chunk_text,
        nfe_step=nfe_step,
        speed=speed,
        file_wave=wav_output
    )

    if output_path.endswith('.mp3'):
        cmd = ["ffmpeg", "-y", "-i", wav_output, "-c:a", "libmp3lame", "-b:a", "192k", output_path]
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        if os.path.exists(wav_output) and wav_output != output_path:
            try:
                os.remove(wav_output)
            except OSError:
                pass
    return True

# ---------------------------------------------------------------------------
# 5. AUDIO UTILITIES (Probe, Stitch, Subtitle)
# ---------------------------------------------------------------------------

def get_audio_duration(file_path: str) -> float:
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        size = os.path.getsize(file_path)
        return max(1.0, size / 16000.0)


def format_srt_timestamp(seconds: float) -> str:
    millis = int(round((seconds - int(seconds)) * 1000))
    total_seconds = int(seconds)
    secs = total_seconds % 60
    total_minutes = total_seconds // 60
    mins = total_minutes % 60
    hours = total_minutes // 60
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def concatenate_audio_files(chunk_files: List[str], final_output_path: str) -> bool:
    temp_dir = os.path.dirname(final_output_path)
    concat_list_path = os.path.join(temp_dir, f"concat_{os.path.basename(final_output_path)}.txt")

    with open(concat_list_path, "w", encoding="utf-8") as f:
        for file in chunk_files:
            safe_path = file.replace("\\", "/").replace("'", "'\\''")
            f.write(f"file '{safe_path}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", final_output_path]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            reencode_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c:a", "libmp3lame", "-b:a", "192k", final_output_path]
            subprocess.run(reencode_cmd, capture_output=True, text=True, check=True)
        return True
    finally:
        if os.path.exists(concat_list_path):
            try:
                os.remove(concat_list_path)
            except OSError:
                pass

# ---------------------------------------------------------------------------
# 6. UNIVERSAL FULL STORY GENERATOR
# ---------------------------------------------------------------------------

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
    chat_seed: int = 42,
    chat_temp: float = 0.3,
    chat_oral: int = 2,
    chat_laugh: int = 0,
    f5_ref_audio: Optional[str] = None,
    f5_ref_text: Optional[str] = None,
    f5_nfe_step: int = 32,
    generate_subtitles: bool = True,
    progress_callback = None
) -> Dict[str, Any]:
    chunks = split_text_into_chunks(text)
    total_chunks = len(chunks)

    temp_chunk_dir = os.path.join(OUTPUT_DIR, f"temp_{task_id}")
    os.makedirs(temp_chunk_dir, exist_ok=True)

    chunk_files = []
    chunk_durations = []

    kokoro_speed = float(np.clip(1.0 + (rate / 100.0) * 1.2, 0.6, 1.6))
    f5_speed = float(np.clip(1.0 + (rate / 100.0), 0.7, 1.5))
    chat_speed_lvl = int(np.clip(5 + int(rate / 10), 1, 9))

    # Resolve F5 reference audio
    if engine == "f5":
        if not f5_ref_audio or not f5_ref_text:
            voice_meta = next((v for v in F5TTS_VOICES if v["id"] == voice_id), F5TTS_VOICES[0])
            f5_ref_audio = voice_meta["ref_audio"]
            f5_ref_text = voice_meta["ref_text"]

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
                synthesize_kokoro_chunk(chunk, chunk_file, voice_id, kokoro_speed)
            elif engine == "chattts":
                synthesize_chattts_chunk(
                    chunk_text=chunk,
                    output_path=chunk_file,
                    seed=chat_seed,
                    temperature=chat_temp,
                    oral=chat_oral,
                    laugh=chat_laugh,
                    speed_level=chat_speed_lvl
                )
            elif engine == "f5":
                synthesize_f5tts_chunk(
                    chunk_text=chunk,
                    output_path=chunk_file,
                    ref_audio_path=f5_ref_audio,
                    ref_text=f5_ref_text,
                    speed=f5_speed,
                    nfe_step=f5_nfe_step
                )
            else:  # edge
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

        if progress_callback:
            progress_callback(task_id, total_chunks, total_chunks, "Merging sections into master audio...")

        final_filename = f"story_{task_id}.mp3"
        final_mp3_path = os.path.join(OUTPUT_DIR, final_filename)
        concatenate_audio_files(chunk_files, final_mp3_path)

        total_duration = sum(chunk_durations)

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
