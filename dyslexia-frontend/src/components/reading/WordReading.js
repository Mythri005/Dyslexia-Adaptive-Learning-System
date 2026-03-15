

import React, { useEffect } from 'react';
import voiceService from '../../services/voiceService';
import './WordReading.css';

const WordReading = ({ item, feedback, loading, cameraAnalysis }) => {
  useEffect(() => {
    if (item?.ai_instruction) {
      voiceService.playAudio(item.ai_instruction);
    }
    
    if (item?.speak_text) {
      // Speak the word after a short delay
      setTimeout(() => {
        voiceService.playAudio(item.speak_text);
      }, 1500);
    }
  }, [item]);

  useEffect(() => {
    if (feedback?.ai_feedback) {
      voiceService.playAudio(feedback.ai_feedback);
    }
  }, [feedback]);

  const handleHearAgain = () => {
    if (item?.speak_text) {
      voiceService.playAudio(item.speak_text);
    }
  };

  const handleHearSlowly = () => {
    if (item?.speak_text) {
      voiceService.playAudio(item.speak_text, { rate: 0.7 });
    }
  };

  if (!item) return null;

  return (
    <div className="word-reading card">
      {cameraAnalysis?.needs_help && (
        <div className="help-banner">
          🆘 {cameraAnalysis.help_message}
        </div>
      )}

      <div className="reading-header">
        <h2>Word Reading Practice</h2>
        {item?.category && (
          <span className="difficulty-badge">
            {item.category.toUpperCase()}
          </span>
        )}
      </div>

      <div className="reading-content">
        <div className="instruction">
          <p>Listen to the word and repeat it clearly:</p>
        </div>

        <div className="word-display">
          <div className="main-word">
            {item.display_text || item.full_text}
          </div>
          <div className="word-phonetic">
            {item.expected_pronunciation && (
              <span>Say: "{item.expected_pronunciation}"</span>
            )}
          </div>
        </div>

        <div className="audio-controls">
          <button onClick={handleHearAgain} className="btn hear-btn">
            🔊 Hear Word Again
          </button>
          <button onClick={handleHearSlowly} className="btn slow-btn">
            🐢 Hear Slowly
          </button>
        </div>

        {feedback && !feedback.is_correct && (
          <div className="correction-guide">
            <h4>🔄 Let's Practice Together:</h4>
            <div className="correction-steps">
              <div className="step">
                <span className="step-number">1</span>
                <span className="step-text">Listen to the word again</span>
              </div>
              <div className="step">
                <span className="step-number">2</span>
                <span className="step-text">Say each sound slowly</span>
              </div>
              <div className="step">
                <span className="step-number">3</span>
                <span className="step-text">Put the sounds together</span>
              </div>
              <div className="step">
                <span className="step-number">4</span>
                <span className="step-text">Try recording again</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WordReading;