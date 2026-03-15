import React from 'react';
import './MathQuestion.css';

const MathQuestion = ({ question, userAnswer, onAnswerChange, onSubmit, feedback, loading, cameraAnalysis }) => {

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      onSubmit();
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return '#4CAF50';
      case 'medium': return '#FF9800';
      case 'hard': return '#F44336';
      default: return '#667eea';
    }
  };

  return (
    <div className="math-question card">

      {/* ✅ ONLY KEEP NORMAL HELP MESSAGE — REMOVE STRESS LINE */}
      {cameraAnalysis?.needs_help && (
        <div className="help-banner">
          🆘 {cameraAnalysis.help_message}
        </div>
      )}

      <div className="question-header">
        <h2>Math Problem</h2>
        {question?.category && (
          <span 
            className="difficulty-badge"
            style={{ backgroundColor: getDifficultyColor(question.category) }}
          >
            {question.category.toUpperCase()}
          </span>
        )}
      </div>

      <div className="question-content">
        <div className="question-text">
          {question.question || "What is 5 + 3?"}
        </div>

        {question?.explanation && !feedback && (
          <div className="question-hint">
            💡 Hint: {question.explanation}
          </div>
        )}

        {!question?.explanation && !feedback && (
          <div className="question-hint">
            💡 Think carefully about the problem!
          </div>
        )}

        <div className="answer-section">
          <input
            type="text"
            value={userAnswer}
            onChange={(e) => onAnswerChange(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your answer here..."
            className="answer-input"
            disabled={loading}
            autoFocus
          />
          
          <button
            onClick={onSubmit}
            disabled={!userAnswer.trim() || loading}
            className="btn submit-btn"
          >
            {loading ? 'Checking...' : 'Submit Answer'}
          </button>
        </div>

        {feedback && (
          <div className={`feedback ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
            <div className="feedback-header">
              {feedback.is_correct ? '🎉 Correct!' : '💡 Let me help you'}
            </div>
            <div className="feedback-message">
              {feedback.ai_feedback || 
               (feedback.is_correct ? "Great job!" : "Don't worry, let's try again!")}
            </div>
            {!feedback.is_correct && feedback.correct_answer && (
              <div className="correct-answer">
                Correct answer: <strong>{feedback.correct_answer}</strong>
              </div>
            )}
            {feedback.points_earned > 0 && (
              <div className="points-earned">
                +{feedback.points_earned} points! ✨
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MathQuestion;
