import React, { useState, useEffect, useRef } from 'react';
import voiceService from '../../services/voiceService';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onRecordingComplete, expectedText, disabled }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);
  const [recognition, setRecognition] = useState(null);
  const [transcript, setTranscript] = useState('');
  const transcriptRef = useRef('');

  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isRecording]);

  const startRecording = async () => {
    console.log('🎤 Starting recording...');
    setError(null);
    setTranscript('');
    transcriptRef.current = '';
    
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        setError('Speech recognition not supported in this browser');
        return;
      }

      const recognitionInstance = new SpeechRecognition();
      recognitionInstance.lang = 'en-US';
      recognitionInstance.continuous = true;
      recognitionInstance.interimResults = false;

      recognitionInstance.onresult = (event) => {
        const text = Array.from(event.results)
          .map(result => result[0].transcript)
          .join(' ');
        setTranscript(text);
        transcriptRef.current = text;
        console.log('🗣️ YOU SAID:', text);
      };

      recognitionInstance.onerror = (event) => {
        console.error('❌ Recognition error:', event.error);
        setError(`Recognition error: ${event.error}`);
      };

      recognitionInstance.start();
      setRecognition(recognitionInstance);
      setIsRecording(true);
      setRecordingTime(0);
      setAudioUrl(null);
      console.log('✅ Recording started successfully');
    } catch (err) {
      setError(err.message);
      console.error('❌ Failed to start recording:', err);
    }
  };

  const stopRecording = async () => {
  console.log('⏹️ Stopping recognition...');
  
  if (recognition) {
    return new Promise((resolve) => {
      recognition.onend = () => {
        const finalTranscript = transcriptRef.current;
        
        setIsRecording(false);
        setAudioUrl('completed');
        setRecognition(null);

        console.log('✅ Recognition stopped');
        console.log('🗣️ Final transcript:', finalTranscript);

        if (onRecordingComplete) {
          console.log('📤 Calling onRecordingComplete with transcript');
          onRecordingComplete(finalTranscript);
        } else {
          setError('Submission function not available');
        }
        resolve();
      };
      
      recognition.stop();
    });
  }
};


  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="voice-recorder">
      <div className="recorder-controls">
        {!isRecording ? (
          <button
            className="btn record-btn"
            onClick={startRecording}
            disabled={disabled}
          >
            {audioUrl ? '🔄 Record Again' : '🎤 Start Recording'}
          </button>
        ) : (
          <button
            className="btn stop-btn"
            onClick={stopRecording}
          >
            ⏹️ Stop Recording ({formatTime(recordingTime)})
          </button>
        )}
      </div>

      {isRecording && (
        <div className="recording-indicator">
          <div className="pulse-animation"></div>
          <span>Recording... Speak clearly into your microphone!</span>
        </div>
      )}

      {audioUrl && (
        <div className="audio-preview">
          <p className="submission-note">✅ Recording submitted for evaluation!</p>
          {transcript && (
            <div className="transcript-display">
              <strong>You said:</strong> "{transcript}"
            </div>
          )}
        </div>
      )}

      {expectedText && (
        <div className="expected-text">
          <strong>Try saying:</strong> "{expectedText}"
        </div>
      )}

      {!isRecording && !audioUrl && (
        <div className="recording-instructions">
          <p>Click "Start Recording" and read the word aloud clearly</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {/* Debug info */}
      {process.env.NODE_ENV === 'development' && (
        <div className="debug-info">
          <small>Debug: {disabled ? 'Disabled' : 'Enabled'} | Expected: "{expectedText}"</small>
        </div>
      )}
    </div>
  );
};

export default VoiceRecorder;