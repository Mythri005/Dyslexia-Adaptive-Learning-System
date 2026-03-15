import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import './ModuleSelection.css';

const ModuleSelection = () => {
  const navigate = useNavigate();
  const { currentUser } = useUser();

  const modules = [
    {
      id: 'math',
      title: '🔢 Math Adventure',
      description: 'Solve fun math problems with AI help',
      color: '#667eea',
      features: ['Adaptive difficulty', 'Real-time help', 'Progress tracking']
    },
    {
      id: 'spelling',
      title: '📝 Spelling Wizard',
      description: 'Master spelling with interactive games',
      color: '#f093fb',
      features: ['Missing letters', 'Complete words', 'AI pronunciation']
    },
    {
      id: 'reading',
      title: '📖 Reading Master',
      description: 'Improve reading and pronunciation',
      color: '#4facfe',
      features: ['Word practice', 'Sentences', 'Paragraphs', 'Real-time feedback']
    }
  ];

  const handleModuleSelect = (moduleId) => {
    navigate(`/${moduleId}`);
  };

  return (
    <div className="module-selection fade-in">
      <div className="welcome-section card">
        <h2>Hello, {currentUser?.name}! 👋</h2>
        <p>Choose what you'd like to learn today:</p>
      </div>

      <div className="modules-grid">
        {modules.map((module) => (
          <div 
            key={module.id}
            className="module-card card"
            style={{ borderColor: module.color }}
            onClick={() => handleModuleSelect(module.id)}
          >
            <div className="module-header">
              <h3>{module.title}</h3>
              <div 
                className="module-icon"
                style={{ backgroundColor: module.color }}
              >
                {module.title.split(' ')[0]}
              </div>
            </div>
            
            <p className="module-description">{module.description}</p>
            
            <ul className="module-features">
              {module.features.map((feature, index) => (
                <li key={index}>✓ {feature}</li>
              ))}
            </ul>
            
            <button 
              className="btn module-btn"
              style={{ 
                background: `linear-gradient(135deg, ${module.color} 0%, ${module.color}99 100%)` 
              }}
            >
              Start Learning →
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModuleSelection;