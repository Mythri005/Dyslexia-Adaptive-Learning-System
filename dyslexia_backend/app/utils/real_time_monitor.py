import cv2
import numpy as np
import threading
import time
import queue
from collections import deque
from app.utils.camera_utils import camera_utils
from app.utils.speech_utils import speech_utils
import base64

class RealTimeMonitor:
    def __init__(self):
        self.camera_active = False
        self.monitoring_active = False
        self.camera_thread = None
        self.analysis_thread = None
        self.voice_thread = None
        
        # Real-time data buffers
        self.pulse_buffer = deque(maxlen=100)
        self.stress_buffer = deque(maxlen=50)
        self.attention_buffer = deque(maxlen=50)
        self.voice_buffer = queue.Queue()
        
        # Current monitoring data
        self.current_pulse = 75
        self.current_stress = 0.5
        self.current_attention = 0.7
        self.voice_activity = False
        self.last_analysis_time = time.time()
        
    def start_real_time_monitoring(self, user_id, session_type="math"):
        """Start real-time monitoring of pulse, camera, and voice"""
        if self.monitoring_active:
            return {"status": "already_running"}
        
        self.monitoring_active = True
        self.user_id = user_id
        self.session_type = session_type
        
        # Start camera monitoring thread
        self.camera_thread = threading.Thread(target=self._camera_monitoring_loop)
        self.camera_thread.daemon = True
        self.camera_thread.start()
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._analysis_loop)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
        # Start voice monitoring thread
        self.voice_thread = threading.Thread(target=self._voice_monitoring_loop)
        self.voice_thread.daemon = True
        self.voice_thread.start()
        
        return {
            "status": "started",
            "message": "Real-time monitoring started for pulse, camera, and voice",
            "user_id": user_id,
            "session_type": session_type
        }
    
    def stop_real_time_monitoring(self):
        """Stop all real-time monitoring"""
        self.monitoring_active = False
        self.camera_active = False
        
        if self.camera_thread:
            self.camera_thread.join(timeout=1)
        if self.analysis_thread:
            self.analysis_thread.join(timeout=1)
        if self.voice_thread:
            self.voice_thread.join(timeout=1)
            
        return {"status": "stopped", "message": "Real-time monitoring stopped"}
    
    def _camera_monitoring_loop(self):
        """Continuous camera monitoring for pulse and stress detection"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot access camera for real-time monitoring")
            return
        
        self.camera_active = True
        print("📹 Starting real-time camera monitoring...")
        
        frame_count = 0
        last_pulse_calculation = time.time()
        
        while self.monitoring_active and self.camera_active:
            ret, frame = cap.read()
            if not ret:
                continue
            
            frame_count += 1
            
            # Analyze frame every 0.5 seconds for real-time response
            current_time = time.time()
            if current_time - self.last_analysis_time >= 0.5:
                self.last_analysis_time = current_time
                
                # Convert frame for analysis
                _, buffer = cv2.imencode('.jpg', frame)
                image_base64 = "data:image/jpeg;base64," + base64.b64encode(buffer).decode('utf-8')
                
                # Get real-time analysis
                analysis = camera_utils.analyze_stress_and_attention(image_base64, "Real-time monitoring")
                
                # Update current metrics
                self.current_stress = analysis.get('stress_level', 0.5)
                self.current_attention = analysis.get('attention_score', 0.7)
                
                # Calculate pulse from face analysis (simulated for now)
                if current_time - last_pulse_calculation >= 2.0:  # Every 2 seconds
                    self.current_pulse = self._calculate_real_time_pulse(frame, analysis)
                    self.pulse_buffer.append(self.current_pulse)
                    last_pulse_calculation = current_time
                
                # Store in buffers
                self.stress_buffer.append(self.current_stress)
                self.attention_buffer.append(self.current_attention)
            
            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)
        
        cap.release()
        print("📹 Real-time camera monitoring stopped")
    
    def _calculate_real_time_pulse(self, frame, analysis):
        """Calculate pulse rate from facial video analysis"""
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Simple pulse simulation based on stress and attention
            base_pulse = 70
            stress_effect = int(self.current_stress * 25)
            attention_effect = int((1 - self.current_attention) * 15)
            
            # Add some realistic variation
            random_variation = np.random.randint(-3, 4)
            
            pulse = base_pulse + stress_effect + attention_effect + random_variation
            
            # Ensure realistic bounds
            pulse = max(60, min(120, pulse))
            
            return pulse
            
        except Exception as e:
            print(f"❌ Pulse calculation error: {e}")
            return 75  # Default fallback
    
    def _voice_monitoring_loop(self):
        """Continuous voice activity monitoring"""
        print("🎤 Starting real-time voice monitoring...")
        
        # This would integrate with continuous audio recording
        # For now, we'll simulate voice activity detection
        
        while self.monitoring_active:
            # Simulate voice activity detection
            # In real implementation, this would use:
            # - PyAudio for continuous recording
            # - Voice activity detection (VAD) algorithms
            # - Real-time speech analysis
            
            self.voice_activity = np.random.random() > 0.7  # Simulate 30% voice activity
            
            if self.voice_activity:
                # Simulate processing voice data
                voice_data = {
                    "timestamp": time.time(),
                    "activity_detected": True,
                    "volume_level": np.random.uniform(0.1, 1.0),
                    "speech_detected": np.random.random() > 0.3
                }
                self.voice_buffer.put(voice_data)
            
            time.sleep(0.5)  # Check every 0.5 seconds
        
        print("🎤 Real-time voice monitoring stopped")
    
    def _analysis_loop(self):
        """Continuous analysis of monitoring data"""
        print("📊 Starting real-time analysis loop...")
        
        last_alert_time = 0
        alert_cooldown = 10  # seconds between alerts
        
        while self.monitoring_active:
            current_time = time.time()
            
            # Check for critical conditions
            if self.current_stress > 0.8 and (current_time - last_alert_time) > alert_cooldown:
                self._trigger_stress_alert()
                last_alert_time = current_time
            
            elif self.current_attention < 0.3 and (current_time - last_alert_time) > alert_cooldown:
                self._trigger_attention_alert()
                last_alert_time = current_time
            
            elif self.current_pulse > 100 and (current_time - last_alert_time) > alert_cooldown:
                self._trigger_pulse_alert()
                last_alert_time = current_time
            
            time.sleep(1)  # Analyze every second
    
    def _trigger_stress_alert(self):
        """Trigger alert for high stress"""
        alert_data = {
            "type": "high_stress",
            "level": "warning",
            "message": "High stress detected! Consider easier questions.",
            "stress_level": self.current_stress,
            "timestamp": time.time()
        }
        print(f"🚨 STRESS ALERT: {alert_data['message']} (Level: {self.current_stress:.2f})")
        
        # Send to frontend via WebSocket or store for API retrieval
        self._store_alert(alert_data)
    
    def _trigger_attention_alert(self):
        """Trigger alert for low attention"""
        alert_data = {
            "type": "low_attention",
            "level": "warning", 
            "message": "Low attention detected! Student might be distracted.",
            "attention_level": self.current_attention,
            "timestamp": time.time()
        }
        print(f"🚨 ATTENTION ALERT: {alert_data['message']} (Level: {self.current_attention:.2f})")
        self._store_alert(alert_data)
    
    def _trigger_pulse_alert(self):
        """Trigger alert for high pulse rate"""
        alert_data = {
            "type": "high_pulse",
            "level": "warning",
            "message": "Elevated pulse rate detected! Student might be anxious.",
            "pulse_rate": self.current_pulse,
            "timestamp": time.time()
        }
        print(f"🚨 PULSE ALERT: {alert_data['message']} (Rate: {self.current_pulse} BPM)")
        self._store_alert(alert_data)
    
    def _store_alert(self, alert_data):
        """Store alert for API retrieval"""
        # In production, this would store in database or send via WebSocket
        pass
    
    def get_current_metrics(self):
        """Get current real-time metrics"""
        return {
            "pulse_rate": self.current_pulse,
            "stress_level": self.current_stress,
            "attention_level": self.current_attention,
            "voice_activity": self.voice_activity,
            "monitoring_active": self.monitoring_active,
            "timestamp": time.time()
        }
    
    def get_historical_data(self, metric="all", window=30):
        """Get historical monitoring data"""
        data = {
            "pulse": list(self.pulse_buffer)[-window:],
            "stress": list(self.stress_buffer)[-window:],
            "attention": list(self.attention_buffer)[-window:],
            "timestamps": [time.time() - i for i in range(min(window, len(self.pulse_buffer)))]
        }
        
        if metric != "all":
            return data.get(metric, [])
        
        return data

# Global real-time monitor instance
real_time_monitor = RealTimeMonitor()

