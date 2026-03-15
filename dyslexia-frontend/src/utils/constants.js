// Application constants

export const MODULES = {
  MATH: 'math',
  SPELLING: 'spelling',
  READING: 'reading'
};

export const SPELLING_MODES = {
  MISSING_LETTERS: 'missing_letters',
  COMPLETE_WORDS: 'complete_words'
};

export const READING_MODES = {
  WORDS: 'words',
  SENTENCES: 'sentences',
  PARAGRAPHS: 'paragraphs'
};

export const DIFFICULTY_LEVELS = {
  EASY: 'easy',
  MEDIUM: 'medium',
  HARD: 'hard'
};

export const POINTS_SYSTEM = {
  BASE_POINTS: {
    EASY: 10,
    MEDIUM: 20,
    HARD: 30
  },
  BONUS_MULTIPLIERS: {
    QUICK_CORRECT: 1.5,
    STREAK_BONUS: 2.0,
    STRESS_MANAGE: 1.2
  },
  STREAK_THRESHOLDS: {
    MIN_STREAK: 3,
    MAX_STREAK_BONUS: 20
  }
};

export const STRESS_THRESHOLDS = {
  LOW: 0.3,
  MEDIUM: 0.6,
  HIGH: 0.8
};

export const ATTENTION_THRESHOLDS = {
  LOW: 0.3,
  MEDIUM: 0.6,
  HIGH: 0.8
};

export const SESSION_SETTINGS = {
  QUESTIONS_PER_SESSION: 10,
  MAX_ATTEMPTS_PER_QUESTION: 3,
  TIME_LIMIT_PER_QUESTION: 60, // seconds
  BREAK_INTERVAL: 10 // questions
};

export const CAMERA_SETTINGS = {
  ANALYSIS_INTERVAL: 2000, // milliseconds
  STRESS_CHECK_INTERVAL: 5000, // milliseconds
  MAX_CAMERA_WIDTH: 640,
  MAX_CAMERA_HEIGHT: 480
};

export const VOICE_SETTINGS = {
  RECORDING_DURATION: 5000, // milliseconds
  SILENCE_THRESHOLD: 0.01,
  MIN_VOICE_ENERGY: 0.02
};

export const API_ENDPOINTS = {
  BASE_URL: 'http://localhost:5001/api',
  HEALTH: '/health',
  USERS: '/users',
  MATH: {
    START: '/math/start',
    QUESTION: '/math/question',
    SUBMIT: '/math/submit',
    CONTINUE: '/math/continue',
    PROGRESS: '/math/progress',
    END: '/math/end'
  },
  SPELLING: {
    START: '/spelling/start',
    QUESTION: '/spelling/question',
    SUBMIT: '/spelling/submit',
    PROGRESS: '/spelling/progress',
    END: '/spelling/end'
  },
  READING: {
    START: '/reading/start',
    ITEM: '/reading/item',
    EVALUATE: '/reading/evaluate',
    HELP: '/reading/help',
    PROGRESS: '/reading/progress',
    END: '/reading/end'
  },
  CAMERA: {
    ANALYZE: '/camera/analyze',
    TEST: '/camera/test'
  },
  MONITORING: {
    START: '/monitoring/start',
    STOP: '/monitoring/stop',
    METRICS: '/monitoring/metrics',
    STATUS: '/monitoring/status',
    ALERTS: '/monitoring/alerts'
  }
};

export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  CAMERA_ERROR: 'Camera access denied. Please allow camera permissions.',
  MICROPHONE_ERROR: 'Microphone access denied. Please allow microphone permissions.',
  SESSION_EXPIRED: 'Session expired. Please start again.',
  INVALID_USER: 'User not found. Please register again.',
  DATA_LOAD_ERROR: 'Failed to load data. Please try again.'
};

export const SUCCESS_MESSAGES = {
  SESSION_STARTED: 'Learning session started successfully!',
  ANSWER_SUBMITTED: 'Answer submitted successfully!',
  PROGRESS_SAVED: 'Progress saved successfully!',
  USER_CREATED: 'User profile created successfully!',
  SESSION_COMPLETED: 'Session completed successfully!'
};

export const COLORS = {
  PRIMARY: '#667eea',
  SECONDARY: '#f093fb',
  SUCCESS: '#4CAF50',
  WARNING: '#FF9800',
  ERROR: '#F44336',
  INFO: '#2196F3',
  LIGHT_BLUE: '#4facfe',
  LIGHT_PURPLE: '#764ba2',
  BACKGROUND: '#f8f9fa',
  TEXT_PRIMARY: '#333333',
  TEXT_SECONDARY: '#666666',
  TEXT_LIGHT: '#999999'
};

export const ANIMATION_DURATIONS = {
  FAST: 300,
  NORMAL: 500,
  SLOW: 800
};

export default {
  MODULES,
  SPELLING_MODES,
  READING_MODES,
  DIFFICULTY_LEVELS,
  POINTS_SYSTEM,
  STRESS_THRESHOLDS,
  SESSION_SETTINGS,
  CAMERA_SETTINGS,
  VOICE_SETTINGS,
  API_ENDPOINTS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  COLORS,
  ANIMATION_DURATIONS
};