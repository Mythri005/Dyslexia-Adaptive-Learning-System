import axios from 'axios';

const API_BASE_URL = "https://ai-powered-adaptive-learning-system-i87g.onrender.com/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });
    
    return Promise.reject(error);
  }
);

// Helper function to convert blob to base64
export const blobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

// Health check
export const healthCheck = () => api.get('/health');

// User APIs
export const userAPI = {
  createUser: (userData) => api.post('/users', userData),
  getUser: (userId) => api.get(`/users/${userId}`),
  updateProgress: (userId, progressData) => api.put(`/users/${userId}/progress`, progressData),
  // Add login method
  login: (credentials) => api.post('/users/login', credentials),
  // Add method to check existing user
  findUser: (name, age) => api.get(`/users/find?name=${encodeURIComponent(name)}&age=${age}`),
};

// Math APIs - Enhanced for dataset integration
export const mathAPI = {
  startSession: (data) => api.post('/math/start', {
    user_id: data.user_id,
    difficulty: data.difficulty || 'easy',
    age: data.age
  }),
  
  getQuestion: (data) => api.post('/math/question', {
    user_id: data.user_id,
    difficulty: data.difficulty,
    previous_question: data.previous_question,
    stress_level: data.stress_level,
    performance: data.performance
  }),
  
  submitAnswer: (data) => api.post('/math/submit', {
    user_id: data.user_id,
    question_id: data.question_id,
    answer: data.answer,
    response_time: data.response_time,
    difficulty: data.difficulty,
    camera_data: data.camera_data,
    current_stress: data.current_stress
  }),
  
  continueSession: (data) => api.post('/math/continue', {
    user_id: data.user_id,
    session_id: data.session_id
  }),
  
  endSession: (data) => api.post('/math/end', {
    user_id: data.user_id,
    session_id: data.session_id,
    final_score: data.final_score
  }),
  
  getProgress: (userId) => api.get(`/math/progress?user_id=${userId}`),
};

// Spelling APIs - Enhanced for dataset integration
export const spellingAPI = {
  startSession: (data) => api.post('/spelling/start', {
    user_id: data.user_id,
    mode: data.mode,
    difficulty: data.difficulty || 'easy',
    age: data.age
  }),
  
  getQuestion: (data) => api.post('/spelling/question', {
    user_id: data.user_id,
    mode: data.mode,
    difficulty: data.difficulty,
    previous_question: data.previous_question,
    stress_level: data.stress_level,
    performance: data.performance
  }),
  
  submitAnswer: (data) => api.post('/spelling/submit', {
    user_id: data.user_id,
    question_id: data.question_id,
    answer: data.answer,
    response_time: data.response_time,
    mode: data.mode,
    difficulty: data.difficulty,
    camera_data: data.camera_data,
    stress_level: data.stress_level
  }),
  
  endSession: (data) => api.post('/spelling/end', {
    user_id: data.user_id,
    session_id: data.session_id,
    final_score: data.final_score,
    mode: data.mode
  }),
  
  getProgress: (userId) => api.get(`/spelling/progress?user_id=${userId}`),
};

// Reading APIs - Enhanced for dataset integration
export const readingAPI = {
  startSession: (data) => api.post('/reading/start', {
    user_id: data.user_id,
    mode: data.mode,
    difficulty: data.difficulty || 'easy',
    age: data.age
  }),
  
  getItem: (data) => api.post('/reading/item', {
    user_id: data.user_id,
    mode: data.mode,
    difficulty: data.difficulty,
    previous_item: data.previous_item,
    stress_level: data.stress_level,
    performance: data.performance
  }),
  
  evaluatePronunciation: async (data) => {
  try {
    console.log('📝 Submitting spoken text for evaluation...');

    if (!data.transcribed_text) {
      console.warn("❌ No spoken text provided");
      throw new Error("Spoken text missing");
    }

    const payload = {
      user_id: data.user_id,
      spoken_text: data.transcribed_text,
      expected_text: data.expected_text,
      current_item: data.current_item,
      camera_data: data.camera_data,
      mode: data.mode,
      difficulty: data.difficulty
    };

    return api.post('/reading/evaluate', payload, {
      timeout: 45000,
    });

  } catch (error) {
    console.error('❌ Error preparing pronunciation request:', error);
    throw error;
  }
},
  
  getHelp: (data) => api.post('/reading/help', data),
  
  continueSession: (data) => api.post('/reading/continue', {
    user_id: data.user_id,
    session_id: data.session_id
  }),
  
  endSession: (data) => api.post('/reading/end', {
    user_id: data.user_id,
    session_id: data.session_id,
    final_score: data.final_score,
    mode: data.mode
  }),
  
  getProgress: (userId) => api.get(`/reading/progress?user_id=${userId}`),
};

// Camera APIs
export const cameraAPI = {
  analyze: (data) => api.post('/camera/analyze', data),
  test: () => api.get('/camera/test'),
};

// Monitoring APIs
export const monitoringAPI = {
  start: (data) => api.post('/monitoring/start', data),
  stop: (data) => api.post('/monitoring/stop', data),
  getMetrics: (userId) => api.get(`/monitoring/metrics?user_id=${userId}`),
  getStatus: () => api.get('/monitoring/status'),
  getAlerts: (userId) => api.get(`/monitoring/alerts?user_id=${userId}`),
};

// Utility function to check backend connectivity
export const checkBackendConnectivity = async () => {
  try {
    const response = await healthCheck();
    return {
      connected: true,
      status: response.status,
      data: response.data
    };
  } catch (error) {
    return {
      connected: false,
      error: error.message,
      status: error.response?.status
    };
  }
};

export default api;
