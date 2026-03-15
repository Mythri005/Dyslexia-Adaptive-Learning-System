import React from "react";
import { useNavigate } from "react-router-dom";
import "./Pages.css";

const FeaturesPage = () => {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      <button className="back-btn" onClick={() => navigate("/")}>
        ← Back
      </button>

      <h1>Platform Features</h1>

      <div className="page-content">
        <div className="feature-card">
          <h3>Adaptive AI Algorithm</h3>
          <p>Adjusts difficulty based on performance.</p>
        </div>

        <div className="feature-card">
          <h3>Computer Vision Monitoring</h3>
          <p>Tracks attention using facial recognition.</p>
        </div>

        <div className="feature-card">
          <h3>Speech Recognition</h3>
          <p>Analyzes pronunciation during reading.</p>
        </div>

        <div className="feature-card">
          <h3>Progress Analytics</h3>
          <p>Tracks improvement across modules.</p>
        </div>
      </div>
    </div>
  );
};

export default FeaturesPage;