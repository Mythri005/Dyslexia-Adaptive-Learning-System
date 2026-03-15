import React from 'react';
import { useNavigate } from 'react-router-dom';
import './SpellingResults.css';

const SpellingResults = ({ 
  results, 
  onContinue, 
  onExit, 
  mode,
  // NEW PROPS FOR CUMULATIVE DATA
  cumulativeReports = 0, 
  cumulativePoints = 0 
}) => {
  const navigate = useNavigate();

  // 1. Calculate Session Stats (Current Session Only)
  const sessionTotal = results.total_questions || 5;
  const sessionCorrect = results.correct_answers || 0;
  const sessionAccuracy = sessionTotal > 0 ? Math.round((sessionCorrect / sessionTotal) * 100) : 0;
  const sessionPoints = results.points_earned || 0;
  const sessionStreak = results.best_streak || 0;

  // 2. Use Cumulative Stats if available, otherwise fallback to session stats
  const totalReports = cumulativeReports > 0 ? cumulativeReports : 1;
  const totalPoints = cumulativePoints > 0 ? cumulativePoints : sessionPoints;

  const getPerformanceMessage = (accuracy) => {
    if (accuracy >= 85) return "🏆 Outstanding spelling! You're a champion!";
    if (accuracy >= 70) return "🌟 Excellent work! Keep shining!";
    if (accuracy >= 55) return "👍 Good progress! You're improving!";
    return "💪 Keep practicing — you'll master it!";
  };

  const getModeTitle = () => {
    return mode === 'missing_letters' ? 'Missing Letters' : 'Complete Words';
  };

  const getGrade = (accuracy) => {
    if (accuracy >= 90) return { grade: 'A+', color: '#4CAF50' };
    if (accuracy >= 80) return { grade: 'A', color: '#4CAF50' };
    if (accuracy >= 70) return { grade: 'B', color: '#FF9800' };
    if (accuracy >= 60) return { grade: 'C', color: '#FF9800' };
    if (accuracy >= 50) return { grade: 'D', color: '#F44336' };
    return { grade: 'F', color: '#F44336' };
  };

  const grade = getGrade(sessionAccuracy);

  // ✅ PROFESSIONAL PRINT HANDLER
  const handlePrintReport = () => {
    document.body.classList.add('printing');
    window.print();
    setTimeout(() => {
      document.body.classList.remove('printing');
    }, 100);
  };

  return (
    <div className="spelling-results fade-in">
      <div className="results-card card">

        <div className="results-header">
          <h1>📝 {getModeTitle()} Complete!</h1>
          <p>{getPerformanceMessage(sessionAccuracy)}</p>
          <span className="total-questions-badge">
            {sessionTotal} Words Completed
          </span>
        </div>

        <div className="results-stats">
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-value">{sessionCorrect}/{sessionTotal}</div>
            <div className="stat-label">Correct</div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-value">{sessionAccuracy}%</div>
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
          <h3>📚 Spelling Insights</h3>
          <p>
            {sessionAccuracy >= 70 
              ? "🎯 Excellent! You're ready for harder words!" 
              : "🌱 Focus on letter sounds and syllable breaks"}
          </p>
          <p>
            {sessionStreak >= 3 
              ? `🔥 Amazing ${sessionStreak}-word streak!` 
              : "💪 Try to build a longer streak next time"}
          </p>
          <p className="summary-stats">
            {sessionCorrect}/{sessionTotal} correct • {sessionPoints} points earned this session
          </p>
        </div>

        {/* NO-PRINT BUTTONS */}
        <div className="results-actions no-print">
          <button onClick={onContinue} className="btn btn-success">
            Continue {getModeTitle()} (Next 5 Words 🚀)
          </button>
          <button onClick={handlePrintReport} className="btn btn-secondary">
            🖨️ Print Report
          </button>
          <button onClick={onExit} className="btn">
            ← Back to Modules
          </button>
        </div>

        {/* PRINT-ONLY FOOTER */}
        <div className="print-only">
          <div className="print-date">
            Report generated: {new Date().toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </div>
          <div className="print-footer">
            Dyslexia Adaptive Learning System • Spelling Report
          </div>
        </div>

        {/* ENCOURAGEMENT - HIDDEN IN PRINT */}
        <div className="encouragement no-print">
          <p>🎉 Every word you learn makes you smarter — keep going!</p>
        </div>

      </div>
    </div>
  );
};

export default SpellingResults;