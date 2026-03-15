import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Header from './components/common/Header';
import Footer from './components/common/Footer';
import HomePage from './components/home/HomePage';
import UserRegistration from './components/dashboard/UserRegistration';
import ModuleSelection from './components/dashboard/ModuleSelection';
import MathModule from './components/math/MathModule';
import SpellingModule from './components/spelling/SpellingModule';
import ReadingModule from './components/reading/ReadingModule';
import ProgressReport from './components/dashboard/ProgressReport';
import { UserProvider, useUser } from './contexts/UserContext';
import './App.css';
import FeaturesPage from "./components/pages/FeaturesPage";
import HowItWorksPage from "./components/pages/HowItWorksPage";
import TechnologyPage from "./components/pages/TechnologyPage";

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { currentUser, loading } = useUser();
  
  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner">🎯</div>
        <h2>Loading...</h2>
      </div>
    );
  }
  
  return currentUser ? children : <Navigate to="/" />;
};

function AppContent() {
  const { currentUser } = useUser();

  return (
    <Router>
      <div className="App">
        <Header />
        <main className="main-content">
          <Routes>
            <Route 
              path="/" 
              element={currentUser ? <Navigate to="/modules" /> : <HomePage />} 
            />
            <Route 
              path="/register" 
              element={currentUser ? <Navigate to="/modules" /> : <UserRegistration />} 
            />
            <Route 
              path="/features" 
              element={<FeaturesPage />} 
            />
            <Route 
              path="/how-it-works" 
              element={<HowItWorksPage />} 
            />
            <Route 
              path="/technology" 
              element={<TechnologyPage />} 
            />
            <Route 
              path="/modules" 
              element={
                <ProtectedRoute>
                  <ModuleSelection />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/math" 
              element={
                <ProtectedRoute>
                  <MathModule />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/spelling" 
              element={
                <ProtectedRoute>
                  <SpellingModule />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/reading" 
              element={
                <ProtectedRoute>
                  <ReadingModule />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/report" 
              element={
                <ProtectedRoute>
                  <ProgressReport />
                </ProtectedRoute>
              } 
            />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

function App() {
  return (
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
}

export default App;