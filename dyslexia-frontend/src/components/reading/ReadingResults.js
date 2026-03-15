import React from 'react';
import { useNavigate } from 'react-router-dom';
import './ReadingResults.css';

const ReadingResults = ({ 
  results, 
  onContinue, 
  onExit, 
  isCheckpoint,
  mode,
  // NEW PROPS FOR CUMULATIVE DATA
  cumulativeReports = 0, 
  cumulativePoints = 0 
}) => {
  const navigate = useNavigate();

  // 1. Calculate Session Stats (Current Session Only)
  const sessionTotal = results.total_questions || results.items_attempted || 5;
  const sessionCorrect = results.correct_pronunciations || results.correct_answers || 0;
  const sessionAccuracy = sessionTotal > 0 ? Math.round((sessionCorrect / sessionTotal) * 100) : 0;
  const sessionPoints = results.points_earned || 0;
  const sessionStreak = results.best_streak || results.current_streak || 0;

  // 2. Use Cumulative Stats if available, otherwise fallback to session stats
  const totalReports = cumulativeReports > 0 ? cumulativeReports : (isCheckpoint ? 1 : 0);
  const totalPoints = cumulativePoints > 0 ? cumulativePoints : sessionPoints;
  
  // Calculate Cumulative Accuracy (Weighted Average)
  let displayAccuracy = sessionAccuracy;
  if (cumulativeReports > 0 && cumulativePoints > 0) {
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
    if (displayAccuracy >= 85) return "🌟 Outstanding reading! You're a reading superstar!";
    if (displayAccuracy >= 70) return "🎉 Excellent work! Your reading is improving!";
    if (displayAccuracy >= 55) return "👍 Good progress! Keep going!";
    return "💪 Keep practicing — you're getting better!";
  };

  const getStreakMessage = () => {
    if (sessionStreak >= 5) return "🔥 WOW! You're on a super streak!";
    if (sessionStreak >= 3) return "⭐ Nice streak! Keep it going!";
    return "🙂 Try building a longer streak next time!";
  };

  const getModeTitle = () => {
    switch (mode) {
      case 'words': return 'Word Reading';
      case 'sentences': return 'Sentence Reading';
      case 'paragraphs': return 'Paragraph Reading';
      default: return 'Reading Practice';
    }
  };

  const getModeIcon = () => {
    switch (mode) {
      case 'words': return '🔤';
      case 'sentences': return '📝';
      case 'paragraphs': return '📄';
      default: return '📖';
    }
  };

  const grade = getGrade(displayAccuracy);

  const handlePrintReport = () => {
    document.body.classList.add('printing');
    window.print();
    setTimeout(() => {
      document.body.classList.remove('printing');
    }, 100);
  };

  const handleBackToModules = () => {
    if (onExit) onExit();
    else navigate('/modules');
  };

  return (
    <div className="reading-results report-page fade-in">
      <div className="results-card card">
        <div className="results-header">
          <h1>{getModeIcon()} {getModeTitle()} Complete!</h1>
          <p>{getFunMessage()}</p>
          <span className="total-questions-badge">
            {sessionTotal} Items Completed
          </span>
        </div>

        <div className="results-stats">
          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-value">{sessionCorrect}/{sessionTotal}</div>
            <div className="stat-label">Correct Readings</div>
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
              ? "🎯 Excellent progress! You're mastering reading concepts!" 
              : "🌱 Keep practicing! Every word makes you stronger."}
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

        {/* Reading Specific Achievements Section */}
        <div className="reading-achievements">
          <h3>🏅 Reading Achievements</h3>
          <div className="achievements-grid">
            <div className="achievement">
              <span className="achievement-icon">🎯</span>
              <div>
                <strong>Pronunciation Progress</strong>
                <p>Clearer and more confident reading</p>
              </div>
            </div>
            <div className="achievement">
              <span className="achievement-icon">🔥</span>
              <div>
                <strong>Streak Builder</strong>
                <p>Great consistency streak</p>
              </div>
            </div>
            <div className="achievement">
              <span className="achievement-icon">🚀</span>
              <div>
                <strong>Fluency Growth</strong>
                <p>Improved flow and expression</p>
              </div>
            </div>
          </div>
        </div>

        <div className="results-actions no-print">
          {isCheckpoint && (
            <button onClick={onContinue} className="btn btn-success">
              Continue Reading (Next 5 Questions)
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

export default ReadingResults;