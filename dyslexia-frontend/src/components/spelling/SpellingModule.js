import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { spellingAPI, monitoringAPI } from '../../services/api';
import CameraFeed from '../common/CameraFeed';
import MissingLetters from './MissingLetters';
import CompleteWords from './CompleteWords';
import SpellingResults from './SpellingResults';
import LoadingSpinner from '../common/LoadingSpinner';
import './SpellingModule.css';

const QUESTIONS_PER_ROUND = 5;

const SpellingModule = () => {
  const navigate = useNavigate();
  const { currentUser, updateProgress } = useUser();
  const [mode, setMode] = useState(null);
  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cameraAnalysis, setCameraAnalysis] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [sessionSummary, setSessionSummary] = useState(null);

  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [correctAnswers, setCorrectAnswers] = useState(0);
  const [currentStreak, setCurrentStreak] = useState(0);
  const [bestStreak, setBestStreak] = useState(0);
  const [pointsEarned, setPointsEarned] = useState(0);
  const [initialLoading, setInitialLoading] = useState(false);

  useEffect(() => {
    if (!currentUser) navigate('/');
  }, [currentUser, navigate]);

  const createMissingLettersPattern = (word) => {
    if (word.length <= 3) return word[0] + '_' + word.slice(2);
    const randomIndex = Math.floor(Math.random() * (word.length - 2)) + 1;
    return word.slice(0, randomIndex) + '_' + word.slice(randomIndex + 1);
  };

  const createDisplayPatternForSpeech = (word) => {
    const pattern = createMissingLettersPattern(word);
    return pattern.split('').map(char => char === '_' ? 'underscore' : char).join(' ');
  };

  const generateMockQuestion = (mode, difficulty = 'easy') => {
    const words = {
      easy: ['cat', 'dog', 'sun', 'hat', 'pen', 'cup', 'box', 'fan', 'egg', 'jam'],
      medium: ['house', 'water', 'apple', 'table', 'chair', 'clock', 'brush', 'cloud', 'dream', 'flower'],
      hard: ['elephant', 'computer', 'beautiful', 'mountain', 'garden', 'kitchen', 'pencil', 'basket', 'yellow', 'purple']
    };

    const randomWord = words[difficulty][Math.floor(Math.random() * words[difficulty].length)];

    return {
      id: Date.now(),
      display_text: mode === 'missing_letters'
        ? createMissingLettersPattern(randomWord)
        : randomWord,
      speak_text: randomWord,
      category: difficulty,
      ai_instruction: mode === 'missing_letters'
        ? `Complete the missing letter of ${randomWord}: ${createDisplayPatternForSpeech(randomWord)}`
        : `Spell the word: ${randomWord}`,
      complete_word: randomWord
    };
  };

  const startSession = async (selectedMode) => {
    setMode(selectedMode);
    setInitialLoading(true);
    setLoading(true);

    setQuestionsAnswered(0);
    setCorrectAnswers(0);
    setCurrentStreak(0);
    setBestStreak(0);
    setPointsEarned(0);
    setFeedback(null);
    setShowResults(false);
    setSessionSummary(null);

    try {
      await monitoringAPI.start({ user_id: currentUser.id, module: 'spelling' });

      const response = await spellingAPI.startSession({
        user_id: currentUser.id,
        mode: selectedMode
      });

      setSession(response.data.session_data);
      setCurrentQuestion(response.data.current_question);
    } catch {
      // FIX: Ensure mock question is generated immediately
      const mockQuestion = generateMockQuestion(selectedMode, 'easy');
      setCurrentQuestion(mockQuestion);
    } finally {
      setLoading(false);
      setInitialLoading(false);
    }
  };

  // ✅ REAL AI DIFFICULTY LOGIC
  const determineNextDifficulty = () => {
    const stress = cameraAnalysis?.stress_level || 0.5;
    const attention = cameraAnalysis?.attention_score || 50;

    const accuracy = questionsAnswered > 0
      ? (correctAnswers / questionsAnswered) * 100
      : 100;

    // High stress OR low attention → EASY
    if (stress > 0.7 || attention < 45) return 'easy';

    // High attention + good accuracy → HARD
    if (attention > 75 && accuracy > 70) return 'hard';

    // Otherwise → MEDIUM
    return 'medium';
  };

  const getNextQuestion = async () => {
    try {
      const next = await spellingAPI.getQuestion({
        user_id: currentUser.id,
        camera_data: cameraAnalysis,
        current_difficulty: determineNextDifficulty(),
        stress_level: cameraAnalysis?.stress_level || 0.5
      });

      setCurrentQuestion(next.data.question);
    } catch {
      // FIX: Ensure mode is passed correctly
      const mockQuestion = generateMockQuestion(mode, determineNextDifficulty());
      setCurrentQuestion(mockQuestion);
    }
  };

  const handleAnswerSubmit = async (answer) => {
    if (!currentQuestion) {
      console.error('No current question available');
      return;
    }
    
    setLoading(true);

    try {
      const response = await spellingAPI.submitAnswer({
        user_id: currentUser.id,
        answer,
        camera_data: cameraAnalysis,
        current_question: currentQuestion,
        stress_level: cameraAnalysis?.stress_level || 0.5
      });

      const result = response.data;
      setFeedback(result);

      const wasCorrect = result.is_correct;
      const newQuestionsAnswered = questionsAnswered + 1;

      const updatedCorrect = correctAnswers + (wasCorrect ? 1 : 0);
      const updatedPoints = pointsEarned + (wasCorrect ? (result.points_earned || 10) : 0);
      const updatedStreak = wasCorrect ? currentStreak + 1 : 0;
      const updatedBestStreak = Math.max(bestStreak, updatedStreak);

      setQuestionsAnswered(newQuestionsAnswered);
      setCorrectAnswers(updatedCorrect);
      setPointsEarned(updatedPoints);
      setCurrentStreak(updatedStreak);
      setBestStreak(updatedBestStreak);

      if (newQuestionsAnswered % QUESTIONS_PER_ROUND === 0) {
        const accuracy = Math.round((updatedCorrect / newQuestionsAnswered) * 100);

        const summary = {
          correct_answers: updatedCorrect,
          total_questions: newQuestionsAnswered,
          accuracy,
          points_earned: updatedPoints,
          current_streak: updatedStreak,
          best_streak: updatedBestStreak,
          session_complete: true,
          recommendations: [
            "Practice spelling words aloud daily",
            "Break words into syllables",
            "Use the words in sentences",
            updatedCorrect < 3 ? "Focus on letter patterns" : "Try more challenging words"
          ]
        };

        if (updateProgress) {
          updateProgress('spelling', {
            mode,
            totalPoints: updatedPoints,
            accuracy,
            sessionType: mode,
            timestamp: new Date().toISOString()
          });
        }

        setSessionSummary(summary);
        setShowResults(true);
        await monitoringAPI.stop({ user_id: currentUser.id });
        return;
      }

      setTimeout(() => {
        getNextQuestion();
        setFeedback(null);
      }, 1500);

    } catch {
      // FIX: Ensure fallback question is generated with correct mode
      const fallbackQuestion = generateMockQuestion(mode, determineNextDifficulty());
      setTimeout(() => {
        setCurrentQuestion(fallbackQuestion);
        setFeedback(null);
      }, 1500);
    } finally {
      setLoading(false);
    }
  };

  const handleContinue = async () => {
    setShowResults(false);
    setSessionSummary(null);
    setFeedback(null);
    setLoading(true);

    // ✅ Reset only streak, NOT total progress
    setCurrentStreak(0);

    try {
      await monitoringAPI.start({ user_id: currentUser.id, module: 'spelling' });

      const response = await spellingAPI.startSession({
        user_id: currentUser.id,
        mode: mode
      });

      setSession(response.data.session_data);
      setCurrentQuestion(response.data.current_question);
    } catch {
      const mockQuestion = generateMockQuestion(mode, 'easy');
      setCurrentQuestion(mockQuestion);
    } finally {
      setLoading(false);
    }
  };

  const handleExit = () => {
    monitoringAPI.stop({ user_id: currentUser.id });
    navigate('/modules');
  };

  if (!mode) {
    return (
      <div className="spelling-module mode-selection fade-in">
        <div className="mode-selection-card card">
          <h1>📝 Spelling Wizard</h1>
          <p>Choose your spelling challenge:</p>

          <div className="mode-options">
            <div className="mode-option card" onClick={() => startSession('missing_letters')}>
              <div className="mode-icon">🔤</div>
              <h3>Missing Letters</h3>
              <p>Fill in the missing letters to complete words</p>
              <button className="btn">Start Missing Letters</button>
            </div>

            <div className="mode-option card" onClick={() => startSession('complete_words')}>
              <div className="mode-icon">📝</div>
              <h3>Complete Words</h3>
              <p>Listen and spell complete words</p>
              <button className="btn btn-success">Start Complete Words</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (initialLoading) {
    return <LoadingSpinner message="Loading Spelling..." size="large" />;
  }

  if (showResults && sessionSummary) {
    return (
      <SpellingResults
        results={sessionSummary}
        onContinue={handleContinue}
        onExit={handleExit}
        mode={mode}
      />
    );
  }

  return (
    <div className="spelling-module fade-in">
      <div className="module-header card">
        <h1>📝 Spelling Wizard</h1>

        <div className="session-info">
          <span>Questions: {questionsAnswered + 1}</span>
          <span>Correct: {correctAnswers}</span>
          <span>Points: {pointsEarned}</span>
          <span>Streak: {currentStreak} 🔥</span>
          {currentQuestion?.category && <span>Level: {currentQuestion.category}</span>}
        </div>
      </div>

      <div className="module-content">
        <CameraFeed onAnalysisUpdate={setCameraAnalysis} />

        {mode === 'missing_letters' && currentQuestion && (
          <MissingLetters
            question={currentQuestion}
            onSubmit={handleAnswerSubmit}
            feedback={feedback}
            loading={loading}
            cameraAnalysis={cameraAnalysis}
          />
        )}

        {mode === 'complete_words' && currentQuestion && (
          <CompleteWords
            question={currentQuestion}
            onSubmit={handleAnswerSubmit}
            feedback={feedback}
            loading={loading}
            cameraAnalysis={cameraAnalysis}
          />
        )}

        {!currentQuestion && !loading && (
          <div className="no-question-message card">
            <p>No question available. Please try again.</p>
            <button onClick={() => startSession(mode)} className="btn">
              Restart Session
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SpellingModule;