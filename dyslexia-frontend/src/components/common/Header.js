import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import './Header.css';

const Header = () => {
  const { currentUser, logoutUser } = useUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    logoutUser();
    navigate('/');
  };

  const handleViewProgress = () => {
    navigate('/report');
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <h1>🎯 Dyslexia Adaptive Learning</h1>
        </div>
        <div className="user-info">
          {currentUser && (
            <div className="user-details">
              <span className="user-name">Welcome back, {currentUser.name}!</span>
              <span className="user-age">Age: {currentUser.age}</span>
              <div className="user-actions">
                <button onClick={handleViewProgress} className="btn-header">
                  📊 View Progress
                </button>
                <button onClick={handleLogout} className="btn-header logout">
                  🚪 Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;