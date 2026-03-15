import React, { useRef,useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { mathAPI, monitoringAPI } from '../../services/api';
import CameraFeed from '../common/CameraFeed';
import MathQuestion from './MathQuestion';
import MathResults from './MathResults';

const QUESTIONS_PER_ROUND = 5;

const MathModule = () => {
  const navigate = useNavigate();
  const { currentUser, updateProgress } = useUser();

  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);

  const [totalQuestionsAnswered, setTotalQuestionsAnswered] = useState(0);
  const [totalCorrectAnswers, setTotalCorrectAnswers] = useState(0);
  const [roundQuestionsAnswered, setRoundQuestionsAnswered] = useState(0);
  const [cumulativeQuestionCount, setCumulativeQuestionCount] = useState(0); // NEW - tracks actual question number

  const [currentDifficulty, setCurrentDifficulty] = useState('easy');
  const [cameraAnalysis, setCameraAnalysis] = useState(null);
  const [sessionSummary, setSessionSummary] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [showContinuePrompt, setShowContinuePrompt] = useState(false);

  // ✅ NEW TRIGGER STATE
  const [resetSerialTrigger, setResetSerialTrigger] = useState(0);

  const videoRef = useRef(null);
  const serialPortRef = useRef(null);
  const readerRef = useRef(null);
  const stopReadingRef = useRef(false);

  const [analysis, setAnalysis] = useState(null);
  const [serialConnected, setSerialConnected] = useState(false);

  const speak = (text) => {
    if (!text) return;
    const msg = new SpeechSynthesisUtterance(text);
    msg.rate = 0.95;
    msg.pitch = 1.1;
    msg.volume = 1;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(msg);
  };

  useEffect(() => {
    startSession();
  }, []);

  const startSession = async () => {
    setLoading(true);
    try {
      await monitoringAPI.start({ user_id: currentUser.id, module: 'math' });

      const response = await mathAPI.startSession({
        user_id: currentUser.id,
        difficulty: 'easy',
        age: currentUser.age
      });

      setSession({
        points_earned: 0,
        current_streak: 0,
        best_streak: 0,
        session_id: response.data.session_id
      });

      setSessionId(response.data.session_id);
      setCumulativeQuestionCount(0); // Initialize to 0
      setTotalQuestionsAnswered(0);
      setTotalCorrectAnswers(0);
      setRoundQuestionsAnswered(0);

      speak("Welcome to Math Practice! Let's solve some fun questions!");
      await getNewQuestion('easy');

    } catch {
      setFeedback({ is_correct: false, ai_feedback: "Math service unavailable." });
    } finally {
      setLoading(false);
    }
  };

  const adjustDifficulty = () => {
    if (!cameraAnalysis) return currentDifficulty;

    const attention = cameraAnalysis.attention_score || 50;
    const stress = cameraAnalysis.stress_level || 0.5;
    const accuracy = totalQuestionsAnswered > 0
      ? (totalCorrectAnswers / totalQuestionsAnswered) * 100
      : 100;

    let newDifficulty = currentDifficulty;

    if (attention < 45 || stress > 0.7) newDifficulty = "easy";
    else if (attention > 75 && accuracy > 70) newDifficulty = "hard";
    else newDifficulty = "medium";

    setCurrentDifficulty(newDifficulty);
    return newDifficulty;
  };

  const getNewQuestion = async (difficulty = null) => {
    setLoading(true);
    try {
      const adaptiveDifficulty = adjustDifficulty();

      const response = await mathAPI.getQuestion({
        user_id: currentUser.id,
        difficulty: difficulty || adaptiveDifficulty,
        stress_level: cameraAnalysis?.stress_level || 0.5
      });

      setCurrentQuestion(response.data.question);

    } catch {
      setFeedback({ is_correct: false, ai_feedback: "Failed to load question." });
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = async () => {
    if (!userAnswer.trim()) return;

    setLoading(true);
    try {
      const response = await mathAPI.submitAnswer({
        user_id: currentUser.id,
        question_id: currentQuestion.id,
        answer: userAnswer.trim(),
        difficulty: currentDifficulty
      });

      processAnswerResult(response.data);

    } catch {
      setFeedback({ is_correct: false, ai_feedback: "Submit failed." });
      setLoading(false);
    }
  };

  const processAnswerResult = (result) => {
    setFeedback(result);

    // Increment ALL counters
    setRoundQuestionsAnswered(prev => prev + 1);
    setTotalQuestionsAnswered(prev => prev + 1);
    setCumulativeQuestionCount(prev => prev + 1); // NEW - increments continuously

    if (result.is_correct) {
      setTotalCorrectAnswers(prev => prev + 1);
      speak("Great job! That's correct!");

      setSession(prev => {
        const newStreak = (prev?.current_streak || 0) + 1;
        return {
          ...prev,
          points_earned: (prev?.points_earned || 0) + 10,
          current_streak: newStreak,
          best_streak: Math.max(prev?.best_streak || 0, newStreak)
        };
      });

    } else {
      speak("Nice try! Keep going!");
      setSession(prev => ({ ...prev, current_streak: 0 }));
    }

    // Check if we've completed 5 questions in THIS ROUND
    if (roundQuestionsAnswered + 1 >= QUESTIONS_PER_ROUND) {
      setTimeout(() => setShowContinuePrompt(true), 1200);
    } else {
      setTimeout(() => {
        getNewQuestion();
        setUserAnswer('');
        setFeedback(null);
      }, 1200);
    }
  };

  const endSession = async () => {
    const accuracy = totalQuestionsAnswered > 0
      ? Math.round((totalCorrectAnswers / totalQuestionsAnswered) * 100)
      : 0;

    await mathAPI.endSession({
      user_id: currentUser.id,
      session_id: sessionId,
      final_score: accuracy,
      total_questions: totalQuestionsAnswered, // Send cumulative total
      correct_answers: totalCorrectAnswers
    });

    const summary = {
      correct_answers: totalCorrectAnswers,
      questions_answered: totalQuestionsAnswered, // Use cumulative total
      points_earned: session?.points_earned || 0,
      accuracy,
      current_streak: session?.current_streak || 0,
      best_streak: session?.best_streak || 0
    };

    setSessionSummary(summary);

    updateProgress("math", {
      totalPoints: summary.points_earned,
      accuracy: summary.accuracy,
      totalQuestions: summary.questions_answered
    });

    setShowResults(true);
  };

  const handleContinueSession = async () => {
    setResetSerialTrigger(prev => prev + 1); // ✅ Trigger child reset
    setShowContinuePrompt(false);
    setRoundQuestionsAnswered(0); // Reset ROUND counter only
    setFeedback(null);
    
    // Call backend to continue session
    try {
      await mathAPI.continueSession({
        user_id: currentUser.id,
        session_id: sessionId
      });
      
      // Get next question - keep existing difficulty or adjust
      await getNewQuestion(currentDifficulty);
    } catch (error) {
      console.error("Failed to continue session:", error);
      await getNewQuestion(currentDifficulty);
    }
  };

  const handleStopSession = async () => {
    setResetSerialTrigger(prev => prev + 1); // ✅ Trigger child reset
    setShowContinuePrompt(false);
    await endSession();
  };

  if (showContinuePrompt) {
  return (
    <MathResults
      results={{
        correct_answers: totalCorrectAnswers,
        questions_answered: totalQuestionsAnswered,
        points_earned: session?.points_earned || 0,
        accuracy:
          totalQuestionsAnswered > 0
            ? Math.round((totalCorrectAnswers / totalQuestionsAnswered) * 100)
            : 0,
        current_streak: session?.current_streak || 0,
        best_streak: session?.best_streak || 0
      }}
      onContinue={handleContinueSession}
      onExit={handleStopSession}
      module="math"
      isCheckpoint={true}
    />
  );
}

  if (showResults && sessionSummary) {
    return <MathResults results={sessionSummary} module="math" />;
  }

  return (
    <div className="math-module fade-in">
      <div className="module-header card">
        <h1>🔢 Math Adventure</h1>

        <div className="session-info">
          <span>Question: {cumulativeQuestionCount + 1}</span> {/* Shows actual question number */}
          <span>Round: {roundQuestionsAnswered + 1}/{QUESTIONS_PER_ROUND}</span>
          <span>Total: {totalQuestionsAnswered + 1}/?</span> {/* Optional */}
          <span>Points: {session?.points_earned || 0}</span>
          <span>🔥 Streak: {session?.current_streak || 0}</span>
          <span>Difficulty: {currentDifficulty}</span>
        </div>
      </div>

      <CameraFeed 
        onAnalysisUpdate={setCameraAnalysis} 
        resetSerialTrigger={resetSerialTrigger} 
      />

      {currentQuestion && (
        <MathQuestion
          question={currentQuestion}
          userAnswer={userAnswer}
          onAnswerChange={setUserAnswer}
          onSubmit={handleAnswerSubmit}
          feedback={feedback}
          loading={loading}
          cameraAnalysis={cameraAnalysis}
        />
      )}
    </div>
  );
};

export default MathModule;
