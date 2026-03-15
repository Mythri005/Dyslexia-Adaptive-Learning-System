class AdaptiveAlgorithm:
    def __init__(self):
        self.difficulty_thresholds = {
            'easy_to_medium': 0.7,   # 70% accuracy to move to medium
            'medium_to_hard': 0.75,  # 75% accuracy to move to hard
            'hard_to_medium': 0.6,   # Below 60% move back to medium
            'medium_to_easy': 0.5    # Below 50% move back to easy
        }
        
        self.stress_impact = 0.3  # How much stress affects difficulty adjustment
    
    def adjust_difficulty(self, current_difficulty, accuracy, stress_level):
        """
        Adjust difficulty based on performance and stress
        """
        # Adjust thresholds based on stress
        stress_adjustment = (1 - stress_level) * self.stress_impact
        easy_threshold = self.difficulty_thresholds['easy_to_medium'] - stress_adjustment
        medium_threshold = self.difficulty_thresholds['medium_to_hard'] - stress_adjustment
        
        if current_difficulty == 'easy':
            if accuracy >= easy_threshold and stress_level < 0.6:
                return 'medium'
            else:
                return 'easy'
                
        elif current_difficulty == 'medium':
            if accuracy >= medium_threshold and stress_level < 0.5:
                return 'hard'
            elif accuracy < self.difficulty_thresholds['medium_to_easy'] or stress_level > 0.8:
                return 'easy'
            else:
                return 'medium'
                
        else:  # hard
            if accuracy < self.difficulty_thresholds['hard_to_medium'] or stress_level > 0.7:
                return 'medium'
            else:
                return 'hard'
    
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
