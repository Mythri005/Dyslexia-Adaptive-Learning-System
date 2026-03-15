class AdaptiveAlgorithm:
    def __init__(self):
        self.difficulty_thresholds = {
            'easy_to_medium': 0.7,   # 70% accuracy to move to medium
            'medium_to_hard': 0.75,  # 75% accuracy to move to hard
            'hard_to_medium': 0.6,   # Below 60% move back to medium
            'medium_to_easy': 0.5    # Below 50% move back to easy
        }
        
        self.stress_impact = 0.3  # How much stress affects difficulty adjustment
    
    def adjust_difficulty(self, current_difficulty, accuracy, stress_level, attention_score, pulse_rate):
        """
        Adjust difficulty based on performance and stress
        High stress = easier questions, Low stress = harder questions
        """
        # SAFE FALLBACKS
        if pulse_rate is None:
            pulse_rate = 75   # neutral resting BPM

        if stress_level is None:
            stress_level = 0  # neutral stress

        # Normalize all inputs between 0–1
        
        accuracy_factor = accuracy  # already 0–1
        
        attention_factor = max(0.0, min(1.0, attention_score / 100))  # FIXED normalization
        
        pulse_stress = min(1.0, abs(pulse_rate - 75) / 50)
        
        # Convert pulse into performance-friendly metric
        pulse_factor = 1 - pulse_stress
        
        # Convert stress into performance-friendly metric
        stress_factor = 1 - stress_level
        
        # Equal weighted adaptive score (25% each)
        adaptive_score = (
            accuracy_factor * 0.25 +
            attention_factor * 0.25 +
            stress_factor * 0.25 +
            pulse_factor * 0.25
        )
        
        # Clamp between 0–1
        adaptive_score = max(0.0, min(1.0, adaptive_score))
        
        # Difficulty decision based on adaptive score
        if adaptive_score >= 0.75:
            return 'hard'
        elif adaptive_score >= 0.5:
            return 'medium'
        else:
            return 'easy'
    
    def should_provide_hint(self, consecutive_wrong, stress_level, time_spent):
        """
        Decide whether to provide a hint to the student
        """
        hint_conditions = [
            consecutive_wrong >= 2,
            stress_level > 0.8,
            time_spent > 30  # 30 seconds on same question
        ]
        
        return any(hint_conditions)
    
    def calculate_stress_impact(self, stress_level, attention_score):
        """
        Calculate overall impact of stress and attention on learning
        """
        # High stress and low attention = high impact (needs help)
        stress_impact = stress_level * 0.6 + (1 - attention_score) * 0.4
        return min(1.0, stress_impact)