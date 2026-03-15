class RewardSystem:
    def __init__(self):
        self.base_points = {
            'easy': 10,
            'medium': 20,
            'hard': 30
        }
        
        self.bonus_multipliers = {
            'quick_correct': 1.5,    # Answer correctly in less than 10 seconds
            'streak_bonus': 2.0,     # Multiple correct answers in a row
            'stress_manage': 1.2     # Good performance under stress
        }
    
    def calculate_reward(self, difficulty, is_correct, response_time, stress_level, streak_count=0):
        """Calculate points reward for an answer"""
        if not is_correct:
            return 0, "Good try! Keep practicing!"
        
        base_points = self.base_points[difficulty]
        total_points = base_points
        
        # Bonus for quick correct answers
        if response_time < 10:  # Less than 10 seconds
            total_points = int(base_points * self.bonus_multipliers['quick_correct'])
            message = f"Amazing! {total_points} points for quick thinking!"
        
        # Bonus for streaks
        elif streak_count >= 3:
            total_points = int(base_points * self.bonus_multipliers['streak_bonus'])
            message = f"Fantastic streak! {total_points} points!"
        
        # Bonus for managing stress
        elif stress_level < 0.4:
            total_points = int(base_points * self.bonus_multipliers['stress_manage'])
            message = f"Great focus! {total_points} points!"
        
        else:
            message = f"Excellent! {total_points} points!"
        
        return total_points, message
    
    def get_level_up_message(self, old_level, new_level):
        """Get message for level progression"""
        level_names = {
            'easy': 'Beginner',
            'medium': 'Intermediate', 
            'hard': 'Advanced'
        }
        
        return f"🎉 Level Up! You've progressed from {level_names[old_level]} to {level_names[new_level]}!"

# Global reward system instance
reward_system = RewardSystem()
