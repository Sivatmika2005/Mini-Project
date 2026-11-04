import React, { useState, useEffect, useRef } from 'react';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

// ==============================================================================
// RICH WELLNESS DATA & SCIENTIFIC PROTOCOLS
// ==============================================================================

const BREATHING_TECHNIQUES = {
  box: {
    name: 'Box Breathing (4-4-4-4)',
    badge: 'Navy SEAL Tactical Focus',
    subtitle: 'Calms acute adrenaline surges, sharpens mental focus, and steadies pulse.',
    science: 'Equal-ratio breathing regulates the autonomic nervous system by modulating the baroreflex and balancing sympathetic and parasympathetic tones.',
    phases: [
      { name: 'Inhale', duration: 4, instruction: 'Breathe in slowly through your nose, expanding your lower abdomen.' },
      { name: 'Hold', duration: 4, instruction: 'Gently suspend your breath without straining your throat or chest.' },
      { name: 'Exhale', duration: 4, instruction: 'Release breath steadily through your mouth, emptying your lungs.' },
      { name: 'Hold', duration: 4, instruction: 'Rest in stillness before taking the next conscious breath.' },
    ],
    bestFor: 'Pre-exam nerves, public speaking jitters, intense anxiety spikes, and entering deep study focus.',
  },
  relax: {
    name: '4-7-8 Relaxing Breath',
    badge: 'Natural Nervous System Sedative',
    subtitle: 'Developed by Dr. Andrew Weil to switch the body into deep parasympathetic rest.',
    science: 'An extended 8-second exhale dramatically engages the vagus nerve (cranial nerve X), directly suppressing acetylcholine release at the heart sinoatrial node.',
    phases: [
      { name: 'Inhale', duration: 4, instruction: 'Inhale quietly through your nose for 4 seconds.' },
      { name: 'Hold', duration: 7, instruction: 'Retain the oxygen gently in your lungs for 7 seconds.' },
      { name: 'Exhale', duration: 8, instruction: 'Make an audible whoosh sound as you exhale completely for 8 seconds.' },
      { name: 'Rest', duration: 1, instruction: 'Soft natural pause.' },
    ],
    bestFor: 'Bedtime insomnia, acute racing thoughts, hyperventilation, and high physical tension.',
  },
  sigh: {
    name: 'Physiological Sigh',
    badge: 'Stanford Neuroscience Protocol',
    subtitle: 'The fastest biologically documented method to reduce autonomic arousal in real-time.',
    science: 'Discovered in respiratory neurobiology (Jack Feldman lab, popularized by Dr. Andrew Huberman). The double-inhale pops open collapsed alveoli in the lungs, maximally offloading built-up carbon dioxide.',
    phases: [
      { name: 'Inhale', duration: 2, instruction: 'Take a deep breath in through your nose...' },
      { name: 'Hold', duration: 1, instruction: 'Now take a quick, sharp top-off sip of air to fill lungs to maximum capacity!' },
      { name: 'Exhale', duration: 6, instruction: 'Release all air through your mouth in one long, slow, sighing exhale.' },
      { name: 'Rest', duration: 2, instruction: 'Feel your shoulders naturally drop away from your ears.' },
    ],
    bestFor: 'Instant panic attacks, sudden anger/frustration, chest tightness, and rapid emotional grounding.',
  },
  coherent: {
    name: 'Coherent / Resonance Breathing (5-5)',
    badge: 'Heart Rate Variability (HRV) Sync',
    subtitle: 'Synchronizes respiration with heart rate rhythm at ~6 breaths per minute.',
    science: 'Resonant frequency breathing maximizes respiratory sinus arrhythmia (RSA) and Heart Rate Variability (HRV), creating peak biological cardiovascular coherence.',
    phases: [
      { name: 'Inhale', duration: 5, instruction: 'Inhale smoothly and continuously into your belly for 5 seconds.' },
      { name: 'Exhale', duration: 5, instruction: 'Exhale smoothly without pause or holding for 5 seconds.' },
    ],
    bestFor: 'Daily stress prevention, sustained meditation, emotional balance, and stabilizing blood pressure.',
  },
};

const GROUNDING_STEPS = [
  {
    sense: 'Sight',
    count: 5,
    icon: '👁️',
    title: '5 Things You Can See',
    desc: 'Notice small, overlooked details around you: a shadow on the floor, the texture of a desk, a speck of light, a color you like, or the shape of a doorway.',
    example: 'E.g., "The blue spine of that book, the wood grain on the table, sunlight hitting the window frame..."',
  },
  {
    sense: 'Touch',
    count: 4,
    icon: '🖐️',
    title: '4 Things You Can Physically Feel',
    desc: 'Shift your attention to tactile contact: the fabric of your clothes against your skin, the solid floor beneath your soles, cool air on your cheeks, or the smooth back of your phone.',
    example: 'E.g., "The soft cotton of my shirt, the weight of my feet planted on the floor, the cool keys under my fingertips..."',
  },
  {
    sense: 'Hearing',
    count: 3,
    icon: '👂',
    title: '3 Things You Can Hear',
    desc: 'Tune into auditory layers: listen past your thoughts. Can you hear a distant vehicle, the hum of a computer fan, a bird chirping outside, or the rhythm of your own breath?',
    example: 'E.g., "The low hum of the air conditioner, leaves rustling in the wind, footsteps down the hall..."',
  },
  {
    sense: 'Smell',
    count: 2,
    icon: '👃',
    title: '2 Things You Can Smell',
    desc: 'Gently breathe in through your nose. Look for subtle scents: laundry detergent, coffee, crisp air, wood, or even the neutral scent of your room.',
    example: 'E.g., "The faint hint of hand sanitizer, fresh morning air..."',
  },
  {
    sense: 'Taste / Affirmation',
    count: 1,
    icon: '👅',
    title: '1 Thing You Can Taste or Appreciate',
    desc: 'Notice any lingering taste (mint, tea, water), or state one undeniable truth about this present moment: "I am safe in this room right now."',
    example: 'E.g., "The clean taste of water, or telling myself: I am here, grounded, and breathing."',
  },
];

const CATEGORIZED_AFFIRMATIONS = {
  anxiety: {
    label: '🌿 Anxiety & Overwhelm',
    items: [
      'My anxiety is a temporary physical reaction, not a prophecy of what will happen.',
      'I do not have to solve my entire life today; I only need to handle the next small step.',
      'This feeling is uncomfortable, but it is not dangerous, and it will pass.',
      'I give myself permission to pause, breathe, and let my nervous system reset.',
      'I can hold uncertainty and still be safe in this present moment.',
    ],
  },
  compassion: {
    label: '💛 Self-Compassion & Worth',
    items: [
      'I am allowed to take up space, make mistakes, and learn without shame.',
      'Rest is not a reward I must earn; it is an essential human biological need.',
      'I choose to speak to myself with the same kindness I would offer a dear friend.',
      'My productivity does not define my inherent worth as a human being.',
      'I am doing the best I can with the emotional resources available to me today.',
    ],
  },
  focus: {
    label: '🎯 Academic & Life Focus',
    items: [
      'I am capable of learning difficult things one concept at a time.',
      'One bad exam or tough day does not erase my intelligence or my future.',
      'I focus only on what is within my control: my preparation, my breath, and my effort.',
      'I replace comparison with curiosity; everyone walks their own distinct timeline.',
      'Consistency in small steps always triumphs over sporadic perfection.',
    ],
  },
  rest: {
    label: '🌙 Rest & Letting Go',
    items: [
      'The day is now complete; I release everything I did not accomplish into tomorrow.',
      'I loosen my grip on the future and welcome peaceful, restorative stillness.',
      'My mind is slowing down, my body is heavy and relaxed, and I am safe.',
      'Sleep is restoring my brain, healing my emotions, and preparing me for a fresh dawn.',
    ],
  },
};

export default function WellnessTips({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [latestCheckin, setLatestCheckin] = useState(null);
  const [activeTab, setActiveTab] = useState('breathing');
  const [showSosModal, setShowSosModal] = useState(false);

  // Breathing state
  const [breathingKey, setBreathingKey] = useState('box');
  const [isBreathingRunning, setIsBreathingRunning] = useState(false);
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [phaseSecondsLeft, setPhaseSecondsLeft] = useState(4);
  const [completedCycles, setCompletedCycles] = useState(0);

  // Grounding state
  const [groundingChecked, setGroundingChecked] = useState([false, false, false, false, false]);

  // Affirmations state
  const [affirmationCategory, setAffirmationCategory] = useState('all');
  const [featuredAffirmation, setFeaturedAffirmation] = useState(
    'I do not have to solve my entire life today; I only need to handle the next small step.'
  );
  const [copyFeedback, setCopyFeedback] = useState(false);

  // Load latest check-in for dynamic recommendations
  useEffect(() => {
    async function loadLatest() {
      try {
        const res = await api.getLatestCheckin();
        setLatestCheckin(res.latest);
      } catch (e) {}
    }
    loadLatest();
  }, []);

  const activeTech = BREATHING_TECHNIQUES[breathingKey];

  // Breathing timer engine
  useEffect(() => {
    let interval = null;
    if (isBreathingRunning) {
      interval = setInterval(() => {
        setPhaseSecondsLeft((prev) => {
          if (prev <= 1) {
            // Move to next phase
            const nextIndex = (currentPhaseIndex + 1) % activeTech.phases.length;
            if (nextIndex === 0) {
              setCompletedCycles((c) => c + 1);
            }
            setCurrentPhaseIndex(nextIndex);
            return activeTech.phases[nextIndex].duration;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isBreathingRunning, currentPhaseIndex, activeTech]);

  const handleSelectTechnique = (key) => {
    setIsBreathingRunning(false);
    setBreathingKey(key);
    setCurrentPhaseIndex(0);
    setPhaseSecondsLeft(BREATHING_TECHNIQUES[key].phases[0].duration);
    setCompletedCycles(0);
  };

  const toggleBreathing = () => {
    if (!isBreathingRunning && phaseSecondsLeft <= 0) {
      setCurrentPhaseIndex(0);
      setPhaseSecondsLeft(activeTech.phases[0].duration);
    }
    setIsBreathingRunning(!isBreathingRunning);
  };

  const resetBreathing = () => {
    setIsBreathingRunning(false);
    setCurrentPhaseIndex(0);
    setPhaseSecondsLeft(activeTech.phases[0].duration);
    setCompletedCycles(0);
  };

  const toggleGroundingItem = (index) => {
    const updated = [...groundingChecked];
    updated[index] = !updated[index];
    setGroundingChecked(updated);
  };

  const resetGrounding = () => {
    setGroundingChecked([false, false, false, false, false]);
  };

  const handleShuffleAffirmation = () => {
    const allList = Object.values(CATEGORIZED_AFFIRMATIONS).flatMap((cat) => cat.items);
    const pool =
      affirmationCategory === 'all'
        ? allList
        : CATEGORIZED_AFFIRMATIONS[affirmationCategory]?.items || allList;
    const randomPick = pool[Math.floor(Math.random() * pool.length)];
    setFeaturedAffirmation(randomPick);
  };

  const handleCopyAffirmation = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(featuredAffirmation);
      setCopyFeedback(true);
      setTimeout(() => setCopyFeedback(false), 2200);
    }
  };

  const currentPhase = activeTech.phases[currentPhaseIndex];
  const phaseClass = currentPhase.name.toLowerCase();

  const stress = latestCheckin?.stress_level ?? 5;
  const energy = latestCheckin?.energy_level ?? 5;
  const mood = latestCheckin?.mood ?? 'Calm';
  const sleep = latestCheckin?.sleep_quality ?? 'Fair';

  const completedGroundingCount = groundingChecked.filter(Boolean).length;

  return (
    <div className="app-layout">
      <Sidebar currentPage="wellness_tips" onNavigate={onNavigate} />

      <main className="main-content">
        {/* Header with Navigation */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.75rem', fontWeight: 800, color: 'var(--ink)' }}>
              {t('wellness_title')}
            </h2>
            <p className="aw-muted" style={{ margin: '4px 0 0', fontSize: '0.94rem' }}>
              {t('wellness_subtitle')}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              className="btn-secondary"
              style={{
                background: 'rgba(239, 68, 68, 0.08)',
                color: '#dc2626',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                fontWeight: 700,
              }}
              onClick={() => setShowSosModal(!showSosModal)}
            >
              {showSosModal ? '✕ Close SOS' : '🆘 60s Panic SOS'}
            </button>
            <button className="btn-secondary" onClick={() => onNavigate('dashboard')}>
              ← Dashboard
            </button>
          </div>
        </div>

        {/* 🆘 EMERGENCY 60-SECOND SOS OVERWHELM RESET MODAL / DRAWER */}
        {showSosModal && (
          <div
            className="aw-card"
            style={{
              marginTop: '16px',
              border: '2px solid #ef4444',
              background: 'linear-gradient(135deg, rgba(254,242,242,0.95), rgba(255,255,255,0.95))',
              animation: 'fadeIn 0.3s ease',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <div style={{ fontSize: '1.15rem', fontWeight: 800, color: '#b91c1c' }}>
                🚨 Immediate 60-Second Acute Panic &amp; Overwhelm Protocol
              </div>
              <span className="wellness-info-pill" style={{ background: '#fee2e2', color: '#b91c1c' }}>
                Biological First-Aid
              </span>
            </div>
            <p style={{ fontSize: '0.92rem', color: '#4b5563', lineHeight: 1.6, margin: '4px 0 14px' }}>
              If you are feeling flooded, dissociating, experiencing a racing heart, or overwhelmed right now, perform these three physical actions in sequence:
            </p>
            <div className="grid-3" style={{ gap: '14px' }}>
              <div style={{ padding: '14px', background: '#ffffff', borderRadius: '14px', border: '1px solid rgba(239,68,68,0.2)' }}>
                <div style={{ fontWeight: 700, color: '#b91c1c', marginBottom: '4px' }}>
                  1. The Physiological Sigh
                </div>
                <div style={{ fontSize: '0.88rem', color: 'var(--ink)', lineHeight: 1.5 }}>
                  Take a deep inhale through your nose... then immediately take a sharp second "sip" of air to fill lungs completely. <strong>Exhale very slowly through mouth</strong> with a sigh. Repeat 3 times.
                </div>
              </div>
              <div style={{ padding: '14px', background: '#ffffff', borderRadius: '14px', border: '1px solid rgba(239,68,68,0.2)' }}>
                <div style={{ fontWeight: 700, color: '#b91c1c', marginBottom: '4px' }}>
                  2. Cold Water Reset
                </div>
                <div style={{ fontSize: '0.88rem', color: 'var(--ink)', lineHeight: 1.5 }}>
                  Hold an ice cube or run freezing cold water over your wrists and face for 15 seconds. This stimulates the <strong>mammalian dive reflex</strong>, dropping heart rate by 15-25% automatically.
                </div>
              </div>
              <div style={{ padding: '14px', background: '#ffffff', borderRadius: '14px', border: '1px solid rgba(239,68,68,0.2)' }}>
                <div style={{ fontWeight: 700, color: '#b91c1c', marginBottom: '4px' }}>
                  3. Physical Contact
                </div>
                <div style={{ fontSize: '0.88rem', color: 'var(--ink)', lineHeight: 1.5 }}>
                  Push your bare feet firmly into the floor. Touch a solid object (desk, wall, stone). Tell yourself out loud: <em>"My name is [Name]. I am safe in this room. This anxiety wave will pass."</em>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 1. DYNAMIC CHECK-IN RECOMMENDATION BANNER */}
        {latestCheckin ? (
          <div
            className="aw-card"
            style={{
              background: 'linear-gradient(135deg, rgba(236,235,255,0.7), rgba(233,249,240,0.8))',
              border: '1.5px solid rgba(124,124,235,0.25)',
              margin: '18px 0',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
              <div style={{ fontWeight: 800, fontSize: '1.05rem', color: '#6366f1' }}>
                🤖 Personalized AI Wellness Recommendation
              </div>
              <span className="wellness-info-pill">Live Biological Context</span>
            </div>
            <div style={{ fontSize: '0.92rem', color: '#1a1a2e', lineHeight: 1.5, marginBottom: '12px' }}>
              Based on your latest check-in metrics: Mood <b>{mood}</b>, Stress <b>{stress}/10</b>, Energy <b>{energy}/10</b>, Sleep <b>{sleep}</b>:
            </div>

            {stress >= 7 ? (
              <div className="alert-box alert-info" style={{ margin: 0, background: 'rgba(239,68,68,0.06)', borderLeft: '4px solid #ef4444' }}>
                ⚡ <strong>High Stress Priority:</strong> Your sympathetic nervous system is heavily activated. We recommend switching to the <strong>🫁 Breathing</strong> tab and launching <strong>Box Breathing (4-4-4-4)</strong> or the <strong>Physiological Sigh</strong> right now to lower heart rate and cortisol levels.
              </div>
            ) : energy <= 4 ? (
              <div className="alert-box alert-info" style={{ margin: 0, background: 'rgba(245,158,11,0.06)', borderLeft: '4px solid #f59e0b' }}>
                🔋 <strong>Fatigue &amp; Energy Priority:</strong> You reported depleted energy. Avoid harsh caffeine spikes; instead check the <strong>🌙 Sleep &amp; Circadian</strong> tab for the 10-3-2-1-0 protocol and practice the <strong>3-Minute Somatic Reset</strong> in Meditation.
              </div>
            ) : sleep === 'Poor' || sleep === 'Fair' ? (
              <div className="alert-box alert-info" style={{ margin: 0, background: 'rgba(99,102,241,0.06)', borderLeft: '4px solid #6366f1' }}>
                🌙 <strong>Sleep Restorative Priority:</strong> Your sleep was subpar last night. Review our <strong>Circadian Light Science</strong> and apply the <strong>4-7-8 Relaxing Breath</strong> before bed tonight to restore deep Slow-Wave Sleep (SWS).
              </div>
            ) : (
              <div className="alert-box alert-success" style={{ margin: 0 }}>
                ✨ <strong>Optimal Equilibrium:</strong> You are in a clear, balanced headspace today! Explore the <strong>⚡ Stress Resilience (Circle of Control)</strong> or reinforce positive neuroplasticity in <strong>✨ Affirmations</strong>.
              </div>
            )}
          </div>
        ) : (
          <div className="alert-box alert-info" style={{ margin: '18px 0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              💡 <strong>Pro-Tip:</strong> Log your <strong>Daily Check-In</strong> to unlock real-time recommendations tailored dynamically to your stress, energy, and sleep patterns!
            </div>
            <button className="btn-primary" style={{ padding: '6px 14px', fontSize: '0.85rem' }} onClick={() => onNavigate('checkin')}>
              Log Today's Check-In →
            </button>
          </div>
        )}

        {/* 2. CATEGORY NAVIGATION TABS */}
        <div className="tabs-container" style={{ marginTop: '20px' }}>
          {[
            { id: 'breathing', label: '🫁 Breathwork & Nervous System' },
            { id: 'meditation', label: '🧘 Guided Mindfulness' },
            { id: 'grounding', label: '🖐️ Somatic Grounding' },
            { id: 'sleep', label: '🌙 Sleep & Circadian' },
            { id: 'stress', label: '⚡ Stress Resilience & CBT' },
            { id: 'affirmations', label: '✨ Affirmations & Mindset' },
          ].map((tab) => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ==================================================================== */}
        {/* TAB 1: BREATHWORK & NERVOUS SYSTEM REGULATION */}
        {/* ==================================================================== */}
        {activeTab === 'breathing' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Interactive Breathing Pacer Card */}
            <div className="aw-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
                <div>
                  <h3 style={{ margin: '0 0 4px', fontSize: '1.3rem', color: 'var(--ink)' }}>
                    🫁 Interactive Respiratory Pacer
                  </h3>
                  <p className="aw-muted" style={{ margin: 0, fontSize: '0.9rem' }}>
                    Select a clinically backed breathwork protocol below and follow the visual pacer.
                  </p>
                </div>
                <span className="wellness-info-pill">{activeTech.badge}</span>
              </div>

              {/* Protocol Selector Buttons */}
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', margin: '18px 0 10px' }}>
                {Object.entries(BREATHING_TECHNIQUES).map(([k, t]) => (
                  <button
                    key={k}
                    className={`btn-secondary ${breathingKey === k ? 'btn-primary' : ''}`}
                    style={{
                      padding: '8px 16px',
                      fontSize: '0.88rem',
                      fontWeight: 700,
                      borderRadius: '10px',
                    }}
                    onClick={() => handleSelectTechnique(k)}
                  >
                    {t.name}
                  </button>
                ))}
              </div>

              {/* Description & Science */}
              <div style={{ padding: '12px 16px', background: 'rgba(124,124,235,0.06)', borderRadius: '12px', fontSize: '0.88rem', lineHeight: 1.6 }}>
                <div><strong>Protocol Focus:</strong> {activeTech.subtitle}</div>
                <div style={{ marginTop: '4px', color: 'var(--muted)' }}>
                  <strong>Neuroscience Mechanism:</strong> {activeTech.science}
                </div>
              </div>

              {/* Visual Animated Breathing Circle */}
              <div className="wellness-interactive-pacer">
                <div className={`breathing-pacer-circle ${isBreathingRunning ? phaseClass : 'rest'}`}>
                  <div style={{ fontSize: '0.82rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--accent)' }}>
                    {isBreathingRunning ? currentPhase.name : 'Ready'}
                  </div>
                  <div style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--ink)', lineHeight: 1 }}>
                    {isBreathingRunning ? phaseSecondsLeft : activeTech.phases[0].duration}s
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '4px' }}>
                    Cycle: {completedCycles}
                  </div>
                </div>

                <div style={{ maxWidth: '420px', textAlign: 'center', margin: '8px 0 16px', minHeight: '44px' }}>
                  <p style={{ margin: 0, fontSize: '0.94rem', fontWeight: 600, color: 'var(--ink)' }}>
                    {isBreathingRunning
                      ? currentPhase.instruction
                      : 'Click "Start Pacer" and breathe in rhythm with the expanding circle.'}
                  </p>
                </div>

                <div style={{ display: 'flex', gap: '12px' }}>
                  <button
                    className="btn-primary"
                    style={{ padding: '10px 28px', fontSize: '1rem', fontWeight: 700, borderRadius: '999px' }}
                    onClick={toggleBreathing}
                  >
                    {isBreathingRunning ? '⏸ Pause Pacer' : '▶ Start Pacer'}
                  </button>
                  <button
                    className="btn-secondary"
                    style={{ padding: '10px 20px', fontSize: '0.9rem', borderRadius: '999px' }}
                    onClick={resetBreathing}
                  >
                    ↺ Reset
                  </button>
                </div>
              </div>

              {/* Best Times to Practice */}
              <div style={{ fontSize: '0.86rem', color: 'var(--muted)', marginTop: '12px' }}>
                💡 <strong>Optimal Application:</strong> {activeTech.bestFor}
              </div>
            </div>

            {/* Deep Scientific Education Cards */}
            <div className="grid-2" style={{ gap: '18px' }}>
              <div className="aw-card">
                <h4 style={{ margin: '0 0 10px', color: 'var(--ink)' }}>
                  🧠 The Vagus Nerve &amp; Heart-Rate Deceleration
                </h4>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.65, color: 'var(--muted)', margin: 0 }}>
                  When you inhale, your diaphragm moves down, increasing chest cavity space and allowing your heart to expand slightly. Blood flow accelerates, prompting the brain to temporarily speed up heart rate.
                  <br /><br />
                  Conversely, when you <strong>prolong your exhale</strong>, the diaphragm moves up, compressing the heart. The brain senses this increase in pressure and signals the <strong>vagus nerve</strong> to release acetylcholine, naturally braking the heart rate and switching off panic alarms.
                </p>
              </div>

              <div className="aw-card">
                <h4 style={{ margin: '0 0 10px', color: 'var(--ink)' }}>
                  🫁 Chest vs. Diaphragmatic Mechanics
                </h4>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.65, color: 'var(--muted)', margin: 0 }}>
                  <strong>Shallow Chest Breathing:</strong> Uses secondary neck and shoulder muscles. Signals oxygen deprivation to the amygdala, generating chronic low-grade anxiety and tension headaches.
                  <br /><br />
                  <strong>Diaphragmatic Belly Breathing:</strong> Maximizes ventilation in the lower lung lobes where parasympathetic receptors are most concentrated. To practice: place one hand on your chest and one on your belly; only the belly hand should rise and fall.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* TAB 2: GUIDED MEDITATION & MINDFULNESS */}
        {/* ==================================================================== */}
        {activeTab === 'meditation' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div className="aw-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h3 style={{ margin: 0, fontSize: '1.3rem', color: 'var(--ink)' }}>
                  🧘 Evidence-Based Mindfulness Protocols
                </h3>
                <span className="wellness-info-pill">Neuroplastic Training</span>
              </div>
              <p className="aw-muted" style={{ margin: '0 0 16px', fontSize: '0.9rem', lineHeight: 1.6 }}>
                Mindfulness is not about stopping your thoughts; it is the non-judgmental practice of observing thoughts without getting emotionally entangled in them.
              </p>

              <div className="grid-2" style={{ gap: '16px' }}>
                {/* 1. Body Scan */}
                <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(124,124,235,0.04)', border: '1px solid rgba(124,124,235,0.15)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <strong style={{ color: 'var(--ink)', fontSize: '1rem' }}>1. Full-Body Somatic Scan</strong>
                    <span style={{ fontSize: '0.8rem', color: 'var(--accent)', fontWeight: 700 }}>7-10 Mins</span>
                  </div>
                  <p style={{ fontSize: '0.87rem', lineHeight: 1.6, color: 'var(--muted)', margin: '6px 0 10px' }}>
                    Systematically release micro-contractions stored in muscle tissue:
                  </p>
                  <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.85rem', lineHeight: 1.7, color: 'var(--ink)' }}>
                    <li><strong>Forehead &amp; Jaw:</strong> Unclench teeth, drop tongue from the roof of mouth.</li>
                    <li><strong>Trapezius &amp; Neck:</strong> Drop shoulders 2 inches down and away from ears.</li>
                    <li><strong>Solar Plexus &amp; Belly:</strong> Soften abdomen, allow breath to expand unhindered.</li>
                    <li><strong>Pelvic Floor &amp; Legs:</strong> Release gripped pelvic muscles; anchor feet into floor.</li>
                  </ul>
                </div>

                {/* 2. Leaves on a Stream */}
                <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(124,124,235,0.04)', border: '1px solid rgba(124,124,235,0.15)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <strong style={{ color: 'var(--ink)', fontSize: '1rem' }}>2. "Leaves on a Stream" Decentering</strong>
                    <span style={{ fontSize: '0.8rem', color: 'var(--accent)', fontWeight: 700 }}>CBT &amp; ACT Tool</span>
                  </div>
                  <p style={{ fontSize: '0.87rem', lineHeight: 1.6, color: 'var(--muted)', margin: '6px 0 10px' }}>
                    Cognitive defusion practice to stop catastrophic thought spirals:
                  </p>
                  <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.85rem', lineHeight: 1.7, color: 'var(--ink)' }}>
                    <li>Visualize yourself sitting beside a gentle, slowly flowing woodland stream.</li>
                    <li>Whenever an anxious thought pops up (<em>"What if I fail?"</em>), place it on a floating leaf.</li>
                    <li>Watch it drift down the river until it disappears around the bend.</li>
                    <li>Do not argue with the thought. You are the riverbank, not the floating debris.</li>
                  </ul>
                </div>

                {/* 3. Metta Meditation */}
                <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(124,124,235,0.04)', border: '1px solid rgba(124,124,235,0.15)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <strong style={{ color: 'var(--ink)', fontSize: '1rem' }}>3. Loving-Kindness (Metta) Practice</strong>
                    <span style={{ fontSize: '0.8rem', color: 'var(--accent)', fontWeight: 700 }}>Self-Compassion</span>
                  </div>
                  <p style={{ fontSize: '0.87rem', lineHeight: 1.6, color: 'var(--muted)', margin: '6px 0 10px' }}>
                    Shown in fMRI studies to down-regulate the default mode network (DMN):
                  </p>
                  <div style={{ padding: '10px 14px', background: '#ffffff', borderRadius: '10px', fontSize: '0.84rem', fontStyle: 'italic', lineHeight: 1.6, color: '#4338ca' }}>
                    "May I be safe from inner and outer harm.<br />
                    May I be healthy, peaceful, and strong.<br />
                    May I navigate life's challenges with ease and self-acceptance."
                  </div>
                  <div style={{ fontSize: '0.8rem', color: 'var(--muted)', marginTop: '8px' }}>
                    Repeat for yourself, then radiate outward toward loved ones and all living beings.
                  </div>
                </div>

                {/* 4. S.T.O.P. Micro-Meditation */}
                <div style={{ padding: '16px', borderRadius: '16px', background: 'rgba(124,124,235,0.04)', border: '1px solid rgba(124,124,235,0.15)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                    <strong style={{ color: 'var(--ink)', fontSize: '1rem' }}>4. The 60-Second S.T.O.P. Technique</strong>
                    <span style={{ fontSize: '0.8rem', color: 'var(--accent)', fontWeight: 700 }}>On-The-Go Reset</span>
                  </div>
                  <p style={{ fontSize: '0.87rem', lineHeight: 1.6, color: 'var(--muted)', margin: '6px 0 10px' }}>
                    Use between study blocks, lectures, or meetings:
                  </p>
                  <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.85rem', lineHeight: 1.7, color: 'var(--ink)' }}>
                    <li><strong>S — Stop:</strong> Pause your physical typing, speaking, or movement.</li>
                    <li><strong>T — Take a breath:</strong> One slow, deep inhalation and complete exhalation.</li>
                    <li><strong>O — Observe:</strong> Notice feelings without labeling them as good or bad.</li>
                    <li><strong>P — Proceed:</strong> Continue your task with intentional calm.</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* TAB 3: SOMATIC & SENSORY GROUNDING */}
        {/* ==================================================================== */}
        {activeTab === 'grounding' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Interactive 5-4-3-2-1 Sensory Checklist */}
            <div className="aw-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <h3 style={{ margin: 0, fontSize: '1.3rem', color: 'var(--ink)' }}>
                  🖐️ Interactive 5-4-3-2-1 Sensory Grounding Tool
                </h3>
                <span className="wellness-info-pill">
                  {completedGroundingCount}/5 Completed
                </span>
              </div>
              <p className="aw-muted" style={{ margin: '0 0 16px', fontSize: '0.9rem', lineHeight: 1.6 }}>
                Anxiety lives in anticipatory mental projections of the future. By engaging your 5 physical senses in the present room, you pull sensory bandwidth away from the threat-detection amygdala. Click each step as you complete it:
              </p>

              {/* Steps List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {GROUNDING_STEPS.map((step, idx) => {
                  const isDone = groundingChecked[idx];
                  return (
                    <div
                      key={idx}
                      className={`grounding-step-item ${isDone ? 'completed' : ''}`}
                      onClick={() => toggleGroundingItem(idx)}
                    >
                      <input
                        type="checkbox"
                        checked={isDone}
                        onChange={() => {}}
                        style={{ marginTop: '4px', width: '18px', height: '18px', cursor: 'pointer', accentColor: '#10b981' }}
                      />
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '3px' }}>
                          <span style={{ fontSize: '1.2rem' }}>{step.icon}</span>
                          <strong style={{ fontSize: '0.98rem', color: isDone ? '#065f46' : 'var(--ink)' }}>
                            {step.title}
                          </strong>
                          {isDone && (
                            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#10b981' }}>
                              ✓ Grounded
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '0.88rem', color: 'var(--muted)', lineHeight: 1.5 }}>
                          {step.desc}
                        </div>
                        <div style={{ fontSize: '0.82rem', color: 'var(--accent)', marginTop: '4px', fontStyle: 'italic' }}>
                          {step.example}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Grounding Action Bar */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px' }}>
                {completedGroundingCount === 5 ? (
                  <div style={{ color: '#10b981', fontWeight: 700, fontSize: '0.95rem' }}>
                    🎉 Outstanding! You have fully anchored all 5 senses to the present moment.
                  </div>
                ) : (
                  <div style={{ fontSize: '0.86rem', color: 'var(--muted)' }}>
                    Complete all 5 sensory anchors for full nervous system grounding.
                  </div>
                )}
                <button className="btn-secondary" style={{ padding: '6px 14px', fontSize: '0.85rem' }} onClick={resetGrounding}>
                  ↺ Reset Checklist
                </button>
              </div>
            </div>

            {/* Acute Somatic Techniques */}
            <div className="grid-2" style={{ gap: '18px' }}>
              <div className="aw-card">
                <h4 style={{ margin: '0 0 10px', color: 'var(--ink)' }}>
                  🧊 The Mammalian Dive Reflex (Cold Shock)
                </h4>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.65, color: 'var(--muted)', margin: 0 }}>
                  <strong>Evolutionary Biology:</strong> When marine mammals dive into cold water, their bodies prioritize oxygen conservation by abruptly lowering their heart rate.
                  <br /><br />
                  <strong>Human Protocol:</strong> Press an ice pack, cold can, or ice water bowl across your eyes, bridge of nose, and upper cheeks for 15-20 seconds while holding your breath. Trigeminal nerve sensors immediately trigger the vagal brake, reducing panic heart rates by 15-25% without medication.
                </p>
              </div>

              <div className="aw-card">
                <h4 style={{ margin: '0 0 10px', color: 'var(--ink)' }}>
                  🦋 Bilateral Stimulation (The Butterfly Hug)
                </h4>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.65, color: 'var(--muted)', margin: 0 }}>
                  <strong>EMDR-Informed Stabilization:</strong> Developed by Lucina Artigas during crisis disaster relief. Alternating tactile stimulation helps integrate distressing emotional memory networks between the left and right cerebral hemispheres.
                  <br /><br />
                  <strong>Protocol:</strong> Cross your arms over your chest, hooking your thumbs like butterfly wings. Alternately tap left and right clavicles with your fingers in a gentle, rhythmic tempo (1-2-1-2) while taking slow, unhurried breaths.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* TAB 4: SLEEP HYGIENE & CIRCADIAN SCIENCE */}
        {/* ==================================================================== */}
        {activeTab === 'sleep' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* 10-3-2-1-0 Framework */}
            <div className="aw-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h3 style={{ margin: 0, fontSize: '1.3rem', color: 'var(--ink)' }}>
                  🌙 The Evidence-Based "10-3-2-1-0" Sleep Protocol
                </h3>
                <span className="wellness-info-pill">Sleep Architecture</span>
              </div>
              <p className="aw-muted" style={{ margin: '0 0 18px', fontSize: '0.9rem', lineHeight: 1.6 }}>
                Sleep is the single most powerful biological foundation for emotional regulation, memory consolidation, and mental resilience. Structure your evening with the 10-3-2-1-0 countdown:
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', gap: '14px', padding: '14px', borderRadius: '12px', background: 'rgba(124,124,235,0.05)', border: '1px solid rgba(124,124,235,0.12)' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#6366f1', minWidth: '45px' }}>10h</div>
                  <div>
                    <strong>10 Hours Before Bed — Caffeine Cutoff</strong>
                    <div style={{ fontSize: '0.88rem', color: 'var(--muted)', marginTop: '2px', lineHeight: 1.5 }}>
                      Caffeine has an average half-life of 5 to 7 hours and competitively blocks adenosine receptors. Even if you fall asleep with caffeine in your bloodstream, it suppresses restorative Deep Slow-Wave Sleep (SWS).
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '14px', padding: '14px', borderRadius: '12px', background: 'rgba(124,124,235,0.05)', border: '1px solid rgba(124,124,235,0.12)' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#6366f1', minWidth: '45px' }}>3h</div>
                  <div>
                    <strong>3 Hours Before Bed — Heavy Food &amp; Alcohol Cessation</strong>
                    <div style={{ fontSize: '0.88rem', color: 'var(--muted)', marginTop: '2px', lineHeight: 1.5 }}>
                      Digesting rich or spicy foods raises core body temperature, preventing sleep onset. Alcohol may sedate consciousness, but it severely fragments REM sleep, worsening morning anxiety and brain fog.
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '14px', padding: '14px', borderRadius: '12px', background: 'rgba(124,124,235,0.05)', border: '1px solid rgba(124,124,235,0.12)' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#6366f1', minWidth: '45px' }}>2h</div>
                  <div>
                    <strong>2 Hours Before Bed — Analytical Work Wind-Down</strong>
                    <div style={{ fontSize: '0.88rem', color: 'var(--muted)', marginTop: '2px', lineHeight: 1.5 }}>
                      Power down intense coding, studying, or emotionally charged arguments. Allow the prefrontal cortex to transition from problem-solving mode into passive relaxation.
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '14px', padding: '14px', borderRadius: '12px', background: 'rgba(124,124,235,0.05)', border: '1px solid rgba(124,124,235,0.12)' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#6366f1', minWidth: '45px' }}>1h</div>
                  <div>
                    <strong>1 Hour Before Bed — The "Digital Sunset"</strong>
                    <div style={{ fontSize: '0.88rem', color: 'var(--muted)', marginTop: '2px', lineHeight: 1.5 }}>
                      Blue photons (460–480 nm) emitted by smartphones and monitors fool retinal ganglion cells into thinking it is midday, suppressing pineal melatonin synthesis. Switch to amber lamps or reading a paper book.
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '14px', padding: '14px', borderRadius: '12px', background: 'rgba(124,124,235,0.05)', border: '1px solid rgba(124,124,235,0.12)' }}>
                  <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#10b981', minWidth: '45px' }}>0</div>
                  <div>
                    <strong>0 — Times You Hit the Snooze Button</strong>
                    <div style={{ fontSize: '0.88rem', color: 'var(--muted)', marginTop: '2px', lineHeight: 1.5 }}>
                      Hitting snooze restarts a sleep cycle that cannot finish in 9 minutes, inducing severe sleep inertia and elevated morning cortisol. Get out of bed on your first alarm.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Circadian Biology Details */}
            <div className="grid-2" style={{ gap: '18px' }}>
              <div className="aw-card">
                <h4 style={{ margin: '0 0 10px', color: 'var(--ink)' }}>
                  ☀️ Morning Sunlight Anchoring
                </h4>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.65, color: 'var(--muted)', margin: 0 }}>
                  View 10–15 minutes of outdoor sunlight within 30–60 minutes of waking (without sunglasses; through windows is 50x less effective).
                  <br /><br />
                  This stimulates intrinsically photosensitive retinal ganglion cells (ipRGCs) that calibrate your brain's master clock (the suprachiasmatic nucleus), triggering a healthy morning cortisol surge while setting a timer for natural melatonin release ~14–16 hours later.
                </p>
              </div>

              <div className="aw-card">
                <h4 style={{ margin: '0 0 10px', color: 'var(--ink)' }}>
                  ❄️ Core Temperature &amp; The 20-Min Rule
                </h4>
                <p style={{ fontSize: '0.9rem', lineHeight: 1.65, color: 'var(--muted)', margin: 0 }}>
                  <strong>Thermal Drop:</strong> The human brain must decrease its core temperature by ~1°C (2–3°F) to initiate slow-wave sleep. Keep bedroom temperatures cool (65–68°F / 18–20°C).
                  <br /><br />
                  <strong>The 20-Minute Stimulus Rule:</strong> If you are still awake after 20 minutes in bed, do not toss and turn. Leave the bedroom, sit in dim light, read or stretch, and only return when eyelids feel heavy. Protect the brain's association: Bed = Sleep.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* TAB 5: STRESS RESILIENCE & CBT REFRAMING */}
        {/* ==================================================================== */}
        {activeTab === 'stress' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* The Circle of Control */}
            <div className="aw-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <h3 style={{ margin: 0, fontSize: '1.3rem', color: 'var(--ink)' }}>
                  ⚡ The Circle of Control (Stoic &amp; CBT Model)
                </h3>
                <span className="wellness-info-pill">Energy Allocation</span>
              </div>
              <p className="aw-muted" style={{ margin: '0 0 16px', fontSize: '0.9rem', lineHeight: 1.6 }}>
                Much of modern mental fatigue stems from exerting emotional energy on things you cannot influence. Clarify where your agency lies:
              </p>

              <div className="grid-2" style={{ gap: '16px' }}>
                <div className="control-circle-box in-control">
                  <h4 style={{ color: '#047857', margin: '0 0 10px', fontSize: '1.05rem' }}>
                    🎯 Inside Your Circle of Control (Focus Here)
                  </h4>
                  <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.88rem', lineHeight: 1.8, color: 'var(--ink)' }}>
                    <li>How you respond to unexpected setbacks or news.</li>
                    <li>Your daily boundaries and how often you say "no".</li>
                    <li>Your sleep schedule, hydration, and nutrition.</li>
                    <li>The internal narrative and self-compassion you practice.</li>
                    <li>The focused preparation and honest effort you put in today.</li>
                    <li>Seeking professional counseling or leaning on trusted friends.</li>
                  </ul>
                </div>

                <div className="control-circle-box out-control">
                  <h4 style={{ color: '#b91c1c', margin: '0 0 10px', fontSize: '1.05rem' }}>
                    🌪️ Outside Your Circle of Control (Practice Release)
                  </h4>
                  <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.88rem', lineHeight: 1.8, color: 'var(--ink)' }}>
                    <li>Other people's judgments, moods, and opinions of you.</li>
                    <li>Future exam questions, project grades, or interview outcomes.</li>
                    <li>Past mistakes or missed opportunities you cannot alter.</li>
                    <li>Sudden disruptions, traffic, or technical glitches.</li>
                    <li>The general state of the world and global headlines.</li>
                    <li>Whether other people choose to follow through on promises.</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Cognitive Reframing (CBT Catch, Check, Change) */}
            <div className="aw-card">
              <h4 style={{ margin: '0 0 10px', color: 'var(--ink)', fontSize: '1.15rem' }}>
                🔄 CBT Cognitive Reframing: Catch It, Check It, Change It
              </h4>
              <p className="aw-muted" style={{ margin: '0 0 16px', fontSize: '0.9rem', lineHeight: 1.6 }}>
                Automatic Negative Thoughts (ANTs) are distorted cognitive shortcuts the brain generates under stress. Practice replacing distortions with grounded truth:
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ padding: '14px', borderRadius: '12px', background: 'rgba(124,124,235,0.04)', borderLeft: '4px solid #ef4444' }}>
                  <div style={{ fontWeight: 700, color: '#dc2626', fontSize: '0.88rem' }}>
                    Distortion: Catastrophizing ("Everything is falling apart")
                  </div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--ink)', marginTop: '4px' }}>
                    <em>Thought:</em> "If I don't ace this presentation, my career will be completely ruined."
                  </div>
                  <div style={{ fontSize: '0.88rem', color: '#047857', marginTop: '4px', fontWeight: 600 }}>
                    ✨ Reframe: "I am nervous because I care about doing well. However, one presentation does not define my career. I have prepared, and I can handle whatever feedback arises."
                  </div>
                </div>

                <div style={{ padding: '14px', borderRadius: '12px', background: 'rgba(124,124,235,0.04)', borderLeft: '4px solid #f59e0b' }}>
                  <div style={{ fontWeight: 700, color: '#d97706', fontSize: '0.88rem' }}>
                    Distortion: All-or-Nothing / Black-and-White Thinking
                  </div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--ink)', marginTop: '4px' }}>
                    <em>Thought:</em> "I missed my morning study goal, so today is a total failure."
                  </div>
                  <div style={{ fontSize: '0.88rem', color: '#047857', marginTop: '4px', fontWeight: 600 }}>
                    ✨ Reframe: "Progress is non-linear. Missing the morning does not ruin the afternoon. A focused 25 minutes now is far more valuable than abandoning the whole day."
                  </div>
                </div>

                <div style={{ padding: '14px', borderRadius: '12px', background: 'rgba(124,124,235,0.04)', borderLeft: '4px solid #6366f1' }}>
                  <div style={{ fontWeight: 700, color: '#4f46e5', fontSize: '0.88rem' }}>
                    Distortion: Mind Reading &amp; Imposter Syndrome
                  </div>
                  <div style={{ fontSize: '0.88rem', color: 'var(--ink)', marginTop: '4px' }}>
                    <em>Thought:</em> "Everyone in the room can tell that I don't know what I'm doing."
                  </div>
                  <div style={{ fontSize: '0.88rem', color: '#047857', marginTop: '4px', fontWeight: 600 }}>
                    ✨ Reframe: "I cannot read minds. People are usually preoccupied with their own tasks and insecurities. I earned my seat at this table, and I am here to learn and contribute."
                  </div>
                </div>
              </div>
            </div>

            {/* The H.A.L.T. Audit */}
            <div className="aw-card">
              <h4 style={{ margin: '0 0 8px', color: 'var(--ink)' }}>
                🍎 The H.A.L.T. Biological Audit
              </h4>
              <p className="aw-muted" style={{ margin: '0 0 14px', fontSize: '0.88rem' }}>
                Before accepting a catastrophic thought as fact, pause and check these 4 physiological levers:
              </p>
              <div className="grid-2" style={{ gap: '12px' }}>
                <div style={{ padding: '10px 14px', background: 'rgba(124,124,235,0.05)', borderRadius: '10px' }}>
                  <strong>H — Hungry?</strong> Low blood glucose triggers adrenaline release that mimics panic attacks. Drink water and eat protein.
                </div>
                <div style={{ padding: '10px 14px', background: 'rgba(124,124,235,0.05)', borderRadius: '10px' }}>
                  <strong>A — Angry?</strong> Unspoken resentment or violated boundaries elevate cortisol. Acknowledge and state your need calmly.
                </div>
                <div style={{ padding: '10px 14px', background: 'rgba(124,124,235,0.05)', borderRadius: '10px' }}>
                  <strong>L — Lonely?</strong> Prolonged isolation triggers primal threat circuits. Text or talk with someone you trust for 5 minutes.
                </div>
                <div style={{ padding: '10px 14px', background: 'rgba(124,124,235,0.05)', borderRadius: '10px' }}>
                  <strong>T — Tired?</strong> An exhausted prefrontal cortex cannot regulate the amygdala. Step away and sleep or rest.
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* TAB 6: EVIDENCE-BASED AFFIRMATIONS & MINDSET */}
        {/* ==================================================================== */}
        {activeTab === 'affirmations' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {/* Featured Affirmation Generator Card */}
            <div
              className="aw-card"
              style={{
                background: 'linear-gradient(135deg, rgba(238,242,255,0.8), rgba(240,253,244,0.8))',
                border: '1.5px solid rgba(124,124,235,0.3)',
                textAlign: 'center',
                padding: '30px 24px',
              }}
            >
              <div style={{ fontSize: '0.85rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#6366f1', marginBottom: '10px' }}>
                ✨ Featured Affirmation of the Moment
              </div>
              <div
                style={{
                  fontSize: '1.35rem',
                  fontWeight: 700,
                  color: 'var(--ink)',
                  lineHeight: 1.6,
                  maxWidth: '750px',
                  margin: '0 auto 20px',
                  fontFamily: "'Poppins', sans-serif",
                }}
              >
                "{featuredAffirmation}"
              </div>

              <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', flexWrap: 'wrap' }}>
                <button
                  className="btn-primary"
                  style={{ padding: '10px 22px', fontSize: '0.92rem', fontWeight: 700, borderRadius: '999px' }}
                  onClick={handleShuffleAffirmation}
                >
                  🎲 Shuffle Affirmation
                </button>
                <button
                  className="btn-secondary"
                  style={{ padding: '10px 20px', fontSize: '0.92rem', borderRadius: '999px' }}
                  onClick={handleCopyAffirmation}
                >
                  {copyFeedback ? '✓ Copied to Clipboard!' : '📋 Copy Text'}
                </button>
              </div>
            </div>

            {/* Categorized Affirmation Library */}
            <div className="aw-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: 'var(--ink)' }}>
                  📚 Categorized Affirmation Library
                </h3>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  <button
                    className={`btn-secondary ${affirmationCategory === 'all' ? 'btn-primary' : ''}`}
                    style={{ padding: '5px 12px', fontSize: '0.8rem', borderRadius: '8px' }}
                    onClick={() => setAffirmationCategory('all')}
                  >
                    All Categories
                  </button>
                  {Object.entries(CATEGORIZED_AFFIRMATIONS).map(([k, cat]) => (
                    <button
                      key={k}
                      className={`btn-secondary ${affirmationCategory === k ? 'btn-primary' : ''}`}
                      style={{ padding: '5px 12px', fontSize: '0.8rem', borderRadius: '8px' }}
                      onClick={() => setAffirmationCategory(k)}
                    >
                      {cat.label}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '14px' }}>
                {Object.entries(CATEGORIZED_AFFIRMATIONS)
                  .filter(([k]) => affirmationCategory === 'all' || affirmationCategory === k)
                  .flatMap(([k, cat]) =>
                    cat.items.map((item, idx) => (
                      <div
                        key={`${k}-${idx}`}
                        style={{
                          padding: '14px 18px',
                          background: 'rgba(124,124,235,0.04)',
                          borderRadius: '12px',
                          fontWeight: 600,
                          color: 'var(--ink)',
                          borderLeft: '4px solid var(--accent)',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          gap: '12px',
                        }}
                      >
                        <div style={{ fontSize: '0.93rem', lineHeight: 1.5 }}>"{item}"</div>
                        <button
                          className="btn-secondary"
                          style={{ padding: '4px 10px', fontSize: '0.78rem', whiteSpace: 'nowrap' }}
                          onClick={() => {
                            setFeaturedAffirmation(item);
                            window.scrollTo({ top: 120, behavior: 'smooth' });
                          }}
                        >
                          Focus on This ↑
                        </button>
                      </div>
                    ))
                  )}
              </div>
            </div>

            {/* Scientific Theory Behind Affirmations */}
            <div className="aw-card">
              <h4 style={{ margin: '0 0 10px', color: 'var(--ink)' }}>
                🧠 The Neuroscience of Self-Affirmation Theory
              </h4>
              <p style={{ fontSize: '0.9rem', lineHeight: 1.65, color: 'var(--muted)', margin: 0 }}>
                Pioneered by social psychologist Claude Steele (1988), <strong>Self-Affirmation Theory</strong> demonstrates that when people reflect on core personal values, brain activity in the <strong>ventromedial prefrontal cortex (vmPFC)</strong> and <strong>ventral striatum</strong> increases.
                <br /><br />
                This neural activity acts as a protective psychological buffer, down-regulating cortisol responses during stressful performance reviews and reducing defensiveness. Effective affirmations do not deny reality or indulge in toxic positivity; rather, they remind the nervous system of your fundamental capability, resilience, and inherent worth.
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
