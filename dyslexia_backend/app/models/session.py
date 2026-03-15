from app import db
from datetime import datetime

class LearningSession(db.Model):
    __tablename__ = 'learning_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    average_stress_level = db.Column(db.Float, default=0.0)
    points_earned = db.Column(db.Integer, default=0)
    
    def complete_session(self, correct_answers, total_questions, stress_level, points):
        self.end_time = datetime.utcnow()
        self.correct_answers = correct_answers
        self.total_questions = total_questions
        self.average_stress_level = stress_level
        self.points_earned = points
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'module': self.module,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'accuracy': round((self.correct_answers / self.total_questions * 100), 2) if self.total_questions > 0 else 0,
            'average_stress_level': self.average_stress_level,
            'points_earned': self.points_earned
        }
