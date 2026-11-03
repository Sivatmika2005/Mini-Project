import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

const AFFIRMATIONS = [
  'I am allowed to take up space and rest.',
  'I am doing the best I can with what I have today.',
  'My feelings are valid, and they will pass.',
  'I choose to be kind to myself.',
  'Progress is still progress, no matter how small.',
];

export default function WellnessTips({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [latestCheckin, setLatestCheckin] = useState(null);
  const [activeTab, setActiveTab] = useState('breathing');

  useEffect(() => {
    async function loadLatest() {
      try {
        const res = await api.getLatestCheckin();
        setLatestCheckin(res.latest);
      } catch (e) {}
    }
    loadLatest();
  }, []);

  const stress = latestCheckin?.stress_level ?? 5;
  const energy = latestCheckin?.energy_level ?? 5;
  const mood = latestCheckin?.mood ?? 'Calm';
  const sleep = latestCheckin?.sleep_quality ?? 'Fair';

  return (
    <div className="app-layout">
      <Sidebar currentPage="wellness_tips" onNavigate={onNavigate} />

      <main className="main-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
          <h2>{t('wellness_title')}</h2>
          <button className="btn-secondary" onClick={() => onNavigate('dashboard')}>
            ← Dashboard
          </button>
        </div>
        <p className="aw-muted">{t('wellness_subtitle')}</p>

        {/* 1. Dynamic Recommendation Banner */}
        {latestCheckin ? (
          <div
            className="aw-card"
            style={{
              background: 'linear-gradient(135deg, rgba(236,235,255,0.7), rgba(233,249,240,0.8))',
              border: '1.5px solid rgba(124,124,235,0.25)',
              margin: '18px 0',
            }}
          >
            <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#7c7ceb', marginBottom: '4px' }}>
              🤖 Dynamic Recommendation for You Today
            </div>
            <div style={{ fontSize: '0.92rem', color: '#1a1a2e', lineHeight: 1.5, marginBottom: '10px' }}>
              Based on your latest check-in (<b>{mood}</b>, Stress: <b>{stress}/10</b>, Energy: <b>{energy}/10</b>, Sleep: <b>{sleep}</b>):
            </div>

            {stress >= 7 ? (
              <div className="alert-box alert-info" style={{ margin: 0 }}>
                ⚡ <strong>Stress Priority:</strong> Your stress level is elevated. We strongly recommend trying the{' '}
                <strong>Box Breathing (4-4-4-4)</strong> or <strong>5-4-3-2-1 Grounding</strong> tab right now.
              </div>
            ) : energy <= 4 ? (
              <div className="alert-box alert-info" style={{ margin: 0 }}>
                🔋 <strong>Energy Priority:</strong> You reported low energy. Try the <strong>3-Minute Meditation</strong> or
                check out the <strong>Sleep</strong> hygiene guide below.
              </div>
            ) : (
              <div className="alert-box alert-success" style={{ margin: 0 }}>
                ✨ <strong>Balance Priority:</strong> You are in a balanced mood state! Read through the{' '}
                <strong>Positive Affirmations</strong> to strengthen your mindset.
              </div>
            )}
          </div>
        ) : (
          <div className="alert-box alert-info" style={{ margin: '18px 0' }}>
            💡 <strong>Tip:</strong> Log a <strong>Daily Check-In</strong> to unlock customized daily recommendations tailored
            specifically to your stress and energy levels!
          </div>
        )}

        {/* 2. Wellness Category Tabs */}
        <div className="tabs-container" style={{ marginTop: '20px' }}>
          {[
            { id: 'breathing', label: '🫁 Breathing' },
            { id: 'meditation', label: '🧘 Meditation' },
            { id: 'grounding', label: '🖐️ Grounding' },
            { id: 'sleep', label: '🌙 Sleep' },
            { id: 'stress', label: '⚡ Stress Management' },
            { id: 'affirmations', label: '✨ Affirmations' },
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

        {/* Tab Content */}
        {activeTab === 'breathing' && (
          <div className="aw-card">
            <h4>Box Breathing Technique (4-4-4-4)</h4>
            <p style={{ lineHeight: '1.7', marginTop: '10px' }}>
              1. Breathe in slowly through your nose for <strong>4 seconds</strong>.<br />
              2. Hold your breath gently for <strong>4 seconds</strong>.<br />
              3. Breathe out slowly through your mouth for <strong>4 seconds</strong>.<br />
              4. Hold for <strong>4 seconds</strong> before breathing in again.<br /><br />
              Repeat for 4-6 cycles. This activates the vagus nerve and lowers heart rate.
            </p>
          </div>
        )}

        {activeTab === 'meditation' && (
          <div className="aw-card">
            <h4>3-Minute Reset Meditation</h4>
            <p style={{ lineHeight: '1.7', marginTop: '10px' }}>
              Find a comfortable posture and unclamp your jaw.<br /><br />
              • <strong>Minute 1:</strong> Simply observe your natural breath without attempting to change it.<br />
              • <strong>Minute 2:</strong> Scan your body from forehead to toes, releasing shoulder tension.<br />
              • <strong>Minute 3:</strong> Silently repeat a grounding phrase: <em>"I am present, safe, and capable."</em><br /><br />
              Gently open your eyes when ready.
            </p>
          </div>
        )}

        {activeTab === 'grounding' && (
          <div className="aw-card">
            <h4>5-4-3-2-1 Sensory Grounding</h4>
            <p style={{ lineHeight: '1.7', marginTop: '10px' }}>
              Acknowledge surroundings to pull focus away from anxious thoughts:<br />
              • <strong>5</strong> objects you can see around you<br />
              • <strong>4</strong> textures or objects you can touch<br />
              • <strong>3</strong> distinct sounds you can hear<br />
              • <strong>2</strong> scents you can smell<br />
              • <strong>1</strong> taste or positive thought
            </p>
          </div>
        )}

        {activeTab === 'sleep' && (
          <div className="aw-card">
            <h4>Sleep Hygiene Essentials</h4>
            <p style={{ lineHeight: '1.7', marginTop: '10px' }}>
              • <strong>Consistent Schedule:</strong> Go to bed and wake up at the same time every day.<br />
              • <strong>Digital Sunset:</strong> Turn off bright screens 30-45 minutes before bed.<br />
              • <strong>Cool &amp; Dark Room:</strong> Keep bedroom temperatures slightly cool (65-68°F / 18-20°C).<br />
              • <strong>4-7-8 Breathing:</strong> Inhale for 4s, hold for 7s, exhale for 8s to trigger parasympathetic relaxation.
            </p>
          </div>
        )}

        {activeTab === 'stress' && (
          <div className="aw-card">
            <h4>Practical Stress Management</h4>
            <p style={{ lineHeight: '1.7', marginTop: '10px' }}>
              • <strong>Brain Dump:</strong> Write out every pending worry on paper to clear working memory.<br />
              • <strong>Micro-Breaks:</strong> Stand up, stretch, and step away from work every 45-60 minutes.<br />
              • <strong>Physical Movement:</strong> Even a 10-minute brisk walk lowers cortisol and releases endorphins.<br />
              • <strong>Boundaries:</strong> Give yourself permission to say no to non-essential obligations.
            </p>
          </div>
        )}

        {activeTab === 'affirmations' && (
          <div className="aw-card">
            <h4>Daily Positive Affirmations</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '12px' }}>
              {AFFIRMATIONS.map((aff, i) => (
                <div
                  key={i}
                  style={{
                    padding: '12px 16px',
                    background: 'rgba(124,124,235,0.06)',
                    borderRadius: '12px',
                    fontWeight: 600,
                    color: 'var(--ink)',
                    borderLeft: '4px solid var(--accent)',
                  }}
                >
                  "{aff}"
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
