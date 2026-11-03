import React from 'react';
import Navbar from '../components/Navbar';
import { useAuth } from '../context/AuthContext';

export default function Landing({ onNavigate }) {
  const { user } = useAuth();

  const features = [
    { icon: '💬', title: 'AI Chat Support', desc: 'Talk it through with an empathetic AI companion, anytime you need support.' },
    { icon: '📈', title: 'Mood Tracking', desc: 'Log your mood, stress, and energy to spot patterns over time.' },
    { icon: '📔', title: 'Personal Journal', desc: 'Write freely and revisit your reflections whenever you like.' },
    { icon: '🌱', title: 'Wellness Tips', desc: 'Breathing, grounding, and mindfulness exercises on demand.' },
    { icon: '🔎', title: 'Progress Insights', desc: 'See non-diagnostic trends that help you understand yourself.' },
  ];

  const steps = [
    { num: '1', title: 'Create Account', desc: 'Sign up in seconds with just your email and password' },
    { num: '2', title: 'Daily Check-In', desc: 'Log your mood, stress levels, and thoughts each day' },
    { num: '3', title: 'Track Progress', desc: 'View insights and patterns to understand yourself better' },
  ];

  return (
    <div className="main-content no-sidebar">
      <Navbar onNavigate={onNavigate} currentPage="landing" />

      {/* Hero Section */}
      <section className="aw-hero">
        <div className="hero-left">
          <div className="hero-tagline">AI-Powered Mental Wellness</div>
          <h1>
            Your Mental<br />Wellness Companion
          </h1>
          <p className="subtitle">
            Track your emotions, understand your mood, and improve your mental well-being with AI-powered insights and support.
          </p>

          <div className="hero-buttons">
            <button
              className="btn-primary"
              onClick={() => onNavigate(user ? 'checkin' : 'login')}
            >
              Start Your Journey
            </button>
            <button
              className="btn-secondary"
              onClick={() => onNavigate('resources')}
            >
              Explore Features
            </button>
          </div>

          <div className="aw-badge">
            🔒 100% Private &amp; Secure • HIPAA-Compliant
          </div>
        </div>

        <div className="hero-right">
          <img
            src="/assets/robot/robot.svg"
            alt="AI wellness robot mascot"
            style={{ width: '100%', maxWidth: '380px', display: 'block', margin: '0 auto' }}
          />
        </div>
      </section>

      {/* Stats Section */}
      <section className="aw-stats-section">
        <div className="aw-stat-item">
          <div className="aw-stat-number">24/7</div>
          <div className="aw-stat-label">AI Support</div>
        </div>
        <div className="aw-stat-item">
          <div className="aw-stat-number">100%</div>
          <div className="aw-stat-label">Private</div>
        </div>
        <div className="aw-stat-item">
          <div className="aw-stat-number">Free</div>
          <div className="aw-stat-label">To Use</div>
        </div>
      </section>

      {/* Features Section */}
      <div style={{ textAlign: 'center', marginTop: '40px' }}>
        <div className="aw-section-title">Comprehensive Features</div>
        <p className="aw-muted" style={{ marginTop: '-4px', marginBottom: '24px' }}>
          Everything you need to check in with yourself, every day.
        </p>
      </div>

      <div className="features-grid">
        {features.map((f, i) => (
          <div className="aw-feature-card" key={i}>
            <div className="aw-feature-icon">{f.icon}</div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--ink)' }}>
              {f.title}
            </div>
            <div className="aw-muted" style={{ fontSize: '0.82rem', lineHeight: '1.45' }}>
              {f.desc}
            </div>
          </div>
        ))}
      </div>

      {/* How it works */}
      <div style={{ textAlign: 'center', marginTop: '48px' }}>
        <div className="aw-section-title">How It Works</div>
        <p className="aw-muted" style={{ marginTop: '-4px', marginBottom: '24px' }}>
          Get started in three simple steps
        </p>
      </div>

      <div className="steps-grid">
        {steps.map((s, i) => (
          <div className="aw-step-card" key={i}>
            <div className="aw-step-number">{s.num}</div>
            <div className="aw-step-title">{s.title}</div>
            <div className="aw-step-desc">{s.desc}</div>
          </div>
        ))}
      </div>

      {/* Medical Disclaimer Card */}
      <div className="aw-card" style={{ textAlign: 'center', marginTop: '36px', padding: '20px' }}>
        <div style={{ fontSize: '0.85rem' }} className="aw-muted">
          <strong>Important:</strong> AI Wellness is a supportive tool, not a medical service. It does not diagnose
          conditions or replace licensed therapists or doctors. If you're in crisis, please
          see the Resources page for professional help.
        </div>
      </div>
    </div>
  );
}
