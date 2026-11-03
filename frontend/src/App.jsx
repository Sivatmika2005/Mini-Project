import React, { useState, useEffect } from 'react';
import { useAuth } from './context/AuthContext';

import Landing from './pages/Landing';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CheckIn from './pages/CheckIn';
import Chat from './pages/Chat';
import Journal from './pages/Journal';
import WellnessTips from './pages/WellnessTips';
import Insights from './pages/Insights';
import Resources from './pages/Resources';
import ProfessionalSupport from './pages/ProfessionalSupport';
import Profile from './pages/Profile';

export default function App() {
  const { user, loading } = useAuth();
  const [page, setPage] = useState('landing');

  useEffect(() => {
    // Handle URL parameters on initial load
    const params = new URLSearchParams(window.location.search);
    if (params.get('oobCode') || params.get('mode') === 'resetPassword') {
      setPage('login');
      return;
    }

    if (!loading) {
      if (user && page === 'landing') {
        // stay or navigate
      }
    }
  }, [user, loading]);

  const handleNavigate = (targetPage) => {
    window.scrollTo(0, 0);
    setPage(targetPage);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column' }}>
        <div style={{ fontSize: '3rem', marginBottom: '12px' }}>🌿</div>
        <div style={{ fontWeight: 600, color: 'var(--ink)' }}>Loading AI Mental Wellness Companion...</div>
      </div>
    );
  }

  switch (page) {
    case 'landing':
      return <Landing onNavigate={handleNavigate} />;
    case 'login':
      return <Login onNavigate={handleNavigate} />;
    case 'dashboard':
      return <Dashboard onNavigate={handleNavigate} />;
    case 'checkin':
      return <CheckIn onNavigate={handleNavigate} />;
    case 'chat':
      return <Chat onNavigate={handleNavigate} />;
    case 'journal':
      return <Journal onNavigate={handleNavigate} />;
    case 'wellness_tips':
      return <WellnessTips onNavigate={handleNavigate} />;
    case 'insights':
      return <Insights onNavigate={handleNavigate} />;
    case 'resources':
      return <Resources onNavigate={handleNavigate} />;
    case 'professional_support':
      return <ProfessionalSupport onNavigate={handleNavigate} />;
    case 'profile':
      return <Profile onNavigate={handleNavigate} />;
    default:
      return <Landing onNavigate={handleNavigate} />;
  }
}
