import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '../components/Sidebar';
import RobotAssistant from '../components/RobotAssistant';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

const MOOD_EMOJIS = {
  Happy: '😊',
  Calm: '😌',
  Neutral: '😐',
  Sad: '😔',
  Anxious: '😰',
  Angry: '😡',
  Stressed: '😫',
};

export default function Dashboard({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [latestCheckin, setLatestCheckin] = useState(null);
  const [checkins, setCheckins] = useState([]);
  const [journals, setJournals] = useState([]);
  const [loading, setLoading] = useState(true);

  // Companion Widget State
  const [companionText, setCompanionText] = useState("Hello! I'm your AI Wellness Companion. How are you feeling today?");
  const [userTranscript, setUserTranscript] = useState('');
  const [typedInput, setTypedInput] = useState('');
  const [robotState, setRobotState] = useState('robot-idle'); // 'robot-idle' | 'robot-listening' | 'robot-thinking' | 'robot-speaking'
  const [isListening, setIsListening] = useState(false);
  const [voiceError, setVoiceError] = useState('');

  const recognitionRef = useRef(null);
  const utteranceRef = useRef(null);
  const requestIdRef = useRef(0);
  const navTimeoutRef = useRef(null);

  const stopAllRobotActivity = () => {
    // 1. Invalidate in-flight AI requests to prevent race conditions
    requestIdRef.current += 1;

    // 2. Stop active speech recognition immediately
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (e) {
        try { recognitionRef.current.stop(); } catch (ignored) {}
      }
    }
    setIsListening(false);

    // 3. Immediately cancel browser SpeechSynthesis & clear audio queue
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }

    // 4. Clear pending navigation timer if any
    if (navTimeoutRef.current) {
      clearTimeout(navTimeoutRef.current);
      navTimeoutRef.current = null;
    }

    // 5. Return robot to idle state
    setRobotState('robot-idle');
  };

  useEffect(() => {
    return () => {
      stopAllRobotActivity();
    };
  }, []);

  useEffect(() => {
    async function loadData() {
      try {
        const [cLatest, cAll, jAll] = await Promise.all([
          api.getLatestCheckin().catch(() => ({ latest: null })),
          api.getCheckins().catch(() => ({ checkins: [] })),
          api.getJournals().catch(() => ({ entries: [] })),
        ]);
        setLatestCheckin(cLatest.latest);
        setCheckins(cAll.checkins || []);
        setJournals(jAll.entries || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const calculateStreak = (checkinList) => {
    if (!checkinList || checkinList.length === 0) return 0;
    const dates = Array.from(new Set(checkinList.map((c) => (c.created_at || '').slice(0, 10)))).sort().reverse();
    const today = new Date().toISOString().slice(0, 10);
    const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);

    if (dates[0] !== today && dates[0] !== yesterday) return 0;

    let streak = 0;
    let curr = new Date(dates[0] === today ? Date.now() : Date.now() - 86400000);
    const dateSet = new Set(dates);

    while (dateSet.has(curr.toISOString().slice(0, 10))) {
      streak += 1;
      curr.setDate(curr.getDate() - 1);
    }
    return streak;
  };

  const streakCount = calculateStreak(checkins);

  let wellnessScore = 70;
  if (checkins.length > 0 && latestCheckin) {
    const stress = latestCheckin.stress_level || 5;
    const energy = latestCheckin.energy_level || 5;
    wellnessScore = Math.min(100, Math.max(20, Math.round(100 - stress * 6 + energy * 4)));
  }

  const speakText = (text, reqId) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      if (!text || (reqId && reqId !== requestIdRef.current)) return;

      const cleanSpoken = text.replace(/[*_~`#]/g, '').trim();
      const utterance = new SpeechSynthesisUtterance(cleanSpoken);
      utteranceRef.current = utterance; // Prevent garbage collection in Chrome/Edge
      utterance.rate = 1.0;
      utterance.pitch = 1.05;
      utterance.onstart = () => {
        if (reqId && reqId !== requestIdRef.current) {
          window.speechSynthesis.cancel();
          setRobotState('robot-idle');
          return;
        }
        setRobotState('robot-speaking');
      };
      utterance.onend = () => {
        setRobotState('robot-idle');
        utteranceRef.current = null;
      };
      utterance.onerror = () => {
        setRobotState('robot-idle');
        utteranceRef.current = null;
      };

      if (window.speechSynthesis.paused) {
        window.speechSynthesis.resume();
      }
      window.speechSynthesis.speak(utterance);
    }
  };

  const detectNavigationIntent = (text) => {
    const lower = (text || '').toLowerCase().trim();

    // Check-in
    if (/(check\s*in|daily\s*check|mood\s*check|log\s*mood)/i.test(lower)) {
      return { target: 'checkin', label: 'Daily Check-In' };
    }
    // Chat
    if (/(chat|conversation|ai\s*chat|talk\s*to\s*(ai|companion))/i.test(lower) && /(go|open|take|switch|navigate|show|start)/i.test(lower)) {
      return { target: 'chat', label: 'AI Chat' };
    }
    // Journal
    if (/(journal|diary|reflections|write\s*journal|my\s*journal)/i.test(lower) && /(go|open|take|switch|navigate|show|write)/i.test(lower)) {
      return { target: 'journal', label: 'Journal' };
    }
    // Wellness Tips / Exercises
    if (/(wellness\s*tips|tips|breathing|mindfulness|grounding|exercises|relax)/i.test(lower) && /(go|open|take|switch|navigate|show|see)/i.test(lower)) {
      return { target: 'wellness_tips', label: 'Wellness Tips' };
    }
    // Insights
    if (/(insight|analytics|trends|statistics|my\s*stats|graphs)/i.test(lower) && /(go|open|take|switch|navigate|show|see)/i.test(lower)) {
      return { target: 'insights', label: 'Insights' };
    }
    // Resources / Helplines
    if (/(resource|helpline|helplines|crisis|hotline|emergency)/i.test(lower) && !/(doctor|psychiatrist|professional)/i.test(lower) && /(go|open|take|switch|navigate|show|see)/i.test(lower)) {
      return { target: 'resources', label: 'Resources' };
    }
    // Professional Support / Psychiatrist
    if (/(psychiatrist|doctor|professional\s*support|therapist|clinical|clinic|hospital)/i.test(lower) && /(go|open|take|switch|navigate|show|find|see|talk)/i.test(lower)) {
      return { target: 'professional_support', label: 'Professional Support' };
    }
    // Profile / Settings
    if (/(profile|setting|settings|preferences|account|my\s*account)/i.test(lower) && /(go|open|take|switch|navigate|show|see)/i.test(lower)) {
      return { target: 'profile', label: 'Profile & Settings' };
    }
    // Dashboard / Home
    if (/(dashboard|home|main\s*page|home\s*screen)/i.test(lower) && /(go|open|take|switch|navigate|show)/i.test(lower)) {
      return { target: 'dashboard', label: 'Dashboard' };
    }

    // Direct pattern "go to <page>"
    const directMatch = lower.match(/(?:go\s+to|open|take\s+me\s+to|navigate\s+to|switch\s+to|show\s+me)\s+(.+)/i);
    if (directMatch) {
      const pageKey = directMatch[1].trim();
      if (pageKey.includes('check')) return { target: 'checkin', label: 'Daily Check-In' };
      if (pageKey.includes('chat')) return { target: 'chat', label: 'AI Chat' };
      if (pageKey.includes('journal')) return { target: 'journal', label: 'Journal' };
      if (pageKey.includes('tip') || pageKey.includes('breath') || pageKey.includes('mindful')) return { target: 'wellness_tips', label: 'Wellness Tips' };
      if (pageKey.includes('insight') || pageKey.includes('trend')) return { target: 'insights', label: 'Insights' };
      if (pageKey.includes('resource') || pageKey.includes('help')) return { target: 'resources', label: 'Resources' };
      if (pageKey.includes('doctor') || pageKey.includes('psychiatrist') || pageKey.includes('professional') || pageKey.includes('support')) return { target: 'professional_support', label: 'Professional Support' };
      if (pageKey.includes('profile') || pageKey.includes('setting')) return { target: 'profile', label: 'Profile & Settings' };
      if (pageKey.includes('dash') || pageKey.includes('home')) return { target: 'dashboard', label: 'Dashboard' };
    }
    return null;
  };

  const handleCompanionSubmit = async (textToSend) => {
    const cleanMsg = (textToSend !== undefined ? textToSend : typedInput).trim();
    if (!cleanMsg) return;

    const thisRequestId = ++requestIdRef.current;

    setUserTranscript(cleanMsg);
    setTypedInput('');
    setVoiceError('');
    setRobotState('robot-thinking');

    // 1. Check if user issued a voice navigation command (e.g. "go to journal", "open check in")
    const navIntent = detectNavigationIntent(cleanMsg);
    if (navIntent) {
      if (thisRequestId !== requestIdRef.current) return;
      const confirmReply = `Taking you to the ${navIntent.label} page now!`;
      setCompanionText(confirmReply);
      speakText(confirmReply, thisRequestId);
      navTimeoutRef.current = setTimeout(() => {
        if (thisRequestId === requestIdRef.current) {
          onNavigate(navIntent.target);
        }
      }, 1200);
      return;
    }

    // 2. Otherwise, run conversational reasoning through MedGemma + Emotion Classifier
    try {
      const res = await api.companionChat(cleanMsg);
      // If user cancelled/stopped while request was in-flight, drop the response
      if (thisRequestId !== requestIdRef.current) return;

      setCompanionText(res.reply);
      speakText(res.clean_speech_text || res.reply, thisRequestId);
    } catch (e) {
      if (thisRequestId !== requestIdRef.current) return;
      setCompanionText("I'm right here with you. Take a slow, calm breath.");
      setRobotState('robot-idle');
    }
  };

  const toggleVoiceRecording = () => {
    setVoiceError('');
    // If robot is active (listening, thinking, speaking) -> STOP / CANCEL EVERYTHING IMMEDIATELY
    if (isListening || robotState === 'robot-speaking' || robotState === 'robot-thinking') {
      stopAllRobotActivity();
      return;
    }

    // Otherwise (IDLE) -> START LISTENING
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError('Speech recognition is not supported in this browser. Please type below.');
      return;
    }

    stopAllRobotActivity(); // Reset state & audio before starting new recognition

    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
      setRobotState('robot-listening');
      setVoiceError('');
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setIsListening(false);
      handleCompanionSubmit(transcript);
    };

    recognition.onerror = (event) => {
      setIsListening(false);
      setRobotState('robot-idle');
      if (event.error === 'not-allowed') {
        setVoiceError('Microphone permission blocked. Please allow mic in browser settings or type below.');
      } else if (event.error === 'no-speech') {
        setVoiceError('No speech detected. Please try again or type below.');
      } else if (event.error === 'network') {
        setVoiceError('Network error on speech recognition. You can type below anytime!');
      } else {
        setVoiceError(`Voice input note (${event.error}). You can type below!`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      if (robotState === 'robot-listening') {
        setRobotState('robot-idle');
      }
    };

    recognitionRef.current = recognition;
    try {
      recognition.start();
    } catch (e) {
      setIsListening(false);
      setRobotState('robot-idle');
      setVoiceError('Could not start microphone. You can type below anytime.');
    }
  };

  const formatGreeting = (name) => {
    if (!name) return 'Hi, Friend 👋';
    const clean = String(name).replace(/[*_~`]/g, '').trim();
    const formatted = clean ? clean.charAt(0).toUpperCase() + clean.slice(1) : 'Friend';
    return `Hi, ${formatted} 👋`;
  };

  const mood = latestCheckin ? latestCheckin.mood : '—';
  const stress = latestCheckin ? latestCheckin.stress_level : '—';

  return (
    <div className="app-layout">
      <Sidebar currentPage="dashboard" onNavigate={onNavigate} />

      <main className="main-content">
        <h2>{user ? formatGreeting(user.username) : 'Hi there 👋'}</h2>
        <p className="aw-quote">{t('dash_quote')}</p>

        {/* KPI Summary Cards */}
        <div className="grid-5" style={{ marginTop: '20px' }}>
          <div className="aw-card" style={{ textAlign: 'center', padding: '16px' }}>
            <div className="aw-muted" style={{ fontSize: '0.82rem' }}>
              {t('dash_todays_mood')}
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '4px' }}>
              {MOOD_EMOJIS[mood] || ''} {mood}
            </div>
          </div>

          <div className="aw-card" style={{ textAlign: 'center', padding: '16px' }}>
            <div className="aw-muted" style={{ fontSize: '0.82rem' }}>
              {t('dash_wellness_score')}
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent)', marginTop: '4px' }}>
              🌿 {wellnessScore}/100
            </div>
          </div>

          <div className="aw-card" style={{ textAlign: 'center', padding: '16px' }}>
            <div className="aw-muted" style={{ fontSize: '0.82rem' }}>
              {t('dash_stress_level')}
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '4px' }}>
              ⚡ {stress}/10
            </div>
          </div>

          <div className="aw-card" style={{ textAlign: 'center', padding: '16px' }}>
            <div className="aw-muted" style={{ fontSize: '0.82rem' }}>
              {t('dash_checkin_streak')}
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ff6b8b', marginTop: '4px' }}>
              🔥 {streakCount}
            </div>
          </div>

          <div className="aw-card" style={{ textAlign: 'center', padding: '16px' }}>
            <div className="aw-muted" style={{ fontSize: '0.82rem' }}>
              {t('dash_journal_entries')}
            </div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, marginTop: '4px' }}>
              📔 {journals.length}
            </div>
          </div>
        </div>

        {/* AI Wellness Robot Companion Card */}
        <div className="aw-card" style={{ marginTop: '24px', padding: '32px 24px', textAlign: 'center' }}>
          <div style={{ maxWidth: '640px', margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            {/* Robot Image with Interactive Animations */}
            <div style={{ textAlign: 'center', marginBottom: '14px', width: '100%', maxWidth: '280px' }}>
              <RobotAssistant state={robotState.replace('robot-', '')} />
              <div style={{ marginTop: '12px' }}>
                <span className="aw-pill">
                  {robotState === 'robot-listening'
                    ? '🎤 Listening...'
                    : robotState === 'robot-thinking'
                    ? '💭 Thinking...'
                    : robotState === 'robot-speaking'
                    ? '🔊 Speaking...'
                    : '🟢 Ready'}
                </span>
              </div>
            </div>

            {/* Speech Bubble & Voice Controls */}
            <div style={{ width: '100%', marginTop: '8px' }}>
              {userTranscript && (
                <div style={{ fontSize: '0.86rem', color: 'var(--accent)', fontWeight: 600, marginBottom: '8px' }}>
                  You said: "{userTranscript}"
                </div>
              )}

              <div
                style={{
                  background: 'rgba(124, 124, 235, 0.08)',
                  padding: '18px 24px',
                  borderRadius: '20px',
                  fontSize: '1.05rem',
                  lineHeight: '1.6',
                  color: 'var(--ink)',
                  marginBottom: '18px',
                  border: '1px solid rgba(124, 124, 235, 0.16)',
                  textAlign: 'center',
                }}
              >
                {companionText}
              </div>

              {/* Voice Error Notice */}
              {voiceError && (
                <div
                  style={{
                    fontSize: '0.85rem',
                    color: '#e05260',
                    background: 'rgba(224, 82, 96, 0.08)',
                    padding: '8px 14px',
                    borderRadius: '12px',
                    marginBottom: '14px',
                    border: '1px solid rgba(224, 82, 96, 0.2)',
                    textAlign: 'center',
                  }}
                >
                  ⚠️ {voiceError}
                </div>
              )}

              {/* Text + Voice Input Form */}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleCompanionSubmit();
                }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  maxWidth: '520px',
                  margin: '0 auto 16px auto',
                  width: '100%',
                }}
              >
                <input
                  type="text"
                  placeholder="Type a reflection or click 🎙️ to talk..."
                  value={typedInput}
                  onChange={(e) => setTypedInput(e.target.value)}
                  disabled={robotState === 'robot-thinking'}
                  style={{
                    flex: 1,
                    margin: 0,
                    padding: '12px 18px',
                    borderRadius: '24px',
                    fontSize: '0.95rem',
                  }}
                />

                <button
                  type="submit"
                  className="btn-primary"
                  disabled={!typedInput.trim() || robotState === 'robot-thinking'}
                  style={{
                    borderRadius: '24px',
                    padding: '11px 20px',
                    fontSize: '0.92rem',
                    flexShrink: 0,
                    cursor: (!typedInput.trim() || robotState === 'robot-thinking') ? 'not-allowed' : 'pointer',
                  }}
                >
                  Send
                </button>

                <button
                  type="button"
                  className={(isListening || robotState === 'robot-speaking' || robotState === 'robot-thinking') ? 'btn-primary' : 'btn-secondary'}
                  style={{
                    borderRadius: '50%',
                    width: '48px',
                    height: '48px',
                    padding: 0,
                    fontSize: '1.25rem',
                    flexShrink: 0,
                    cursor: 'pointer',
                    animation: (isListening || robotState === 'robot-speaking' || robotState === 'robot-thinking') ? 'pulse 1.2s infinite' : 'none',
                    boxShadow: (isListening || robotState === 'robot-speaking' || robotState === 'robot-thinking') ? '0 0 16px rgba(124, 124, 235, 0.5)' : 'none',
                  }}
                  onClick={toggleVoiceRecording}
                  title={(isListening || robotState === 'robot-speaking' || robotState === 'robot-thinking') ? 'Click to stop' : 'Click to speak'}
                >
                  {(isListening || robotState === 'robot-speaking' || robotState === 'robot-thinking') ? '⏹️' : '🎙️'}
                </button>
              </form>

              {/* Quick Conversation Starter Chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '8px', maxWidth: '540px', margin: '0 auto' }}>
                {[
                  { label: "🧘 Breathing Exercise", prompt: "Can you guide me through a calming breathing exercise?" },
                  { label: "⚡ Feeling Stressed", prompt: "I'm feeling really stressed today, can we talk?" },
                  { label: "🌱 Grounding Technique", prompt: "Teach me a quick 5-4-3-2-1 grounding exercise." },
                  { label: "✨ Had a Great Day", prompt: "I had a wonderful day today and wanted to share!" },
                ].map((chip, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleCompanionSubmit(chip.prompt)}
                    disabled={robotState === 'robot-thinking'}
                    style={{
                      background: 'rgba(124, 124, 235, 0.08)',
                      border: '1px solid rgba(124, 124, 235, 0.2)',
                      borderRadius: '16px',
                      padding: '6px 14px',
                      fontSize: '0.82rem',
                      color: 'var(--ink)',
                      cursor: robotState === 'robot-thinking' ? 'not-allowed' : 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(124, 124, 235, 0.18)')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'rgba(124, 124, 235, 0.08)')}
                  >
                    {chip.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
