import { useState, useEffect } from 'react';
import voiceService from '../services/voiceService';

export const useVoiceRecording = (onRecordingComplete) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState(null);

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
    try {
      const result = await voiceService.startRecording();
      if (result.success) {
        setIsRecording(true);
        setRecordingTime(0);
        setAudioUrl(null);
        setError(null);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const stopRecording = async () => {
    try {
      const result = await voiceService.stopRecording();
      if (result) {
        setIsRecording(false);
        setAudioUrl(result.url);
        onRecordingComplete && onRecordingComplete(result.blob);
        setError(null);
        return result.blob;
      }
    } catch (err) {
      setError(err.message);
    }
    return null;
  };

  const analyzePronunciation = async (audioBlob, expectedText) => {
    try {
      const result = await voiceService.analyzePronunciation(audioBlob, expectedText);
      return result;
    } catch (err) {
      setError(err.message);
      return null;
    }
  };

  const playAudio = (text, options = {}) => {
    voiceService.playAudio(text, options);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return {
    isRecording,
    recordingTime,
    audioUrl,
    error,
    startRecording,
    stopRecording,
    analyzePronunciation,
    playAudio,
    formatTime
  };
};

export default useVoiceRecording;