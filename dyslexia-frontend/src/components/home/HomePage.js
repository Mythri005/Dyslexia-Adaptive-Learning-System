import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import LoginModal from '../auth/LoginForm';
import SignupModal from '../auth/SignupForm';
import './HomePage.css';

const HomePage = () => {
  const navigate = useNavigate();
  const { currentUser } = useUser();
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  useEffect(() => {
    if (currentUser) {
      navigate('/modules');
    }
  }, [currentUser, navigate]);

  const handleDemoAccess = () => {
    const demoUser = {
      id: `demo_${Date.now()}`,
      name: 'Guest User',
      age: 10,
      email: 'guest@example.com',
      isDemo: true
    };
    localStorage.setItem('dyslexia_currentUser', JSON.stringify(demoUser));
    window.location.reload();
  };

  return (
    <div className="home-page">

      {/* NAVBAR */}
      <nav className="nav">
        <div className="nav-container">

          <div className="nav-logo">
            <div className="logo-icon">
              <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="16" cy="16" r="14" stroke="#6366f1" strokeWidth="2.5"/>
                <circle cx="16" cy="16" r="8" stroke="#ec4899" strokeWidth="2.5"/>
                <circle cx="16" cy="16" r="3" fill="#f97316"/>
              </svg>
            </div>
            <span className="logo-text">Dyslexia Adaptive Learning</span>
          </div>

          <div className="nav-links">
            <Link to="/features">Features</Link>
            <Link to="/how-it-works">How It Works</Link>
            <Link to="/technology">Technology</Link>
          </div>

          <div className="nav-buttons">
            <button className="nav-btn primary" onClick={() => setShowLogin(true)}>
              Sign In
            </button>
          </div>

        </div>
      </nav>

      {/* HERO */}
      <div className="hero-section">
        <div className="hero-glow" />
        <div className="main-container">

          {/* LEFT */}
          <div className="hero-column">
            <h1 className="hero-title">
              AI-Powered Adaptive<br />Learning Platform
            </h1>
            <p className="hero-subtitle">
              Personalized education tailored for children with{' '}
              <span className="highlight-dyslexia">dyslexia</span>
            </p>
            <p className="hero-description">
              An intelligent adaptive learning system powered by AI,
              computer vision, and feedback to help
              children with dyslexia improve their math, spelling, and reading skills.
            </p>
            <div className="hero-buttons">
              <button className="btn-primary" onClick={() => setShowSignup(true)}>
                Create Free Account
              </button>
              <button className="btn-secondary" onClick={handleDemoAccess}>
                Try Demo
              </button>
            </div>
          </div>

          {/* RIGHT */}
          <div className="modules-column">
            <div className="modules-wrapper">

              <div className="module-card">
                <div className="module-icon">🧮</div>
                <div className="module-content">
                  <h3>Math Module</h3>
                  <p>Adaptive arithmetic problems</p>
                </div>
              </div>

              <div className="module-card">
                <div className="module-icon">✏️</div>
                <div className="module-content">
                  <h3>Spelling Module</h3>
                  <p>Missing letters &amp; complete words</p>
                </div>
              </div>

              <div className="module-card">
                <div className="module-icon">📖</div>
                <div className="module-content">
                  <h3>Reading Module</h3>
                  <p>Words, sentences &amp; paragraphs</p>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>

      {showLogin && <LoginModal onClose={() => setShowLogin(false)} />}
      {showSignup && <SignupModal onClose={() => setShowSignup(false)} />}

    </div>
  );
};

export default HomePage;