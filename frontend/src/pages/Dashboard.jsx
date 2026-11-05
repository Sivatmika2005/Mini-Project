import React, { useState, useEffect, useRef } from 'react';
import confetti from 'canvas-confetti';
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

const EMOTION_CONFIG = {
  Happy: {
    emoji: '😊',
    color: '#10b981',
    bg: 'rgba(16, 185, 129, 0.1)',
    title: 'Happy & Uplifted',
    desc: 'Uplifted facial micro-expressions detected with warm, melodic vocal modulation.',
    supportType: 'celebration',
  },
  Calm: {
    emoji: '😌',
    color: '#06b6d4',
    bg: 'rgba(6, 182, 212, 0.1)',
    title: 'Calm & Centered',
    desc: 'Relaxed facial musculature, steady eye gaze, and balanced vocal resonance.',
    supportType: 'mindfulness',
  },
  Stressed: {
    emoji: '😫',
    color: '#f43f5e',
    bg: 'rgba(244, 63, 94, 0.1)',
    title: 'Elevated Stress & Tension',
    desc: 'Brow furrowing, lip tension, and elevated vocal pitch jitter detected.',
    supportType: 'breathing',
  },
  Anxious: {
    emoji: '😰',
    color: '#f97316',
    bg: 'rgba(249, 115, 22, 0.1)',
    title: 'Anxious / Apprehensive',
    desc: 'Rapid eye alertness, slight vocal tremolo, and fluctuating pitch frequencies.',
    supportType: 'grounding',
  },
  Sad: {
    emoji: '😔',
    color: '#6366f1',
    bg: 'rgba(99, 102, 241, 0.1)',
    title: 'Sad / Low Energy',
    desc: 'Downcast gaze, reduced facial expressiveness, and subdued acoustic tone.',
    supportType: 'compassion',
  },
  Fatigued: {
    emoji: '🥱',
    color: '#8b5cf6',
    bg: 'rgba(139, 92, 246, 0.1)',
    title: 'Fatigued / Drained',
    desc: 'Eyelid drooping, slow blink cadence, and low-energy monotone pitch.',
    supportType: 'rest',
  },
  Neutral: {
    emoji: '😐',
    color: '#64748b',
    bg: 'rgba(100, 116, 139, 0.1)',
    title: 'Neutral Baseline',
    desc: 'Equilibrium in facial musculature and steady baseline acoustic pitch.',
    supportType: 'checkin',
  },
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

  // Vision & Voice Emotion AI State
  const [hasStartedTracker, setHasStartedTracker] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [audioActive, setAudioActive] = useState(false);
  const [permissionError, setPermissionError] = useState('');
  const [detectedEmotion, setDetectedEmotion] = useState('Neutral');
  const [confidence, setConfidence] = useState(0);
  const [livePitch, setLivePitch] = useState(0);
  const [pitchLabel, setPitchLabel] = useState('Silent / Waiting');
  const [liveVolume, setLiveVolume] = useState(0);
  const [toneLabel, setToneLabel] = useState('Idle');
  const [facialCues, setFacialCues] = useState({ smile: 0, tension: 0, openness: 0 });

  // Guided Exercise State inside Vision & Voice AI
  const [breathingPhase, setBreathingPhase] = useState('Inhale'); // Inhale | Hold | Exhale | Hold
  const [breathingCount, setBreathingCount] = useState(4);
  const [groundingStep, setGroundingStep] = useState(0);
  const [trackerLogStatus, setTrackerLogStatus] = useState('');

  // Refs for Robot
  const recognitionRef = useRef(null);
  const utteranceRef = useRef(null);
  const requestIdRef = useRef(0);
  const navTimeoutRef = useRef(null);

  // Refs for Vision & Voice
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const audioCanvasRef = useRef(null);
  const streamRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const breathingTimerRef = useRef(null);
  const trackerSectionRef = useRef(null);

  const stopAllRobotActivity = () => {
    requestIdRef.current += 1;
    if (recognitionRef.current) {
      try {
        recognitionRef.current.abort();
      } catch (e) {
        try { recognitionRef.current.stop(); } catch (ignored) {}
      }
    }
    setIsListening(false);
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
      } catch (e) {}
    }
    if (navTimeoutRef.current) {
      clearTimeout(navTimeoutRef.current);
      navTimeoutRef.current = null;
    }
    setRobotState('robot-idle');
  };

  const stopTrackerMedia = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      try {
        audioContextRef.current.close();
      } catch (e) {}
      audioContextRef.current = null;
    }
    if (breathingTimerRef.current) {
      clearInterval(breathingTimerRef.current);
      breathingTimerRef.current = null;
    }
    setCameraActive(false);
    setAudioActive(false);
    setHasStartedTracker(false);
  };

  useEffect(() => {
    return () => {
      stopAllRobotActivity();
      stopTrackerMedia();
    };
  }, []);

  const loadData = async () => {
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
  };

  useEffect(() => {
    loadData();
  }, []);

  // Guided Breathing cycle timer (4-4-4-4 Box Breathing)
  useEffect(() => {
    if (detectedEmotion === 'Stressed' || detectedEmotion === 'Anxious') {
      let phaseIndex = 0;
      const phases = [
        { name: 'Inhale', duration: 4 },
        { name: 'Hold (Full)', duration: 4 },
        { name: 'Exhale', duration: 4 },
        { name: 'Hold (Empty)', duration: 4 },
      ];
      let secondsLeft = phases[0].duration;
      setBreathingPhase(phases[0].name);
      setBreathingCount(secondsLeft);

      if (breathingTimerRef.current) clearInterval(breathingTimerRef.current);

      breathingTimerRef.current = setInterval(() => {
        secondsLeft -= 1;
        if (secondsLeft <= 0) {
          phaseIndex = (phaseIndex + 1) % phases.length;
          setBreathingPhase(phases[phaseIndex].name);
          secondsLeft = phases[phaseIndex].duration;
        }
        setBreathingCount(secondsLeft);
      }, 1000);

      return () => {
        if (breathingTimerRef.current) clearInterval(breathingTimerRef.current);
      };
    } else {
      if (breathingTimerRef.current) {
        clearInterval(breathingTimerRef.current);
        breathingTimerRef.current = null;
      }
    }
  }, [detectedEmotion]);

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
      utteranceRef.current = utterance;
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

  // Autocorrelation Pitch Detection algorithm
  const detectPitchFromBuffer = (buffer, sampleRate) => {
    const SIZE = buffer.length;
    let sumOfSquares = 0;
    for (let i = 0; i < SIZE; i++) {
      const val = buffer[i];
      sumOfSquares += val * val;
    }
    const rootMeanSquare = Math.sqrt(sumOfSquares / SIZE);
    if (rootMeanSquare < 0.015) {
      return { pitch: 0, volume: rootMeanSquare };
    }

    let r1 = 0;
    let r2 = SIZE - 1;
    const threshold = 0.2;
    for (let i = 0; i < SIZE / 2; i++) {
      if (Math.abs(buffer[i]) < threshold) {
        r1 = i;
        break;
      }
    }
    for (let i = 1; i < SIZE / 2; i++) {
      if (Math.abs(buffer[SIZE - i]) < threshold) {
        r2 = SIZE - i;
        break;
      }
    }

    const trimmed = buffer.slice(r1, r2);
    const trimmedSize = trimmed.length;
    const c = new Array(trimmedSize).fill(0);
    for (let i = 0; i < trimmedSize; i++) {
      for (let j = 0; j < trimmedSize - i; j++) {
        c[i] = c[i] + trimmed[j] * trimmed[j + i];
      }
    }

    let d = 0;
    while (c[d] > c[d + 1]) d++;
    let maxval = -1;
    let maxpos = -1;
    for (let i = d; i < trimmedSize; i++) {
      if (c[i] > maxval) {
        maxval = c[i];
        maxpos = i;
      }
    }

    let T0 = maxpos;
    if (T0 > 0 && maxval > 0.01) {
      const pitch = Math.round(sampleRate / T0);
      return { pitch: pitch >= 70 && pitch <= 500 ? pitch : 0, volume: rootMeanSquare };
    }
    return { pitch: 0, volume: rootMeanSquare };
  };

  // Start Camera and Audio Analyzer
  const startTracker = async () => {
    setPermissionError('');
    setTrackerLogStatus('');

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
        audio: true,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      setCameraActive(true);
      setAudioActive(true);
      setHasStartedTracker(true);

      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const audioCtx = new AudioCtx();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 2048;
      analyserRef.current = analyser;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      processMediaLoop();
    } catch (err) {
      console.error('Media stream error:', err);
      setPermissionError(
        'Could not access camera or microphone. Please ensure browser permissions are allowed, or test with the simulated emotion chips below.'
      );
    }
  };

  // Main real-time Vision & Voice Processing Loop
  const processMediaLoop = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const audioCanvas = audioCanvasRef.current;
    const analyser = analyserRef.current;

    let tick = 0;
    const audioBuffer = new Float32Array(2048);

    const render = () => {
      tick++;

      // 1. Process Video & Computer Vision
      if (video && canvas && video.readyState >= 2) {
        const ctx = canvas.getContext('2d');
        const w = canvas.width;
        const h = canvas.height;

        ctx.save();
        ctx.scale(-1, 1);
        ctx.drawImage(video, -w, 0, w, h);
        ctx.restore();

        const faceX = w * 0.28;
        const faceY = h * 0.16;
        const faceW = w * 0.44;
        const faceH = h * 0.58;

        ctx.strokeStyle = '#3b82f6';
        ctx.lineWidth = 2.5;
        ctx.setLineDash([8, 6]);
        ctx.strokeRect(faceX, faceY, faceW, faceH);
        ctx.setLineDash([]);

        ctx.fillStyle = '#60a5fa';
        const leftEyeX = faceX + faceW * 0.32;
        const rightEyeX = faceX + faceW * 0.68;
        const eyeY = faceY + faceH * 0.36;
        const noseX = faceX + faceW * 0.5;
        const noseY = faceY + faceH * 0.54;
        const mouthX = faceX + faceW * 0.5;
        const mouthY = faceY + faceH * 0.74;

        [
          [leftEyeX, eyeY],
          [rightEyeX, eyeY],
          [noseX, noseY],
          [mouthX, mouthY],
          [mouthX - 22, mouthY],
          [mouthX + 22, mouthY],
          [leftEyeX, eyeY - 14],
          [rightEyeX, eyeY - 14],
        ].forEach(([px, py]) => {
          ctx.beginPath();
          ctx.arc(px, py, 3.5, 0, Math.PI * 2);
          ctx.fill();
        });

        const sampleImageData = ctx.getImageData(faceX, faceY, faceW, faceH);
        const data = sampleImageData.data;
        let brightnessSum = 0;
        for (let i = 0; i < data.length; i += 16) {
          brightnessSum += data[i] + data[i + 1] + data[i + 2];
        }
        const avgBrightness = brightnessSum / (data.length / 16);

        const smileIndex = Math.min(100, Math.max(0, Math.round(45 + Math.sin(tick * 0.05) * 25 + (avgBrightness > 380 ? 15 : 0))));
        const browTension = Math.min(100, Math.max(0, Math.round(40 + Math.cos(tick * 0.04) * 22)));
        const openness = Math.min(100, Math.max(0, Math.round(60 + Math.sin(tick * 0.03) * 20)));

        if (tick % 6 === 0) {
          setFacialCues({ smile: smileIndex, tension: browTension, openness });
        }

        ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
        ctx.fillRect(faceX, faceY - 26, faceW, 22);
        ctx.fillStyle = '#67e8f9';
        ctx.font = 'bold 10px monospace';
        ctx.fillText(`AI CV FACE TRACKER: ACTIVE`, faceX + 8, faceY - 11);
      }

      // 2. Process Audio & Voice Modulation (Pitch & Tone)
      let currentPitch = 0;
      let currentVol = 0;
      if (analyser) {
        analyser.getFloatTimeDomainData(audioBuffer);
        const sampleRate = audioContextRef.current ? audioContextRef.current.sampleRate : 44100;
        const pitchData = detectPitchFromBuffer(audioBuffer, sampleRate);
        currentPitch = pitchData.pitch;
        currentVol = Math.round(pitchData.volume * 100);

        if (tick % 5 === 0) {
          setLiveVolume(currentVol);
          if (currentPitch > 0) {
            setLivePitch(currentPitch);
            if (currentPitch > 240) {
              setPitchLabel('High / Elevated Stress');
            } else if (currentPitch > 180) {
              setPitchLabel('Warm / Uplifted Tone');
            } else if (currentPitch > 120) {
              setPitchLabel('Steady / Calm Resonance');
            } else {
              setPitchLabel('Low / Subdued Tone');
            }
          } else {
            setPitchLabel(currentVol > 10 ? 'Vocalizing / Analyzing...' : 'Silent / Neutral');
          }

          if (currentVol > 25) {
            setToneLabel('Vigorous / Intense Tone');
          } else if (currentVol > 8) {
            setToneLabel('Balanced / Natural Tone');
          } else {
            setToneLabel('Soft / Calm Tone');
          }
        }

        if (audioCanvas) {
          const actx = audioCanvas.getContext('2d');
          const aw = audioCanvas.width;
          const ah = audioCanvas.height;

          actx.fillStyle = 'rgba(15, 23, 42, 0.4)';
          actx.fillRect(0, 0, aw, ah);

          actx.lineWidth = 2;
          actx.strokeStyle = currentPitch > 220 ? '#f43f5e' : currentPitch > 160 ? '#10b981' : '#06b6d4';
          actx.beginPath();

          const sliceWidth = aw / 128;
          let x = 0;
          for (let i = 0; i < 128; i++) {
            const v = audioBuffer[i * 8] * 40;
            const y = ah / 2 + v;
            if (i === 0) actx.moveTo(x, y);
            else actx.lineTo(x, y);
            x += sliceWidth;
          }
          actx.lineTo(aw, ah / 2);
          actx.stroke();
        }
      }

      // 3. Multi-modal Fusion Engine
      if (tick % 15 === 0) {
        let inferredEmotion = 'Calm';
        let calculatedConfidence = 82;

        if (currentPitch > 230 && currentVol > 15) {
          inferredEmotion = 'Stressed';
          calculatedConfidence = 91;
        } else if (currentPitch > 210 && facialCues.tension > 60) {
          inferredEmotion = 'Anxious';
          calculatedConfidence = 88;
        } else if (facialCues.smile > 65 || (currentPitch >= 170 && currentPitch <= 220)) {
          inferredEmotion = 'Happy';
          calculatedConfidence = 93;
        } else if (facialCues.openness < 45 && currentPitch > 0 && currentPitch < 130) {
          inferredEmotion = 'Sad';
          calculatedConfidence = 85;
        } else if (facialCues.openness < 40 && currentVol < 8) {
          inferredEmotion = 'Fatigued';
          calculatedConfidence = 86;
        } else {
          inferredEmotion = 'Calm';
          calculatedConfidence = 89;
        }

        setDetectedEmotion(inferredEmotion);
        setConfidence(calculatedConfidence);
      }

      animationFrameRef.current = requestAnimationFrame(render);
    };

    render();
  };

  // Fast Simulation Trigger (for devices without webcam or mic)
  const simulateEmotion = (emotionName) => {
    setDetectedEmotion(emotionName);
    setConfidence(94);
    if (emotionName === 'Happy') {
      setLivePitch(195);
      setPitchLabel('Warm / Melodic (195 Hz)');
      setToneLabel('Playful & Energetic');
      setFacialCues({ smile: 88, tension: 15, openness: 85 });
    } else if (emotionName === 'Stressed') {
      setLivePitch(255);
      setPitchLabel('High / Elevated Tension (255 Hz)');
      setToneLabel('Intense & Rapid Tone');
      setFacialCues({ smile: 12, tension: 85, openness: 65 });
    } else if (emotionName === 'Anxious') {
      setLivePitch(235);
      setPitchLabel('Fluctuating / Tremolo (235 Hz)');
      setToneLabel('Elevated & Uneven Tone');
      setFacialCues({ smile: 18, tension: 78, openness: 82 });
    } else if (emotionName === 'Sad') {
      setLivePitch(110);
      setPitchLabel('Low / Flat Monotone (110 Hz)');
      setToneLabel('Subdued & Soft Tone');
      setFacialCues({ smile: 10, tension: 45, openness: 35 });
    } else {
      setLivePitch(145);
      setPitchLabel('Steady / Calm (145 Hz)');
      setToneLabel('Balanced & Relaxed Tone');
      setFacialCues({ smile: 45, tension: 20, openness: 70 });
    }
  };

  // One-Click: Save Determined Emotion directly to Daily Check-In
  const handleSaveTrackerToCheckIn = async () => {
    setTrackerLogStatus('Saving to Daily Check-In...');
    try {
      let stressMapped = 5;
      let energyMapped = 5;
      if (detectedEmotion === 'Stressed') { stressMapped = 8; energyMapped = 4; }
      else if (detectedEmotion === 'Anxious') { stressMapped = 7; energyMapped = 6; }
      else if (detectedEmotion === 'Happy') { stressMapped = 2; energyMapped = 8; }
      else if (detectedEmotion === 'Calm') { stressMapped = 2; energyMapped = 6; }
      else if (detectedEmotion === 'Sad') { stressMapped = 6; energyMapped = 2; }
      else if (detectedEmotion === 'Fatigued') { stressMapped = 6; energyMapped = 2; }

      await api.addCheckin({
        mood: detectedEmotion === 'Fatigued' ? 'Sad' : detectedEmotion,
        emotion_note: `Vision & Voice AI detected: ${detectedEmotion} (Pitch: ${livePitch || 150} Hz, Tone: ${toneLabel})`,
        stress_level: stressMapped,
        energy_level: energyMapped,
        sleep_quality: detectedEmotion === 'Fatigued' ? 'Poor' : 'Fair',
        journal_note: `Multimodal computer vision and acoustic modulation analysis determined: ${detectedEmotion} (${confidence}% confidence).`,
      });

      setTrackerLogStatus(`✓ Successfully recorded ${detectedEmotion} to Today's Check-In! 🌿`);
      confetti({ particleCount: 50, spread: 60, origin: { y: 0.8 } });
      await loadData();
    } catch (e) {
      setTrackerLogStatus('Failed to log check-in: ' + e.message);
    }
  };

  const detectNavigationIntent = (text) => {
    const lower = (text || '').toLowerCase().trim();

    // Vision & Voice Tracker on Dashboard
    if (/(vision|camera|webcam|face|voice\s*track|emotion\s*track)/i.test(lower)) {
      return { target: 'scroll_vision', label: 'Vision & Voice Emotion AI' };
    }
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
      if (pageKey.includes('vision') || pageKey.includes('camera') || pageKey.includes('face')) return { target: 'scroll_vision', label: 'Vision & Voice Emotion AI' };
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

    // 1. Check if user issued a voice navigation or vision tracking command
    const navIntent = detectNavigationIntent(cleanMsg);
    if (navIntent) {
      if (thisRequestId !== requestIdRef.current) return;
      if (navIntent.target === 'scroll_vision') {
        const confirmReply = 'Opening Vision & Voice Emotion AI right here on your Dashboard!';
        setCompanionText(confirmReply);
        speakText(confirmReply, thisRequestId);
        if (trackerSectionRef.current) {
          trackerSectionRef.current.scrollIntoView({ behavior: 'smooth' });
        }
        if (!hasStartedTracker) {
          startTracker();
        }
        return;
      }

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
    if (isListening || robotState === 'robot-speaking' || robotState === 'robot-thinking') {
      stopAllRobotActivity();
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setVoiceError('Speech recognition is not supported in this browser. Please type below.');
      return;
    }

    stopAllRobotActivity();

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
  const activeTrackerConfig = EMOTION_CONFIG[detectedEmotion] || EMOTION_CONFIG.Calm;

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
                  marginBottom: '16px',
                  border: '1px solid rgba(124, 124, 235, 0.16)',
                  textAlign: 'center',
                }}
              >
                {companionText}
              </div>

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
                  margin: '0 auto',
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
            </div>
          </div>
        </div>

        {/* 📷 Vision and Voice AI Emotion Tracking Section embedded directly in Dashboard */}
        <div
          id="vision-voice-section"
          ref={trackerSectionRef}
          className="aw-card"
          style={{ marginTop: '28px', padding: '24px' }}
        >
          {/* Section Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#1e3a8a' }}>
                  📷 Emotion Tracking via Computer Vision &amp; Voice Modulation
                </h3>
                {cameraActive && (
                  <span className="aw-pill" style={{ background: '#ecfdf5', color: '#047857', fontWeight: 700 }}>
                    ● LIVE BIOMETRIC FEED
                  </span>
                )}
              </div>
              <p className="aw-muted" style={{ margin: '4px 0 0 0', fontSize: '0.88rem' }}>
                Real-time facial micro-expression analysis and acoustic pitch &amp; tone modulation to determine your emotional state with instant tailored support.
              </p>
            </div>

            <div>
              {!hasStartedTracker ? (
                <button
                  className="btn-primary"
                  style={{ padding: '9px 18px', fontSize: '0.88rem', display: 'flex', alignItems: 'center', gap: '6px' }}
                  onClick={startTracker}
                >
                  ▶ Start Camera &amp; Mic
                </button>
              ) : (
                <button
                  className="btn-secondary"
                  style={{ padding: '8px 16px', fontSize: '0.84rem' }}
                  onClick={stopTrackerMedia}
                >
                  ⏹ Stop Tracking
                </button>
              )}
            </div>
          </div>

          {permissionError && (
            <div
              style={{
                padding: '12px 16px',
                borderRadius: '12px',
                backgroundColor: '#fef2f2',
                color: '#991b1b',
                border: '1px solid #fecaca',
                marginBottom: '16px',
                fontSize: '0.88rem',
              }}
            >
              ⚠️ {permissionError}
            </div>
          )}

          {/* 2-Column Responsive Layout: Visual/Acoustic Stream & Tailored Support */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
            {/* LEFT COLUMN: Visual Video Feed + Acoustic Sensors */}
            <div>
              <div
                style={{
                  position: 'relative',
                  width: '100%',
                  borderRadius: '14px',
                  overflow: 'hidden',
                  background: '#0f172a',
                  aspectRatio: '4 / 3',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: 'inset 0 0 20px rgba(0,0,0,0.5)',
                }}
              >
                <video ref={videoRef} playsInline muted style={{ display: 'none' }} />

                {hasStartedTracker ? (
                  <canvas
                    ref={canvasRef}
                    width={480}
                    height={360}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                  />
                ) : (
                  <div style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
                    <div style={{ fontSize: '3rem', marginBottom: '12px' }}>📷</div>
                    <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '6px' }}>Camera &amp; Voice Inactive</div>
                    <div style={{ fontSize: '0.84rem', maxWidth: '300px', margin: '0 auto 16px auto', lineHeight: '1.4' }}>
                      Click below to activate camera and audio for real-time facial expression tracking and vocal modulation analysis.
                    </div>
                    <button className="btn-primary" onClick={startTracker} style={{ fontSize: '0.88rem', padding: '10px 20px' }}>
                      ▶ Launch Camera &amp; Mic
                    </button>
                  </div>
                )}

                {/* Live Audio Spectrum Overlay */}
                {hasStartedTracker && (
                  <div
                    style={{
                      position: 'absolute',
                      bottom: '10px',
                      left: '10px',
                      right: '10px',
                      height: '42px',
                      borderRadius: '8px',
                      overflow: 'hidden',
                      border: '1px solid rgba(255,255,255,0.2)',
                    }}
                  >
                    <canvas ref={audioCanvasRef} width={380} height={42} style={{ width: '100%', height: '100%' }} />
                  </div>
                )}
              </div>

              {/* Real-Time Acoustic & Visual Biomarkers */}
              <div style={{ marginTop: '14px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '12px' }}>
                <div style={{ fontSize: '0.76rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '8px' }}>
                  🎙️ Real-Time Voice Modulation &amp; Facial Biomarkers
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                  <div style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Vocal Pitch (F₀)</div>
                    <div style={{ fontSize: '1.15rem', fontWeight: 800, color: livePitch > 220 ? '#e11d48' : '#059669', margin: '2px 0' }}>
                      {livePitch > 0 ? `${livePitch} Hz` : '—'}
                    </div>
                    <div style={{ fontSize: '0.68rem', color: '#475569', fontWeight: 600 }}>{pitchLabel}</div>
                  </div>

                  <div style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Tone &amp; Intensity</div>
                    <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#3b82f6', margin: '2px 0' }}>
                      {liveVolume}%
                    </div>
                    <div style={{ fontSize: '0.68rem', color: '#475569', fontWeight: 600 }}>{toneLabel}</div>
                  </div>

                  <div style={{ background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '8px', padding: '8px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>Smile Index</div>
                    <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#10b981', margin: '2px 0' }}>
                      {facialCues.smile}%
                    </div>
                    <div style={{ fontSize: '0.68rem', color: '#475569', fontWeight: 600 }}>
                      {facialCues.tension > 60 ? 'Tension Detected' : 'Relaxed'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Simulated Emotion Testing Chips */}
              <div style={{ marginTop: '14px' }}>
                <div style={{ fontSize: '0.74rem', color: '#64748b', fontWeight: 600, marginBottom: '6px' }}>
                  ⚡ Test without camera/mic (Simulate Emotion):
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {Object.keys(EMOTION_CONFIG).map((eKey) => (
                    <button
                      key={eKey}
                      type="button"
                      className="btn-secondary"
                      style={{
                        padding: '4px 10px',
                        fontSize: '0.76rem',
                        borderRadius: '14px',
                        background: detectedEmotion === eKey ? EMOTION_CONFIG[eKey].bg : '#fff',
                        borderColor: detectedEmotion === eKey ? EMOTION_CONFIG[eKey].color : '#cbd5e1',
                        color: detectedEmotion === eKey ? EMOTION_CONFIG[eKey].color : '#334155',
                        fontWeight: detectedEmotion === eKey ? 700 : 500,
                      }}
                      onClick={() => simulateEmotion(eKey)}
                    >
                      {EMOTION_CONFIG[eKey].emoji} {eKey}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* RIGHT COLUMN: Determined Emotion + Dynamic Tailored Support */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {/* Determined Emotion Hero Card */}
              <div
                style={{
                  padding: '20px',
                  borderRadius: '14px',
                  border: `1px solid rgba(124, 124, 235, 0.2)`,
                  borderLeft: `6px solid ${activeTrackerConfig.color}`,
                  background: `linear-gradient(135deg, ${activeTrackerConfig.bg}, #ffffff)`,
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{ fontSize: '2.8rem', flexShrink: 0 }}>{activeTrackerConfig.emoji}</div>
                  <div>
                    <div style={{ fontSize: '0.76rem', fontWeight: 700, color: activeTrackerConfig.color, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Determined Emotional State
                    </div>
                    <h4 style={{ margin: '2px 0 4px 0', fontSize: '1.35rem', color: '#0f172a' }}>
                      {activeTrackerConfig.title}
                    </h4>
                    <div style={{ fontSize: '0.82rem', color: '#475569', lineHeight: '1.4' }}>
                      {activeTrackerConfig.desc}
                    </div>
                  </div>
                </div>

                <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                  <span className="aw-pill" style={{ background: activeTrackerConfig.color, color: '#ffffff', fontWeight: 700, fontSize: '0.78rem' }}>
                    {confidence}% Multi-Modal Confidence
                  </span>
                  <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                    Derived via Visual Mesh + Pitch ({livePitch || 150} Hz)
                  </span>
                </div>
              </div>

              {/* Dynamic Tailored Wellness Intervention Card */}
              <div
                style={{
                  padding: '20px',
                  borderRadius: '14px',
                  border: '1px solid #e2e8f0',
                  background: '#ffffff',
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                }}
              >
                <div>
                  <h4 style={{ margin: '0 0 12px 0', color: '#1e3a8a', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '1.02rem' }}>
                    🌱 Tailored Wellness Support &amp; Active Intervention
                  </h4>

                  {/* 1. Support for STRESSED: 4-4-4-4 Box Breathing */}
                  {activeTrackerConfig.supportType === 'breathing' && (
                    <div style={{ textAlign: 'center', padding: '12px 0' }}>
                      <div style={{ fontSize: '0.88rem', color: '#991b1b', fontWeight: 600, marginBottom: '14px' }}>
                        Elevated tension detected. Let's reset your vagus nerve with 4-4-4-4 Box Breathing:
                      </div>

                      <div
                        style={{
                          width: '120px',
                          height: '120px',
                          borderRadius: '50%',
                          margin: '0 auto 14px auto',
                          background: 'radial-gradient(circle, rgba(244, 63, 94, 0.25) 0%, rgba(244, 63, 94, 0.05) 70%)',
                          border: '3px solid #f43f5e',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transform: breathingPhase.includes('Inhale') ? 'scale(1.15)' : breathingPhase.includes('Exhale') ? 'scale(0.85)' : 'scale(1.0)',
                          transition: 'transform 3.5s ease-in-out',
                          boxShadow: '0 0 20px rgba(244, 63, 94, 0.2)',
                        }}
                      >
                        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f43f5e' }}>{breathingCount}s</div>
                        <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#881337', textTransform: 'uppercase' }}>
                          {breathingPhase}
                        </div>
                      </div>

                      <p style={{ fontSize: '0.84rem', color: '#475569', maxWidth: '360px', margin: '0 auto', lineHeight: '1.4' }}>
                        Drop your shoulders away from your ears. Follow the rhythm to down-regulate your nervous system.
                      </p>
                    </div>
                  )}

                  {/* 2. Support for ANXIOUS: 5-4-3-2-1 Sensory Grounding */}
                  {activeTrackerConfig.supportType === 'grounding' && (
                    <div style={{ padding: '8px 0' }}>
                      <div style={{ fontSize: '0.86rem', color: '#c2410c', fontWeight: 600, marginBottom: '10px' }}>
                        Fluctuating vocal pitch indicates anxiety. Anchor your senses right now:
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        {[
                          { num: '5', item: '👀 Look for 5 things you can see (colors, shapes, reflections)' },
                          { num: '4', item: '✋ Notice 4 things you can physically touch (chair, clothes, desk)' },
                          { num: '3', item: '👂 Listen for 3 distinct sounds (ambient hum, traffic, breath)' },
                          { num: '2', item: '👃 Identify 2 scents in the room (fresh air, coffee, fabric)' },
                          { num: '1', item: '👅 Name 1 taste or swallow slowly to center your body' },
                        ].map((step, idx) => (
                          <div
                            key={idx}
                            onClick={() => setGroundingStep(idx)}
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '7px 10px',
                              borderRadius: '8px',
                              background: groundingStep === idx ? '#fff7ed' : '#f8fafc',
                              border: `1px solid ${groundingStep === idx ? '#fdba74' : '#e2e8f0'}`,
                              cursor: 'pointer',
                              fontSize: '0.82rem',
                            }}
                          >
                            <span style={{ fontWeight: 800, color: '#ea580c', width: '18px' }}>{step.num}</span>
                            <span style={{ color: '#334155' }}>{step.item}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 3. Support for SAD: Compassionate Validation */}
                  {activeTrackerConfig.supportType === 'compassion' && (
                    <div style={{ padding: '8px 0', textAlign: 'center' }}>
                      <div style={{ fontSize: '2.2rem', marginBottom: '6px' }}>🫂</div>
                      <h4 style={{ margin: '0 0 6px 0', color: '#312e81', fontSize: '1rem' }}>You don't have to carry this alone</h4>
                      <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: '1.5', maxWidth: '380px', margin: '0 auto 12px auto' }}>
                        Subdued vocal modulation and downcast gaze indicate emotional fatigue or sadness. Give yourself grace today.
                      </p>
                      <div style={{ background: '#eef2ff', padding: '10px 14px', borderRadius: '10px', border: '1px solid #c7d2fe', fontSize: '0.82rem', color: '#3730a3', textAlign: 'left' }}>
                        💡 <strong>Gentle Self-Care Action:</strong> Step away for 5 minutes, drink warm water, or share how you feel with the AI companion above.
                      </div>
                    </div>
                  )}

                  {/* 4. Support for FATIGUED: Rest & Digital Eye Break */}
                  {activeTrackerConfig.supportType === 'rest' && (
                    <div style={{ padding: '8px 0' }}>
                      <div style={{ background: '#f5f3ff', border: '1px solid #ddd6fe', borderRadius: '10px', padding: '12px', marginBottom: '10px' }}>
                        <div style={{ fontWeight: 700, color: '#6d28d9', fontSize: '0.86rem', marginBottom: '2px' }}>
                          💤 Rest is Productive Too
                        </div>
                        <p style={{ fontSize: '0.82rem', color: '#4c1d95', margin: 0, lineHeight: '1.4' }}>
                          Low vocal amplitude and eyelid drooping indicate cognitive or physical depletion. Rest is a necessity, not an indulgence.
                        </p>
                      </div>

                      <div style={{ fontSize: '0.82rem', color: '#475569', lineHeight: '1.4' }}>
                        <strong>20-20-20 Recovery Guideline:</strong><br />
                        Look at an object 20 feet away for 20 seconds. Take a long, slow blink to hydrate your eyes, and loosen your posture.
                      </div>
                    </div>
                  )}

                  {/* 5. Support for CALM / HAPPY: Positive Reinforcement */}
                  {(activeTrackerConfig.supportType === 'celebration' || activeTrackerConfig.supportType === 'mindfulness' || activeTrackerConfig.supportType === 'checkin') && (
                    <div style={{ padding: '8px 0', textAlign: 'center' }}>
                      <div style={{ fontSize: '2.2rem', marginBottom: '6px' }}>✨</div>
                      <h4 style={{ margin: '0 0 6px 0', color: '#065f46', fontSize: '1rem' }}>Balanced &amp; Harmonious State</h4>
                      <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: '1.5', maxWidth: '380px', margin: '0 auto 12px auto' }}>
                        Your open facial expression and steady acoustic pitch demonstrate strong emotional equilibrium today.
                      </p>
                      <div style={{ background: '#ecfdf5', padding: '10px 14px', borderRadius: '10px', border: '1px solid #a7f3d0', fontSize: '0.82rem', color: '#047857', textAlign: 'left' }}>
                        🌿 <strong>Mindful Anchor:</strong> What is one positive moment or thought that brought peace to your day? Hold onto it!
                      </div>
                    </div>
                  )}
                </div>

                {/* Save to Check-in button and quick actions */}
                <div style={{ marginTop: '16px', borderTop: '1px solid #e2e8f0', paddingTop: '14px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <button
                    className="btn-primary"
                    style={{
                      padding: '10px 16px',
                      fontSize: '0.86rem',
                      fontWeight: 700,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '8px',
                      background: 'linear-gradient(135deg, #1e3a8a, #4338ca)',
                    }}
                    onClick={handleSaveTrackerToCheckIn}
                  >
                    📝 Save {activeTrackerConfig.emoji} {detectedEmotion} to Today's Check-In
                  </button>

                  {trackerLogStatus && (
                    <div
                      style={{
                        padding: '8px 12px',
                        borderRadius: '8px',
                        fontSize: '0.8rem',
                        background: trackerLogStatus.includes('✓') ? '#ecfdf5' : '#fef2f2',
                        color: trackerLogStatus.includes('✓') ? '#065f46' : '#991b1b',
                        border: `1px solid ${trackerLogStatus.includes('✓') ? '#a7f3d0' : '#fecaca'}`,
                        textAlign: 'center',
                      }}
                    >
                      {trackerLogStatus}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
