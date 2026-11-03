import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { api } from '../api/client';

export default function Login({ onNavigate }) {
  const { login, register, user } = useAuth();
  const { t } = useLanguage();

  const [tab, setTab] = useState('login'); // 'login' | 'signup'
  const [showForgotPass, setShowForgotPass] = useState(false);

  // Login form
  const [loginIdentifier, setLoginIdentifier] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form
  const [regUsername, setRegUsername] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');
  const [regConfirmPassword, setRegConfirmPassword] = useState('');

  // Forgot password form
  const [resetEmail, setResetEmail] = useState('');

  // Reset password action code (oobCode)
  const [oobCode, setOobCode] = useState('');
  const [mode, setMode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');

  // UI state
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  useEffect(() => {
    if (user) {
      onNavigate('dashboard');
    }
  }, [user, onNavigate]);

  useEffect(() => {
    // Check URL parameters for oobCode / mode
    const params = new URLSearchParams(window.location.search);
    const code = params.get('oobCode');
    const m = params.get('mode');
    if (code) setOobCode(code);
    if (m) setMode(m);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!loginIdentifier.trim() || !loginPassword) {
      setErrorMsg('Please enter both username/email and password.');
      return;
    }

    setLoading(true);
    try {
      await login(loginIdentifier.trim(), loginPassword);
      setSuccessMsg('Welcome back! Redirecting to Dashboard...');
      setTimeout(() => onNavigate('dashboard'), 400);
    } catch (err) {
      setErrorMsg(err.message || 'Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!regUsername.trim() || regUsername.trim().length < 3) {
      setErrorMsg('Username must be at least 3 characters.');
      return;
    }
    if (!regEmail.trim()) {
      setErrorMsg('Please enter a valid email address.');
      return;
    }
    if (!regPassword || regPassword.length < 6) {
      setErrorMsg('Password must be at least 6 characters.');
      return;
    }
    if (regPassword !== regConfirmPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await register(regUsername.trim(), regEmail.trim(), regPassword);
      setSuccessMsg('Account created successfully! Redirecting...');
      setTimeout(() => onNavigate('dashboard'), 500);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to create account.');
    } finally {
      setLoading(false);
    }
  };

  const handleSendResetEmail = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!resetEmail.trim()) {
      setErrorMsg('Please enter your registered email address.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.resetPasswordRequest(resetEmail.trim());
      setSuccessMsg(res.message || 'Password reset link sent!');
    } catch (err) {
      setErrorMsg(err.message || 'Failed to process reset request.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReset = async (e) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    if (!newPassword || newPassword.length < 6) {
      setErrorMsg('Password must be at least 6 characters.');
      return;
    }
    if (newPassword !== confirmNewPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.confirmPasswordReset(oobCode, newPassword);
      setSuccessMsg(res.message || 'Password reset successfully! You can now log in.');
      setOobCode('');
      setMode('');
    } catch (err) {
      setErrorMsg(err.message || 'Invalid or expired reset link.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-content no-sidebar">
      <Navbar onNavigate={onNavigate} currentPage="login" />

      <button
        className="btn-secondary"
        style={{ marginBottom: '16px' }}
        onClick={() => onNavigate('landing')}
      >
        ← Back to Home
      </button>

      <div style={{ maxWidth: '480px', margin: '0 auto' }}>
        {/* Header Card */}
        <div className="aw-login-card">
          <div style={{ fontSize: '2.2rem', marginBottom: '4px' }}>🌿</div>
          <h2 style={{ margin: '0 0 4px 0', fontSize: '1.55rem', fontWeight: 800 }}>
            {t('app_title')}
          </h2>
          <p className="aw-muted" style={{ margin: 0, fontSize: '0.88rem' }}>
            Welcome back! Please sign in to your account.
          </p>
        </div>

        {/* Notifications */}
        {errorMsg && <div className="alert-box alert-error">{errorMsg}</div>}
        {successMsg && <div className="alert-box alert-success">{successMsg}</div>}

        {/* Action Code Reset Mode */}
        {oobCode || mode === 'resetPassword' ? (
          <div className="aw-card">
            <h4 style={{ marginBottom: '4px' }}>Set New Password 🔑</h4>
            <p className="aw-muted" style={{ fontSize: '0.85rem', marginBottom: '16px' }}>
              Please enter your new password below. It will be securely updated in Firebase Authentication.
            </p>

            <form onSubmit={handleConfirmReset}>
              <div className="form-group">
                <label>New Password (6+ chars)</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password"
                  required
                />
              </div>

              <div className="form-group">
                <label>Confirm New Password</label>
                <input
                  type="password"
                  value={confirmNewPassword}
                  onChange={(e) => setConfirmNewPassword(e.target.value)}
                  placeholder="Confirm new password"
                  required
                />
              </div>

              <button type="submit" className="btn-primary btn-full" disabled={loading}>
                {loading ? 'Updating password...' : 'Update Password →'}
              </button>
            </form>

            <div style={{ marginTop: '14px' }}>
              <button
                className="btn-secondary btn-full"
                onClick={() => {
                  setOobCode('');
                  setMode('');
                  setShowForgotPass(false);
                }}
              >
                ← Return to Log In
              </button>
            </div>
          </div>
        ) : showForgotPass ? (
          <div className="aw-card">
            <h4 style={{ marginBottom: '4px' }}>Reset Your Password 🔑</h4>
            <p className="aw-muted" style={{ fontSize: '0.85rem', marginBottom: '16px' }}>
              Enter your registered email address below to receive a secure password reset link.
            </p>

            <form onSubmit={handleSendResetEmail}>
              <div className="form-group">
                <label>Registered Email Address</label>
                <input
                  type="email"
                  value={resetEmail}
                  onChange={(e) => setResetEmail(e.target.value)}
                  placeholder="name@example.com"
                  required
                />
              </div>

              <button type="submit" className="btn-primary btn-full" disabled={loading}>
                {loading ? 'Processing...' : 'Send Reset Link →'}
              </button>
            </form>

            <div style={{ marginTop: '14px' }}>
              <button
                className="btn-secondary btn-full"
                onClick={() => setShowForgotPass(false)}
              >
                ← Back to Log In
              </button>
            </div>
          </div>
        ) : (
          <div className="aw-card">
            {/* Tabs */}
            <div className="tabs-container" style={{ justifyContent: 'center' }}>
              <button
                className={`tab-btn ${tab === 'login' ? 'active' : ''}`}
                onClick={() => {
                  setTab('login');
                  setErrorMsg('');
                }}
              >
                🔒 Log In
              </button>
              <button
                className={`tab-btn ${tab === 'signup' ? 'active' : ''}`}
                onClick={() => {
                  setTab('signup');
                  setErrorMsg('');
                }}
              >
                🌱 Create Account
              </button>
            </div>

            {tab === 'login' ? (
              <form onSubmit={handleLogin}>
                <div className="form-group">
                  <label>Username or Email</label>
                  <input
                    type="text"
                    value={loginIdentifier}
                    onChange={(e) => setLoginIdentifier(e.target.value)}
                    placeholder="e.g. sivat or name@gmail.com"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Password</label>
                  <input
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="Enter password"
                    required
                  />
                </div>

                <div style={{ textAlign: 'right', marginBottom: '12px' }}>
                  <button
                    type="button"
                    style={{
                      background: 'none',
                      border: 'none',
                      color: 'var(--accent)',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                    }}
                    onClick={() => setShowForgotPass(true)}
                  >
                    Forgot Password?
                  </button>
                </div>

                <button type="submit" className="btn-primary btn-full" disabled={loading}>
                  {loading ? 'Authenticating...' : 'Log In to Account →'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister}>
                <div className="form-group">
                  <label>Username</label>
                  <input
                    type="text"
                    value={regUsername}
                    onChange={(e) => setRegUsername(e.target.value)}
                    placeholder="e.g. sivat"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Email Address</label>
                  <input
                    type="email"
                    value={regEmail}
                    onChange={(e) => setRegEmail(e.target.value)}
                    placeholder="name@example.com"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Password (6+ characters)</label>
                  <input
                    type="password"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="Create password"
                    required
                  />
                </div>

                <div className="form-group">
                  <label>Confirm Password</label>
                  <input
                    type="password"
                    value={regConfirmPassword}
                    onChange={(e) => setRegConfirmPassword(e.target.value)}
                    placeholder="Confirm password"
                    required
                  />
                </div>

                <button type="submit" className="btn-primary btn-full" disabled={loading}>
                  {loading ? 'Creating account...' : 'Create Account →'}
                </button>
              </form>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
