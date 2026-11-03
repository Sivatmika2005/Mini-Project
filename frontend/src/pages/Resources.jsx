import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

const HELPLINES = [
  { title: '🚨 Emergency Services (US)', desc: 'Call 911 for immediate danger or medical emergencies.', action: 'Call 911' },
  { title: '📞 988 Suicide & Crisis Lifeline (US & Canada)', desc: 'Call or Text 988 (Available 24/7, Free & Confidential).', action: 'Call/Text 988' },
  { title: '💬 Crisis Text Line', desc: 'Text HOME to 741741 to connect with a crisis counselor 24/7.', action: 'Text 741741' },
  { title: '🇮🇳 Vandrevala Foundation (India)', desc: '24/7 Mental Health Helpline: +91 9999 666 555.', action: 'Call +91 9999666555' },
  { title: '🇮🇳 NIMHANS Toll-Free (India)', desc: 'Toll-free 24/7 helpline: 080-46110007.', action: 'Call 080-46110007' },
  { title: '🇬🇧 NHS Mental Health (UK)', desc: 'Call 111 for urgent mental health support.', action: 'Call 111' },
  { title: '🌐 International Helplines', desc: 'Find support in your country at https://findahelpline.com/', action: 'findahelpline.com' },
];

const ARTICLES = [
  {
    title: 'Understanding Stress vs Anxiety',
    body: 'Anxiety is a sustained emotional response to perceived threats, while stress is usually triggered by immediate external pressure. Learning to distinguish them helps tailor self-care.',
  },
  {
    title: 'Navigating Burnout Recovery',
    body: 'Burnout develops gradually through chronic overwork. Recovery requires clear boundaries, adequate physical sleep, digital detoxification, and reconnecting with hobbies.',
  },
  {
    title: 'Cognitive Reframing Techniques',
    body: 'Identify automatic negative thoughts (ANTs). Ask yourself: Is this thought based on factual evidence or emotion? What is a more balanced perspective?',
  },
  {
    title: 'Sleep Hygiene & Circadian Rhythms',
    body: 'Consistent sleep schedules anchor your body clock. Keep your room dark, avoid screens 45 minutes before sleep, and view morning sunlight within 30 minutes of waking.',
  },
];

const FAQS = [
  {
    q: 'Is my check-in and chat data private?',
    a: 'Yes. All check-ins and journal entries are securely stored in your personal database session. We do not sell or transmit your personal reflections.',
  },
  {
    q: 'Can AI Wellness diagnose mental health conditions?',
    a: 'No. AI Wellness is a supportive self-care tool, not clinical healthcare. It cannot diagnose illnesses or prescribe treatments.',
  },
  {
    q: 'What should I do in an emergency?',
    a: 'Please use the 24/7 emergency helplines listed in the Helplines tab or dial your local emergency number (like 911 or 112) immediately.',
  },
];

export default function Resources({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [activeTab, setActiveTab] = useState('helplines');
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedArticles, setExpandedArticles] = useState({});
  const [expandedFaqs, setExpandedFaqs] = useState({});

  const toggleArticle = (i) => {
    setExpandedArticles((prev) => ({ ...prev, [i]: !prev[i] }));
  };

  const toggleFaq = (i) => {
    setExpandedFaqs((prev) => ({ ...prev, [i]: !prev[i] }));
  };

  const query = searchQuery.toLowerCase();

  const filteredHelplines = HELPLINES.filter(
    (h) => !query || h.title.toLowerCase().includes(query) || h.desc.toLowerCase().includes(query)
  );

  const filteredArticles = ARTICLES.filter(
    (a) => !query || a.title.toLowerCase().includes(query) || a.body.toLowerCase().includes(query)
  );

  const filteredFaqs = FAQS.filter(
    (f) => !query || f.q.toLowerCase().includes(query) || f.a.toLowerCase().includes(query)
  );

  const content = (
    <main className={user ? 'main-content' : 'main-content no-sidebar'}>
      {!user && <Navbar onNavigate={onNavigate} currentPage="resources" />}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
        <h2>{t('resources_title')}</h2>
        <button
          className="btn-secondary"
          onClick={() => onNavigate(user ? 'dashboard' : 'landing')}
        >
          {user ? '← Back to Dashboard' : '← Back to Home'}
        </button>
      </div>
      <p className="aw-muted">{t('resources_subtitle')}</p>

      {/* Red Urgent Disclaimer */}
      <div
        className="aw-card"
        style={{
          borderLeft: '5px solid #ff6b8b',
          background: '#fff5f6',
          margin: '18px 0',
          padding: '16px',
        }}
      >
        <b style={{ color: '#d63031', fontSize: '1.05rem' }}>⚠️ Immediate Crisis Notice:</b>
        <br />
        AI Wellness Companion is an automated self-help tool, <b>not clinical healthcare or medical treatment</b>.
        If you or someone you know is in immediate danger or experiencing thoughts of self-harm, please contact 24/7 emergency services or a crisis helpline immediately.
      </div>

      {/* Search Bar */}
      <div style={{ margin: '18px 0' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="🔎 Search Resources by topic: anxiety, helplines, sleep, depression..."
        />
      </div>

      {/* Tabs */}
      <div className="tabs-container">
        {[
          { id: 'helplines', label: '🚨 24/7 Crisis Helplines' },
          { id: 'articles', label: '📚 Articles & Guides' },
          { id: 'mindfulness', label: '🧘 Mindfulness & Breathing' },
          { id: 'faqs', label: '❓ Frequently Asked Questions' },
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

      {/* Tab: Helplines */}
      {activeTab === 'helplines' && (
        <div>
          <h3>Emergency 24/7 Helplines</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '14px' }}>
            {filteredHelplines.map((h, i) => (
              <div
                key={i}
                className="aw-card"
                style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '1.05rem', color: 'var(--ink)' }}>
                    {h.title}
                  </div>
                  <div className="aw-muted" style={{ fontSize: '0.9rem', marginTop: '4px' }}>
                    {h.desc}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Articles */}
      {activeTab === 'articles' && (
        <div>
          <h3>Mental Health Articles &amp; Psychoeducation</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '14px' }}>
            {filteredArticles.map((a, i) => (
              <div key={i} className="aw-card">
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    fontWeight: 700,
                  }}
                  onClick={() => toggleArticle(i)}
                >
                  <span>📖 {a.title}</span>
                  <span>{expandedArticles[i] ? '▲' : '▼'}</span>
                </div>
                {expandedArticles[i] && (
                  <p style={{ marginTop: '12px', lineHeight: '1.6', fontSize: '0.92rem' }}>
                    {a.body}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab: Mindfulness */}
      {activeTab === 'mindfulness' && (
        <div className="aw-card">
          <h4>4-7-8 Parasympathetic Breathing Exercise</h4>
          <p className="aw-muted" style={{ lineHeight: '1.7', marginTop: '10px' }}>
            1. Exhale completely through your mouth.<br />
            2. Inhale quietly through your nose for <b>4 seconds</b>.<br />
            3. Hold your breath for <b>7 seconds</b>.<br />
            4. Exhale audibly through your mouth for <b>8 seconds</b>.<br /><br />
            Repeat for 4 complete cycles.
          </p>
        </div>
      )}

      {/* Tab: FAQs */}
      {activeTab === 'faqs' && (
        <div>
          <h3>Frequently Asked Questions</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '14px' }}>
            {filteredFaqs.map((f, i) => (
              <div key={i} className="aw-card">
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    cursor: 'pointer',
                    fontWeight: 700,
                  }}
                  onClick={() => toggleFaq(i)}
                >
                  <span>❓ {f.q}</span>
                  <span>{expandedFaqs[i] ? '▲' : '▼'}</span>
                </div>
                {expandedFaqs[i] && (
                  <p style={{ marginTop: '12px', lineHeight: '1.6', fontSize: '0.92rem' }}>
                    {f.a}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </main>
  );

  return user ? (
    <div className="app-layout">
      <Sidebar currentPage="resources" onNavigate={onNavigate} />
      {content}
    </div>
  ) : (
    content
  );
}
