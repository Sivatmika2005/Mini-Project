import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

const MOODS = [
  { emoji: '😊', label: 'Happy' },
  { emoji: '😌', label: 'Calm' },
  { emoji: '😐', label: 'Neutral' },
  { emoji: '😔', label: 'Sad' },
  { emoji: '😰', label: 'Anxious' },
  { emoji: '😡', label: 'Angry' },
  { emoji: '😫', label: 'Stressed' },
];

const SLEEP_OPTIONS = ['Very Poor', 'Poor', 'Fair', 'Good', 'Excellent'];

export default function CheckIn({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [latestCheckin, setLatestCheckin] = useState(null);
  const [selectedMood, setSelectedMood] = useState(null);
  const [emotionNote, setEmotionNote] = useState('');
  const [stressLevel, setStressLevel] = useState(5);
  const [energyLevel, setEnergyLevel] = useState(5);
  const [sleepQuality, setSleepQuality] = useState('Fair');
  const [journalNote, setJournalNote] = useState('');

  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    async function loadLatest() {
      try {
        const res = await api.getLatestCheckin();
        setLatestCheckin(res.latest);
      } catch (e) {}
    }
    loadLatest();
  }, []);

  const todayStr = new Date().toISOString().slice(0, 10);
  const hasCheckedInToday = latestCheckin && (latestCheckin.created_at || '').startsWith(todayStr);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!selectedMood) {
      setErrorMsg('Please select a mood emoji above before submitting.');
      return;
    }

    setLoading(true);
    try {
      await api.addCheckin({
        mood: selectedMood,
        emotion_note: emotionNote,
        stress_level: stressLevel,
        energy_level: energyLevel,
        sleep_quality: sleepQuality,
        journal_note: journalNote,
      });

      const savedMood = selectedMood;
      setSelectedMood(null);
      setEmotionNote('');
      setJournalNote('');

      setSuccessMsg(
        `Check-in saved! Recorded mood: ${savedMood}. Great job taking care of yourself today! 🌿`
      );

      // Trigger Confetti Celebration
      confetti({
        particleCount: 50,
        spread: 60,
        origin: { y: 0.6 },
        colors: ['#7c7ceb', '#a5a6f6', '#b7f0d4', '#bcd9fb', '#f6c6dc'],
      });
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save check-in.');
    } finally {
      setLoading(false);
    }
  };

  const progressVal = selectedMood ? 100 : 50;

  return (
    <div className="app-layout">
      <Sidebar currentPage="checkin" onNavigate={onNavigate} />

      <main className="main-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
          <h2>{t('checkin_title')}</h2>
          <button className="btn-secondary" onClick={() => onNavigate('dashboard')}>
            ← Dashboard
          </button>
        </div>
        <p className="aw-muted">{t('checkin_subtitle')}</p>

        {hasCheckedInToday && !successMsg && (
          <div className="alert-box alert-info" style={{ marginTop: '14px' }}>
            🌱 <strong>You've already checked in today!</strong> Your mood was recorded as{' '}
            <strong>{latestCheckin.mood}</strong> (Stress: {latestCheckin.stress_level}/10).
            You can submit another check-in below to update your status.
          </div>
        )}

        {successMsg && <div className="alert-box alert-success" style={{ marginTop: '14px' }}>{successMsg}</div>}
        {errorMsg && <div className="alert-box alert-error" style={{ marginTop: '14px' }}>{errorMsg}</div>}

        {/* Progress bar */}
        <div style={{ marginTop: '16px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, marginBottom: '6px' }}>
            <span>{selectedMood ? 'Step 2/2: Detail Reflection' : 'Step 1/2: Select Your Mood'}</span>
            <span>{progressVal}%</span>
          </div>
          <div style={{ height: '8px', background: 'rgba(124,124,235,0.15)', borderRadius: '999px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${progressVal}%`,
                background: 'linear-gradient(90deg, #7c7ceb, #6669e5)',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
        </div>

        {/* Step 1: Mood Selector */}
        <div className="aw-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '8px' }}>
            <h3 style={{ fontSize: '1.15rem', margin: 0 }}>
              Step 1: How are you feeling today?
            </h3>
            <button
              type="button"
              className="btn-secondary"
              style={{
                fontSize: '0.82rem',
                fontWeight: 600,
                padding: '6px 14px',
                borderRadius: '16px',
                background: 'rgba(124, 124, 235, 0.08)',
                borderColor: 'rgba(124, 124, 235, 0.25)',
                color: 'var(--accent)',
                cursor: 'pointer',
              }}
              onClick={() => onNavigate('dashboard')}
            >
              📷 Detect via Vision &amp; Voice on Dashboard →
            </button>
          </div>

          <div className="grid-7">
            {MOODS.map((m) => {
              const isSelected = selectedMood === m.label;
              return (
                <button
                  key={m.label}
                  type="button"
                  className={isSelected ? 'btn-primary' : 'btn-secondary'}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    padding: '12px 8px',
                    borderRadius: '16px',
                    fontSize: '0.9rem',
                    gap: '4px',
                  }}
                  onClick={() => setSelectedMood(m.label)}
                >
                  <span style={{ fontSize: '1.8rem' }}>{m.emoji}</span>
                  <span style={{ fontWeight: 700 }}>{m.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Step 2: Reflections & Sliders Form */}
        <div className="aw-card" style={{ marginTop: '20px' }}>
          <h3 style={{ fontSize: '1.15rem', marginBottom: '16px' }}>
            Step 2: Reflections &amp; Levels
          </h3>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>What's contributing to this feeling? (optional)</label>
              <input
                type="text"
                value={emotionNote}
                onChange={(e) => setEmotionNote(e.target.value)}
                placeholder="Work, family, sleep, weather, etc."
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label>
                  Stress Level (1 = Very Low, 10 = Severe): <strong>{stressLevel}/10</strong>
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={stressLevel}
                  onChange={(e) => setStressLevel(Number(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--accent)' }}
                />
              </div>

              <div className="form-group">
                <label>
                  Energy Level (1 = Exhausted, 10 = High Energy): <strong>{energyLevel}/10</strong>
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={energyLevel}
                  onChange={(e) => setEnergyLevel(Number(e.target.value))}
                  style={{ width: '100%', accentColor: 'var(--accent)' }}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Sleep quality last night</label>
              <select
                value={sleepQuality}
                onChange={(e) => setSleepQuality(e.target.value)}
              >
                {SLEEP_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Journal note (optional)</label>
              <textarea
                rows="4"
                value={journalNote}
                onChange={(e) => setJournalNote(e.target.value)}
                placeholder="Anything on your mind you'd like to reflect on..."
              />
            </div>

            <button type="submit" className="btn-primary btn-full" disabled={loading}>
              {loading ? 'Saving Check-In...' : 'Submit Daily Check-In →'}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
