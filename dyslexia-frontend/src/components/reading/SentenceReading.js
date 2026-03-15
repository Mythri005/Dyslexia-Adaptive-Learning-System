import React, { useEffect, useState } from 'react';
import voiceService from '../../services/voiceService';
import './SentenceReading.css';

const SentenceReading = ({ item, feedback, loading, cameraAnalysis }) => {
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [sentencePracticeMode, setSentencePracticeMode] = useState(false);

  useEffect(() => {
    if (item?.ai_instruction) {
      voiceService.playAudio(item.ai_instruction);
    }
    
    // Reset mode when item changes
    setCurrentWordIndex(item?.current_word_index || 0);
    setSentencePracticeMode(feedback?.sentence_practice_mode || false);
  }, [item]);

  useEffect(() => {
    if (feedback?.ai_feedback) {
      voiceService.playAudio(feedback.ai_feedback);
    }
    if (feedback?.sentence_practice_mode) {
      setSentencePracticeMode(true);
    }
  }, [feedback]);

  const handleHearSentence = () => {
    if (item?.full_text) {
      voiceService.playAudio(item.full_text);
    }
  };

  const handleHearSentenceSlowly = () => {
    if (item?.full_text) {
      voiceService.playAudio(item.full_text, { rate: 0.6 });
    }
  };

  const handleHearCurrentWord = () => {
    if (item?.speak_text) {
      voiceService.playAudio(item.speak_text);
    }
  };

  const renderSentenceWithHighlight = () => {
    if (!item?.full_text) return null;
    
    return (
      <div className="sentence-display">
        {item.full_text}
      </div>
    );
  };

  if (!item) return null;

  return (
    <div className="sentence-reading card">
      {cameraAnalysis?.needs_help && (
        <div className="help-banner">
          🆘 {cameraAnalysis.help_message}
        </div>
      )}

      <div className="reading-header">
        <h2>Sentence Reading Practice</h2>
        {item?.category && (
          <span className="difficulty-badge">
            {item.category.toUpperCase()}
          </span>
        )}
      </div>

      <div className="reading-content">
        <div className="instruction">
          {sentencePracticeMode ? (
            <p className="complete-sentence-instruction">
              🎯 <strong>Now say the complete sentence:</strong>
            </p>
          ) : (
            <p>Practice reading the sentence:</p>
          )}
        </div>

        <div className="sentence-section">
          {renderSentenceWithHighlight()}
        </div>

        {sentencePracticeMode && (
          <div className="complete-sentence-practice">
            <div className="complete-sentence-display">
              "{item.full_text}"
            </div>
            <div className="practice-badge">
              🔴 Click record and say the complete sentence
            </div>
          </div>
        )}

        <div className="audio-controls">
          <button onClick={handleHearSentence} className="btn hear-btn">
            🔊 Hear Full Sentence
          </button>

          <button onClick={handleHearSentenceSlowly} className="btn slow-btn">
            🐢 Hear Sentence Slowly
          </button>
        </div>
      </div>
    </div>
  );
};

export default SentenceReading;