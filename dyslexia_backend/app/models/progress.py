from app import db
from datetime import datetime

class Progress(db.Model):
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    module = db.Column(db.String(50), nullable=False)  # 'math', 'spelling', 'reading'
    current_level = db.Column(db.String(20), default='easy')  # 'easy', 'medium', 'hard'
    total_points = db.Column(db.Integer, default=0)
    questions_attempted = db.Column(db.Integer, default=0)
    questions_correct = db.Column(db.Integer, default=0)
    strength = db.Column(db.Text)  # JSON string of strengths
    weakness = db.Column(db.Text)  # JSON string of weaknesses
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'module': self.module,
            'current_level': self.current_level,
            'total_points': self.total_points,
            'questions_attempted': self.questions_attempted,
            'questions_correct': self.questions_correct,
            'accuracy': round((self.questions_correct / self.questions_attempted * 100), 2) if self.questions_attempted > 0 else 0,
            'strength': self.strength,
            'weakness': self.weakness
        }
