class CameraService {
  constructor() {
    this.stream = null;
    this.videoElement = null;
    this.isActive = false;
  }

  async startCamera(videoElement) {
    try {
      this.videoElement = videoElement;

      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 }
      });

      this.videoElement.srcObject = this.stream;

      // ✅ Wait for metadata before play
      await new Promise(resolve => {
        this.videoElement.onloadedmetadata = resolve;
      });

      await this.videoElement.play().catch(() => {
        console.warn("Camera autoplay prevented — user interaction needed");
      });

      this.isActive = true;
      return { success: true, message: 'Camera started successfully' };

    } catch (error) {
      console.error('Error starting camera:', error);
      return { success: false, error: error.message };
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }

    if (this.videoElement) {
      this.videoElement.srcObject = null;
    }

    this.isActive = false;
  }

  captureFrame() {
    if (!this.videoElement || !this.isActive) return null;

    const canvas = document.createElement('canvas');
    canvas.width = this.videoElement.videoWidth || 640;
    canvas.height = this.videoElement.videoHeight || 480;

    const context = canvas.getContext('2d');
    context.drawImage(this.videoElement, 0, 0);

    return canvas.toDataURL('image/jpeg', 0.9);
  }

  async analyzeFrame(currentQuestion = null) {
    try {
      const imageData = this.captureFrame();
      if (!imageData) return this.getDefaultAnalysis();

      const response = await fetch('http://localhost:5001/api/camera/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_data: imageData,
          current_question: currentQuestion
        }),
      });

      if (!response.ok) {
        console.warn("Camera API failed — using fallback");
        return this.getDefaultAnalysis();
      }

      const data = await response.json();
      return this.normalizeAnalysis(data);

    } catch {
      console.warn("Camera analysis fallback triggered");
      return this.getDefaultAnalysis();
    }
  }

  normalizeAnalysis(data) {
    return {
      attention_score: data.attention_score ?? 50,
      stress_level: data.stress_level ?? 0.2,
      is_high_stress: data.is_high_stress ?? false,
      face_detected: data.face_detected ?? false,
      eye_detected: data.eye_detected ?? false,
      pulse_rate: data.pulse_rate ?? 75,
      needs_help: data.needs_help ?? false,
      help_message: data.help_message ?? "",
      difficulty_action: data.difficulty_action ?? "keep",
      analysis_type: "live"
    };
  }

  getDefaultAnalysis() {
    return {
      attention_score: 50,
      stress_level: 0.2,
      is_high_stress: false,
      face_detected: false,
      eye_detected: false,
      pulse_rate: 75,
      needs_help: false,
      help_message: "Using fallback AI",
      difficulty_action: "keep",
      analysis_type: "default"
    };
  }
}

export default new CameraService();
