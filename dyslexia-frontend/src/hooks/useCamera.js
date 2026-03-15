import { useState, useEffect, useRef } from 'react';
import cameraService from '../services/cameraService';

export const useCamera = (onAnalysisUpdate, currentQuestion) => {
  const videoRef = useRef(null);

  const [isActive, setIsActive] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [attentionScore, setAttentionScore] = useState(0);
  const [difficultyAction, setDifficultyAction] = useState("keep");
  const [needsHelp, setNeedsHelp] = useState(false);
  const [error, setError] = useState(null);

  // Start camera on mount
  useEffect(() => {
    startCamera();

    return () => {
      cameraService.stopCamera();
    };
  }, []);

  // Poll backend analysis every 2 seconds
  useEffect(() => {
    let interval;

    if (isActive) {
      interval = setInterval(async () => {
        try {
          const newAnalysis = await cameraService.analyzeFrame(currentQuestion);

          if (newAnalysis) {
            setAnalysis(newAnalysis);

            // Extract AI metrics
            setAttentionScore(newAnalysis.attention_score || 0);
            setDifficultyAction(newAnalysis.difficulty_action || "keep");
            setNeedsHelp(newAnalysis.needs_help || false);

            // Send data back to modules (Math/Reading/Spelling)
            if (onAnalysisUpdate) {
              onAnalysisUpdate({
                ...newAnalysis,
                attentionScore: newAnalysis.attention_score || 0,
                difficultyAction: newAnalysis.difficulty_action || "keep",
                needsHelp: newAnalysis.needs_help || false
              });
            }
          }
        } catch (err) {
          setError(err.message || "Camera analysis error");
        }
      }, 2000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isActive, currentQuestion, onAnalysisUpdate]);

  // Start camera
  const startCamera = async () => {
    try {
      const result = await cameraService.startCamera(videoRef.current);

      if (result.success) {
        setIsActive(true);
        setError(null);
      } else {
        setError(result.error || "Camera permission denied");
      }
    } catch (err) {
      setError(err.message);
    }
  };

  // Stop camera
  const stopCamera = () => {
    cameraService.stopCamera();
    setIsActive(false);
  };

  // Capture frame manually if needed
  const captureFrame = () => {
    return cameraService.captureFrame();
  };

  return {
    videoRef,
    isActive,
    analysis,
    attentionScore,
    difficultyAction,
    needsHelp,
    error,
    startCamera,
    stopCamera,
    captureFrame
  };
};

export default useCamera;
