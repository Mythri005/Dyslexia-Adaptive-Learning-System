import React, { useState, useEffect } from 'react';
import { monitoringAPI } from '../../services/api';
import { useUser } from '../../contexts/UserContext';
import './RealTimeMetrics.css';

const RealTimeMetrics = ({ module, isActive = true }) => {
  const { currentUser } = useUser();
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!currentUser || !isActive) return;

    let interval;

    const fetchMetrics = async () => {
      try {
        const response = await monitoringAPI.getMetrics(currentUser.id);
        if (response.data) {
          setMetrics(response.data);
          setError(null);
        }
      } catch (err) {
        console.error('Error fetching metrics:', err);
        setError('Unable to fetch real-time metrics');
        // Use simulated data as fallback
        setMetrics(getSimulatedMetrics());
      } finally {
        setLoading(false);
      }
    };

    // Fetch immediately
    fetchMetrics();

    // Set up interval for real-time updates
    if (isActive) {
      interval = setInterval(fetchMetrics, 3000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [currentUser, isActive, module]);

  const getSimulatedMetrics = () => {
    return {
      camera: {
        status: 'active',
        current_attention: 0.7 + Math.random() * 0.2,
        current_stress: 0.3 + Math.random() * 0.3,
        current_pulse: 70 + Math.floor(Math.random() * 20),
        trends: {
          attention_trend: Math.random() > 0.5 ? 'increasing' : 'stable',
          stress_trend: Math.random() > 0.5 ? 'decreasing' : 'stable',
          pulse_trend: 'stable'
        },
        alerts: []
      },
      voice: {
        status: 'active',
        current_energy: 0.4 + Math.random() * 0.4,
        current_speech_rate: 120 + Math.floor(Math.random() * 60),
        current_pitch: 180 + Math.floor(Math.random() * 80),
        current_clarity: 0.6 + Math.random() * 0.3,
        is_speaking: Math.random() > 0.7,
        trends: {
          energy_trend: Math.random() > 0.5 ? 'increasing' : 'stable',
          speech_rate_trend: 'stable',
          pitch_trend: Math.random() > 0.5 ? 'decreasing' : 'stable'
        }
      },
      timestamp: new Date().toISOString()
    };
  };

  const getStressLevel = (stress) => {
    if (stress < 0.4) return { level: 'low', color: '#4CAF50', icon: '😊' };
    if (stress < 0.7) return { level: 'medium', color: '#FF9800', icon: '😐' };
    return { level: 'high', color: '#F44336', icon: '😰' };
  };

  const getAttentionLevel = (attention) => {
    if (attention > 0.7) return { level: 'high', color: '#4CAF50', icon: '👀' };
    if (attention > 0.4) return { level: 'medium', color: '#FF9800', icon: '👁️' };
    return { level: 'low', color: '#F44336', icon: '🙈' };
  };

  const getPulseLevel = (pulse) => {
    if (pulse < 60) return { level: 'low', color: '#4CAF50' };
    if (pulse < 80) return { level: 'normal', color: '#2196F3' };
    if (pulse < 100) return { level: 'elevated', color: '#FF9800' };
    return { level: 'high', color: '#F44336' };
  };

  const getVoiceEnergyLevel = (energy) => {
    if (energy > 0.1) return { level: 'active', color: '#4CAF50', icon: '🎤' };
    return { level: 'quiet', color: '#666', icon: '🔇' };
  };

  if (loading) {
    return (
      <div className="real-time-metrics card">
        <div className="metrics-header">
          <h3>📊 Real-time Metrics</h3>
          <div className="status-indicator loading">Loading...</div>
        </div>
        <div className="loading-placeholder">
          <div className="skeleton skeleton-text"></div>
          <div className="skeleton skeleton-text"></div>
          <div className="skeleton skeleton-text"></div>
        </div>
      </div>
    );
  }

  if (error && !metrics) {
    return (
      <div className="real-time-metrics card">
        <div className="metrics-header">
          <h3>📊 Real-time Metrics</h3>
          <div className="status-indicator error">Offline</div>
        </div>
        <div className="error-state">
          <p>❌ {error}</p>
          <p className="error-help">Using simulated data for demonstration</p>
        </div>
      </div>
    );
  }

  const stressInfo = getStressLevel(metrics?.camera?.current_stress || 0.5);
  const attentionInfo = getAttentionLevel(metrics?.camera?.current_attention || 0.5);
  const pulseInfo = getPulseLevel(metrics?.camera?.current_pulse || 75);
  const voiceInfo = getVoiceEnergyLevel(metrics?.voice?.current_energy || 0);

  return (
    <div className="real-time-metrics card">
      <div className="metrics-header">
        <h3>📊 Real-time Metrics</h3>
        <div className="status-indicator active">
          ● Live
        </div>
      </div>

      <div className="metrics-grid">
        {/* Camera Metrics */}
        <div className="metric-category">
          <h4>📷 Camera Analysis</h4>
          <div className="metric-group">
            <div className="metric-item">
              <div className="metric-label">
                <span className="metric-icon">{stressInfo.icon}</span>
                Stress Level
              </div>
              <div className="metric-value" style={{ color: stressInfo.color }}>
                {Math.round((metrics?.camera?.current_stress || 0) * 100)}%
              </div>
              <div className="metric-trend">
                {metrics?.camera?.trends?.stress_trend === 'increasing' ? '↗️' :
                 metrics?.camera?.trends?.stress_trend === 'decreasing' ? '↘️' : '➡️'}
              </div>
            </div>

            <div className="metric-item">
              <div className="metric-label">
                <span className="metric-icon">{attentionInfo.icon}</span>
                Attention
              </div>
              <div className="metric-value" style={{ color: attentionInfo.color }}>
                {Math.round((metrics?.camera?.current_attention || 0) * 100)}%
              </div>
              <div className="metric-trend">
                {metrics?.camera?.trends?.attention_trend === 'increasing' ? '↗️' :
                 metrics?.camera?.trends?.attention_trend === 'decreasing' ? '↘️' : '➡️'}
              </div>
            </div>

            <div className="metric-item">
              <div className="metric-label">
                <span className="metric-icon">❤️</span>
                Pulse Rate
              </div>
              <div className="metric-value" style={{ color: pulseInfo.color }}>
                {metrics?.camera?.current_pulse || 75} BPM
              </div>
              <div className="metric-trend">
                {metrics?.camera?.trends?.pulse_trend === 'increasing' ? '↗️' :
                 metrics?.camera?.trends?.pulse_trend === 'decreasing' ? '↘️' : '➡️'}
              </div>
            </div>
          </div>
        </div>

        {/* Voice Metrics */}
        <div className="metric-category">
          <h4>🎤 Voice Analysis</h4>
          <div className="metric-group">
            <div className="metric-item">
              <div className="metric-label">
                <span className="metric-icon">{voiceInfo.icon}</span>
                Voice Activity
              </div>
              <div className="metric-value" style={{ color: voiceInfo.color }}>
                {metrics?.voice?.is_speaking ? 'Speaking' : 'Quiet'}
              </div>
              <div className="metric-trend">
                {metrics?.voice?.trends?.energy_trend === 'increasing' ? '↗️' :
                 metrics?.voice?.trends?.energy_trend === 'decreasing' ? '↘️' : '➡️'}
              </div>
            </div>

            <div className="metric-item">
              <div className="metric-label">
                <span className="metric-icon">🗣️</span>
                Speech Rate
              </div>
              <div className="metric-value">
                {metrics?.voice?.current_speech_rate || 0} WPM
              </div>
              <div className="metric-trend">
                {metrics?.voice?.trends?.speech_rate_trend === 'increasing' ? '↗️' :
                 metrics?.voice?.trends?.speech_rate_trend === 'decreasing' ? '↘️' : '➡️'}
              </div>
            </div>

            <div className="metric-item">
              <div className="metric-label">
                <span className="metric-icon">🎵</span>
                Voice Clarity
              </div>
              <div className="metric-value">
                {Math.round((metrics?.voice?.current_clarity || 0) * 100)}%
              </div>
              <div className="metric-trend">
                {metrics?.voice?.trends?.pitch_trend === 'increasing' ? '↗️' :
                 metrics?.voice?.trends?.pitch_trend === 'decreasing' ? '↘️' : '➡️'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Alerts */}
      {metrics?.camera?.alerts && metrics.camera.alerts.length > 0 && (
        <div className="alerts-section">
          <h4>🚨 Active Alerts</h4>
          <div className="alerts-list">
            {metrics.camera.alerts.slice(0, 3).map((alert, index) => (
              <div key={index} className={`alert alert-${alert.severity}`}>
                <div className="alert-icon">
                  {alert.severity === 'high' ? '🔴' : '🟡'}
                </div>
                <div className="alert-content">
                  <div className="alert-message">{alert.message}</div>
                  <div className="alert-time">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Help Recommendations */}
      <div className="recommendations">
        <h4>💡 AI Recommendations</h4>
        <div className="recommendation-list">
          {stressInfo.level === 'high' && (
            <div className="recommendation-item">
              <span className="rec-icon">🔄</span>
              <span>High stress detected. Consider easier questions.</span>
            </div>
          )}
          {attentionInfo.level === 'low' && (
            <div className="recommendation-item">
              <span className="rec-icon">👀</span>
              <span>Low attention. Student might need a break.</span>
            </div>
          )}
          {pulseInfo.level === 'high' && (
            <div className="recommendation-item">
              <span className="rec-icon">❤️</span>
              <span>Elevated pulse. Check if student is anxious.</span>
            </div>
          )}
          {(!stressInfo.level === 'high' && !attentionInfo.level === 'low' && !pulseInfo.level === 'high') && (
            <div className="recommendation-item">
              <span className="rec-icon">✅</span>
              <span>All metrics are in optimal range. Great learning environment!</span>
            </div>
          )}
        </div>
      </div>

      <div className="metrics-footer">
        <span className="last-update">
          Last update: {metrics?.timestamp ? new Date(metrics.timestamp).toLocaleTimeString() : 'Just now'}
        </span>
        <span className="data-source">
          {error ? 'Simulated Data' : 'Live Data'}
        </span>
      </div>
    </div>
  );
};

export default RealTimeMetrics;