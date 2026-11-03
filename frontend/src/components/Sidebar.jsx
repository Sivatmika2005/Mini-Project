import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';

export default function Sidebar({ currentPage, onNavigate }) {
  const { user, logout } = useAuth();
  const { t } = useLanguage();

  const formatGreeting = (name) => {
    if (!name) return 'Hi, Friend 👋';
    const clean = String(name).replace(/[*_~`]/g, '').trim();
    const formatted = clean ? clean.charAt(0).toUpperCase() + clean.slice(1) : 'Friend';
    return `Hi, ${formatted} 👋`;
  };

  const menu = [
    { id: 'dashboard', label: t('nav_dashboard') },
    { id: 'checkin', label: t('nav_checkin') },
    { id: 'chat', label: t('nav_chat') },
    { id: 'journal', label: t('nav_journal') },
    { id: 'wellness_tips', label: t('nav_wellness_tips') },
    { id: 'insights', label: t('nav_insights') },
    { id: 'resources', label: t('nav_resources') },
    { id: 'professional_support', label: t('nav_professional_support') },
  ];

  return (
    <aside className="sidebar-container">
      <div className="sidebar-title">{t('app_title')}</div>

      {user && (
        <div className="sidebar-greeting-row">
          <div className="sidebar-greeting">{formatGreeting(user.username)}</div>
          <button
            className="btn-secondary"
            style={{ padding: '4px 8px', height: '32px', minWidth: '32px' }}
            title={t('nav_profile')}
            onClick={() => onNavigate('profile')}
          >
            ⚙️
          </button>
        </div>
      )}

      <hr style={{ margin: '8px 0 14px 0', borderColor: 'rgba(124,124,235,0.15)' }} />

      <nav style={{ flex: 1 }}>
        {menu.map((item) => (
          <button
            key={item.id}
            className={`sidebar-btn ${currentPage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <hr style={{ margin: '14px 0 10px 0', borderColor: 'rgba(124,124,235,0.15)' }} />

      <button
        className="sidebar-btn"
        style={{ color: 'var(--ink)' }}
        onClick={() => {
          logout();
          onNavigate('landing');
        }}
      >
        {t('nav_logout')}
      </button>
    </aside>
  );
}
