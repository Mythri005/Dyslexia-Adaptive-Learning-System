import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { readingAPI, monitoringAPI, checkBackendConnectivity } from '../../services/api';
import CameraFeed from '../common/CameraFeed';
import VoiceRecorder from '../common/VoiceRecorder';
import WordReading from './WordReading';
import SentenceReading from './SentenceReading';
import ParagraphReading from './ParagraphReading';
import ReadingResults from './ReadingResults';
import './ReadingModule.css';

const ReadingModule = () => {
  const navigate = useNavigate();
  const { currentUser, updateProgress } = useUser();
  const [mode, setMode] = useState(null);
  const [session, setSession] = useState(null);
  const [currentItem, setCurrentItem] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [cameraAnalysis, setCameraAnalysis] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [sessionSummary, setSessionSummary] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [itemsAttempted, setItemsAttempted] = useState(0);
  const [pointsEarned, setPointsEarned] = useState(0);
  const [totalCorrectAnswers, setTotalCorrectAnswers] = useState(0);
  const [currentStreak, setCurrentStreak] = useState(0);
  const [currentDifficulty, setCurrentDifficulty] = useState('easy');
  const [backendStatus, setBackendStatus] = useState('checking');
  const [error, setError] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    if (!currentUser) {
      navigate('/');
      return;
    }

    // Check backend connectivity
    const checkBackend = async () => {
      console.log('🔍 Checking backend connectivity...');
      const status = await checkBackendConnectivity();
      setBackendStatus(status.connected ? 'connected' : 'disconnected');
      console.log('📡 Backend status:', status);
      
      if (!status.connected) {
        setError(`Backend server not connected: ${status.error}`);
      }
    };
    
    checkBackend();
  }, [currentUser, navigate]);

  // ✅ FIXED: Correct accuracy calculation using correct answers, not points
  const determineNextDifficulty = (isCorrect, stressLevel) => {
    const stress = stressLevel || cameraAnalysis?.stress_level || 0.5;
    const attention = cameraAnalysis?.attention_score || 50;

    // ✅ CORRECTED: Calculate accuracy based on correct answers, not points
    const correctAnswers = totalCorrectAnswers;

    const accuracy = itemsAttempted > 0
      ? (correctAnswers / itemsAttempted) * 100
      : 100;

    console.log(`📊 Difficulty calculation - Items: ${itemsAttempted}, Points: ${pointsEarned}, Correct: ${correctAnswers}, Accuracy: ${accuracy}%`);

    // 😰 HIGH STRESS or 👀 LOW ATTENTION → EASY
    if (stress > 0.7 || attention < 45) {
      return 'easy';
    }

    // ❌ Wrong answer + stress → downgrade
    if (!isCorrect && stress > 0.55) {
      return 'easy';
    }

    // 🎯 HIGH ATTENTION + GOOD ACCURACY → HARD
    if (attention > 75 && accuracy > 70 && currentStreak >= 2) {
      if (currentDifficulty === 'easy') return 'medium';
      if (currentDifficulty === 'medium') return 'hard';
    }

    // ❌ Repeated mistakes → downgrade
    if (!isCorrect && currentDifficulty === 'hard') return 'medium';
    if (!isCorrect && currentDifficulty === 'medium') return 'easy';

    // Default → maintain current
    return currentDifficulty;
  };

  const startSession = async (selectedMode) => {
    console.log('🚀 Starting reading session for mode:', selectedMode);
    
    setMode(selectedMode);
    setLoading(true);
    setItemsAttempted(0);
    setPointsEarned(0);
    setCurrentStreak(0);
    setTotalCorrectAnswers(0);
    setCurrentDifficulty('easy');
    setFeedback(null);
    setError(null);
    setSession(null);
    setCurrentItem(null);
    setSessionId(null);
    setShowResults(false);
    setSessionSummary(null);
    setCameraAnalysis(null);
    
    try {
      // Stop any existing monitoring first
      if (currentUser) {
        try {
          await monitoringAPI.stop({ user_id: currentUser.id });
        } catch (e) {
          console.log('No active session to stop');
        }
      }

      // Start monitoring
      await monitoringAPI.start({
        user_id: currentUser.id,
        module: 'reading',
        mode: selectedMode
      });

      // Start reading session with backend
      const response = await readingAPI.startSession({
        user_id: currentUser.id,
        mode: selectedMode,
        difficulty: 'easy',
        age: currentUser.age
      });

      console.log('✅ Session started successfully:', response.data);
      
      setSession(response.data.session_data);
      setSessionId(response.data.session_id);
      setCurrentItem(response.data.current_item);
      
    } catch (error) {
      console.error('❌ Error starting reading session:', error);
      setError(`Failed to start session: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getNextItem = async (isCorrect) => {
  if (showResults) return;
  try {
    const nextDifficulty = determineNextDifficulty(isCorrect, cameraAnalysis?.stress_level || 0.5);
    setCurrentDifficulty(nextDifficulty);

    console.log(`🎚️ Getting next item with difficulty: ${nextDifficulty}`);
    console.log('📝 Previous item ID:', currentItem?.id);
    
    // ✅ CORRECTED: Calculate correct answers from points
    const correctAnswers = totalCorrectAnswers;
    
    const nextItemResponse = await readingAPI.getItem({
      user_id: currentUser.id,
      mode: mode,
      difficulty: nextDifficulty,
      stress_level: cameraAnalysis?.stress_level || 0.5,
      performance: {
        correct_pronunciations: correctAnswers,
        total_items: itemsAttempted,
        accuracy: itemsAttempted > 0
          ? Math.round((correctAnswers / itemsAttempted) * 100)
          : 0,
        current_streak: currentStreak
      },
      previous_item: currentItem
    });

    console.log('🆕 Next item received:', nextItemResponse.data.item);
    setCurrentItem(nextItemResponse.data.item);
    
  } catch (error) {
    console.error('❌ Error getting next item:', error);
    setError(`Failed to load next item: ${error.message}`);
  }
};

  const handlePronunciationSubmit = async (spokenText) => {
    console.log('🎯 handlePronunciationSubmit called');
    console.log('🗣️ Spoken text:', spokenText);

    if (!currentItem) {
      const errorMsg = 'No current item available';
      console.error('❌', errorMsg);
      setError(errorMsg);
      return;
    }

    if (!spokenText || spokenText.trim() === '') {
      const errorMsg = 'No speech recognized';
      console.error('❌', errorMsg);
      setError(errorMsg);
      return;
    }

    if (!currentUser) {
      const errorMsg = 'No user logged in';
      console.error('❌', errorMsg);
      setError(errorMsg);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('📤 Submitting text for evaluation...');
      
      const evaluationData = {
        user_id: currentUser.id,
        transcribed_text: spokenText.trim(),
        expected_text: currentItem.expected_pronunciation || currentItem.speak_text || currentItem.full_text,
        current_item: currentItem,
        camera_data: cameraAnalysis,
        mode: mode,
        difficulty: currentItem.category || currentDifficulty
      };

      console.log('📝 Evaluation data prepared');
      
      const response = await readingAPI.evaluatePronunciation(evaluationData);
      console.log('✅ Evaluation response received:', response.data);
      
      const result = response.data;
      
      // Log transcription
      const transcript = result.spoken_text || result.transcription || result.text || result.recognized_text;
      if (transcript) {
        console.log('🗣️ YOU SAID:', transcript);
        if (result.pronunciation_score) {
          console.log('📊 Confidence:', Math.round(result.pronunciation_score * 100) + '%');
        }
      }
      
      setFeedback(result);

      // Update progress based on result
      const isCorrect = result.is_correct;
      let pointsAdded = 0;
      
      if (isCorrect) {
        pointsAdded = result.points_earned || 10;
        setPointsEarned(prev => prev + pointsAdded);
        setCurrentStreak(prev => prev + 1);
        setTotalCorrectAnswers(prev => prev + 1);
        console.log(`🎉 Correct! +${pointsAdded} points, streak: ${currentStreak + 1}`);
      } else {
        setCurrentStreak(0);
        console.log('💡 Incorrect, streak reset to 0');
      }

      // 🔧 FIXED: Only increment itemsAttempted when backend says move_to_next
      if (result.move_to_next) {
        const newItemsAttempted = itemsAttempted + 1;
        setItemsAttempted(newItemsAttempted);
        console.log(`📈 Progress: ${newItemsAttempted}/5 items completed`);
      }

      // 🔥 FIXED: Check for checkpoint_reached - USE LOCAL STATE, NOT BACKEND
      if (result.checkpoint_reached) {
        console.log('🏁 Checkpoint reached, saving progress to database...');

        try {
          // 🔥 END SESSION TO SAVE TO DATABASE
          await readingAPI.endSession({
            user_id: currentUser.id,
            mode: mode,
            session_id: sessionId
          });

          console.log('✅ Progress saved to database');

          // 🔥 CRITICAL FIX: Use local state for results, NOT backend getProgress
          // Like Math and Spelling modules do
          const sessionCorrect = totalCorrectAnswers + (isCorrect ? 1 : 0);
          const sessionAttempted = itemsAttempted + 1;
          const sessionPoints = pointsEarned + (isCorrect ? (result.points_earned || 10) : 0);

          console.log('📊 Session stats - Correct:', sessionCorrect, 'Attempted:', sessionAttempted, 'Points:', sessionPoints);

          const sessionSummaryData = {
            correct_pronunciations: sessionCorrect,
            total_questions: sessionAttempted,
            accuracy: Math.round((sessionCorrect / sessionAttempted) * 100),
            points_earned: sessionPoints,
            current_streak: sessionCorrect,
            best_streak: sessionCorrect,

            grade:
              sessionCorrect >= 5 ? 'A+' :
              sessionCorrect >= 4 ? 'A' :
              sessionCorrect >= 3 ? 'B' :
              sessionCorrect >= 2 ? 'C' :
              sessionCorrect >= 1 ? 'D' : 'F',

            module: 'reading',
            mode,
            isCheckpoint: true
          };

          setSessionSummary(sessionSummaryData);

          // 🔥 SAVE TO LOCALSTORAGE FOR PROGRESS REPORT
          try {
            const storedProgress = JSON.parse(localStorage.getItem('dyslexia_userProgress') || '{}');

            if (!storedProgress.reading) {
              storedProgress.reading = {
                sessionsCompleted: 0,
                totalPoints: 0,
                totalAccuracy: 0,
                averageAccuracy: 0
              };
            }

            const reading = storedProgress.reading;

            reading.sessionsCompleted = (reading.sessionsCompleted || 0) + 1;
            reading.totalPoints = (reading.totalPoints || 0) + (sessionPoints || 0);

            const oldTotalAccuracy = (reading.totalAccuracy || 0) * (reading.sessionsCompleted - 1);
            const newTotalAccuracy = oldTotalAccuracy + (sessionSummaryData.accuracy || 0);

            reading.totalAccuracy = newTotalAccuracy / reading.sessionsCompleted;
            reading.averageAccuracy = Math.round(reading.totalAccuracy);

            localStorage.setItem('dyslexia_userProgress', JSON.stringify(storedProgress));
            
            if (updateProgress) {
              updateProgress("reading", {
                totalPoints: sessionPoints || 0,
                accuracy: sessionSummaryData.accuracy || 0,
                totalQuestions: 5
              });
            }
            
            console.log('✅ Saved checkpoint progress to localStorage:', storedProgress.reading);
            
          } catch (storageError) {
            console.error('Error saving to localStorage:', storageError);
          }

          setShowResults(true);
          
        } catch (error) {
          console.error('❌ Error saving progress at checkpoint:', error);
          // Fallback to showing summary without saving
          setSessionSummary({
            correct_pronunciations: totalCorrectAnswers,
            total_questions: 5,
            accuracy: Math.round((totalCorrectAnswers / (itemsAttempted + 1)) * 100),
            points_earned: pointsEarned,
            current_streak: currentStreak,
            best_streak: currentStreak,
            grade: "—",
            recommendations: [],
            module: 'reading',
            mode,
            isCheckpoint: true
          });
          setShowResults(true);
        }
        
      } else if (result.move_to_next) {
        // Get next item after a short delay
        console.log('⏳ Getting next item in 2 seconds...');
        
        setTimeout(async () => {
          await getNextItem(isCorrect);
          setFeedback(null);
        }, 2000);
      }

    } catch (error) {
      console.error('❌ Error in pronunciation evaluation:', error);
      
      let errorMessage = 'Evaluation failed. ';
      
      if (error.response) {
        errorMessage += `Server error: ${error.response.status} - ${error.response.data?.error || error.response.statusText}`;
      } else if (error.request) {
        errorMessage += 'No response from server. Please check if the backend is running.';
      } else {
        errorMessage += error.message;
      }
      
      setError(errorMessage);
      
      // Provide fallback feedback
      setFeedback({
        is_correct: false,
        ai_feedback: "Evaluation service unavailable. Please try again.",
        pronunciation_score: 0,
        points_earned: 0,
        move_to_next: true
      });
      
    } finally {
      setLoading(false);
      setIsRecording(false);
    }
  };

  const endSession = async (wasCorrect) => {
    try {
      // ✅ FIXED: Pass userId directly, not as object
      const progressResponse = await readingAPI.getProgress(currentUser.id);

      const backendSummary = progressResponse.data;

      await readingAPI.endSession({
        user_id: currentUser.id,
        session_id: sessionId,
        final_score: backendSummary.accuracy || 0,
        mode: mode
      });

      const summary = {
        ...backendSummary,
        module: 'reading',
        mode,
        isFinal: true
      };

      console.log('📊 Session summary:', summary);
      
      if (updateProgress) {
        updateProgress('reading', {
          mode,
          totalPoints: backendSummary.points_earned || 0,
          accuracy: backendSummary.accuracy || 0,
          sessionType: mode,
          timestamp: new Date().toISOString()
        });
      }

      // 🔥 SAVE TO LOCALSTORAGE FOR PROGRESS REPORT
      try {
        // Get existing progress from localStorage
        const storedProgress = JSON.parse(localStorage.getItem('dyslexia_userProgress') || '{}');
        
        // Initialize reading if not exists
        if (!storedProgress.reading) {
          storedProgress.reading = {
            sessionsCompleted: 0,
            totalPoints: 0,
            totalAccuracy: 0,
            averageAccuracy: 0
          };
        }
        
        // Update reading progress
        const reading = storedProgress.reading;
        reading.sessionsCompleted = (reading.sessionsCompleted || 0) + 1;
        reading.totalPoints = (reading.totalPoints || 0) + (backendSummary.points_earned || 0);
        
        // Calculate running average accuracy
        const oldTotalAccuracy = (reading.totalAccuracy || 0) * (reading.sessionsCompleted - 1);
        const newTotalAccuracy = oldTotalAccuracy + (backendSummary.accuracy || 0);
        reading.totalAccuracy = newTotalAccuracy / reading.sessionsCompleted;
        reading.averageAccuracy = Math.round(reading.totalAccuracy);
        
        // Save back to localStorage
        localStorage.setItem('dyslexia_userProgress', JSON.stringify(storedProgress));
        console.log('✅ Saved reading progress to localStorage:', storedProgress.reading);
        
      } catch (storageError) {
        console.error('Error saving to localStorage:', storageError);
      }

      setSessionSummary(summary);
      setShowResults(true);

      await monitoringAPI.stop({ user_id: currentUser.id });

    } catch (error) {
      console.error('Error ending session:', error);

      // Fallback to manual calculation if backend fails
      const totalAttempted = itemsAttempted + 1;
      const correctCount = wasCorrect ? totalAttempted : totalAttempted - 1;
      const safeTotal = totalAttempted > 0 ? totalAttempted : 1;
      const accuracy = Math.round((correctCount / safeTotal) * 100);
      const totalPoints = pointsEarned + (wasCorrect ? 10 : 0);

      setSessionSummary({
        correct_pronunciations: correctCount,
        total_questions: safeTotal,
        accuracy,
        points_earned: totalPoints,
        current_streak: wasCorrect ? currentStreak : 0,
        best_streak: currentStreak,
        grade: accuracy >= 90 ? 'A+' : accuracy >= 80 ? 'A' : accuracy >= 70 ? 'B' : accuracy >= 60 ? 'C' : accuracy >= 50 ? 'D' : 'F',
        recommendations: getRecommendations(wasCorrect, cameraAnalysis?.stress_level),
        module: 'reading',
        mode,
        isFinal: true
      });

      setShowResults(true);
    }
  };

  const getRecommendations = (isCorrect, stressLevel) => {
    const recommendations = [];
    
    if (!isCorrect) {
      if (mode === 'words') {
        recommendations.push("Practice saying the word slowly and clearly");
        recommendations.push("Break the word into individual sounds");
        recommendations.push("Listen carefully to the pronunciation");
      } else if (mode === 'sentences') {
        recommendations.push("Read each word in the sentence separately first");
        recommendations.push("Practice the sentence with proper pauses");
        recommendations.push("Focus on difficult words in the sentence");
      } else {
        recommendations.push("Read one sentence at a time");
        recommendations.push("Focus on difficult words in the paragraph");
        recommendations.push("Practice reading with expression");
      }
    }
    
    if (stressLevel > 0.6) {
      recommendations.push("Take a deep breath before reading");
      recommendations.push("Read at a comfortable pace - no need to rush");
      recommendations.push("Remember it's okay to make mistakes");
    }
    
    if (isCorrect) {
      recommendations.push("Great job! Try more challenging materials");
      recommendations.push("Practice reading with expression and confidence");
      recommendations.push("Continue reading aloud every day");
    }
    
    return recommendations.length > 0 ? recommendations : [
      "Practice regularly for best results",
      "Read aloud every day to improve",
      "Try different types of reading materials"
    ];
  };

  // ✅ FIXED: Continue with proper reset for new set of questions
  // ✅ FIXED: Continue with proper reset for new set of questions
  const handleContinue = async () => {
    try {

      console.log("🔄 Continuing with new session...");

      setShowResults(false);
      setFeedback(null);

      await readingAPI.continueSession({
        user_id: currentUser.id,
        session_id: sessionId
      });

      // DO NOT reset totals
      setCurrentStreak(0);

      setCurrentItem(null);

      // load fresh question
      const response = await readingAPI.startSession({
        user_id: currentUser.id,
        mode: mode,
        difficulty: 'easy',
        age: currentUser.age
      });

      setSession(response.data.session_data);
      setSessionId(response.data.session_id);
      setCurrentItem(response.data.current_item);

    } catch (error) {
      console.error("Continue session error:", error);
    }
  };

  const handleExit = () => {
    if (currentUser) {
      monitoringAPI.stop({ user_id: currentUser.id });
    }
    
    // 🔥 FORCE RESET ALL STATE BEFORE NAVIGATING
    setMode(null);
    setSession(null);
    setCurrentItem(null);
    setFeedback(null);
    setLoading(false);
    setCameraAnalysis(null);
    setShowResults(false);
    setSessionSummary(null);
    setItemsAttempted(0);
    setPointsEarned(0);
    setCurrentStreak(0);
    setTotalCorrectAnswers(0);
    setCurrentDifficulty('easy');
    setError(null);
    setSessionId(null);
    
    navigate('/modules');
  };

  const handleRecordingStart = () => {
    setIsRecording(true);
    setError(null);
  };

  const handleRecordingComplete = (spokenText) => {
    console.log('🎤 Recording complete, submitting for evaluation...');
    handlePronunciationSubmit(spokenText);
  };

  const retrySession = () => {
    if (mode) {
      startSession(mode);
    }
  };

  if (!mode) {
    return (
      <div className="reading-module mode-selection fade-in">
        <div className="mode-selection-card card">
          <h1>📖 Reading Master</h1>
          <p>Choose your reading practice:</p>
          
          {backendStatus === 'disconnected' && (
            <div className="backend-warning">
              ⚠️ Backend server not connected. Please make sure the server is running on port 5001.
              <br />
              <small>Error: {error}</small>
            </div>
          )}
          
          <div className="mode-options">
            <div className="mode-option card" onClick={() => startSession('words')}>
              <div className="mode-icon">🔤</div>
              <h3>Word Reading</h3>
              <p>Practice reading individual words with AI feedback</p>
              <ul>
                <li>✓ Uses word_dataset1.xlsx</li>
                <li>✓ Clear word pronunciation</li>
                <li>✓ Instant feedback</li>
                <li>✓ Build vocabulary</li>
              </ul>
              <button className="btn">Start Word Reading</button>
            </div>
            
            <div className="mode-option card" onClick={() => startSession('sentences')}>
              <div className="mode-icon">📝</div>
              <h3>Sentence Reading</h3>
              <p>Read complete sentences word by word</p>
              <ul>
                <li>✓ Uses sentences1.xlsx</li>
                <li>✓ Word-by-word practice</li>
                <li>✓ Sentence fluency</li>
                <li>✓ Context understanding</li>
              </ul>
              <button className="btn btn-success">Start Sentence Reading</button>
            </div>

            <div className="mode-option card" onClick={() => startSession('paragraphs')}>
              <div className="mode-icon">📄</div>
              <h3>Paragraph Reading</h3>
              <p>Practice reading full paragraphs</p>
              <ul>
                <li>✓ Uses paragraphs1.xlsx</li>
                <li>✓ Extended reading practice</li>
                <li>✓ Comprehension skills</li>
                <li>✓ Reading endurance</li>
              </ul>
              <button className="btn btn-warning">Start Paragraph Reading</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading && !session) {
    return (
      <div className="reading-module loading">
        <div className="loading-spinner">📖</div>
        <h2>Starting {mode === 'words' ? 'Word' : mode === 'sentences' ? 'Sentence' : 'Paragraph'} Reading...</h2>
        <p>Loading from server...</p>
      </div>
    );
  }

  if (showResults && sessionSummary) {
    return (
      <ReadingResults 
        results={sessionSummary}
        onContinue={handleContinue}
        onExit={handleExit}
        mode={mode}
        isCheckpoint={true}
      />
    );
  }

  const getModeTitle = () => {
    switch (mode) {
      case 'words': return 'Word Reading';
      case 'sentences': return 'Sentence Reading';
      case 'paragraphs': return 'Paragraph Reading';
      default: return 'Reading Practice';
    }
  };

  return (
    <div className="reading-module fade-in">
      <div className="module-header card">
        <h1>📖 Reading Master - {getModeTitle()}</h1>
        <p>Practice your reading skills! Listen and repeat after the AI.</p>
        
        {error && (
          <div className="error-banner">
            ⚠️ {error}
            <button onClick={retrySession} className="btn btn-small">Retry</button>
          </div>
        )}
        
        <div className="session-info">
          {/* ✅ Shows current question position without hardcoded limit */}
          <span>Question: {itemsAttempted + 1}</span>
          <span>Points: {pointsEarned}</span>
          <span>Streak: {currentStreak} 🔥</span>
          <span>Level: {currentDifficulty.toUpperCase()}</span>
        </div>

        {cameraAnalysis?.stress_level > 0.7 && (
          <div className="stress-alert">
            😊 Take your time and breathe. I'll help you with easier reading materials.
          </div>
        )}
      </div>

      <div className="module-content">
        <div className="monitoring-section">
          <CameraFeed 
            onAnalysisUpdate={setCameraAnalysis}
            currentQuestion={currentItem?.display_text || currentItem?.full_text}
          />
        </div>

        <div className="reading-content">
          {mode === 'words' && currentItem && (
            <WordReading
              item={currentItem}
              feedback={feedback}
              loading={loading}
              cameraAnalysis={cameraAnalysis}
            />
          )}
          
          {mode === 'sentences' && currentItem && (
            <SentenceReading
              item={currentItem}
              feedback={feedback}
              loading={loading}
              cameraAnalysis={cameraAnalysis}
            />
          )}
          
          {mode === 'paragraphs' && currentItem && (
            <ParagraphReading
              item={currentItem}
              feedback={feedback}
              loading={loading}
              cameraAnalysis={cameraAnalysis}
            />
          )}

          {!currentItem && !loading && (
            <div className="no-item-message card">
              <h3>No reading item available</h3>
              <p>Please check if the server is running and try again.</p>
              <button onClick={retrySession} className="btn">
                Retry Session
              </button>
            </div>
          )}

          {currentItem && (
            <div className="recording-section">
              <VoiceRecorder
                onRecordingStart={handleRecordingStart}
                onRecordingComplete={handleRecordingComplete}
                expectedText={currentItem.expected_pronunciation || currentItem.speak_text || currentItem.full_text}
                disabled={loading || isRecording}
              />
            </div>
          )}

          {cameraAnalysis?.needs_help && (
            <div className="help-message">
              <div className="help-banner">
                🆘 {cameraAnalysis.help_message}
              </div>
            </div>
          )}

          {feedback && (
            <div className={`reading-feedback ${feedback.is_correct ? 'correct' : 'incorrect'}`}>
              <div className="feedback-header">
                {feedback.is_correct ? '🎉 Excellent Reading!' : '💡 Practice Tip'}
                {feedback.is_correct && feedback.points_earned > 0 && (
                  <span className="points-badge">+{feedback.points_earned} points!</span>
                )}
              </div>
              <div className="feedback-message">
                {feedback.ai_feedback}
              </div>
              {feedback.pronunciation_score && (
                <div className="pronunciation-score">
                  Pronunciation Score: {Math.round(feedback.pronunciation_score * 100)}%
                </div>
              )}
              {!feedback.is_correct && cameraAnalysis?.stress_level > 0.6 && (
                <div className="stress-help">
                  😊 Take a deep breath and try again. You're doing great!
                </div>
              )}
            </div>
          )}

          {loading && (
            <div className="loading-indicator">
              <div className="loading-spinner-small"></div>
              <p>Evaluating your pronunciation...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReadingModule;