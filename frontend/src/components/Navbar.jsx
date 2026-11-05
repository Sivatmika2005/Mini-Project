import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { useLanguage } from '../context/LanguageContext';

export default function Navbar({ onNavigate, currentPage }) {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const [popoverOpen, setPopoverOpen] = useState(false);
  const popoverRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        setPopoverOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const formatDisplayName = (name) => {
    if (!name) return 'Friend';
    const clean = String(name).replace(/[*_~`]/g, '').trim();
    return clean ? clean.charAt(0).toUpperCase() + clean.slice(1) : 'Friend';
  };

  const userDisplay = user ? formatDisplayName(user.username) : 'My Profile';

  const toggleTheme = () => {
    const nextTheme = theme === 'Light' ? 'Dark' : 'Light';
    setTheme(nextTheme);
  };

  return (
    <div className="navbar-container">
      <div className="logo" onClick={() => onNavigate('landing')}>
        🌿 AI <span>Wellness</span>
      </div>

      <div className="nav-actions">
        {user ? (
          <>
            <button
              className="nav-btn"
              onClick={() => onNavigate('landing')}
            >
              Home
            </button>
            <button
              className="nav-btn"
              onClick={() => onNavigate('resources')}
            >
              Resources
            </button>
            <button
              className="nav-btn"
              onClick={() => onNavigate('dashboard')}
            >
              Dashboard
            </button>

            <div className="popover-wrapper" ref={popoverRef}>
              <button
                className="nav-btn"
                onClick={() => setPopoverOpen(!popoverOpen)}
                style={{ fontWeight: 700 }}
              >
                👤 {userDisplay} ▼
              </button>

              {popoverOpen && (
                <div className="popover-menu">
                  <div style={{ fontWeight: 700, marginBottom: 2, color: 'var(--ink)' }}>
                    {userDisplay}
                  </div>
                  <div className="aw-muted" style={{ fontSize: '0.82rem', marginBottom: 6 }}>
                    Signed in
                  </div>
                  <hr style={{ margin: '6px 0', borderColor: 'rgba(124,124,235,0.15)' }} />

                  <button
                    className="sidebar-btn"
                    style={{ border: 'none', padding: '8px 12px', marginBottom: 2 }}
                    onClick={() => {
                      setPopoverOpen(false);
                      onNavigate('profile');
                    }}
                  >
                    👤 My Profile
                  </button>

                  <button
                    className="sidebar-btn"
                    style={{ border: 'none', padding: '8px 12px', marginBottom: 2 }}
                    onClick={() => {
                      setPopoverOpen(false);
                      onNavigate('profile');
                    }}
                  >
                    ✏️ Edit Name
                  </button>

                  <button
                    className="sidebar-btn"
                    style={{ border: 'none', padding: '8px 12px', marginBottom: 2 }}
                    onClick={() => {
                      toggleTheme();
                    }}
                  >
                    🎨 {theme === 'Light' ? '🌙 Dark Theme' : '☀️ Light Theme'}
                  </button>

                  <hr style={{ margin: '6px 0', borderColor: 'rgba(124,124,235,0.15)' }} />

                  <button
                    className="btn-primary btn-full"
                    style={{ fontSize: '0.88rem', padding: '8px 12px' }}
                    onClick={() => {
                      setPopoverOpen(false);
                      logout();
                      onNavigate('landing');
                    }}
                  >
                    🚪 Log Out
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            <button
              className="nav-btn"
              onClick={() => onNavigate('landing')}
            >
              Home
            </button>
            <button
              className="nav-btn"
              onClick={() => onNavigate('resources')}
            >
              Resources
            </button>
            <button
              className="nav-btn nav-btn-primary"
              onClick={() => onNavigate('login')}
            >
              Log In
            </button>
          </>
        )}
      </div>
    </div>
  );
}
