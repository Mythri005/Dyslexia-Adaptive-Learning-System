# camera_integration.py
import cv2
import base64
import requests
import json
import time
import os
import numpy as np

# Try to import mediapipe, but provide fallback if not available
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    print("✅ MediaPipe loaded successfully")
except ImportError as e:
    MEDIAPIPE_AVAILABLE = False
    print(f"⚠️ MediaPipe not available: {e}")
    print("⚠️ Using fallback head pose detection")
    mp = None

class RealCameraIntegration:
    def __init__(self):
        self.cap = None
        self.is_camera_active = False

        # Load Haar Cascades for face & eye detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml"
        )
        
        # Proctored monitoring timers
        self.last_face_time = time.time()
        self.face_absent_duration = 0
        
        # MediaPipe Face Mesh for head pose (if available)
        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_face_mesh = mp.solutions.face_mesh
                self.face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=2,
                    refine_landmarks=True
                )
                print("✅ MediaPipe Face Mesh initialized")
            except Exception as e:
                print(f"⚠️ MediaPipe Face Mesh initialization failed: {e}")
                self.face_mesh = None
        else:
            self.face_mesh = None
        
    def start_camera(self):
        """Start the system camera"""
        try:
            self.cap = cv2.VideoCapture(0)
            
            if not self.cap.isOpened():
                print("❌ Cannot access camera. Please check permissions.")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_camera_active = True
            print("✅ Camera started successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Camera start error: {e}")
            return False
    
    def capture_frame(self):
        """Capture a frame from camera"""
        if not self.is_camera_active or self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def frame_to_base64(self, frame):
        """Convert OpenCV frame to base64"""
        try:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            return f"data:image/jpeg;base64,{image_base64}"
        except Exception as e:
            print(f"❌ Frame conversion error: {e}")
            return None

    def detect_head_pose_fallback(self, frame, faces):
        """Fallback head pose detection using face position"""
        if len(faces) == 0:
            return "no_face"
        
        h, w, _ = frame.shape
        x, y, w, h = faces[0]
        
        # Get face center
        face_center_x = x + w//2
        frame_center_x = frame.shape[1] // 2
        
        # Simple head pose estimation based on face position
        offset = abs(face_center_x - frame_center_x)
        
        if offset < 30:
            return "looking_center"
        elif face_center_x < frame_center_x:
            return "looking_left"
        else:
            return "looking_right"

    def detect_head_pose(self, frame, faces):
        """Detect if user is looking straight or away (with fallback)"""
        
        # If MediaPipe is not available, use fallback
        if not MEDIAPIPE_AVAILABLE or self.face_mesh is None:
            return self.detect_head_pose_fallback(frame, faces)
        
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)

            if not results.multi_face_landmarks:
                return self.detect_head_pose_fallback(frame, faces)

            face_landmarks = results.multi_face_landmarks[0]

            # Get nose & eye landmarks
            nose = face_landmarks.landmark[1]
            left_eye = face_landmarks.landmark[33]
            right_eye = face_landmarks.landmark[263]

            # Convert to pixel coords
            h, w, _ = frame.shape
            nose_x = int(nose.x * w)
            left_x = int(left_eye.x * w)
            right_x = int(right_eye.x * w)

            # Head direction logic
            eye_center = (left_x + right_x) // 2

            if nose_x < eye_center - 20:
                return "looking_left"
            elif nose_x > eye_center + 20:
                return "looking_right"
            else:
                return "looking_center"
                
        except Exception as e:
            print(f"⚠️ Head pose detection error: {e}")
            return self.detect_head_pose_fallback(frame, faces)

    def local_face_eye_analysis(self, frame):
        """Detect face, eyes & calculate attention score with proctored monitoring"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        eyes = self.eye_cascade.detectMultiScale(gray, 1.3, 5)

        face_detected = len(faces) > 0
        eye_detected = len(eyes) > 0

        current_time = time.time()

        # Track face absence duration
        if face_detected:
            self.last_face_time = current_time
            self.face_absent_duration = 0
        else:
            self.face_absent_duration = current_time - self.last_face_time

        # Multiple face detection (proctoring feature)
        multiple_faces = len(faces) > 1
        
        # Head pose detection (pass faces for fallback)
        head_pose = self.detect_head_pose(frame, faces)

        # Attention Score Logic (Enhanced with proctored monitoring)
        if multiple_faces:
            attention_score = 20   # Cheating / distraction risk
        elif self.face_absent_duration > 3:
            attention_score = 25   # Face missing >3 sec
        elif head_pose != "looking_center":
            attention_score = 40   # Looking away
        elif face_detected and eye_detected:
            attention_score = 95   # Fully attentive
        elif face_detected:
            attention_score = 65   # Partial attention
        else:
            attention_score = 30   # Not attentive

        return (
            face_detected, 
            eye_detected, 
            attention_score, 
            faces, 
            eyes,
            multiple_faces,
            self.face_absent_duration,
            head_pose
        )

    def decide_difficulty(self, attention_score, stress_level):
        """Decide difficulty change based on attention + stress"""
        if attention_score > 80 and stress_level < 0.4:
            return "increase"
        elif attention_score < 50 or stress_level > 0.7:
            return "decrease"
        return "keep"
    
    def analyze_frame(self, frame, current_question=None):
        """Send frame to API + merge local analysis"""
        try:
            image_data = self.frame_to_base64(frame)
            if not image_data:
                return None

            # Local face & eye detection with proctored monitoring
            (face_detected, 
             eye_detected, 
             attention_score, 
             faces, 
             eyes,
             multiple_faces,
             face_absent_duration,
             head_pose) = self.local_face_eye_analysis(frame)
                
            url = os.getenv("CAMERA_API_URL", "http://localhost:5001/api/camera/analyze")
            data = {
                "image_data": image_data,
                "current_question": current_question,
                "face_detected": face_detected,
                "eye_detected": eye_detected,
                "attention_score": attention_score,
                "multiple_faces": multiple_faces,
                "face_absent_duration": face_absent_duration,
                "head_pose": head_pose
            }
            
            response = requests.post(url, json=data, timeout=5)
            
            api_data = {}
            if response.status_code == 200:
                api_data = response.json()
            else:
                print(f"❌ Analysis API error: {response.status_code}")

            stress = api_data.get("stress_level", 0)
            difficulty_action = self.decide_difficulty(attention_score, stress)

            # Determine if help is needed
            needs_help = (
                attention_score < 50 or 
                stress > 0.7 or 
                multiple_faces or 
                face_absent_duration > 3 or
                head_pose != "looking_center"
            )

            # Merge local + API results
            api_data.update({
                "face_detected": face_detected,
                "eye_detected": eye_detected,
                "attention_score": attention_score,
                "difficulty_action": difficulty_action,
                "needs_help": needs_help,
                "multiple_faces": multiple_faces,
                "face_absent_duration": face_absent_duration,
                "head_pose": head_pose
            })

            return api_data
                
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def show_camera_preview(self):
        """Show camera preview window with proctored monitoring alerts"""
        if not self.is_camera_active:
            return
            
        print("📷 Starting camera preview... Press 'q' to quit")
        
        last_check_time = 0
        
        while True:
            frame = self.capture_frame()
            if frame is None:
                break

            # Local analysis with proctored monitoring
            (face_detected, 
             eye_detected, 
             attention_score, 
             faces, 
             eyes,
             multiple_faces,
             face_absent_duration,
             head_pose) = self.local_face_eye_analysis(frame)

            # Draw face boxes
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Draw eye boxes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame, (ex, ey), (ex+ew, ey+eh), (255, 255, 0), 1)

            # Call API every 2 seconds
            if time.time() - last_check_time > 2:
                analysis = self.analyze_frame(frame, "Test Question")
                last_check_time = time.time()

                if analysis:
                    stress = analysis.get('stress_level', 0)
                    pulse = analysis.get('pulse_rate', 0)
                    difficulty = analysis.get('difficulty_action', 'keep')
                    needs_help = analysis.get('needs_help', False)

                    cv2.putText(frame, f"Stress: {stress:.2f}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.putText(frame, f"Attention: {attention_score}", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.putText(frame, f"Pulse: {pulse}", (10, 90),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    cv2.putText(frame, f"Difficulty: {difficulty}", (10, 120),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)

                    if needs_help:
                        cv2.putText(frame, "⚠ NEEDS HELP", (10, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                    # Proctored monitoring alerts
                    if multiple_faces:
                        cv2.putText(frame, "⚠ Multiple Faces Detected",
                                    (10, 180),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                    (0, 0, 255), 2)

                    if face_absent_duration > 3:
                        cv2.putText(frame, "⚠ Face Not Detected",
                                    (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                    (0, 0, 255), 2)
                    
                    if head_pose == "looking_left" or head_pose == "looking_right":
                        cv2.putText(frame, "⚠ Looking Away",
                                    (10, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                    (0, 0, 255), 2)

            cv2.imshow('Dyslexia System - Camera Preview', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.stop_camera()
    
    def stop_camera(self):
        """Stop the camera"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.is_camera_active = False
        print("✅ Camera stopped")

def test_real_camera_with_api():
    """Test complete camera integration with API"""
    camera = RealCameraIntegration()
    
    if camera.start_camera():
        print("\n🔍 Testing single frame analysis...")
        frame = camera.capture_frame()
        if frame is not None:
            analysis = camera.analyze_frame(frame, "2 + 3 = ?")
            if analysis:
                print("✅ Real camera analysis successful!")
                print(json.dumps(analysis, indent=2))
        
        camera.show_camera_preview()
    else:
        print("❌ Failed to start camera")

if __name__ == "__main__":
    test_real_camera_with_api()
