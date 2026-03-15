import React, { useState, useEffect } from 'react';
import voiceService from '../../services/voiceService';
import './MissingLetters.css';

const MissingLetters = ({ question, onSubmit, feedback, loading, cameraAnalysis }) => {
  const [userAnswer, setUserAnswer] = useState('');
  const [hasSpokenInstruction, setHasSpokenInstruction] = useState(false);

  useEffect(() => {
    if (question?.ai_instruction && !hasSpokenInstruction) {
      const timer = setTimeout(() => {
        voiceService.playAudio(question.ai_instruction);
        
        if (question.complete_word) {
          setTimeout(() => {
            voiceService.playAudio(`The complete word is: ${question.complete_word}`);
          }, 1500);
        }
        
        setHasSpokenInstruction(true);
      }, 1000);
      
      return () => clearTimeout(timer);
    }
  }, [question, hasSpokenInstruction]);

  useEffect(() => {
    if (feedback?.ai_feedback && !loading) {
      const timer = setTimeout(() => {
        voiceService.playAudio(feedback.ai_feedback);
        
        if (!feedback.is_correct && feedback.correct_letter) {
          setTimeout(() => {
            voiceService.playAudio(`The missing letter is: ${feedback.correct_letter}`);
          }, 1500);
        }
      }, 500);
      
      return () => clearTimeout(timer);
    }
  }, [feedback, loading]);

  useEffect(() => {
    setHasSpokenInstruction(false);
    setUserAnswer('');
  }, [question]);

  const handleSubmit = () => {
    if (userAnswer.trim()) {
      onSubmit(userAnswer.toUpperCase());
      setUserAnswer('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleSubmit();
    }
  };

  const handleHearQuestionAgain = () => {
    if (question?.ai_instruction) {
      voiceService.playAudio(question.ai_instruction);
      if (question.complete_word) {
        setTimeout(() => {
          voiceService.playAudio(`The complete word is: ${question.complete_word}`);
        }, 1500);
      }
    }
  };

  const handleHearCompleteWord = () => {
    if (question?.complete_word) {
      voiceService.playAudio(`The complete word is: ${question.complete_word}`);
    }
  };

  const handleHearCorrectLetter = () => {
    if (feedback?.correct_letter) {
      voiceService.playAudio(`The missing letter is: ${feedback.correct_letter}`);
    } else if (question?.complete_word) {
      const pattern = question.display_text || '';
      const completeWord = question.complete_word;
      const missingIndex = pattern.indexOf('_');
      if (missingIndex !== -1) {
        const correctLetter = completeWord[missingIndex];
        voiceService.playAudio(`The missing letter is: ${correctLetter}`);
      }
    }
  };

  // ✅ SAFE PATTERN FALLBACK IF display_text IS MISSING
  const buildSafePattern = () => {
    if (question?.display_text?.includes('_')) return question.display_text;

    if (!question?.complete_word) return '';

    const word = question.complete_word;
    const randomIndex = Math.floor(Math.random() * (word.length - 2)) + 1;
    return word.slice(0, randomIndex) + '_' + word.slice(randomIndex + 1);
  };

  const renderWordPattern = () => {
    const pattern = buildSafePattern();
    if (!pattern) return null;

    return (
      <div className="word-pattern">
        {pattern.split('').map((letter, index) => (
          <span
            key={index}
            className={`pattern-letter ${letter === '_' ? 'missing' : ''}`}
          >
            {letter === '_' ? '___' : letter}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="missing-letters card">
      {cameraAnalysis?.needs_help && (
        <div className="help-banner">
          🆘 {cameraAnalysis.help_message}
        </div>
      )}

      <div className="question-header">
        <h2>Fill in the Missing Letter</h2>
        <div className="question-controls">
          {question?.category && (
            <span className="difficulty-badge">
              {question.category.toUpperCase()}
            </span>
          )}
          <button 
            onClick={handleHearQuestionAgain}
            className="btn hear-btn small"
          >
            🔊
          </button>
          <button 
            onClick={handleHearCompleteWord}
            className="btn hear-btn small"
          >
            🔤
          </button>
        </div>
      </div>

      <div className="question-content">
        <div className="instruction">
          <p>Complete the word by entering the missing letter:</p>
          {question?.complete_word && (
            <div className="complete-word-hint">
              <strong>Word to spell:</strong> {question.complete_word}
            </div>
          )}
        </div>

        {renderWordPattern()}

        <div className="answer-section">
          <div className="input-group">
            <label>Missing Letter:</label>
            <input
              type="text"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value.toUpperCase())}
              onKeyPress={handleKeyPress}
              placeholder="Enter letter"
              className="letter-input"
              disabled={loading}
              maxLength="1"
              autoFocus
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={!userAnswer.trim() || loading}
            className="btn submit-btn"
          >
            {loading ? 'Checking...' : 'Submit Letter'}
          </button>
        </div>

        {feedback && (
          <div className={`feedback ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
            <div className="feedback-message">{feedback.ai_feedback}</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MissingLetters;
