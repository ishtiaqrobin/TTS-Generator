/**
 * Storyteller Studio — Frontend Application Logic
 * Supports Hybrid Engine (Edge-TTS & Kokoro-TTS), Voice Selection,
 * Live Pacing & Pitch Fine-tuning, Progress Tracking, and Master Audio Player.
 */

const STATE = {
  engine: 'edge', // 'edge' | 'kokoro'
  edgeVoices: [],
  kokoroVoices: [],
  selectedVoice: null,
  selectedStyle: 'narration-relaxed',
  isGenerating: false,
  taskId: null,
  pollTimer: null,
};

// Sample Stories for instant auditioning & storytelling tests
const SAMPLES = {
  horror: `The grandfather clock in Blackwood Manor struck midnight with a dull, echoing toll that vibrated through the floorboards. Outside, the autumn wind howled against the leaded glass windows, driving sheets of rain into the dark spruce forest.

Julian stood at the top of the spiraling oak staircase, his lantern casting long, distorted shadows across the portrait of his late ancestor. He had been warned never to return to the estate after dark. But the locked mahogany door at the end of the second-floor gallery seemed to hum with an eerie, rhythmic pulse—like the slow heartbeat of something sleeping just beneath the wood.

He took a step forward. The ancient floor groaned in protest. And then, from the stillness behind the locked door, came the distinct sound of a brass key turning slowly in the lock.`,

  scifi: `The navigation array on the starship Daedalus flickered to life as the vessel cleared the event horizon of Sector Nine. Beyond the reinforced viewport, a sea of iridescent cosmic dust swirled around the shattered remnants of an ancient Dyson sphere.

Commander Vance initiated the subspace sensor sweep. For six standard months, they had chased the encrypted harmonic signal across three star systems. Now, the signal was no longer a distant whisper. It was broadcasting from the core of the megastructure—a repetitive mathematical sequence encoded in prime numbers.

"Sensors are locking on," the AI announced, its synthetic voice calm despite the immense gravity well pulling at their shields. "Whatever built this station... it has just detected our approach."`,

  fantasy: `High above the Mistveil Valley, the stone spires of the Forgotten Citadel pierced the twilight sky. Legends spoke of the Ember Crown—an artifact forged in the first fires of creation, said to grant its bearer dominion over both shadow and flame.

Lady Kimberly pulled her velvet cloak tighter against the mountain frost as she approached the ruined archway. In her palm, the glowing runestone pulsed with a warm, amber light, illuminating the ancient glyphs carved into the granite pillars. 

Suddenly, a flock of white ravens burst from the bell tower, scattering into the darkening clouds. A deep, melodic chant echoed from the abyss beneath the altar, carrying the forgotten words of a kingdom that vanished a thousand years ago.`
};

// DOM Elements
const tabEdge = document.getElementById('tab-edge');
const tabKokoro = document.getElementById('tab-kokoro');
const voiceGrid = document.getElementById('voice-grid');
const emotionSection = document.getElementById('emotion-section');
const emotionPills = document.getElementById('emotion-pills');
const intensityGroup = document.getElementById('intensity-group');
const pitchGroup = document.getElementById('pitch-group');
const engineDesc = document.getElementById('engine-desc');

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

// Theme Management (Dark Mode & Light Mode)
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

// Event Listeners
function setupEventListeners() {
  // Theme Toggle Button
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', toggleTheme);
  }

  // Engine Tab Switching
  tabEdge.addEventListener('click', () => switchEngine('edge'));
  tabKokoro.addEventListener('click', () => switchEngine('kokoro'));

  // Text Stats
  storyText.addEventListener('input', updateTextStats);

  // Sliders Live Values
  pauseSlider.addEventListener('input', (e) => {
    pauseVal.textContent = `${e.target.value}ms`;
  });

  speedSlider.addEventListener('input', (e) => {
    const val = parseInt(e.target.value);
    if (STATE.engine === 'kokoro') {
      // Map -30..30 to 0.7x..1.5x
      const factor = (1.0 + (val / 100) * 1.2).toFixed(2);
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

  // Sample Stories Dropdown
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

  // Master Audio Player Controls
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

// Fetch Voices from Backend
async function loadVoiceCatalog() {
  try {
    const res = await fetch('/api/voices');
    const data = await res.json();
    if (data.success) {
      STATE.edgeVoices = data.edge_voices || [];
      STATE.kokoroVoices = data.kokoro_voices || [];
      renderVoiceGrid();
    }
  } catch (err) {
    console.error('Failed to load voices:', err);
  }
}

// Switch between Edge-TTS and Kokoro-TTS
function switchEngine(engine) {
  if (STATE.engine === engine) return;
  STATE.engine = engine;

  if (engine === 'edge') {
    tabEdge.classList.add('active');
    tabKokoro.classList.remove('active');
    emotionSection.classList.remove('hidden');
    intensityGroup.classList.remove('hidden');
    pitchGroup.classList.remove('hidden');
    engineDesc.textContent = 'Edge-TTS: Cloud Neural voices with express-as SSML styles and lightning-fast rendering.';
  } else {
    tabKokoro.classList.add('active');
    tabEdge.classList.remove('active');
    emotionSection.classList.add('hidden');
    intensityGroup.classList.add('hidden');
    pitchGroup.classList.add('hidden');
    engineDesc.textContent = 'Kokoro-82M: State-of-the-art local AI model with human-grade rhythm, cadence, and breath.';
  }

  renderVoiceGrid();
}

// Render Voice Grid
function renderVoiceGrid() {
  voiceGrid.innerHTML = '';
  const voices = STATE.engine === 'edge' ? STATE.edgeVoices : STATE.kokoroVoices;

  if (!voices.length) {
    voiceGrid.innerHTML = '<div style="color:var(--text-muted);font-size:0.8rem;">No voices available.</div>';
    return;
  }

  // Set default selection to first voice
  STATE.selectedVoice = voices[0];

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
      renderEmotionPills();
    });

    voiceGrid.appendChild(card);
  });

  renderEmotionPills();
}

// Render Emotion Pills for Selected Voice
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

// Update Word Count & Duration Estimate
function updateTextStats() {
  const text = storyText.value.trim();
  const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
  const chars = text.length;

  wordCountEl.textContent = words.toLocaleString();
  charCountEl.textContent = chars.toLocaleString();

  // Average narration speed ~140 words per minute
  if (words === 0) {
    estDurationEl.textContent = '~0 min';
  } else {
    const totalMinutes = words / 140;
    const mins = Math.floor(totalMinutes);
    const secs = Math.round((totalMinutes - mins) * 60);
    estDurationEl.textContent = mins > 0 ? `~${mins}m ${secs}s` : `~${secs}s`;
  }
}

// Quick 3s Audition Preview
async function auditionVoicePreview() {
  if (!STATE.selectedVoice) return;

  const originalText = previewText.textContent;
  btnPreview.disabled = true;
  previewText.textContent = 'Generating...';

  try {
    const payload = {
      engine: STATE.engine,
      voice_id: STATE.selectedVoice.id,
      style: STATE.selectedStyle,
      style_degree: parseFloat(intensitySlider.value),
      rate: parseInt(speedSlider.value),
      pitch: parseInt(pitchSlider.value),
      text: STATE.selectedVoice.sample_text || 'The silent corridor stretched endlessly into the shadows of the old manor.'
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

// Generate Full Long-form Story Audio
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

  // Show Progress Card
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

// Poll Progress of Background Generation
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

// Reset Generation Button State
function resetGenerateState() {
  STATE.isGenerating = false;
  btnGenerate.disabled = false;
  generateText.textContent = 'Generate Full Story Audio';
}

// Load Completed Story into Master Player
function setupMasterAudioPlayer(result) {
  masterPlayer.classList.remove('hidden');

  playerTitle.textContent = `${STATE.selectedVoice.name} — ${STATE.selectedVoice.title}`;
  playerMeta.textContent = `${formatTime(result.duration)} • ${result.word_count.toLocaleString()} Words • ${result.chunks_count} Sections`;

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
  }).catch(() => {
    // Autoplay prevented by browser
  });
}

// Master Audio Player Controls
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
