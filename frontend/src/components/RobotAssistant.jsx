import React, { useEffect, useState } from 'react';

/**
 * RobotAssistant Component
 * Provides interactive animations for the existing JPG robot asset:
 * - IDLE: Subtle floating/breathing and natural eye blinking
 * - LISTENING: Subtle glowing aura and attention tilt
 * - THINKING: Thinking tilt and soft antenna/visor pulse
 * - SPEAKING: Real-time talking mouth overlay + pulsing heart
 */
export default function RobotAssistant({ state = 'idle', isSpeaking = false }) {
  // Eye blinking timing
  const [isBlinking, setIsBlinking] = useState(false);

  useEffect(() => {
    // Natural intermittent blink every 3.5 to 5.5 seconds
    const interval = setInterval(() => {
      setIsBlinking(true);
      setTimeout(() => setIsBlinking(false), 160);
    }, 4200);

    return () => clearInterval(interval);
  }, []);

  const activeState = isSpeaking ? 'speaking' : state;

  return (
    <div
      className={`robot-container robot-${activeState}`}
      style={{
        position: 'relative',
        display: 'inline-block',
        width: '100%',
        maxWidth: '280px',
        margin: '0 auto',
        userSelect: 'none',
      }}
    >
      {/* Base JPG Image */}
      <img
        src="/assets/cute_wellness_robot.jpg"
        alt="AI Mental Wellness Robot"
        style={{
          width: '100%',
          display: 'block',
          borderRadius: '24px',
          boxShadow:
            activeState === 'listening'
              ? '0 16px 36px rgba(255, 107, 139, 0.4), 0 0 24px rgba(124, 124, 235, 0.5)'
              : activeState === 'thinking'
              ? '0 16px 36px rgba(99, 102, 241, 0.5), 0 0 20px rgba(99, 102, 241, 0.4)'
              : activeState === 'speaking'
              ? '0 16px 36px rgba(124, 124, 235, 0.45), 0 0 20px rgba(85, 235, 255, 0.35)'
              : '0 16px 32px rgba(124, 124, 235, 0.22)',
          transition: 'box-shadow 0.3s ease',
        }}
      />

      {/* --- Overlay 1: Natural Eye Blinking --- */}
      <div
        className="robot-eye-left"
        style={{
          position: 'absolute',
          top: '28.5%',
          left: '39.5%',
          width: '7.5%',
          height: '6.5%',
          backgroundColor: '#15172b',
          borderRadius: '50%',
          opacity: isBlinking && activeState !== 'listening' ? 0.95 : 0,
          transition: 'opacity 0.08s ease-in-out',
          pointerEvents: 'none',
        }}
      />
      <div
        className="robot-eye-right"
        style={{
          position: 'absolute',
          top: '27.5%',
          left: '53.5%',
          width: '7.5%',
          height: '6.5%',
          backgroundColor: '#15172b',
          borderRadius: '50%',
          opacity: isBlinking && activeState !== 'listening' ? 0.95 : 0,
          transition: 'opacity 0.08s ease-in-out',
          pointerEvents: 'none',
        }}
      />

      {/* --- Overlay 2: Pulsing Chest Heart Glow --- */}
      <div
        className={`robot-heart-glow ${activeState === 'speaking' || activeState === 'listening' ? 'heart-active' : ''}`}
        style={{
          position: 'absolute',
          top: '52.5%',
          left: '46.5%',
          width: '10.5%',
          height: '9%',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255, 105, 180, 0.65) 0%, rgba(236, 72, 153, 0) 75%)',
          pointerEvents: 'none',
          opacity: activeState === 'speaking' || activeState === 'listening' ? 0.9 : 0.25,
          animation:
            activeState === 'speaking' || activeState === 'listening'
              ? 'heartPulse 0.6s ease-in-out infinite alternate'
              : 'heartGentle 2.5s ease-in-out infinite alternate',
          transition: 'opacity 0.3s ease',
        }}
      />
    </div>
  );
}
