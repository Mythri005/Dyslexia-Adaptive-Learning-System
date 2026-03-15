import React from 'react';
import { useNavigate } from 'react-router-dom';
import './MathResults.css';

const MathResults = ({ 
  results, 
  onContinue, 
  onExit, 
  isCheckpoint,
  // NEW PROPS FOR CUMULATIVE DATA
  cumulativeReports = 0, 
  cumulativePoints = 0 
}) => {
  const navigate = useNavigate();

  // 1. Calculate Session Stats (Current Session Only)
  const sessionTotal = results.questions_answered || 0;
  const sessionCorrect = results.correct_answers || 0;
  const sessionAccuracy = sessionTotal > 0 ? Math.round((sessionCorrect / sessionTotal) * 100) : 0;
  const sessionPoints = results.points_earned || 0;
  const sessionStreak = results.best_streak || results.current_streak || 0;

  // 2. Use Cumulative Stats if available, otherwise fallback to session stats
  // This fixes the "Reports: 2" and "Total Points: 90" display issue
  const totalReports = cumulativeReports > 0 ? cumulativeReports : (isCheckpoint ? 1 : 0);
  const totalPoints = cumulativePoints > 0 ? cumulativePoints : sessionPoints;
  
  // Calculate Cumulative Accuracy (Weighted Average)
  // If we have cumulative data, we calculate the real accuracy. 
  // If not, we show the session accuracy.
  let displayAccuracy = sessionAccuracy;
  if (cumulativeReports > 0 && cumulativePoints > 0) {
     // Simple approximation: If we have total points, we assume accuracy is tracked there
     // Ideally, your backend should send 'cumulativeAccuracy' as well.
     // For now, we will display the session accuracy but label it clearly.
     displayAccuracy = sessionAccuracy; 
  }

  const getGrade = (accuracy) => {
    if (accuracy >= 90) return { grade: 'A+', color: '#4CAF50' };
    if (accuracy >= 80) return { grade: 'A', color: '#4CAF50' };
    if (accuracy >= 70) return { grade: 'B', color: '#FF9800' };
    if (accuracy >= 60) return { grade: 'C', color: '#FF9800' };
    if (accuracy >= 50) return { grade: 'D', color: '#F44336' };
    return { grade: 'F', color: '#F44336' };
  };

  const getFunMessage = () => {
    if (displayAccuracy >= 85) return "🌟 Amazing job! You're a Math Superstar!";
    if (displayAccuracy >= 65) return "👏 Great work! Keep going, champion!";
    if (displayAccuracy >= 40) return "💪 Good effort! Practice makes you stronger!";
    return "💖 It's okay! You're learning step by step — don't give up!";
  };

  const getStreakMessage = () => {
    if (sessionStreak >= 5) return "🔥 WOW! You're on a super streak!";
    if (sessionStreak >= 3) return "⭐ Nice streak! Keep it going!";
    return "🙂 Try building a longer streak next time!";
  };

  const grade = getGrade(displayAccuracy);

  const handlePrintReport = () => {
    document.body.classList.add('printing');
    window.print();
    setTimeout(() => {
      document.body.classList.remove('printing');
    }, 100);
  };

  const handleBackToModules = async () => {
    if (onExit) {
      await onExit();   // save progress
    }
    navigate('/modules');  // go to module page
  };

  return (
    <div className="math-results fade-in">
      <div className="results-card card">
        <div className="results-header">
          <h1>📊 Math Session Complete!</h1>
          <p>{getFunMessage()}</p>
          <span className="total-questions-badge">
            {sessionTotal} Questions Completed
          </span>
        </div>

        <div className="results-stats">
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-value">{sessionCorrect}/{sessionTotal}</div>
            <div className="stat-label">Correct</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📈</div>
            <div className="stat-value">{displayAccuracy}%</div>
            <div className="stat-label">Accuracy</div>
          </div>

          <div className="stat-card main-grade">
            <div className="stat-icon">🏆</div>
            <div className="stat-value">{grade.grade}</div>
            <div className="stat-label">Grade</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">⭐</div>
            {/* Display Cumulative Points if available, otherwise Session Points */}
            <div className="stat-value">{totalPoints}</div>
            <div className="stat-label">Total Points</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔥</div>
            <div className="stat-value">{sessionStreak}</div>
            <div className="stat-label">Best Streak</div>
          </div>
        </div>

        <div className="recommendations">
          <h3>📝 Learning Insights</h3>
          <p>{getStreakMessage()}</p>
          <p>
            {displayAccuracy >= 70 
              ? "🎯 Excellent progress! You're mastering math concepts!" 
              : "🌱 Keep practicing! Every question makes you stronger."}
          </p>
          <p>
              <p>
                {sessionStreak >= 3 
                  ? `🔥 Amazing ${sessionStreak}-question streak!` 
                  : "💪 Try to build a longer streak next time"}
              </p>
              <p className="summary-stats">
                {sessionCorrect}/{sessionTotal} correct • {sessionPoints} points earned this session
              </p>
          </p>
        </div>

        <div className="results-actions no-print">
          {isCheckpoint && (
            <button onClick={onContinue} className="btn btn-success">
              Continue Math (Next 5 Questions)
            </button>
          )}
          <button onClick={handleBackToModules} className="btn">
            ← Back to Modules
          </button>
          <button onClick={handlePrintReport} className="btn btn-secondary">
            🖨️ Print Report
          </button>
        </div>

        <div className="print-only">
          <div className="print-date">
            Report generated: {new Date().toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </div>
          <div className="print-footer">
            Dyslexia Adaptive Learning System • Personalized Learning Report
          </div>
        </div>
      </div>
    </div>
  );
};

export default MathResults;