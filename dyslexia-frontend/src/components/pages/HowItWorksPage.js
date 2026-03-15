import React from "react";
import { useNavigate } from "react-router-dom";
import "./Pages.css";

const HowItWorksPage = () => {
  const navigate = useNavigate();

  return (
    <div className="page-container">
      <button className="back-btn" onClick={() => navigate("/")}>
        ← Back
      </button>

      <h1>How It Works</h1>

      <div className="page-content">
        <p>1. Create a student profile.</p>
        <p>2. Select learning module.</p>
        <p>3. AI analyzes performance.</p>
        <p>4. Difficulty adapts automatically.</p>
        <p>5. Progress reports are generated.</p>
      </div>
    </div>
  );
};

export default HowItWorksPage;