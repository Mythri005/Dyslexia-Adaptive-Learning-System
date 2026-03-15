// dyslexia-frontend/src/components/auth/LoginModal.js

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { userAPI } from '../../services/api';
import './AuthModal.css';

const LoginModal = ({ onClose }) => {
  const navigate = useNavigate();
  const { setCurrentUser } = useUser();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await userAPI.login({
        email: formData.email,
        password: formData.password
      });

      const user = response.data.user;
      const backendProgress = response.data.progress;

      // Convert backend format → frontend format
      const formattedProgress = {};

      backendProgress.forEach(p => {
        formattedProgress[p.module] = {
          reports: [],
          totalPoints: p.total_points || 0,
          averageAccuracy: p.accuracy || 0,
          grade: "—",
          strengths: [],
          weaknesses: [],
          sessionsCompleted: 0
        };
      });

      setCurrentUser(user);

      localStorage.setItem(
        `dyslexia_progress_${user.id}`,
        JSON.stringify(formattedProgress)
      );

      localStorage.setItem('dyslexia_userProgress', JSON.stringify(formattedProgress));

      onClose();
      navigate('/modules');
    } catch (err) {
      setError('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content auth-modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>×</button>
        
        <div className="auth-header">
          <h2>Welcome Back</h2>
          <p>Sign in to continue your learning journey</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="auth-submit-btn"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <button 
            type="button" 
            className="auth-demo-btn"
            onClick={() => {
              // Demo login
              const demoUser = {
                id: `demo_${Date.now()}`,
                name: 'Demo User',
                age: 10,
                email: 'demo@example.com',
                isDemo: true
              };
              setCurrentUser(demoUser);
              
              // Initialize empty progress for demo user
              localStorage.setItem('dyslexia_userProgress', JSON.stringify({}));
              
              onClose();
              navigate('/modules');
            }}
          >
            Continue as Guest
          </button>
        </form>

        <div className="auth-footer">
          <p>Don't have an account? <a href="#" onClick={(e) => {
            e.preventDefault();
            onClose();
            // Trigger signup modal
            document.querySelector('[data-signup]')?.click();
          }}>Sign up</a></p>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;