from datetime import datetime
import json

class ReportGenerator:
    
    def _normalize_accuracy(self, session_summary):
        """Safely normalize accuracy to percentage (0-100)"""
        acc = session_summary.get('accuracy', 0)
        if acc <= 1:
            acc = acc * 100
        return round(acc, 2)
    
    def _calculate_average_stress(self, session_summary):
        """Calculate average stress from history or use current"""
        stress_list = session_summary.get('stress_history', [])
        if stress_list:
            avg = sum(stress_list) / len(stress_list)
        else:
            avg = session_summary.get('stress_level', 0)
        return round(avg * 100, 1)
    
    def generate_math_report(self, user_id, session_summary):
        """Generate math performance report"""
        accuracy = self._normalize_accuracy(session_summary)
        points = session_summary.get('points_earned', 0)
        average_stress = self._calculate_average_stress(session_summary)
        
        # Determine strengths and weaknesses based on performance
        if accuracy >= 80:
            strength = "Excellent problem-solving skills and quick thinking"
            weakness = "Ready for more complex mathematical challenges"
            recommendation = "Try advanced problems with multiple steps"
        elif accuracy >= 60:
            strength = "Good understanding of basic mathematical concepts"
            weakness = "Needs more practice with medium-difficulty problems"
            recommendation = "Focus on building speed and accuracy"
        else:
            strength = "Good effort and willingness to learn"
            weakness = "Needs more practice with fundamental concepts"
            recommendation = "Practice basic arithmetic regularly"
        
        report = {
            'user_id': user_id,
            'module': 'math',
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_questions': session_summary.get('questions_answered', 0),
            'correct_answers': session_summary.get('correct_answers', 0),
            'accuracy': accuracy,
            'points_earned': points,
            'current_level': session_summary.get('current_difficulty', 'easy'),
            'longest_streak': session_summary.get('current_streak', 0),
            'average_stress': average_stress,
            'strengths': strength,
            'weaknesses': weakness,
            'recommendations': [
                recommendation,
                "Practice daily for 15-20 minutes",
                "Use visual aids for better understanding"
            ]
        }
        
        # FIX 4: Add user details to report
        report['name'] = session_summary.get('name', 'Unknown')
        report['age'] = session_summary.get('age', 'Unknown')
        report['email'] = session_summary.get('email', 'Unknown')
        
        return report
    
    def generate_spelling_report(self, user_id, session_summary):
        """Generate spelling performance report"""
        accuracy = self._normalize_accuracy(session_summary)
        points = session_summary.get('points_earned', 0)
        mode = session_summary.get('mode', 'missing_letters')
        average_stress = self._calculate_average_stress(session_summary)
        
        if accuracy >= 85:
            strength = "Excellent spelling skills and word recognition"
            weakness = "Ready for more complex vocabulary"
            recommendation = "Practice spelling without visual hints"
        elif accuracy >= 65:
            strength = "Good phonetic understanding and memory"
            weakness = "Needs practice with complete word spelling"
            recommendation = "Work on spelling from dictation"
        else:
            strength = "Good effort in attempting challenging words"
            weakness = "Needs focus on basic phonics and patterns"
            recommendation = "Practice common word families daily"
        
        report = {
            'user_id': user_id,
            'module': 'spelling',
            'mode': mode,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_questions': session_summary.get('questions_answered', 0),
            'correct_answers': session_summary.get('correct_answers', 0),
            'accuracy': accuracy,
            'points_earned': points,
            'current_level': session_summary.get('current_difficulty', 'easy'),
            'longest_streak': session_summary.get('current_streak', 0),
            'average_stress': average_stress,
            'strengths': strength,
            'weaknesses': weakness,
            'recommendations': [
                recommendation,
                "Read aloud to improve spelling recognition",
                "Practice with word games and puzzles"
            ]
        }
        
        # FIX 4: Add user details to report
        report['name'] = session_summary.get('name', 'Unknown')
        report['age'] = session_summary.get('age', 'Unknown')
        report['email'] = session_summary.get('email', 'Unknown')
        
        return report
    
    def generate_reading_report(self, user_id, session_summary):
        """Generate reading performance report"""
        accuracy = self._normalize_accuracy(session_summary)
        points = session_summary.get('points_earned', 0)
        mode = session_summary.get('mode', 'words')
        average_stress = self._calculate_average_stress(session_summary)
        
        if accuracy >= 80:
            strength = "Excellent pronunciation and reading fluency"
            weakness = "Ready for more complex reading materials"
            recommendation = "Practice reading with expression and emotion"
        elif accuracy >= 60:
            strength = "Good word recognition and basic fluency"
            weakness = "Needs work on difficult words and pacing"
            recommendation = "Practice reading aloud regularly"
        else:
            strength = "Good effort and willingness to practice"
            weakness = "Needs focus on basic phonics and sounds"
            recommendation = "Practice basic letter sounds daily"
        
        report = {
            'user_id': user_id,
            'module': 'reading',
            'mode': mode,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'total_items': session_summary.get('items_attempted', 0),
            'correct_pronunciations': session_summary.get('correct_pronunciations', 0),
            'accuracy': accuracy,
            'points_earned': points,
            'current_level': session_summary.get('current_difficulty', 'easy'),
            'longest_streak': session_summary.get('current_streak', 0),
            'average_stress': average_stress,
            'strengths': strength,
            'weaknesses': weakness,
            'recommendations': [
                recommendation,
                "Read for 15 minutes every day",
                "Use audiobooks along with text reading"
            ]
        }
        
        # FIX 4: Add user details to report
        report['name'] = session_summary.get('name', 'Unknown')
        report['age'] = session_summary.get('age', 'Unknown')
        report['email'] = session_summary.get('email', 'Unknown')
        
        return report

# Global report generator instance
report_generator = ReportGenerator()
