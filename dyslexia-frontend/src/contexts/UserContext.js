import React, { createContext, useContext, useState, useEffect } from 'react';

const UserContext = createContext();

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export const UserProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [userProgress, setUserProgress] = useState({});
  const [loading, setLoading] = useState(false);

  // Load saved user + progress
  useEffect(() => {
    const savedUser = localStorage.getItem('dyslexia_currentUser');
    const savedProgress = localStorage.getItem('dyslexia_userProgress');

    if (savedUser) {
      try {
        const user = JSON.parse(savedUser);
        setCurrentUser(user);
        
        // Load user-specific progress
        const userProgressKey = `dyslexia_progress_${user.id}`;
        const userProgress = localStorage.getItem(userProgressKey);
        
        if (userProgress) {
          setUserProgress(JSON.parse(userProgress));
        } else if (savedProgress) {
          // Migrate old progress to user-specific storage
          const progress = JSON.parse(savedProgress);
          localStorage.setItem(userProgressKey, JSON.stringify(progress));
          setUserProgress(progress);
        }
      } catch {
        localStorage.removeItem('dyslexia_currentUser');
        localStorage.removeItem('dyslexia_userProgress');
      }
    }
  }, []);

  // 🎯 Grade Calculator
  const calculateGrade = (accuracy) => {
    if (accuracy >= 90) return 'A+';
    if (accuracy >= 80) return 'A';
    if (accuracy >= 70) return 'B';
    if (accuracy >= 60) return 'C';
    if (accuracy >= 50) return 'D';
    return 'F';
  };

  // ✅ FINAL SAFE updateProgress (Supports multi-reports per module)
  const updateProgress = (module, progress) => {
  setUserProgress(prev => {
    const prevModule = prev[module] || {
      reports: [],
      totalPoints: 0,
      averageAccuracy: 0,
      sessionsCompleted: 0
    };

    // Add new report
    const updatedReports = [...prevModule.reports, progress];

    // Calculate totals
    const totalPoints = updatedReports.reduce(
      (sum, r) => sum + (r.totalPoints || r.points_earned || 0),
      0
    );

    const avgAccuracy = updatedReports.length
      ? Math.round(
          updatedReports.reduce((sum, r) => sum + (r.accuracy || 0), 0) /
          updatedReports.length
        )
      : 0;

    const strengths = [];
    const weaknesses = [];

    if (avgAccuracy >= 80) strengths.push("High Accuracy");
    if (avgAccuracy < 60) weaknesses.push("Needs Accuracy Improvement");

    if (totalPoints >= 50) strengths.push("Strong Performance");
    if (totalPoints < 30) weaknesses.push("Low Score Trend");

    const updatedModule = {
      reports: updatedReports,
      totalPoints,
      averageAccuracy: avgAccuracy,
      grade: calculateGrade(avgAccuracy),
      strengths,
      weaknesses,
      sessionsCompleted: updatedReports.length,
      lastUpdated: new Date().toISOString()
    };

    const newProgress = {
      ...prev,
      [module]: updatedModule
    };

    localStorage.setItem('dyslexia_userProgress', JSON.stringify(newProgress));
    
    // Save to user-specific storage if user is logged in
    if (currentUser) {
      const userProgressKey = `dyslexia_progress_${currentUser.id}`;
      localStorage.setItem(userProgressKey, JSON.stringify(newProgress));
    }

    return newProgress;
  });
};

  // ✅ Check for existing user by name and age
  const findExistingUser = (name, age) => {
    const users = JSON.parse(localStorage.getItem('dyslexia_allUsers') || '[]');
    return users.find(u => u.name === name && u.age === parseInt(age));
  };

  const loginUser = (userData) => {
    setCurrentUser(userData);
    localStorage.setItem('dyslexia_currentUser', JSON.stringify(userData));
    
    // Load user-specific progress
    const userProgressKey = `dyslexia_progress_${userData.id}`;
    const savedProgress = localStorage.getItem(userProgressKey);
    if (savedProgress) {
      setUserProgress(JSON.parse(savedProgress));
      localStorage.setItem('dyslexia_userProgress', savedProgress);
    }
  };

  const logoutUser = () => {
    setCurrentUser(null);
    setUserProgress({});
    localStorage.removeItem('dyslexia_currentUser');
    // Don't remove progress - keep it for next login
  };

  // ✅ Get Module Summary
  const getModuleProgress = (module) => {
    return userProgress[module] || {
      reports: [],
      totalPoints: 0,
      averageAccuracy: 0,
      grade: "—",
      strengths: [],
      weaknesses: [],
      sessionsCompleted: 0,
      lastUpdated: null
    };
  };

  // ✅ OVERALL PROGRESS
  const getOverallProgress = () => {
    const modules = Object.values(userProgress);

    if (!modules.length) return null;

    const totalPoints = modules.reduce((sum, m) => sum + (m.totalPoints || 0), 0);
    const avgAccuracy = Math.round(
      modules.reduce((sum, m) => sum + (m.averageAccuracy || 0), 0) / modules.length
    );

    return {
      totalPoints,
      averageAccuracy: avgAccuracy,
      grade: calculateGrade(avgAccuracy),
      strengths: [...new Set(modules.flatMap(m => m.strengths || []))],
      weaknesses: [...new Set(modules.flatMap(m => m.weaknesses || []))]
    };
  };

  const value = {
    currentUser,
    setCurrentUser: loginUser,
    userProgress,
    updateProgress,
    logoutUser,
    getModuleProgress,
    getOverallProgress,
    loading,
    findExistingUser
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};