import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { userAPI } from '../../services/api';
import './UserRegistration.css';

const UserRegistration = () => {
  const navigate = useNavigate();
  const { setCurrentUser, findExistingUser } = useUser();
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    email: ''
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
      // First check if user exists in localStorage
      const existingUser = findExistingUser(formData.name, formData.age);
      
      if (existingUser) {
        // User exists - load their progress
        setCurrentUser(existingUser);
        navigate('/modules');
        setLoading(false);
        return;
      }

      // If not in localStorage, try backend
      const response = await userAPI.createUser({
        name: formData.name,
        age: parseInt(formData.age),
        email: formData.email || `${formData.name.toLowerCase().replace(/\s+/g, '')}@dyslexiaapp.com`
      });

      if (response.status === 201) {
        const user = response.data.user;
        
        // Save to all users list
        const users = JSON.parse(localStorage.getItem('dyslexia_allUsers') || '[]');
        users.push(user);
        localStorage.setItem('dyslexia_allUsers', JSON.stringify(users));
        localStorage.setItem(`dyslexia_user_${user.id}`, JSON.stringify(user));
        
        // Set user in context
        setCurrentUser(user);
        
        navigate('/modules');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create user');
      
      // Fallback: Check localStorage again or create local user
      const existingUser = findExistingUser(formData.name, formData.age);
      
      if (existingUser) {
        setCurrentUser(existingUser);
        navigate('/modules');
      } else {
        // Create local user
        const localUser = {
          id: `user_${Date.now()}`,
          name: formData.name,
          age: parseInt(formData.age),
          email: formData.email || `${formData.name.toLowerCase().replace(/\s+/g, '')}@dyslexiaapp.com`,
          createdAt: new Date().toISOString()
        };
        
        // Save to all users list
        const users = JSON.parse(localStorage.getItem('dyslexia_allUsers') || '[]');
        users.push(localUser);
        localStorage.setItem('dyslexia_allUsers', JSON.stringify(users));
        localStorage.setItem(`dyslexia_user_${localUser.id}`, JSON.stringify(localUser));
        
        setCurrentUser(localUser);
        navigate('/modules');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="registration-container fade-in">
      <div className="registration-card card">
        <h2>🎯 Welcome to Dyslexia Adaptive Learning</h2>
        <p className="subtitle">Let's get started by creating your learning profile</p>
        
        <form onSubmit={handleSubmit} className="registration-form">
          <div className="form-group">
            <label htmlFor="name">What's your name?</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="Enter your name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="age">How old are you?</label>
            <input
              type="number"
              id="age"
              name="age"
              value={formData.age}
              onChange={handleChange}
              required
              min="5"
              max="18"
              placeholder="Enter your age"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email (optional)</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Creating Profile...' : 'Start Learning Journey 🚀'}
          </button>
        </form>

        <div className="features-preview">
          <h3>Your progress will be saved automatically!</h3>
          <div className="features-grid">
            <div className="feature">
              <span className="feature-icon">💾</span>
              <h4>Auto Save</h4>
              <p>Your progress is saved automatically</p>
            </div>
            <div className="feature">
              <span className="feature-icon">📊</span>
              <h4>Track Progress</h4>
              <p>View your improvement over time</p>
            </div>
            <div className="feature">
              <span className="feature-icon">🔒</span>
              <h4>Secure</h4>
              <p>Your data is safe and private</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserRegistration;