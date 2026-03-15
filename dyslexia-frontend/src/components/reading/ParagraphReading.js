import React, { useEffect, useState } from 'react';
import voiceService from '../../services/voiceService';
import './ParagraphReading.css';

const ParagraphReading = ({ item, feedback, loading, cameraAnalysis }) => {
  const [currentSentenceIndex, setCurrentSentenceIndex] = useState(0);
  const [currentWordIndex, setCurrentWordIndex] = useState(0);
  const [sentences, setSentences] = useState([]);

  useEffect(() => {
    if (item?.full_text) {
      // Split paragraph into sentences
      const sentenceList = item.full_text.split(/[.!?]+/).filter(s => s.trim());
      setSentences(sentenceList);
    }
  }, [item]);

  useEffect(() => {
    if (item?.ai_instruction) {
      voiceService.playAudio(item.ai_instruction);
    }
    
    if (item?.speak_text && currentSentenceIndex < sentences.length) {
      // Speak the current word after a short delay
      setTimeout(() => {
        voiceService.playAudio(item.speak_text);
      }, 1500);
    }
  }, [item, currentSentenceIndex, sentences]);

  useEffect(() => {
    if (feedback?.ai_feedback) {
      voiceService.playAudio(feedback.ai_feedback);
    }
  }, [feedback]);

  const currentSentence = sentences[currentSentenceIndex] || '';
  const words = currentSentence ? currentSentence.trim().split(' ') : [];
  const currentWord = words[currentWordIndex] || '';

  const handleHearParagraph = () => {
    if (item?.full_text) {
      voiceService.playAudio(item.full_text);
    }
  };

  const handleHearParagraphSlowly = () => {
    if (item?.full_text) {
      voiceService.playAudio(item.full_text, { rate: 0.6 });
    }
  };

  const handleHearSentence = () => {
    if (currentSentence) {
      voiceService.playAudio(currentSentence);
    }
  };

  const handleHearCurrentWord = () => {
    if (currentWord) {
      voiceService.playAudio(currentWord);
    }
  };

  const handleNextWord = () => {
    if (currentWordIndex < words.length - 1) {
      setCurrentWordIndex(currentWordIndex + 1);
    } else if (currentSentenceIndex < sentences.length - 1) {
      // Move to next sentence
      setCurrentSentenceIndex(currentSentenceIndex + 1);
      setCurrentWordIndex(0);
    }
  };

  const handlePreviousWord = () => {
    if (currentWordIndex > 0) {
      setCurrentWordIndex(currentWordIndex - 1);
    } else if (currentSentenceIndex > 0) {
      // Move to previous sentence
      setCurrentSentenceIndex(currentSentenceIndex - 1);
      const prevWords = sentences[currentSentenceIndex - 1].trim().split(' ');
      setCurrentWordIndex(prevWords.length - 1);
    }
  };

  const handleNextSentence = () => {
    if (currentSentenceIndex < sentences.length - 1) {
      setCurrentSentenceIndex(currentSentenceIndex + 1);
      setCurrentWordIndex(0);
    }
  };

  const handlePreviousSentence = () => {
    if (currentSentenceIndex > 0) {
      setCurrentSentenceIndex(currentSentenceIndex - 1);
      setCurrentWordIndex(0);
    }
  };

  const renderParagraph = () => {
    if (!item?.full_text) return null;

    return (
      <div className="paragraph-display">
        {sentences.map((sentence, index) => (
          <div key={index} className="paragraph-sentence">
            {sentence}.
          </div>
        ))}
      </div>
    );
  };

  if (!item) return null;

  return (
    <div className="paragraph-reading card">
      {cameraAnalysis?.needs_help && (
        <div className="help-banner">
          🆘 {cameraAnalysis.help_message}
        </div>
      )}

      <div className="reading-header">
        <h2>Paragraph Reading Practice</h2>
        {item?.category && (
          <span className="difficulty-badge">
            {item.category.toUpperCase()}
          </span>
        )}
      </div>

      <div className="reading-content">
        <div className="instruction">
          <p>Practice reading this paragraph sentence by sentence, word by word:</p>
        </div>

        <div className="paragraph-section">
          {renderParagraph()}
        </div>

        <div className="audio-controls">
          <button onClick={handleHearParagraph} className="btn hear-btn">
            📖 Hear Full Paragraph
          </button>

          <button onClick={handleHearParagraphSlowly} className="btn slow-btn">
            🐢 Hear Paragraph Slowly
          </button>
        </div>
      </div>
    </div>
  );
};

export default ParagraphReading;