class VoiceService {
  constructor() {
    this.mediaRecorder = null;
    this.audioChunks = [];
    this.isRecording = false;
    this.stream = null;
  }

  // 🎧 AI SPEECH OUTPUT (Text → Voice)
  playAudio(text, options = {}) {
    if (!('speechSynthesis' in window)) return;

    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.rate = options.rate || 0.95;
    utterance.pitch = options.pitch || 1;
    utterance.volume = options.volume || 1;

    const voices = speechSynthesis.getVoices();

    const preferredVoice =
      voices.find(v => v.lang.startsWith('en') && v.name.includes('Google')) ||
      voices.find(v => v.lang.startsWith('en') && v.name.includes('Microsoft')) ||
      voices.find(v => v.lang.startsWith('en'));

    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }

    speechSynthesis.speak(utterance);
  }

  // 🔤 Spell helper
  spellWordLetterByLetter(word) {
    if (!word) return;
    const spaced = word.split('').join(' ');
    this.playAudio(`Let’s spell it: ${spaced}`, { rate: 0.85 });
  }

  // 🎤 START RECORDING — IMPROVED AUDIO QUALITY
  async startRecording() {
  if (this.isRecording) {
    return { success: false, message: "Already recording" };
  }

  try {
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: 16000,
        noiseSuppression: true,
        echoCancellation: true,
        autoGainControl: true
      }
    });

    this.audioChunks = [];

    this.mediaRecorder = new MediaRecorder(this.stream, {
      mimeType: "audio/webm;codecs=opus"
    });

    this.mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        this.audioChunks.push(event.data);
      }
    };

    this.mediaRecorder.start(200);
    this.isRecording = true;

    console.log("🎙️ High-quality recording started");
    return { success: true };

  } catch (error) {
    console.error("❌ Mic permission denied:", error);
    return { success: false, error: "Microphone permission denied" };
  }
}

  // ⏹️ STOP RECORDING → RETURN AUDIO BLOB (CLEANER OUTPUT)
  stopRecording() {
    return new Promise((resolve) => {
      if (!this.mediaRecorder || !this.isRecording) {
        console.warn("❌ No active recording");
        resolve(null);
        return;
      }

      this.mediaRecorder.onstop = () => {
        try {
          // ✅ CREATE HIGH QUALITY BLOB
          const audioBlob = new Blob(this.audioChunks, {
            type: this.mediaRecorder.mimeType || "audio/webm"
          });

          const audioUrl = URL.createObjectURL(audioBlob);

          console.log("🛑 Recording stopped");
          console.log("🎧 Blob size:", audioBlob.size);

          this.audioChunks = [];
          this.isRecording = false;

          if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
          }

          resolve({
            blob: audioBlob,
            url: audioUrl
          });

        } catch (err) {
          console.error("❌ Failed to create audio blob", err);
          resolve(null);
        }
      };

      this.mediaRecorder.stop();
    });
  }
}

export default new VoiceService();
