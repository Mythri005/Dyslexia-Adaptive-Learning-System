import React, { useState, useEffect } from 'react';
import voiceService from '../../services/voiceService';
import './CompleteWords.css';

const CompleteWords = ({ question, onSubmit, feedback, loading, cameraAnalysis }) => {
  const [userAnswer, setUserAnswer] = useState('');
  const [showHint, setShowHint] = useState(false);
  const [hasSpokenInstruction, setHasSpokenInstruction] = useState(false);
  const [waitingForCorrect, setWaitingForCorrect] = useState(false);

  // 🔊 Speak instruction when question loads
  useEffect(() => {
    if (!question) return;

    setHasSpokenInstruction(false);
    setShowHint(false);
    setUserAnswer('');
    setWaitingForCorrect(false);

    const timer = setTimeout(() => {
      if (question?.ai_instruction) {
        voiceService.playAudio(question.ai_instruction);
        setHasSpokenInstruction(true);
      }
    }, 700);

    return () => clearTimeout(timer);
  }, [question]);

  // 🔊 Speak feedback & teach on wrong answer
  useEffect(() => {
    if (!feedback || loading) return;

    const timer = setTimeout(() => {
      voiceService.playAudio(feedback.ai_feedback);

      // If wrong — spell word slowly
      if (!feedback.is_correct && question?.speak_word) {
        setWaitingForCorrect(true);

        setTimeout(() => {
          voiceService.spellWordLetterByLetter(question.speak_word);
          setShowHint(true);
        }, 1200);
      }

      // If correct — allow next question normally
      if (feedback.is_correct) {
        setWaitingForCorrect(false);
      }

    }, 500);

    return () => clearTimeout(timer);
  }, [feedback, loading, question]);

  // ✅ Submit Answer — child must retry if wrong
  const handleSubmit = () => {
    if (!userAnswer.trim() || loading) return;

    onSubmit(userAnswer.toLowerCase());

    // Only clear input if correct — keep retry if wrong
    if (!waitingForCorrect) {
      setUserAnswer('');
      setShowHint(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !loading) {
      handleSubmit();
    }
  };

  // 💡 Show hint spelling
  const handleShowHint = () => {
    setShowHint(true);

    if (question?.speak_word) {
      voiceService.spellWordLetterByLetter(question.speak_word);
    }
  };

  // 🔊 Hear word again
  const handleHearWordAgain = () => {
    if (question?.speak_word) {
      voiceService.playAudio(`Spell the word: ${question.speak_word}`, { rate: 0.95 });
    }
  };

  // 🔤 Spell for me
  const handleSpellForMe = () => {
    if (question?.speak_word) {
      voiceService.spellWordLetterByLetter(question.speak_word);
      setShowHint(true);
    }
  };

  // 🧠 Render Hint UI
  const renderWordHint = () => {
    if (!question?.speak_word || !showHint) return null;

    return (
      <div className="word-hint">
        <div className="hint-title">Word spelled out:</div>

        <div className="letter-by-letter">
          {question.speak_word.split('').map((letter, index) => (
            <span key={index} className="hint-letter">{letter}</span>
          ))}
        </div>

        <button onClick={handleSpellForMe} className="btn hint-btn small">
          🔊 Spell Again
        </button>
      </div>
    );
  };

  return (
    <div className="complete-words card">
      
      {/* Stress Support */}
      {cameraAnalysis?.needs_help && (
        <div className="help-banner">
          🆘 {cameraAnalysis.help_message}
        </div>
      )}

      <div className="question-header">
        <h2>Spell the Complete Word</h2>

        <div className="question-controls">
          {question?.category && (
            <span className="difficulty-badge">
              {question.category.toUpperCase()}
            </span>
          )}

          <button onClick={handleHearWordAgain} className="btn hear-btn small" title="Hear word again">
            🔊
          </button>
        </div>
      </div>

      <div className="question-content">

        <div className="instruction">
          <p>Listen carefully and spell the word you hear:</p>
        </div>

        {/* Word Display */}
        {question?.speak_word && (
          <div className="word-audio-prompt">
            <div className="word-to-spell">"{question.speak_word}"</div>

            <div className="audio-controls">
              <button onClick={handleHearWordAgain} className="btn hear-again-btn">
                🔊 Hear Word Again
              </button>

              <button onClick={handleSpellForMe} className="btn hint-btn">
                🔤 Spell For Me
              </button>
            </div>
          </div>
        )}

        {/* Input */}
        <div className="answer-section">
          <div className="input-group">
            <label>Type the word:</label>

            <input
              type="text"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter the complete word"
              className="word-input"
              disabled={loading}
              autoFocus
            />
          </div>

          <div className="action-buttons">
            <button
              onClick={handleSubmit}
              disabled={!userAnswer.trim() || loading}
              className="btn submit-btn"
            >
              {loading ? 'Checking...' : 'Submit Word'}
            </button>

            {!showHint && (
              <button onClick={handleShowHint} className="btn hint-btn">
                💡 Show Hint
              </button>
            )}
          </div>
        </div>

        {renderWordHint()}

        {/* Feedback */}
        {feedback && (
          <div className={`feedback ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
            <div className="feedback-header">
              <div className="feedback-title">
                {feedback.is_correct ? '🎉 Perfect Spelling!' : '💡 Let me help you'}

                <button 
                  onClick={() => voiceService.playAudio(feedback.ai_feedback)}
                  className="btn hear-btn small"
                >
                  🔊
                </button>
              </div>
            </div>

            <div className="feedback-message">
              {feedback.ai_feedback}
            </div>

            {!feedback.is_correct && feedback.correct_answer && (
              <div className="correct-spelling">
                Correct spelling: <strong>{feedback.correct_answer}</strong>
              </div>
            )}

            {feedback.points_earned > 0 && (
              <div className="points-earned">
                +{feedback.points_earned} points! ✨
              </div>
            )}
          </div>
        )}

        {/* Celebration */}
        {feedback?.is_correct && question?.speak_word && (
          <div className="spelling-celebration">
            <div className="correct-word-display">
              {question.speak_word.split('').map((letter, index) => (
                <span key={index} className="celebrated-letter">{letter}</span>
              ))}
            </div>

            <div className="celebration-message">
              Excellent spelling! 🎉
            </div>
          </div>
        )}

        {/* Stress Encouragement */}
        {cameraAnalysis?.stress_level > 0.7 && (
          <div className="stress-help">
            <div className="stress-message">😊 You're doing great! Keep trying!</div>
            <div className="stress-tip">Click "Spell For Me" if you need help.</div>
          </div>
        )}

      </div>
    </div>
  );
};

export default CompleteWords;
