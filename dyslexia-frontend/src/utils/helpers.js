// Utility functions for the application

export const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

export const calculateAccuracy = (correct, total) => {
  if (total === 0) return 0;
  return Math.round((correct / total) * 100);
};

export const getDifficultyColor = (difficulty) => {
  switch (difficulty) {
    case 'easy': return '#4CAF50';
    case 'medium': return '#FF9800';
    case 'hard': return '#F44336';
    default: return '#667eea';
  }
};

export const getModuleColor = (module) => {
  switch (module) {
    case 'math': return '#667eea';
    case 'spelling': return '#f093fb';
    case 'reading': return '#4facfe';
    default: return '#667eea';
  }
};

export const generateSessionId = () => {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

export const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const calculateAge = (birthDate) => {
  const today = new Date();
  const birth = new Date(birthDate);
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  
  return age;
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

export const capitalizeFirst = (str) => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const formatNumber = (num) => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

export const getRandomEncouragement = () => {
  const encouragements = [
    "Great job! You're doing amazing!",
    "Well done! Keep up the good work!",
    "Excellent! You're learning so fast!",
    "Fantastic! You're a star learner!",
    "Awesome work! You're getting better every day!",
    "Outstanding! Your hard work is paying off!",
    "Brilliant! You're mastering this!",
    "Superb! Your progress is impressive!",
    "Magnificent! You're on fire!",
    "Terrific! You're crushing it!"
  ];
  return encouragements[Math.floor(Math.random() * encouragements.length)];
};

export const calculateStreakBonus = (streak) => {
  return Math.min(20, streak * 2);
};

export const getPerformanceLevel = (accuracy) => {
  if (accuracy >= 90) return 'excellent';
  if (accuracy >= 80) return 'very good';
  if (accuracy >= 70) return 'good';
  if (accuracy >= 60) return 'satisfactory';
  return 'needs practice';
};