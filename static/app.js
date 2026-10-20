/**
 * Storyteller Studio — Multi-Engine Suite (Edge-TTS, Kokoro-82M, ChatTTS, F5-TTS)
 * Supports 4-Engine Switching, Custom Seed, Voice Cloning, Tokens, and Dual Theme.
 */

const STATE = {
  theme: 'dark',
  engine: 'edge', // 'edge' | 'kokoro' | 'chattts' | 'f5'
  selectedLang: 'all', // 'all' | 'en' | 'fr' | 'ru'
  edgeVoices: [],
  kokoroVoices: [],
  chatttsVoices: [],
  f5ttsVoices: [],
  selectedVoice: null,
  selectedStyle: 'default',
  f5CustomAudioPath: null,
  isGenerating: false,
  taskId: null,
  pollTimer: null,
};

// Sample Stories
const SAMPLES = {
  horror: `The grandfather clock in Blackwood Manor struck midnight with a dull, echoing toll that vibrated through the floorboards. Outside, the autumn wind howled against the leaded glass windows, driving sheets of rain into the dark spruce forest.

Julian stood at the top of the spiraling oak staircase, his lantern casting long, distorted shadows across the portrait of his late ancestor. He had been warned never to return to the estate after dark. But the locked mahogany door at the end of the second-floor gallery seemed to hum with an eerie, rhythmic pulse—like the slow heartbeat of something sleeping just beneath the wood.

He took a step forward. The ancient floor groaned in protest. And then, from the stillness behind the locked door, came the distinct sound of a brass key turning slowly in the lock.`,

  scifi: `The navigation array on the starship Daedalus flickered to life as the vessel cleared the event horizon of Sector Nine. Beyond the reinforced viewport, a sea of iridescent cosmic dust swirled around the shattered remnants of an ancient Dyson sphere.

Commander Vance initiated the subspace sensor sweep. For six standard months, they had chased the encrypted harmonic signal across three star systems. Now, the signal was no longer a distant whisper. It was broadcasting from the core of the megastructure—a repetitive mathematical sequence encoded in prime numbers.

"Sensors are locking on," the AI announced, its synthetic voice calm despite the immense gravity well pulling at their shields. "Whatever built this station... it has just detected our approach."`,

  french: `Dans la pénombre du vieux manoir, une horloge ancienne sonna les douze coups de minuit. Au dehors, le vent d'automne gémissait contre les vitraux, balayant la forêt silencieuse de feuilles d'or.

Henri s'avança lentement au bout de la grande galerie de chêne. La vieille porte sculptée au fond du couloir semblait vibrer d'un mystérieux battement régulier, comme le murmure d'un secret endormi depuis plusieurs siècles. Il s'approcha, le cœur battant, et entendit le grincement discret d'une clé tournant lentement dans la serrure.`,

  russian: `Старинные башенные часы пробили полночь, и их гулкий бой прокатился по пустынным залам старинного поместья. За высокими окнами бушевала осенняя буря, срывая последние золотые листья с вековых дубов.

Дмитрий стоял у винтовой дубовой лестницы, держа в руках старинный фонарь. Он помнил строгое предостережение никогда не оставаться в усадьбе после заката. Но массивная резная дверь в конце галереи словно притягивала его к себе таинственным, едва уловимым шёпотом.`
};

// DOM Elements
const tabEdge = document.getElementById('tab-edge');
const tabKokoro = document.getElementById('tab-kokoro');
const tabChattts = document.getElementById('tab-chattts');
const tabF5 = document.getElementById('tab-f5');

const voiceGrid = document.getElementById('voice-grid');
const voiceGridLabel = document.getElementById('voice-grid-label');
const langPillsBar = document.getElementById('lang-pills-bar');
const emotionSection = document.getElementById('emotion-section');
const emotionPills = document.getElementById('emotion-pills');
const intensityGroup = document.getElementById('intensity-group');
const pitchGroup = document.getElementById('pitch-group');
const engineDesc = document.getElementById('engine-desc');

// ChatTTS specific elements
const chatttsTokenBar = document.getElementById('chattts-token-bar');
const chatttsControls = document.getElementById('chattts-controls');
const chatSeedInput = document.getElementById('chat-seed-input');
const btnRandomSeed = document.getElementById('btn-random-seed');
const tempSlider = document.getElementById('temp-slider');
const tempVal = document.getElementById('temp-val');
const oralSlider = document.getElementById('oral-slider');
const oralVal = document.getElementById('oral-val');
const laughSlider = document.getElementById('laugh-slider');
const laughVal = document.getElementById('laugh-val');

// F5-TTS specific elements
const f5ttsControls = document.getElementById('f5tts-controls');
const f5FileInput = document.getElementById('f5-file-input');
const f5RefTextInput = document.getElementById('f5-ref-text-input');
const nfeSlider = document.getElementById('nfe-slider');
const nfeVal = document.getElementById('nfe-val');

const storyText = document.getElementById('story-text');
const wordCountEl = document.getElementById('word-count');
const charCountEl = document.getElementById('char-count');
const estDurationEl = document.getElementById('est-duration');

const pauseSlider = document.getElementById('pause-slider');
const pauseVal = document.getElementById('pause-val');
const speedSlider = document.getElementById('speed-slider');
const speedVal = document.getElementById('speed-val');
const pitchSlider = document.getElementById('pitch-slider');
const pitchVal = document.getElementById('pitch-val');
const intensitySlider = document.getElementById('intensity-slider');
const intensityVal = document.getElementById('intensity-val');
const chkSubtitles = document.getElementById('chk-subtitles');

const btnSampleTrigger = document.getElementById('btn-sample-trigger');
const samplesMenu = document.getElementById('samples-menu');

const btnPreview = document.getElementById('btn-preview');
const previewIcon = document.getElementById('preview-icon');
const previewText = document.getElementById('preview-text');
const btnGenerate = document.getElementById('btn-generate');
const generateIcon = document.getElementById('generate-icon');
const generateText = document.getElementById('generate-text');

const progressCard = document.getElementById('progress-card');
const progressTitle = document.getElementById('progress-title');
const progressPercent = document.getElementById('progress-percent');
const progressBar = document.getElementById('progress-bar');
const progressSubtext = document.getElementById('progress-subtext');

const masterPlayer = document.getElementById('master-player');
const audioElement = document.getElementById('audio-element');
const previewAudioElement = document.getElementById('preview-audio-element');
const btnPlayPause = document.getElementById('btn-play-pause');
const iconPlay = document.getElementById('icon-play');
const iconPause = document.getElementById('icon-pause');
const seekBar = document.getElementById('seek-bar');
const currTime = document.getElementById('curr-time');
const totalTime = document.getElementById('total-time');
const playerTitle = document.getElementById('player-title');
const playerMeta = document.getElementById('player-meta');
const btnDownloadMp3 = document.getElementById('btn-download-mp3');
const btnDownloadSrt = document.getElementById('btn-download-srt');

const themeToggleBtn = document.getElementById('theme-toggle');
const iconSun = document.getElementById('icon-sun');
const iconMoon = document.getElementById('icon-moon');
const themeText = document.getElementById('theme-text');

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  setupEventListeners();
  await loadVoiceCatalog();
  updateTextStats();
});

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem('storyteller-theme') || 'dark';
  applyTheme(savedTheme);
}

function toggleTheme() {
  const newTheme = STATE.theme === 'dark' ? 'light' : 'dark';
  applyTheme(newTheme);
}

function applyTheme(theme) {
  STATE.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);

  if (theme === 'light') {
    document.documentElement.classList.add('light');
    document.documentElement.classList.remove('dark');
    iconSun.classList.remove('hidden');
    iconMoon.classList.add('hidden');
    themeText.textContent = 'Light';
  } else {
    document.documentElement.classList.add('dark');
    document.documentElement.classList.remove('light');
    iconMoon.classList.remove('hidden');
    iconSun.classList.add('hidden');
    themeText.textContent = 'Dark';
  }

  localStorage.setItem('storyteller-theme', theme);
}

// Event Listeners Setup
function setupEventListeners() {
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
  }

  // Engine Switchers
  tabEdge.addEventListener('click', () => switchEngine('edge'));
  tabKokoro.addEventListener('click', () => switchEngine('kokoro'));
  tabChattts.addEventListener('click', () => switchEngine('chattts'));
  tabF5.addEventListener('click', () => switchEngine('f5'));

  // Language Filter Pills
  document.querySelectorAll('.lang-pill').forEach(pill => {
    pill.addEventListener('click', (e) => {
      document.querySelectorAll('.lang-pill').forEach(p => p.classList.remove('active'));
      const btn = e.target.closest('.lang-pill');
      btn.classList.add('active');
      STATE.selectedLang = btn.dataset.lang;
      renderVoiceGrid();
    });
  });

  // Story Text Updates
  storyText.addEventListener('input', updateTextStats);

  // Quick Insert Tokens for ChatTTS
  document.querySelectorAll('.token-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const token = e.target.dataset.token;
      insertTokenAtCursor(token);
    });
  });

  // Random Seed Button for ChatTTS
  btnRandomSeed.addEventListener('click', () => {
    const randomSeed = Math.floor(Math.random() * 99999) + 1;
    chatSeedInput.value = randomSeed;
  });

  // Custom Reference Audio Upload for F5-TTS
  f5FileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload_reference', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (data.success) {
        STATE.f5CustomAudioPath = data.audio_path;
        alert(`Reference sample "${file.name}" uploaded successfully! Now type what it says in the transcript box.`);
      } else {
        alert('Upload Error: ' + (data.error || 'Failed to upload audio'));
      }
    } catch (err) {
      console.error('File upload error:', err);
      alert('Error uploading file to local server.');
    }
  });

  // Sliders Live Updates
  pauseSlider.addEventListener('input', (e) => {
    pauseVal.textContent = `${e.target.value}ms`;
  });

  speedSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    if (STATE.engine === 'kokoro' || STATE.engine === 'f5') {
      const factor = (1.0 + (val / 100) * 1.0).toFixed(2);
      speedVal.textContent = `${factor}x`;
    } else {
      speedVal.textContent = val === 0 ? 'Normal (0%)' : `${val > 0 ? '+' : ''}${val}%`;
    }
  });

  pitchSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    pitchVal.textContent = val === 0 ? '0 Hz' : `${val > 0 ? '+' : ''}${val} Hz`;
  });

  intensitySlider.addEventListener('input', (e) => {
    intensityVal.textContent = `${parseFloat(e.target.value).toFixed(1)}x`;
  });

  tempSlider.addEventListener('input', (e) => {
    tempVal.textContent = parseFloat(e.target.value).toFixed(2);
  });

  oralSlider.addEventListener('input', (e) => {
    oralVal.textContent = e.target.value;
  });

  laughSlider.addEventListener('input', (e) => {
    laughVal.textContent = e.target.value;
  });

  nfeSlider.addEventListener('input', (e) => {
    nfeVal.textContent = `${e.target.value} steps`;
  });

  // Samples Dropdown
  btnSampleTrigger.addEventListener('click', (e) => {
    e.stopPropagation();
    samplesMenu.classList.toggle('show');
  });

  document.addEventListener('click', () => {
    samplesMenu.classList.remove('show');
  });

  document.querySelectorAll('.dropdown-item').forEach(item => {
    item.addEventListener('click', (e) => {
      const sampleKey = e.target.dataset.sample;
      if (SAMPLES[sampleKey]) {
        storyText.value = SAMPLES[sampleKey];
        updateTextStats();
      }
    });
  });

  // Action Buttons
  btnPreview.addEventListener('click', auditionVoicePreview);
  btnGenerate.addEventListener('click', generateFullStory);

  // Player Controls
  btnPlayPause.addEventListener('click', togglePlayPause);
  audioElement.addEventListener('timeupdate', updateAudioProgress);
  audioElement.addEventListener('loadedmetadata', () => {
    totalTime.textContent = formatTime(audioElement.duration);
    seekBar.max = Math.floor(audioElement.duration);
  });
  audioElement.addEventListener('ended', () => {
    iconPlay.classList.remove('hidden');
    iconPause.classList.add('hidden');
  });

  seekBar.addEventListener('input', () => {
    audioElement.currentTime = seekBar.value;
  });

  document.querySelectorAll('.speed-pill').forEach(pill => {
    pill.addEventListener('click', (e) => {
      document.querySelectorAll('.speed-pill').forEach(p => p.classList.remove('active'));
      e.target.classList.add('active');
      audioElement.playbackRate = parseFloat(e.target.dataset.speed);
    });
  });
}

// Insert Token into Story Script Textarea
function insertTokenAtCursor(token) {
  const startPos = storyText.selectionStart;
  const endPos = storyText.selectionEnd;
  const originalText = storyText.value;

  storyText.value = originalText.substring(0, startPos) + " " + token + " " + originalText.substring(endPos);
  storyText.focus();
  storyText.selectionStart = startPos + token.length + 2;
  storyText.selectionEnd = startPos + token.length + 2;
  updateTextStats();
}

// Fetch Voices Catalog from Server
async function loadVoiceCatalog() {
  try {
    const res = await fetch('/api/voices');
    const data = await res.json();
    if (data.success) {
      STATE.edgeVoices = data.edge_voices || [];
      STATE.kokoroVoices = data.kokoro_voices || [];
      STATE.chatttsVoices = data.chattts_voices || [];
      STATE.f5ttsVoices = data.f5tts_voices || [];
      renderVoiceGrid();
    }
  } catch (err) {
    console.error('Failed to load voice catalog:', err);
  }
}

// Switch between the 4 Engines
function switchEngine(engine) {
  if (STATE.engine === engine) return;
  STATE.engine = engine;

  // Update Tab active styling
  [tabEdge, tabKokoro, tabChattts, tabF5].forEach(tab => tab.classList.remove('active'));

  if (engine === 'edge') {
    tabEdge.classList.add('active');
    chatttsTokenBar.classList.add('hidden');
    chatttsControls.classList.add('hidden');
    f5ttsControls.classList.add('hidden');
    emotionSection.classList.add('hidden'); // Edge neural uses direct modulation
    intensityGroup.classList.add('hidden');
    pitchGroup.classList.remove('hidden');
    if (langPillsBar) langPillsBar.classList.remove('hidden');
    voiceGridLabel.textContent = 'SELECT NARRATOR VOICE';
    engineDesc.textContent = 'Edge-TTS: Advanced Neural Multilingual models (English, French, Russian) with crystal clarity.';
  } else if (engine === 'kokoro') {
    tabKokoro.classList.add('active');
    chatttsTokenBar.classList.add('hidden');
    chatttsControls.classList.add('hidden');
    f5ttsControls.classList.add('hidden');
    emotionSection.classList.add('hidden');
    intensityGroup.classList.add('hidden');
    pitchGroup.classList.add('hidden');
    if (langPillsBar) langPillsBar.classList.remove('hidden');
    voiceGridLabel.textContent = 'SELECT KOKORO-82M VOICE';
    engineDesc.textContent = 'Kokoro-82M: Local 82M parameter StyleTTS2 model with studio human cadence (English, French).';
  } else if (engine === 'chattts') {
    tabChattts.classList.add('active');
    chatttsTokenBar.classList.remove('hidden');
    chatttsControls.classList.remove('hidden');
    f5ttsControls.classList.add('hidden');
    emotionSection.classList.add('hidden');
    intensityGroup.classList.add('hidden');
    pitchGroup.classList.add('hidden');
    if (langPillsBar) langPillsBar.classList.add('hidden');
    voiceGridLabel.textContent = 'SELECT CHATTTS SPEAKER PRESET';
    engineDesc.textContent = 'ChatTTS: Conversational & Storytelling AI with realistic laughter, sighs, and oral breathing.';
  } else if (engine === 'f5') {
    tabF5.classList.add('active');
    chatttsTokenBar.classList.add('hidden');
    chatttsControls.classList.add('hidden');
    f5ttsControls.classList.remove('hidden');
    emotionSection.classList.add('hidden');
    intensityGroup.classList.add('hidden');
    pitchGroup.classList.add('hidden');
    if (langPillsBar) langPillsBar.classList.add('hidden');
    voiceGridLabel.textContent = 'SELECT REFERENCE VOICE (OR UPLOAD YOUR OWN)';
    engineDesc.textContent = 'F5-TTS: Zero-Shot Diffusion Voice Cloning from 5-10 second reference audio samples.';
  }

  renderVoiceGrid();
}

// Render Voice Grid for active engine
function renderVoiceGrid() {
  voiceGrid.innerHTML = '';
  let voices = [];

  if (STATE.engine === 'edge') voices = STATE.edgeVoices;
  else if (STATE.engine === 'kokoro') voices = STATE.kokoroVoices;
  else if (STATE.engine === 'chattts') voices = STATE.chatttsVoices;
  else if (STATE.engine === 'f5') voices = STATE.f5ttsVoices;

  // Filter by selected language if not 'all'
  if (STATE.selectedLang !== 'all' && (STATE.engine === 'edge' || STATE.engine === 'kokoro')) {
    voices = voices.filter(v => {
      const vLang = (v.language || '').toLowerCase();
      const vLocale = (v.locale || '').toLowerCase();
      return vLang === STATE.selectedLang || vLocale.startsWith(STATE.selectedLang);
    });
  }

  if (!voices.length) {
    voiceGrid.innerHTML = '<div class="col-span-2 py-8 text-center text-zinc-500 text-xs">No voices available for this language selection.</div>';
    return;
  }

  STATE.selectedVoice = voices[0];

  // If ChatTTS, set the default seed
  if (STATE.engine === 'chattts' && STATE.selectedVoice.seed) {
    chatSeedInput.value = STATE.selectedVoice.seed;
  }

  // If F5-TTS, set default reference text
  if (STATE.engine === 'f5' && STATE.selectedVoice.ref_text) {
    f5RefTextInput.value = STATE.selectedVoice.ref_text;
  }

  voices.forEach(v => {
    const card = document.createElement('div');
    card.className = `voice-card-item ${v.id === STATE.selectedVoice.id ? 'selected' : ''}`;
    card.innerHTML = `
      <div class="voice-card-top">
        <div class="voice-name-title">
          <span class="voice-name">${v.name}</span>
          <span class="voice-archetype">${v.title}</span>
        </div>
        <span class="voice-tag">${v.tag || v.accent}</span>
      </div>
      <div class="voice-desc">${v.description}</div>
    `;

    card.addEventListener('click', () => {
      document.querySelectorAll('.voice-card-item').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      STATE.selectedVoice = v;

      if (STATE.engine === 'chattts' && v.seed) {
        chatSeedInput.value = v.seed;
      }
      if (STATE.engine === 'f5' && v.ref_text) {
        f5RefTextInput.value = v.ref_text;
      }

      renderEmotionPills();
    });

    voiceGrid.appendChild(card);
  });

  renderEmotionPills();
}

// Render Emotion Pills for Edge-TTS
function renderEmotionPills() {
  emotionPills.innerHTML = '';
  const voice = STATE.selectedVoice;

  if (!voice || STATE.engine !== 'edge' || !voice.supported_styles || !voice.supported_styles.length) {
    return;
  }

  STATE.selectedStyle = voice.default_style || voice.supported_styles[0].id;

  voice.supported_styles.forEach(style => {
    const pill = document.createElement('button');
    pill.className = `emotion-pill ${style.id === STATE.selectedStyle ? 'active' : ''}`;
    pill.textContent = style.label;

    pill.addEventListener('click', () => {
      document.querySelectorAll('.emotion-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      STATE.selectedStyle = style.id;
    });

    emotionPills.appendChild(pill);
  });
}

// Update Word Count & Estimation
function updateTextStats() {
  const text = storyText.value.trim();
  const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
  const chars = text.length;

  wordCountEl.textContent = words.toLocaleString();
  charCountEl.textContent = chars.toLocaleString();

  if (words === 0) {
    estDurationEl.textContent = '~0 min';
  } else {
    const totalMinutes = words / 140;
    const mins = Math.floor(totalMinutes);
    const secs = Math.round((totalMinutes - mins) * 60);
    estDurationEl.textContent = mins > 0 ? `~${mins}m ${secs}s` : `~${secs}s`;
  }
}

// Audition 3s Voice Preview
async function auditionVoicePreview() {
  if (!STATE.selectedVoice) return;

  const originalText = previewText.textContent;
  btnPreview.disabled = true;
  previewText.textContent = 'Generating...';

  // Use user's written prompt if available in the story editor, else fallback to voice sample_text
  let promptText = STATE.selectedVoice.sample_text || 'The silent corridor stretched endlessly into the shadows of the old manor.';
  const userText = storyText.value.trim();
  if (userText.length > 0) {
    const sentences = userText.split(/(?<=[.!?…\n])\s+/).filter(Boolean);
    promptText = sentences.length > 0 ? sentences[0].slice(0, 250) : userText.slice(0, 250);
  }

  try {
    const payload = {
      engine: STATE.engine,
      voice_id: STATE.selectedVoice.id,
      style: STATE.selectedStyle || 'default',
      style_degree: parseFloat(intensitySlider.value),
      rate: parseInt(speedSlider.value),
      pitch: parseInt(pitchSlider.value),
      text: promptText,
      chat_seed: parseInt(chatSeedInput.value) || 42,
      chat_temp: parseFloat(tempSlider.value),
      chat_oral: parseInt(oralSlider.value),
      chat_laugh: parseInt(laughSlider.value),
      f5_ref_audio: STATE.f5CustomAudioPath || STATE.selectedVoice.ref_audio,
      f5_ref_text: f5RefTextInput.value || STATE.selectedVoice.ref_text,
      f5_nfe_step: parseInt(nfeSlider.value)
    };

    const res = await fetch('/api/preview', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.success && data.audio_url) {
      previewAudioElement.src = data.audio_url + '?t=' + Date.now();
      await previewAudioElement.play();
    } else {
      alert('Preview Error: ' + (data.error || 'Failed to generate preview'));
    }
  } catch (err) {
    console.error('Preview error:', err);
    alert('Error connecting to local server.');
  } finally {
    btnPreview.disabled = false;
    previewText.textContent = originalText;
  }
}

// Generate Full Long-form Story
async function generateFullStory() {
  const text = storyText.value.trim();
  if (!text) {
    alert('Please enter your story text first.');
    storyText.focus();
    return;
  }

  if (STATE.isGenerating) return;

  STATE.isGenerating = true;
  btnGenerate.disabled = true;
  generateText.textContent = 'Processing Narrative...';

  progressCard.classList.remove('hidden');
  progressBar.style.width = '0%';
  progressPercent.textContent = '0%';
  progressTitle.textContent = `Generating narrative (${STATE.engine.toUpperCase()})...`;
  progressSubtext.textContent = 'Splitting script into story segments...';

  try {
    const payload = {
      engine: STATE.engine,
      text: text,
      voice_id: STATE.selectedVoice.id,
      style: STATE.selectedStyle,
      style_degree: parseFloat(intensitySlider.value),
      rate: parseInt(speedSlider.value),
      pitch: parseInt(pitchSlider.value),
      pause_ms: parseInt(pauseSlider.value),
      chat_seed: parseInt(chatSeedInput.value) || 42,
      chat_temp: parseFloat(tempSlider.value),
      chat_oral: parseInt(oralSlider.value),
      chat_laugh: parseInt(laughSlider.value),
      f5_ref_audio: STATE.f5CustomAudioPath || STATE.selectedVoice.ref_audio,
      f5_ref_text: f5RefTextInput.value || STATE.selectedVoice.ref_text,
      f5_nfe_step: parseInt(nfeSlider.value),
      generate_subtitles: chkSubtitles.checked
    };

    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.success && data.task_id) {
      STATE.taskId = data.task_id;
      startProgressPolling(data.task_id);
    } else {
      throw new Error(data.error || 'Generation failed to start.');
    }
  } catch (err) {
    console.error('Generation launch error:', err);
    alert('Failed to start story generation: ' + err.message);
    resetGenerateState();
  }
}

// Poll Progress
function startProgressPolling(taskId) {
  if (STATE.pollTimer) clearInterval(STATE.pollTimer);

  STATE.pollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/progress/${taskId}`);
      const task = await res.json();

      if (task.status === 'processing') {
        const pct = task.progress || 0;
        progressBar.style.width = `${pct}%`;
        progressPercent.textContent = `${pct}%`;
        progressSubtext.textContent = task.message || `Processing segment ${task.current_chunk} of ${task.total_chunks}...`;
      } else if (task.status === 'completed') {
        clearInterval(STATE.pollTimer);
        progressBar.style.width = '100%';
        progressPercent.textContent = '100%';
        progressSubtext.textContent = 'Master audio ready!';

        setTimeout(() => {
          progressCard.classList.add('hidden');
          setupMasterAudioPlayer(task.result);
          resetGenerateState();
        }, 800);
      } else if (task.status === 'error') {
        clearInterval(STATE.pollTimer);
        alert('Synthesis Error: ' + task.message);
        resetGenerateState();
      }
    } catch (err) {
      console.error('Polling error:', err);
    }
  }, 750);
}

function resetGenerateState() {
  STATE.isGenerating = false;
  btnGenerate.disabled = false;
  generateText.textContent = 'Generate Full Story Audio';
}

function setupMasterAudioPlayer(result) {
  masterPlayer.classList.remove('hidden');

  playerTitle.textContent = `${STATE.selectedVoice.name} — ${STATE.selectedVoice.title}`;
  playerMeta.textContent = `${formatTime(result.duration)} • ${result.word_count.toLocaleString()} Words • ${result.chunks_count} Sections (${result.engine.toUpperCase()})`;

  audioElement.src = result.audio_url + '?t=' + Date.now();
  btnDownloadMp3.href = `/download/${result.filename}`;
  btnDownloadMp3.setAttribute('download', result.filename);

  if (result.srt_url) {
    btnDownloadSrt.classList.remove('hidden');
    const srtFilename = result.filename.replace('.mp3', '.srt');
    btnDownloadSrt.href = `/download/${srtFilename}`;
    btnDownloadSrt.setAttribute('download', srtFilename);
  } else {
    btnDownloadSrt.classList.add('hidden');
  }

  audioElement.play().then(() => {
    iconPlay.classList.add('hidden');
    iconPause.classList.remove('hidden');
  }).catch(() => {});
}

function togglePlayPause() {
  if (audioElement.paused) {
    audioElement.play();
    iconPlay.classList.add('hidden');
    iconPause.classList.remove('hidden');
  } else {
    audioElement.pause();
    iconPlay.classList.remove('hidden');
    iconPause.classList.add('hidden');
  }
}

function updateAudioProgress() {
  if (!audioElement.duration) return;
  seekBar.value = Math.floor(audioElement.currentTime);
  currTime.textContent = formatTime(audioElement.currentTime);
}

function formatTime(seconds) {
  if (!seconds || isNaN(seconds)) return '00:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins < 10 ? '0' : ''}${mins}:${secs < 10 ? '0' : ''}${secs}`;
}
