"""
Stress Analyzer Module for Adaptive Learning System
Analyzes student stress based on real pulse rate and attention data from IoT devices
"""

class StressAnalyzer:
    def __init__(self):
        self.stress_threshold = 0.7  # Threshold for high stress detection
        self.stress_history = {}      # Store historical stress data per user
        self.ideal_pulse = 75         # Normal resting heart rate in BPM
        self.pulse_range = 40          # Max deviation from ideal pulse (75 ± 40 = 35-115 BPM)
        
    def analyze_stress(self, user_id, pulse_data, facial_data=None):
        """
        Calculate REAL stress based on pulse deviation and attention from facial data
        
        Parameters:
        - user_id: Unique identifier for the student
        - pulse_data: Current heart rate in BPM (from IoT pulse sensor)
        - facial_data: Dictionary containing attention_score from camera
        
        Returns:
        - Dictionary with stress analysis results
        """
        
        # SAFETY CHECK FOR MISSING PULSE
        if pulse_data is None:
            pulse_data = self.ideal_pulse

        # Step 1: Calculate pulse-based stress
        # Higher deviation from ideal pulse (75 BPM) = higher stress
        pulse_deviation = abs(pulse_data - self.ideal_pulse)
        pulse_stress = min(1.0, pulse_deviation / self.pulse_range)
        
        # Step 2: Calculate attention-based stress from facial data
        # Default to 0.5 if no facial data available
        attention_score = 0.5
        if facial_data and isinstance(facial_data, dict):
            attention_score = facial_data.get("attention_score", 0.5)
        
        # SAFETY CHECK FOR NONE ATTENTION SCORE
        if attention_score is None:
            attention_score = 0.5
        
        # Normalize if needed (convert 0-100 scale to 0-1)
        if isinstance(attention_score, (int, float)) and attention_score > 1.0:
            attention_score = attention_score / 100.0
        
        # Lower attention = higher stress
        attention_stress = 1 - attention_score
        
        # Step 3: Combine both factors (50% weight each)
        stress_level = (pulse_stress * 0.5) + (attention_stress * 0.5)
        
        # Step 4: Ensure value is within 0-1 range
        stress_level = max(0.0, min(1.0, stress_level))
        
        # Step 5: Determine if stress is high
        is_high_stress = stress_level > self.stress_threshold
        
        # Step 6: Store in history for trend analysis
        if user_id not in self.stress_history:
            self.stress_history[user_id] = []
        
        self.stress_history[user_id].append({
            'stress_level': stress_level,
            'pulse_data': pulse_data,
            'attention_score': attention_score,
            'pulse_stress': pulse_stress,
            'attention_stress': attention_stress,
            'timestamp': self._get_timestamp()
        })
        
        # Keep only last 50 records per user
        if len(self.stress_history[user_id]) > 50:
            self.stress_history[user_id].pop(0)
        
        # Step 7: Generate recommendation based on stress
        recommendation = self._generate_recommendation(
            stress_level, 
            is_high_stress,
            pulse_data,
            attention_score
        )
        
        return {
            'stress_level': round(stress_level, 2),
            'is_high_stress': is_high_stress,
            'recommendation': recommendation,
            # Additional metrics for debugging/analytics
            'pulse_stress': round(pulse_stress, 2),
            'attention_stress': round(attention_stress, 2),
            'pulse_data': pulse_data,
            'attention_score': round(attention_score, 2)
        }
    
    def _generate_recommendation(self, stress_level, is_high_stress, pulse_data, attention_score):
        """Generate personalized recommendations based on stress patterns"""
        
        if is_high_stress:
            if pulse_data > 95:
                return "easier_questions_with_break"
            elif attention_score < 0.3:
                return "easier_questions_visual_aids"
            else:
                return "easier_questions"
        else:
            if stress_level < 0.3:
                return "challenge_with_harder"
            elif stress_level < 0.5:
                return "continue_current"
            else:
                return "maintain_pace"
    
    def _get_timestamp(self):
        """Get current timestamp for history tracking"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def update_performance(self, user_id, is_correct, response_time):
        """
        Update stress history based on performance
        Kept for backward compatibility
        """
        # This can be used as an additional factor in future versions
        # For now, it's maintained as a placeholder
        performance_score = 1.0 if is_correct else 0.3
        time_factor = min(1.0, response_time / 30.0)
        
        # Store performance data if needed
        if user_id not in self.stress_history:
            self.stress_history[user_id] = []
        
        # You could enhance stress calculation with this data
        pass
    
    def get_stress_trend(self, user_id):
        """Get stress trend for a user over time"""
        if user_id not in self.stress_history or not self.stress_history[user_id]:
            return "no_data"
        
        history = self.stress_history[user_id]
        if len(history) < 3:
            return "insufficient_data"
        
        # Calculate trend from last 5 readings
        recent = history[-5:] if len(history) >= 5 else history
        first_stress = recent[0]['stress_level']
        last_stress = recent[-1]['stress_level']
        
        if last_stress > first_stress * 1.2:
            return "increasing"
        elif last_stress < first_stress * 0.8:
            return "decreasing"
        else:
            return "stable"


# Global stress analyzer instance
stress_analyzer = StressAnalyzer()


# ============================================
# EXAMPLE USAGE AND TEST CASES
# ============================================

if __name__ == "__main__":
    # Create analyzer instance
    analyzer = StressAnalyzer()
    
    # Test Case 1: Student with high pulse, low attention
    print("\n=== Test Case 1: High Stress (Pulse High, Attention Low) ===")
    result1 = analyzer.analyze_stress(
        user_id="student_123",
        pulse_data=110,        # High pulse (>95 BPM)
        facial_data={"attention_score": 0.2}  # Low attention (0-1 scale)
    )
    print(f"Stress Level: {result1['stress_level']}")
    print(f"High Stress: {result1['is_high_stress']}")
    print(f"Recommendation: {result1['recommendation']}")
    print(f"Details: Pulse Stress={result1['pulse_stress']}, Attention Stress={result1['attention_stress']}")
    
    # Test Case 2: Student with normal pulse, good attention
    print("\n=== Test Case 2: Low Stress (Normal Pulse, Good Attention) ===")
    result2 = analyzer.analyze_stress(
        user_id="student_123",
        pulse_data=72,          # Normal pulse (close to 75)
        facial_data={"attention_score": 0.9}  # High attention
    )
    print(f"Stress Level: {result2['stress_level']}")
    print(f"High Stress: {result2['is_high_stress']}")
    print(f"Recommendation: {result2['recommendation']}")
    
    # Test Case 3: Student with facial data as 0-100 scale
    print("\n=== Test Case 3: Camera sends 0-100 scale ===")
    result3 = analyzer.analyze_stress(
        user_id="student_456",
        pulse_data=88,
        facial_data={"attention_score": 95}  # 95% attention (will be converted to 0.95)
    )
    print(f"Stress Level: {result3['stress_level']}")
    print(f"Attention Score (auto-converted): {result3['attention_score']}")
    
    # Test Case 4: No facial data (uses default 0.5)
    print("\n=== Test Case 4: No Facial Data (Uses Default) ===")
    result4 = analyzer.analyze_stress(
        user_id="student_789",
        pulse_data=82,
        facial_data=None  # No camera data
    )
    print(f"Stress Level: {result4['stress_level']}")
    print(f"Default Attention Used: {result4['attention_score']}")
    
    # Test Case 5: Missing pulse data (uses default 75)
    print("\n=== Test Case 5: Missing Pulse Data (Uses Default 75) ===")
    result5 = analyzer.analyze_stress(
        user_id="student_999",
        pulse_data=None,  # Missing pulse data
        facial_data={"attention_score": 0.8}
    )
    print(f"Stress Level: {result5['stress_level']}")
    print(f"Pulse Data (default used): {result5['pulse_data']}")
    print(f"Pulse Stress: {result5['pulse_stress']}")
    
    # Test Case 6: None attention score from facial data
    print("\n=== Test Case 6: None Attention Score (Uses Default 0.5) ===")
    result6 = analyzer.analyze_stress(
        user_id="student_101",
        pulse_data=82,
        facial_data={"attention_score": None}  # Attention score is None
    )
    print(f"Stress Level: {result6['stress_level']}")
    print(f"Attention Score (default used): {result6['attention_score']}")
    
    # Test trend analysis
    print("\n=== Stress Trend Analysis ===")
    trend = analyzer.get_stress_trend("student_123")
    print(f"Trend: {trend}")
