class AudioPlayer {
  constructor() {
    this.audioContext = null;
    this.isPlaying = false;
    this.currentUtterance = null;
  }

  async init() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  speak(text, options = {}) {
    return new Promise((resolve) => {
      if (!('speechSynthesis' in window)) {
        console.warn('Speech synthesis not supported');
        resolve();
        return;
      }

      // Cancel any ongoing speech
      if (this.isPlaying) {
        speechSynthesis.cancel();
      }

      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set options
      utterance.rate = options.rate || 0.8;
      utterance.pitch = options.pitch || 1;
      utterance.volume = options.volume || 1;
      
      // Set voice if available
      if (options.voice) {
        utterance.voice = options.voice;
      } else {
        // Try to get a child-friendly voice
        const voices = speechSynthesis.getVoices();
        const preferredVoice = voices.find(voice => 
          voice.name.includes('Child') || 
          voice.name.includes('Kid') ||
          voice.name.includes('Young')
        ) || voices.find(voice => voice.lang === 'en-US');
        
        if (preferredVoice) {
          utterance.voice = preferredVoice;
        }
      }

      utterance.onstart = () => {
        this.isPlaying = true;
        this.currentUtterance = utterance;
      };

      utterance.onend = () => {
        this.isPlaying = false;
        this.currentUtterance = null;
        resolve();
      };

      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        this.isPlaying = false;
        this.currentUtterance = null;
        resolve();
      };

      speechSynthesis.speak(utterance);
    });
  }

  stop() {
    if (this.isPlaying) {
      speechSynthesis.cancel();
      this.isPlaying = false;
      this.currentUtterance = null;
    }
  }

  speakWordWithLetters(word, options = {}) {
    const letters = word.split('').join(' ');
    return this.speak(`The word ${word} is spelled: ${letters}`, options);
  }

  speakSentenceWithHighlight(sentence, highlightedWord, options = {}) {
    return this.speak(`In the sentence: ${sentence}. The word to practice is: ${highlightedWord}`, options);
  }

  getEncouragement() {
    const encouragements = [
      "Great job! You're doing amazing!",
      "Well done! Keep up the good work!",
      "Excellent! You're learning so fast!",
      "Fantastic! You're a star learner!",
      "Awesome work! You're getting better every day!"
    ];
    return encouragements[Math.floor(Math.random() * encouragements.length)];
  }

  getHelpMessage(module, difficulty, stressLevel = 0.5) {
    const helpMessages = {
      math: {
        easy: "Let me help you! Try counting on your fingers.",
        medium: "Think step by step. You can do this!",
        hard: "This is challenging! Break it down into smaller parts."
      },
      spelling: {
        easy: "Sound it out slowly. What sounds do you hear?",
        medium: "Try breaking the word into syllables.",
        hard: "This is a tricky word! Let's practice it together."
      },
      reading: {
        easy: "Listen carefully and try to repeat after me.",
        medium: "Read it slowly, one word at a time.",
        hard: "Let's break this down into smaller parts."
      }
    };

    const baseMessage = helpMessages[module]?.[difficulty] || "Let me help you with this!";
    
    if (stressLevel > 0.7) {
      return `Don't worry! ${baseMessage} Take your time.`;
    } else if (stressLevel > 0.5) {
      return `You're doing great! ${baseMessage}`;
    } else {
      return baseMessage;
    }
  }

  // Play a sound effect
  playSound(type) {
    const sounds = {
      correct: () => this.playTone(523.25, 200), // C5
      incorrect: () => this.playTone(349.23, 200), // F4
      complete: () => this.playTone(659.25, 300), // E5
      click: () => this.playTone(440, 50) // A4
    };

    if (sounds[type]) {
      sounds[type]();
    }
  }

  playTone(frequency, duration) {
    this.init().then(() => {
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
      
      oscillator.frequency.value = frequency;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);
      
      oscillator.start(this.audioContext.currentTime);
      oscillator.stop(this.audioContext.currentTime + duration / 1000);
    });
  }
}

export default new AudioPlayer();