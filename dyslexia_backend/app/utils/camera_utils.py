import cv2
import numpy as np
import base64
from datetime import datetime
import os
import random
import threading
import time
from collections import deque

# FIX 3: Import StressAnalyzer instead of calculating stress here
from app.modules.common.stress_analyzer import stress_analyzer

# FIX 4: Add serial for ESP32 pulse sensor (uncomment when hardware is ready)
# import serial
# try:
#     ser = serial.Serial('COM3', 9600, timeout=1)  # Adjust COM port as needed
#     ESP32_CONNECTED = True
# except:
#     print("⚠️  ESP32 not connected, using fallback pulse values")
#     ESP32_CONNECTED = False

class CameraUtils:
    def __init__(self):
        # Try to load Haar cascades
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            self.cascade_loaded = True
        except:
            print("⚠️  Haar cascades not available, using simulation mode")
            self.cascade_loaded = False
            
        self.attention_history = deque(maxlen=50)
        self.stress_history = deque(maxlen=50)
        self.last_analysis_time = 0
        self.real_time_data = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
        # Store pulse readings from ESP32
        self.pulse_readings = deque(maxlen=10)  # Keep last 10 readings for smoothing
    
    # FIX 4: Add pulse reading function for ESP32
    def read_pulse_from_esp32(self):
        """Read pulse rate from ESP32 via serial"""
        # If you have ESP32 hardware connected, uncomment this:
        """
        global ESP32_CONNECTED
        if ESP32_CONNECTED:
            try:
                line = ser.readline().decode().strip()
                if line:
                    pulse = float(line)
                    self.pulse_readings.append(pulse)
                    # Return average of last few readings for smoothing
                    if len(self.pulse_readings) > 0:
                        return sum(self.pulse_readings) / len(self.pulse_readings)
                    return pulse
            except Exception as e:
                print(f"⚠️  Error reading pulse from ESP32: {e}")
                ESP32_CONNECTED = False
        """
        
        # Fallback: Return None to indicate no real pulse data
        # The stress analyzer will handle this with default values
        return None
    
    def start_real_time_monitoring(self, user_id):
        """Start real-time monitoring for user"""
        self.monitoring_active = True
        self.real_time_data[user_id] = {
            'attention_scores': deque(maxlen=100),
            'stress_levels': deque(maxlen=100),
            'pulse_rates': deque(maxlen=100),
            'voice_energy': deque(maxlen=100),
            'last_update': datetime.now(),
            'alerts': []
        }
        
        if not self.monitoring_thread:
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
        
        print(f"✅ Real-time monitoring started for user {user_id}")
    
    def stop_real_time_monitoring(self, user_id):
        """Stop real-time monitoring for user"""
        if user_id in self.real_time_data:
            del self.real_time_data[user_id]
        if not self.real_time_data:
            self.monitoring_active = False
        print(f"✅ Real-time monitoring stopped for user {user_id}")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            try:
                # Process all active user sessions
                for user_id in list(self.real_time_data.keys()):
                    self._analyze_user_state(user_id)
                
                time.sleep(2)  # Update every 2 seconds
            except Exception as e:
                print(f"❌ Monitoring loop error: {e}")
                time.sleep(5)
    
    def _analyze_user_state(self, user_id):
        """Analyze user state and generate alerts"""
        if user_id not in self.real_time_data:
            return
        
        user_data = self.real_time_data[user_id]
        
        # Check for concerning patterns
        if len(user_data['stress_levels']) > 10:
            avg_stress = np.mean(list(user_data['stress_levels'])[-10:])
            avg_attention = np.mean(list(user_data['attention_scores'])[-10:])
            avg_pulse = np.mean(list(user_data['pulse_rates'])[-10:]) if user_data['pulse_rates'] else 75
            
            # Generate alerts based on thresholds
            if avg_stress > 0.8:
                self._add_alert(user_id, "high_stress", f"High stress detected: {avg_stress:.2f}")
            elif avg_attention < 0.3:
                self._add_alert(user_id, "low_attention", f"Low attention detected: {avg_attention:.2f}")
            elif avg_pulse > 100:
                self._add_alert(user_id, "high_pulse", f"Elevated pulse rate: {avg_pulse:.1f} BPM")
    
    def _add_alert(self, user_id, alert_type, message):
        """Add alert to user's monitoring data"""
        if user_id in self.real_time_data:
            alert = {
                'type': alert_type,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'severity': 'high' if alert_type in ['high_stress', 'high_pulse'] else 'medium'
            }
            self.real_time_data[user_id]['alerts'].append(alert)
            # Keep only last 10 alerts
            self.real_time_data[user_id]['alerts'] = self.real_time_data[user_id]['alerts'][-10:]
    
    def update_real_time_data(self, user_id, analysis_data, voice_energy=0.0):
        """Update real-time monitoring data"""
        if user_id not in self.real_time_data:
            self.start_real_time_monitoring(user_id)
        
        user_data = self.real_time_data[user_id]
        user_data['attention_scores'].append(analysis_data.get('attention_score', 0.5))
        user_data['stress_levels'].append(analysis_data.get('stress_level', 0.5))
        user_data['pulse_rates'].append(analysis_data.get('pulse_rate', 75))
        user_data['voice_energy'].append(voice_energy)
        user_data['last_update'] = datetime.now()
    
    def get_real_time_metrics(self, user_id):
        """Get current real-time metrics for user"""
        if user_id not in self.real_time_data:
            return None
        
        user_data = self.real_time_data[user_id]
        
        if (datetime.now() - user_data['last_update']).seconds > 10:
            return {'status': 'inactive', 'message': 'No recent data'}
        
        metrics = {
            'status': 'active',
            'current_attention': user_data['attention_scores'][-1] if user_data['attention_scores'] else 0.5,
            'current_stress': user_data['stress_levels'][-1] if user_data['stress_levels'] else 0.5,
            'current_pulse': user_data['pulse_rates'][-1] if user_data['pulse_rates'] else 75,
            'voice_energy': user_data['voice_energy'][-1] if user_data['voice_energy'] else 0.0,
            'trends': {
                'attention_trend': self._calculate_trend(user_data['attention_scores']),
                'stress_trend': self._calculate_trend(user_data['stress_levels']),
                'pulse_trend': self._calculate_trend(user_data['pulse_rates'])
            },
            'alerts': user_data['alerts'][-5:],  # Last 5 alerts
            'last_update': user_data['last_update'].isoformat()
        }
        
        return metrics
    
    def _calculate_trend(self, data):
        """Calculate trend from data points"""
        if len(data) < 5:
            return 'stable'
        
        recent = list(data)[-5:]
        if len(recent) < 2:
            return 'stable'
        
        # Simple linear trend calculation
        x = np.arange(len(recent))
        y = np.array(recent)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.05:
            return 'increasing'
        elif slope < -0.05:
            return 'decreasing'
        else:
            return 'stable'
    
    def analyze_stress_and_attention(self, image_data, current_question=None):
        """
        Comprehensive analysis of stress and attention from REAL camera feed
        """
        try:
            # Decode base64 image
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            img_array = np.frombuffer(base64.b64decode(image_data), np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                return self._get_default_analysis("Frame decode failed")
            
            # Resize for faster processing
            frame = cv2.resize(frame, (320, 240))
            
            if not self.cascade_loaded:
                analysis = self._simulate_analysis_with_visual(frame)
            else:
                analysis = self._real_face_analysis(frame, current_question)
            
            # Update real-time data with the analysis
            self.update_real_time_data(
                user_id="default",
                analysis_data=analysis
            )
            
            return analysis
            
        except Exception as e:
            print(f"❌ Camera analysis error: {e}")
            analysis = self._get_default_analysis(str(e))
            
            # Still try to update with default data
            self.update_real_time_data(
                user_id="default",
                analysis_data=analysis
            )
            
            return analysis
    
    def _real_face_analysis(self, frame, current_question):
        """Real face and eye detection analysis"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            return self._handle_no_face_detected()
        
        # Analyze the largest face
        (x, y, w, h) = max(faces, key=lambda rect: rect[2] * rect[3])
        
        # Detect eyes within face region
        roi_gray = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(roi_gray)
        
        # Calculate metrics based on real detection
        attention_score = self._calculate_real_attention(eyes, w, h)
        
        # FIX 3: Use StressAnalyzer instead of calculating stress here
        # Get pulse rate from ESP32 if available
        pulse_rate = self.read_pulse_from_esp32()
        
        # If no pulse from ESP32, use None (StressAnalyzer will handle with default)
        # The StressAnalyzer will use pulse_data=None and facial_data with attention_score
        stress_data = stress_analyzer.analyze_stress(
            user_id="default",  # You might want to pass actual user_id here
            pulse_data=pulse_rate,  # Will be None if no ESP32, StressAnalyzer handles it
            facial_data={"attention_score": attention_score}
        )
        
        stress_level = stress_data["stress_level"]
        is_high_stress = stress_data["is_high_stress"]
        
        # Check for signs of difficulty
        is_stuck = self._detect_concentration_issues(attention_score)
        needs_help = self._determine_help_needed(stress_level, attention_score, is_stuck)
        
        analysis = {
            'attention_score': attention_score,
            'stress_level': stress_level,
            'is_high_stress': is_high_stress,
            'is_looking_away': attention_score < 0.3,
            'eyes_detected': len(eyes),
            'face_detected': True,
            'pulse_rate': pulse_rate if pulse_rate else 75,  # Use real pulse or fallback
            'pulse_source': 'esp32' if pulse_rate else 'fallback',
            'is_gaze_stuck': is_stuck,
            'needs_help': needs_help,
            'help_message': self._generate_real_help_message(stress_level, attention_score, is_stuck),
            'analysis_type': 'real_camera',
            'timestamp': datetime.now().isoformat()
        }
        
        # Update history for trend analysis
        self.attention_history.append(attention_score)
        self.stress_history.append(stress_level)
        
        return analysis
    
    def _calculate_real_attention(self, eyes, face_width, face_height):
        """Calculate attention based on real eye detection"""
        if len(eyes) == 0:
            return 0.2  # No eyes detected
        
        base_score = min(1.0, len(eyes) / 2.0)
        
        if len(eyes) >= 2:
            # Analyze eye positions for more accurate attention scoring
            eye_positions = []
            for (ex, ey, ew, eh) in eyes:
                eye_center_x = ex + ew // 2
                eye_center_y = ey + eh // 2
                eye_positions.append((eye_center_x, eye_center_y))
            
            # Calculate if eyes are properly aligned and focused
            alignment_score = self._calculate_eye_alignment(eye_positions, face_width)
            stability_score = self._calculate_gaze_stability(eye_positions)
            
            final_score = (base_score * 0.4) + (alignment_score * 0.3) + (stability_score * 0.3)
        else:
            final_score = base_score * 0.7
        
        return min(1.0, max(0.1, final_score))
    
    def _calculate_eye_alignment(self, eye_positions, face_width):
        """Calculate how well eyes are aligned"""
        if len(eye_positions) < 2:
            return 0.5
        
        # Calculate distance between eyes
        eye1_x, eye1_y = eye_positions[0]
        eye2_x, eye2_y = eye_positions[1]
        
        distance = abs(eye1_x - eye2_x)
        normalized_distance = distance / face_width
        
        # Ideal inter-eye distance is about 0.3-0.4 of face width
        ideal_distance = 0.35
        distance_score = 1.0 - min(1.0, abs(normalized_distance - ideal_distance) / 0.2)
        
        return distance_score
    
    def _calculate_gaze_stability(self, eye_positions):
        """Calculate gaze stability (simple version)"""
        # In a real system, you'd compare with previous frames
        # For now, return a reasonable estimate
        return random.uniform(0.6, 0.9)
    
    # FIX 1: REMOVED _calculate_real_stress function completely
    
    # FIX 2: REMOVED _estimate_pulse_from_face function completely
    
    def _detect_concentration_issues(self, attention_score):
        """Detect if user is having concentration issues"""
        # Low attention for extended period might indicate confusion
        if attention_score < 0.4:
            return random.random() < 0.4  # 40% chance if low attention
        return False
    
    def _determine_help_needed(self, stress_level, attention_score, is_stuck):
        """Determine if user needs help"""
        return (stress_level > 0.7 or 
                attention_score < 0.3 or 
                is_stuck or
                random.random() < 0.1)  # 10% random check
    
    def _generate_real_help_message(self, stress_level, attention_score, is_stuck):
        """Generate appropriate help message"""
        if stress_level > 0.8:
            return "I can see you're finding this challenging. Let me give you an easier question!"
        elif stress_level > 0.7:
            return "You're doing great! Let me help you with this one."
        elif attention_score < 0.3:
            return "I notice you're looking away. Let's focus on this together."
        elif is_stuck:
            return "Let me break this down into smaller steps for you."
        else:
            return "Would you like a hint with this question?"
    
    def _simulate_analysis_with_visual(self, frame):
        """Simulate analysis when face detection is not available"""
        # Even without face detection, we can analyze some visual cues
        brightness = np.mean(frame)
        contrast = np.std(frame)
        
        # Simple heuristic based on image properties
        if brightness < 50:  # Dark image
            attention_score = 0.2
        elif brightness > 200:  # Very bright
            attention_score = 0.3
        else:  # Normal lighting
            attention_score = random.uniform(0.5, 0.8)
        
        # FIX 3: Use StressAnalyzer even in simulation mode
        pulse_rate = self.read_pulse_from_esp32()
        
        stress_data = stress_analyzer.analyze_stress(
            user_id="default",
            pulse_data=pulse_rate,
            facial_data={"attention_score": attention_score}
        )
        
        stress_level = stress_data["stress_level"]
        is_high_stress = stress_data["is_high_stress"]
        
        return {
            'attention_score': attention_score,
            'stress_level': stress_level,
            'is_high_stress': is_high_stress,
            'is_looking_away': attention_score < 0.4,
            'eyes_detected': 0,
            'face_detected': False,
            'pulse_rate': pulse_rate if pulse_rate else 75,
            'pulse_source': 'esp32' if pulse_rate else 'fallback',
            'is_gaze_stuck': random.random() < 0.2,
            'needs_help': is_high_stress or attention_score < 0.4,
            'help_message': "I'm here to help if you need it!",
            'analysis_type': 'simulated',
            'timestamp': datetime.now().isoformat()
        }
    
    def _handle_no_face_detected(self):
        """Handle case when no face is detected"""
        # FIX 3: Use StressAnalyzer even when no face detected
        pulse_rate = self.read_pulse_from_esp32()
        
        # When no face, attention is very low
        attention_score = 0.1
        
        stress_data = stress_analyzer.analyze_stress(
            user_id="default",
            pulse_data=pulse_rate,
            facial_data={"attention_score": attention_score}
        )
        
        stress_level = stress_data["stress_level"]
        is_high_stress = stress_data["is_high_stress"]
        
        return {
            'attention_score': attention_score,
            'stress_level': stress_level,
            'is_high_stress': is_high_stress,
            'is_looking_away': True,
            'eyes_detected': 0,
            'face_detected': False,
            'pulse_rate': pulse_rate if pulse_rate else 75,
            'pulse_source': 'esp32' if pulse_rate else 'fallback',
            'is_gaze_stuck': False,
            'needs_help': True,
            'help_message': "I don't see you looking at the screen. Let me help you get started!",
            'analysis_type': 'no_face',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_default_analysis(self, reason="Unknown"):
        """Return default analysis when analysis fails"""
        # FIX 3: Use StressAnalyzer for default case
        pulse_rate = self.read_pulse_from_esp32()
        
        stress_data = stress_analyzer.analyze_stress(
            user_id="default",
            pulse_data=pulse_rate,
            facial_data={"attention_score": 0.5}  # Default attention
        )
        
        stress_level = stress_data["stress_level"]
        is_high_stress = stress_data["is_high_stress"]
        
        return {
            'attention_score': 0.5,
            'stress_level': stress_level,
            'is_high_stress': is_high_stress,
            'is_looking_away': False,
            'eyes_detected': 0,
            'face_detected': False,
            'pulse_rate': pulse_rate if pulse_rate else 75,
            'pulse_source': 'esp32' if pulse_rate else 'fallback',
            'is_gaze_stuck': False,
            'needs_help': False,
            'help_message': "Everything looks good! Keep going!",
            'analysis_type': f'default_{reason}',
            'timestamp': datetime.now().isoformat()
        }

# Global camera utils instance
camera_utils = CameraUtils()
