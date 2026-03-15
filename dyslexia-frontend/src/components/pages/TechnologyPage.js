import React from "react";
import { useNavigate } from "react-router-dom";
import "./Pages.css";

const TechnologyPage = () => {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      <button className="back-btn" onClick={() => navigate("/")}>
        ← Back
      </button>

      <h1>Technology Stack</h1>

      <div className="page-content">
        <p>Frontend: React.js</p>
        <p>Backend: Flask</p>
        <p>Database: SQLite</p>
        <p>AI: Adaptive learning algorithm</p>
        <p>Computer Vision: OpenCV</p>
        <p>Speech Recognition: Web Speech API</p>
      </div>
    </div>
  );
};

export default TechnologyPage;