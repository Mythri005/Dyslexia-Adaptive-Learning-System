import React, { useState, useEffect } from 'react';
import './PulseMonitor.css';

const PulseMonitor = ({ currentPulse = 75, isActive = true }) => {
  const [pulseHistory, setPulseHistory] = useState([]);

  useEffect(() => {
    if (isActive && currentPulse) {
      setPulseHistory(prev => {
        const newHistory = [...prev, currentPulse];
        // Keep only last 20 readings
        return newHistory.slice(-20);
      });
    }
  }, [currentPulse, isActive]);

  const getPulseStatus = () => {
    if (currentPulse < 60) return { status: 'low', color: '#4CAF50', message: 'Calm' };
    if (currentPulse < 80) return { status: 'normal', color: '#2196F3', message: 'Normal' };
    if (currentPulse < 100) return { status: 'elevated', color: '#FF9800', message: 'Elevated' };
    return { status: 'high', color: '#F44336', message: 'High' };
  };

  const pulseStatus = getPulseStatus();

  return (
    <div className="pulse-monitor card">
      <div className="pulse-header">
        <h3>❤️ Pulse Monitor</h3>
        <div className="pulse-status" style={{ color: pulseStatus.color }}>
          {pulseStatus.message}
        </div>
      </div>

      <div className="pulse-display">
        <div className="pulse-value" style={{ color: pulseStatus.color }}>
          {currentPulse}
          <span className="pulse-unit">BPM</span>
        </div>
        <div className="pulse-graph">
          {pulseHistory.map((pulse, index) => (
            <div
              key={index}
              className="pulse-bar"
              style={{
                height: `${((pulse - 50) / 70) * 100}%`,
                backgroundColor: getPulseStatus(pulse).color,
                opacity: 0.6 + (index / pulseHistory.length) * 0.4
              }}
              title={`${pulse} BPM`}
            />
          ))}
        </div>
      </div>

      <div className="pulse-info">
        <div className="info-item">
          <span className="info-label">Status:</span>
          <span className="info-value" style={{ color: pulseStatus.color }}>
            {pulseStatus.status.toUpperCase()}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Trend:</span>
          <span className="info-value">
            {pulseHistory.length > 1 ? 
              (pulseHistory[pulseHistory.length - 1] > pulseHistory[0] ? '↗️ Rising' : 
               pulseHistory[pulseHistory.length - 1] < pulseHistory[0] ? '↘️ Falling' : '➡️ Stable') : 
              '---'}
          </span>
        </div>
      </div>

      {!isActive && (
        <div className="pulse-offline">
          ❤️ Pulse monitoring offline
        </div>
      )}
    </div>
  );
};

export default PulseMonitor;