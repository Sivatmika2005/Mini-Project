import React, { useState } from 'react';
import Sidebar from '../components/Sidebar';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

export default function Profile({ onNavigate }) {
  const { user, updateUser } = useAuth();
  const { theme, setTheme } = useTheme();
  const { language, setLanguage, t } = useLanguage();

  const [editName, setEditName] = useState(user ? user.username : '');
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  const handleUpdateName = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!editName.trim()) {
      setErrorMsg('Name cannot be empty.');
      return;
    }

    setLoading(true);
    try {
      await api.updateName(editName.trim());
      updateUser({ username: editName.trim() });
      setSuccessMsg('Display name updated successfully! 🌿');
    } catch (err) {
      setErrorMsg(err.message || 'Failed to update name.');
    } finally {
      setLoading(false);
    }
  };

  const handleThemeChange = async (newTheme) => {
    setTheme(newTheme);
    try {
      await api.saveSettings({ theme: newTheme, language });
    } catch (e) {}
  };

  const handleLanguageChange = async (newLang) => {
    setLanguage(newLang);
    try {
      await api.saveSettings({ theme, language: newLang });
    } catch (e) {}
  };

  const formatDisplayName = (name) => {
    if (!name) return 'Friend';
    const clean = String(name).replace(/[*_~`]/g, '').trim();
    return clean ? clean.charAt(0).toUpperCase() + clean.slice(1) : 'Friend';
  };

  return (
    <div className="app-layout">
      <Sidebar currentPage="profile" onNavigate={onNavigate} />

      <main className="main-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
          <h2>{t('profile_title')}</h2>
          <button className="btn-secondary" onClick={() => onNavigate('dashboard')}>
            {t('back_to_dashboard')}
          </button>
        </div>
        <p className="aw-muted">{t('profile_subtitle')}</p>

        {successMsg && <div className="alert-box alert-success" style={{ marginTop: '14px' }}>{successMsg}</div>}
        {errorMsg && <div className="alert-box alert-error" style={{ marginTop: '14px' }}>{errorMsg}</div>}

        <div className="grid-2" style={{ marginTop: '20px', gap: '24px' }}>
          {/* Left Column */}
          <div>
            {/* Profile Summary Card */}
            <div className="aw-card" style={{ textAlign: 'center', padding: '30px 20px' }}>
              <div style={{ fontSize: '4rem', marginBottom: '12px' }}>🌿</div>
              <h3 style={{ margin: '0 0 6px 0' }}>{formatDisplayName(user?.username)}</h3>
              <p className="aw-muted" style={{ margin: 0 }}>
                ✉️ {user?.email}
              </p>
              <div
                style={{
                  marginTop: '12px',
                  display: 'inline-block',
                  padding: '4px 14px',
                  background: 'rgba(124,124,235,0.12)',
                  borderRadius: '999px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  color: 'var(--accent)',
                }}
              >
                {t('user_id_label')}: #{user?.id || '1'}
              </div>
            </div>

            {/* Edit Display Name Card */}
            <div className="aw-card" style={{ marginTop: '20px' }}>
              <div className="aw-section-title" style={{ fontSize: '1.15rem' }}>
                {t('edit_display_name')}
              </div>

              <form onSubmit={handleUpdateName} style={{ marginTop: '14px' }}>
                <div className="form-group">
                  <label>{t('display_name_label')}</label>
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    required
                  />
                </div>

                <button type="submit" className="btn-primary btn-full" disabled={loading}>
                  {loading ? 'Saving...' : t('save_display_name')}
                </button>
              </form>
            </div>
          </div>

          {/* Right Column */}
          <div>
            {/* Theme Settings Card */}
            <div className="aw-card">
              <div className="aw-section-title" style={{ fontSize: '1.15rem' }}>
                {t('visual_theme_settings')}
              </div>
              <p className="aw-muted" style={{ fontSize: '0.88rem', margin: '4px 0 16px 0' }}>
                {t('theme_subtitle')}
              </p>

              <div className="form-group">
                <label>{t('select_theme_label')}</label>
                <select value={theme} onChange={(e) => handleThemeChange(e.target.value)}>
                  <option value="Light">Light ☀️</option>
                  <option value="Soft Pastel">Soft Pastel 🌸</option>
                  <option value="Ocean Breeze">Ocean Breeze 🌊</option>
                  <option value="Dark">Midnight Dark 🌙</option>
                </select>
              </div>

              <hr style={{ margin: '24px 0', borderColor: 'rgba(124,124,235,0.15)' }} />

              {/* Language Preferences Card */}
              <div className="aw-section-title" style={{ fontSize: '1.15rem' }}>
                {t('language_preferences')}
              </div>
              <p className="aw-muted" style={{ fontSize: '0.88rem', margin: '4px 0 16px 0' }}>
                {t('lang_subtitle')}
              </p>

              <div className="form-group">
                <label>{t('select_lang_label')}</label>
                <select value={language} onChange={(e) => handleLanguageChange(e.target.value)}>
                  <option value="English">English 🇺🇸</option>
                  <option value="Tamil">தமிழ் (Tamil) 🇮🇳</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
