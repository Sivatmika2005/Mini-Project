import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

const CATEGORIES = ['General Reflection', 'Gratitude', 'Stress Release', 'Daily Check-In', 'Personal Growth'];
const MOOD_OPTIONS = ['😊 Happy', '😌 Calm', '😐 Neutral', '😔 Sad', '😰 Anxious', '😡 Angry', '😫 Stressed'];

export default function Journal({ onNavigate }) {
  const { user } = useAuth();
  const { t } = useLanguage();

  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  // New entry form
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('General Reflection');
  const [moodTag, setMoodTag] = useState('😌 Calm');
  const [content, setContent] = useState('');

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');

  // AI Summary
  const [aiSummary, setAiSummary] = useState('');
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryExpanded, setSummaryExpanded] = useState(false);

  // Status
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    loadJournals();
  }, []);

  const loadJournals = async () => {
    try {
      const res = await api.getJournals();
      setEntries(res.entries || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveEntry = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!content.trim()) {
      setErrorMsg('Please write something before saving your entry.');
      return;
    }

    try {
      await api.addJournal({
        title: title.trim() || `${category} Entry`,
        content: content.trim(),
        mood: moodTag,
        category: category,
      });

      setTitle('');
      setContent('');
      setSuccessMsg('Reflection entry saved successfully! 🌿');
      loadJournals();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to save entry.');
    }
  };

  const handleDeleteEntry = async (id) => {
    if (!window.confirm('Are you sure you want to delete this journal entry?')) return;
    try {
      await api.deleteJournal(id);
      setEntries((prev) => prev.filter((e) => e.id !== id));
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateSummary = async () => {
    setSummaryLoading(true);
    try {
      const res = await api.summarizeJournals();
      setAiSummary(res.summary);
      setSummaryExpanded(true);
    } catch (e) {
      console.error(e);
    } finally {
      setSummaryLoading(false);
    }
  };

  const filteredEntries = entries.filter((e) => {
    const matchesSearch =
      !searchQuery.trim() ||
      (e.title || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
      (e.content || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCat = selectedCategory === 'All Categories' || e.category === selectedCategory;
    return matchesSearch && matchesCat;
  });

  return (
    <div className="app-layout">
      <Sidebar currentPage="journal" onNavigate={onNavigate} />

      <main className="main-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
          <h2>{t('journal_title')}</h2>
          <button className="btn-secondary" onClick={() => onNavigate('dashboard')}>
            ← Dashboard
          </button>
        </div>
        <p className="aw-muted">{t('journal_subtitle')}</p>

        {successMsg && <div className="alert-box alert-success" style={{ marginTop: '14px' }}>{successMsg}</div>}
        {errorMsg && <div className="alert-box alert-error" style={{ marginTop: '14px' }}>{errorMsg}</div>}

        {/* 1. New Entry Form Card */}
        <div className="aw-card" style={{ marginTop: '16px' }}>
          <div className="aw-section-title" style={{ fontSize: '1.25rem' }}>
            Write New Reflection
          </div>

          <form onSubmit={handleSaveEntry} style={{ marginTop: '16px' }}>
            <div className="grid-2">
              <div className="form-group">
                <label>Title (optional)</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Evening Reflections"
                />
              </div>

              <div className="form-group">
                <label>Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  {CATEGORIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Mood Tag</label>
              <select value={moodTag} onChange={(e) => setMoodTag(e.target.value)}>
                {MOOD_OPTIONS.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>What's on your mind today?</label>
              <textarea
                rows="5"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Write freely without judgment..."
                required
              />
            </div>

            <button type="submit" className="btn-primary btn-full">
              Save Reflection Entry →
            </button>
          </form>
        </div>

        {/* 2. Journal History & Filters */}
        <div style={{ marginTop: '32px' }}>
          <h3>Your Journal History</h3>

          <div className="grid-2" style={{ marginTop: '14px' }}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="🔎 Search entries by title or keyword..."
            />

            <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)}>
              <option value="All Categories">All Categories</option>
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          {/* AI Summary Banner */}
          {entries.length >= 2 && (
            <div className="aw-card" style={{ marginTop: '18px', background: 'rgba(124,124,235,0.06)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ fontWeight: 700, color: 'var(--accent)' }}>
                  ✨ AI Pattern Insights &amp; Reflection Summary
                </div>
                <button className="btn-secondary" onClick={handleGenerateSummary} disabled={summaryLoading}>
                  {summaryLoading ? 'Analyzing...' : 'Analyze Recent Journals'}
                </button>
              </div>

              {aiSummary && (
                <div
                  style={{
                    marginTop: '14px',
                    padding: '14px',
                    background: 'white',
                    borderRadius: '12px',
                    lineHeight: '1.6',
                    fontSize: '0.92rem',
                    border: '1px solid rgba(124,124,235,0.18)',
                  }}
                >
                  <div style={{ fontWeight: 700, marginBottom: '6px', color: 'var(--accent-deep)' }}>
                    AI Summary Insights:
                  </div>
                  <div style={{ whiteSpace: 'pre-line' }}>{aiSummary}</div>
                </div>
              )}
            </div>
          )}

          {/* Entries list */}
          <div style={{ marginTop: '18px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {filteredEntries.length === 0 ? (
              <div className="aw-card" style={{ textAlign: 'center', padding: '32px' }}>
                <p className="aw-muted">No matching journal entries found.</p>
              </div>
            ) : (
              filteredEntries.map((e) => (
                <div key={e.id} className="aw-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h4 style={{ margin: '0 0 6px 0', fontSize: '1.1rem' }}>{e.title}</h4>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '10px' }}>
                        <span className="aw-pill">{e.category || 'General'}</span>
                        {e.mood && <span className="aw-pill">{e.mood}</span>}
                        {e.emotion && (
                          <span className="aw-pill" style={{ background: 'rgba(183, 240, 212, 0.4)' }}>
                            Detected Emotion: {e.emotion}
                          </span>
                        )}
                        <span className="aw-muted" style={{ fontSize: '0.8rem', alignSelf: 'center' }}>
                          {(e.created_at || '').slice(0, 16).replace('T', ' ')}
                        </span>
                      </div>
                    </div>

                    <button
                      style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.1rem', opacity: 0.7 }}
                      title="Delete Entry"
                      onClick={() => handleDeleteEntry(e.id)}
                    >
                      🗑️
                    </button>
                  </div>

                  <p style={{ lineHeight: '1.6', fontSize: '0.94rem', whiteSpace: 'pre-line' }}>
                    {e.content}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
