from app.data.data_loader import data_loader
from app.modules.common.adaptive_algorithm import AdaptiveAlgorithm
from app.utils.voice_utils import voice_utils
from app.utils.camera_utils import camera_utils
from app.utils.speech_utils import speech_utils
import random
import time
from datetime import datetime
import logging
from app.modules.common.reward_system import reward_system
from app.models.progress import Progress
from app import db

logger = logging.getLogger(__name__)

class MathService:
    def __init__(self):
        self.adaptive_algo = AdaptiveAlgorithm()
        self.math_data = data_loader.load_math_data()
        self.user_sessions = {}
        logger.info(f"Math service initialized with {len(self.math_data)} questions")
    
    def start_session(self, user_id):
        """Start a new math learning session with real-time monitoring"""
        logger.info(f"Starting math session for user {user_id}")
        
        session_data = {
            'current_question_index': 0,
            'questions_answered': 0,
            'correct_answers': 0,
            'current_difficulty': 'easy',
            'stress_level': 0.0,
            'points_earned': 0,
            'current_streak': 0,
            'consecutive_wrong': 0,
            'needs_help': False,
            'help_provided': False,
            'questions': self._select_initial_questions(),
            'session_started': True,
            'start_time': datetime.now(),
            'real_time_data': {
                'camera_updates': 0,
                'voice_updates': 0,
                'last_stress_level': 0.0,
                'last_attention_score': 0.5
            },
            'time_on_question': 0,
            'question_start_time': datetime.now()
        }
        
        self.user_sessions[user_id] = session_data
        
        # Start real-time monitoring
        camera_utils.start_real_time_monitoring(user_id)
        
        # AI welcome message
        voice_utils.speak("Welcome to Math practice! Let's start with some fun questions.")
        
        logger.info(f"Math session started for user {user_id}")
        return session_data
    
    def _select_initial_questions(self):
        """Select initial set of 10 questions based on easy difficulty"""
        if not self.math_data:
            logger.error("❌ Math dataset is EMPTY")
            return [{
                "question": "⚠ No math questions available. Please upload dataset.",
                "answer": "",
                "category": "easy",
                "explanation": "Dataset missing"
            }]
            
        easy_questions = [q for q in self.math_data if q['category'] == 'easy']
        medium_questions = [q for q in self.math_data if q['category'] == 'medium']
        
        # Start with mostly easy questions
        selected = []
        if easy_questions:
            selected.extend(random.sample(easy_questions, min(8, len(easy_questions))))
        if medium_questions:
            selected.extend(random.sample(medium_questions, min(2, len(medium_questions))))
        
        # If not enough questions, use whatever is available
        if len(selected) < 5:
            all_questions = self.math_data.copy()
            random.shuffle(all_questions)
            selected.extend(all_questions[:5 - len(selected)])
        
        random.shuffle(selected)
        return selected[:5]
    
    def update_real_time_metrics(self, user_id, camera_data=None, voice_data=None):
        """Update real-time monitoring metrics"""
        if user_id not in self.user_sessions:
            return
        
        session = self.user_sessions[user_id]
        
        if camera_data:
            # Update camera metrics
            session['stress_level'] = camera_data.get('stress_level', session['stress_level'])
            session['real_time_data']['last_stress_level'] = camera_data.get('stress_level', 0.0)
            session['real_time_data']['last_attention_score'] = camera_data.get('attention_score', 0.5)
            session['real_time_data']['camera_updates'] += 1
            
            # Check if user needs help based on stress
            if camera_data.get('needs_help', False) and not session['help_provided']:
                session['needs_help'] = True
                help_message = camera_data.get('help_message', "Let me help you with this question.")
                voice_utils.speak(help_message)
                session['help_provided'] = True
    
    def get_next_question(self, user_id, stress_data=None):
        """Get the next math question with stress adaptation"""
        if user_id not in self.user_sessions:
            self.start_session(user_id)
        
        session = self.user_sessions[user_id]
        
        # Check if session has questions
        if not session['questions']:
            return {
                "error": True,
                "message": "Math dataset is empty. Please upload questions."
            }
        
        # Update stress level from camera data
        if stress_data:
            session['stress_level'] = stress_data.get('stress_level', 0.0)
            session['needs_help'] = stress_data.get('needs_help', False)
            
            # If high stress and needs help, provide easier question
            if session['needs_help'] and not session['help_provided']:
                help_message = stress_data.get('help_message', "Let me help you with this question.")
                voice_utils.speak(help_message)
                session['help_provided'] = True
                
                # Replace current question with easier one
                easier_questions = [q for q in self.math_data if q['category'] == 'easy']
                if easier_questions and session['current_question_index'] < len(session['questions']):
                    session['questions'][session['current_question_index']] = random.choice(easier_questions)
                    voice_utils.speak("I've selected an easier question for you. Don't worry!")
        
        # Check if user is stuck on same question for too long
        current_time = datetime.now()
        time_on_question = (current_time - session.get('question_start_time', current_time)).seconds
        session['time_on_question'] = time_on_question
        
        if time_on_question > 60:  # 60 seconds on same question
            voice_utils.speak("Let me give you a hint for this question.")
            if session['current_question_index'] < len(session['questions']):
                current_question = session['questions'][session['current_question_index']]
                hint = f"Try thinking about {current_question.get('explanation', 'this step by step')}"
                voice_utils.speak(hint)
        
        # Check if we've answered all questions in the pool
        if session['current_question_index'] >= len(session['questions']):
            # Automatically get more questions if needed
            logger.info(f"User {user_id} has answered all {len(session['questions'])} questions. Getting more...")
            additional = self._select_next_questions(session['current_difficulty'], count=5)
            session['questions'].extend(additional)
            logger.info(f"Added {len(additional)} questions. New total: {len(session['questions'])}")
        
        question = session['questions'][session['current_question_index']].copy()
        
        # Reset question start time
        session['question_start_time'] = datetime.now()
        
        # Add metadata about progress
        question['progress'] = {
            'answered': session['questions_answered'],
            'total_in_pool': len(session['questions']),
            'remaining': len(session['questions']) - session['current_question_index']
        }
        
        # Add AI instruction for the question
        question['ai_instruction'] = f"Solve this math problem: {question['question']}"
        
        return question

    def _answers_match(self, user_answer, correct_answer):
        """
        FLEXIBLE ANSWER COMPARISON - FIXED VERSION
        Handles different number formats like "19" == "19.0", "5" == "5.0", etc.
        """
        user_str = str(user_answer).strip().lower()
        correct_str = str(correct_answer).strip().lower()
        
        print(f"🔍 DEBUG _answers_match: user='{user_str}', correct='{correct_str}'")
        
        # If they're exactly the same, return True immediately
        if user_str == correct_str:
            print(f"✅ Exact match: '{user_str}' == '{correct_str}'")
            return True
        
        # Try numeric comparison for numbers
        try:
            user_num = float(user_str)
            correct_num = float(correct_str)
            
            print(f"🔍 Numeric comparison: {user_num} vs {correct_num}")
            
            # Allow small floating point tolerance and different formats
            tolerance = 1e-10
            is_match = abs(user_num - correct_num) < tolerance
            print(f"✅ Numeric match: {is_match} (diff: {abs(user_num - correct_num)})")
            return is_match
            
        except (ValueError, TypeError) as e:
            print(f"🔍 Not numbers, doing string comparison: {e}")
            # If not numbers, do case-insensitive string comparison
            return user_str == correct_str
    
    def save_progress_to_db(self, user_id):
        """Save session progress to database"""
        session = self.user_sessions.get(user_id)
        
        if not session:
            return
        
        progress = Progress.query.filter_by(
            user_id=user_id,
            module='math'
        ).first()
        
        if not progress:
            progress = Progress(
                user_id=user_id,
                module='math',
                total_points=session['points_earned'],
                questions_attempted=session['questions_answered'],
                questions_correct=session['correct_answers'],
                current_level=session['current_difficulty']
            )
            db.session.add(progress)
        
        else:
            progress.total_points += session['points_earned']
            progress.questions_attempted += session['questions_answered']
            progress.questions_correct += session['correct_answers']
            progress.current_level = session['current_difficulty']
        
        db.session.commit()
        logger.info(f"Saved math progress for user {user_id}: {session['correct_answers']}/{session['questions_answered']} correct, {session['points_earned']} points")
    
    def submit_answer(self, user_id, answer, response_time, stress_data=None):
        """Submit an answer and get adaptive feedback"""
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        if session['current_question_index'] >= len(session['questions']):
            return {'error': 'No current question'}
            
        current_question = session['questions'][session['current_question_index']]
        
        print(f"🎯 SUBMIT_ANSWER: user_answer='{answer}', correct_answer='{current_question['answer']}'")
        
        # FIXED: Use the flexible answer comparison
        is_correct = self._answers_match(answer, current_question['answer'])
        
        print(f"🎯 FINAL RESULT: is_correct={is_correct}")
        
        # Update session data
        session['questions_answered'] += 1
        session['current_question_index'] += 1
        
        # Update stress level from camera data
        if stress_data:
            session['stress_level'] = stress_data.get('stress_level', session['stress_level'])
        
        if is_correct:
            session['correct_answers'] += 1
            session['current_streak'] += 1
            session['consecutive_wrong'] = 0
            
            # Calculate points with bonus for streaks
            points, reward_message = reward_system.calculate_reward(
                session['current_difficulty'],
                True,
                response_time,
                session['stress_level'],
                session['current_streak']
            )
            session['points_earned'] += points
            
            # AI encouragement based on stress level
            if session['stress_level'] > 0.7:
                encouragement = "Great job overcoming that challenge! You're doing amazing!"
            else:
                encouragement = voice_utils.get_encouragement()
            voice_utils.speak(encouragement)
            
            # ===== REAL-TIME DIFFICULTY UPDATE =====
            accuracy = session['correct_answers'] / session['questions_answered'] if session['questions_answered'] > 0 else 0
            
            metrics = self.get_real_time_metrics(user_id)
            
            attention = 0.5
            pulse = 75
            
            if metrics and metrics.get('camera'):
                attention = metrics['camera'].get('current_attention', 0.5)
                pulse = metrics['camera'].get('current_pulse', 75)
            
            new_difficulty = self.adaptive_algo.adjust_difficulty(
                session['current_difficulty'],
                accuracy,
                session['stress_level'],
                attention,
                pulse
            )
            
            level_up = False
            if new_difficulty != session['current_difficulty']:
                session['current_difficulty'] = new_difficulty
                level_up = True
                level_message = f"🎉 Level Up! You've progressed to {new_difficulty} level!"
                voice_utils.speak(level_message)
            
            feedback = {
                'is_correct': True,
                'correct_answer': current_question['answer'],
                'explanation': current_question.get('explanation', ''),
                'points_earned': points,
                'reward_message': f"{encouragement} You earned {points} points!",
                'ai_feedback': encouragement,
                'total_points': session['points_earned'],
                'current_streak': session['current_streak'],
                'session_complete': session['questions_answered'] >= 5,
                'real_time_metrics': self.get_real_time_metrics(user_id),
                'level_up': level_up,
                'new_difficulty': new_difficulty if level_up else None
            }
            
        else:
            session['current_streak'] = 0
            session['consecutive_wrong'] += 1
            
            # ENHANCED: Better AI help based on stress and consecutive errors
            if session['stress_level'] > 0.8 or session['consecutive_wrong'] >= 2:
                help_msg = "I can see this is challenging. Let me give you an easier question next time!"
                voice_utils.speak(help_msg)
                feedback_msg = f"{help_msg} The correct answer is {current_question['answer']}."
            elif session['consecutive_wrong'] >= 2:
                help_msg = voice_utils.get_help_message('math', current_question['category'])
                voice_utils.speak(help_msg)
                feedback_msg = f"{help_msg} The correct answer is {current_question['answer']}."
            else:
                feedback_msg = f"Good try! The correct answer is {current_question['answer']}."
            
            # ===== REAL-TIME DIFFICULTY UPDATE (for wrong answers too) =====
            accuracy = session['correct_answers'] / session['questions_answered'] if session['questions_answered'] > 0 else 0
            
            metrics = self.get_real_time_metrics(user_id)
            
            attention = 0.5
            pulse = 75
            
            if metrics and metrics.get('camera'):
                attention = metrics['camera'].get('current_attention', 0.5)
                pulse = metrics['camera'].get('current_pulse', 75)
            
            new_difficulty = self.adaptive_algo.adjust_difficulty(
                session['current_difficulty'],
                accuracy,
                session['stress_level'],
                attention,
                pulse
            )
            
            level_down = False
            if new_difficulty != session['current_difficulty']:
                session['current_difficulty'] = new_difficulty
                level_down = True
                level_message = f"Let's try some easier questions to build confidence."
                voice_utils.speak(level_message)
            
            feedback = {
                'is_correct': False,
                'correct_answer': current_question['answer'],
                'explanation': current_question.get('explanation', ''),
                'points_earned': 0,
                'reward_message': "Good effort! Keep trying!",
                'ai_feedback': feedback_msg,
                'total_points': session['points_earned'],
                'current_streak': session['current_streak'],
                'session_complete': session['questions_answered'] >= 5,
                'real_time_metrics': self.get_real_time_metrics(user_id),
                'level_down': level_down,
                'new_difficulty': new_difficulty if level_down else None
            }
        
        # Check if session is complete (10 questions)
        if session['questions_answered'] >= 5:
            from app.utils.report_generator import report_generator
            report = report_generator.generate_math_report(user_id, session)
            feedback['session_complete'] = True
            feedback['report'] = report
            feedback['continue_available'] = True
            
            # Stop monitoring
            camera_utils.stop_real_time_monitoring(user_id)
            
            # AI session completion message based on performance
            if session['correct_answers'] >= 8:
                completion_msg = f"Outstanding work! You earned {session['points_earned']} points with {session['correct_answers']} correct answers!"
            else:
                completion_msg = f"Great job completing the math session! You earned {session['points_earned']} points!"
            voice_utils.speak(completion_msg)
        
        return feedback
    
    def get_real_time_metrics(self, user_id):
        """Get real-time monitoring metrics"""
        if user_id not in self.user_sessions:
            return None
        
        camera_metrics = camera_utils.get_real_time_metrics(user_id)
        
        return {
            'camera': camera_metrics,
            'session': self.user_sessions[user_id]['real_time_data']
        }
    
    def continue_session(self, user_id):
        """Continue with next set of 5 questions - KEEP existing question pool"""
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        # DON'T select new questions from scratch - EXTEND the existing pool
        # Calculate performance so far
        accuracy = session['correct_answers'] / session['questions_answered'] if session['questions_answered'] > 0 else 0
        
        # Get real-time camera metrics
        metrics = self.get_real_time_metrics(user_id)
        
        attention = 0.5
        pulse = 75
        
        if metrics and metrics.get('camera'):
            attention = metrics['camera'].get('current_attention', 0.5)
            pulse = metrics['camera'].get('current_pulse', 75)
        
        # Pass all 4 parameters
        new_difficulty = self.adaptive_algo.adjust_difficulty(
            session['current_difficulty'],
            accuracy,
            session['stress_level'],
            attention,
            pulse
        )
        session['current_difficulty'] = new_difficulty
        
        # Get MORE questions (next 5) based on current difficulty
        additional_questions = self._select_next_questions(new_difficulty, count=5)
        
        # APPEND to existing questions, don't replace
        session['questions'].extend(additional_questions)
        
        # Reset round-specific counters but KEEP cumulative totals
        # session['questions_answered'] - DON'T reset this (keep cumulative)
        # session['correct_answers'] - DON'T reset this (keep cumulative)
        session['help_provided'] = False
        session['time_on_question'] = 0
        session['question_start_time'] = datetime.now()
        
        logger.info(f"Added {len(additional_questions)} new questions for user {user_id}. Total pool: {len(session['questions'])}")
        
        # AI continue message
        if new_difficulty == 'easy':
            voice_utils.speak("Great! Let's continue with some easier questions to build confidence!")
        elif new_difficulty == 'medium':
            voice_utils.speak("Excellent! Let's try some medium level questions now!")
        else:
            voice_utils.speak("Fantastic! You're ready for some challenging questions!")
        
        return {
            'message': 'Session continued', 
            'new_difficulty': new_difficulty,
            'total_questions': len(session['questions']),
            'questions_answered': session['questions_answered']
        }
    
    def _select_next_questions(self, difficulty, count=5):
        """Select next set of questions based on current difficulty"""
        if not self.math_data:
            return []
            
        if difficulty == 'easy':
            distribution = [4, 1, 0]  # 4 easy, 1 medium, 0 hard
        elif difficulty == 'medium':
            distribution = [2, 2, 1]  # 2 easy, 2 medium, 1 hard
        else:  # hard
            distribution = [1, 2, 2]  # 1 easy, 2 medium, 2 hard
        
        easy_q = [q for q in self.math_data if q['category'] == 'easy']
        medium_q = [q for q in self.math_data if q['category'] == 'medium']
        hard_q = [q for q in self.math_data if q['category'] == 'difficult']
        
        selected = []
        
        # Select based on distribution
        if easy_q:
            sample_size = min(distribution[0], len(easy_q))
            if sample_size > 0:
                selected.extend(random.sample(easy_q, sample_size))
        
        if medium_q:
            sample_size = min(distribution[1], len(medium_q))
            if sample_size > 0:
                selected.extend(random.sample(medium_q, sample_size))
        
        if hard_q:
            sample_size = min(distribution[2], len(hard_q))
            if sample_size > 0:
                selected.extend(random.sample(hard_q, sample_size))
        
        # If we don't have enough questions, fill with easy ones
        if len(selected) < count:
            if easy_q:
                additional = random.sample(easy_q, min(count - len(selected), len(easy_q)))
                selected.extend(additional)
        
        random.shuffle(selected)
        return selected[:count]
    
    def _select_questions_based_on_difficulty(self, difficulty):
        """Select questions based on current difficulty level"""
        if not self.math_data:
            return []
            
        if difficulty == 'easy':
            distribution = [8, 2, 0]  # 8 easy, 2 medium, 0 hard
        elif difficulty == 'medium':
            distribution = [5, 4, 1]  # 5 easy, 4 medium, 1 hard
        else:  # hard
            distribution = [3, 4, 3]  # 3 easy, 4 medium, 3 hard
        
        easy_q = [q for q in self.math_data if q['category'] == 'easy']
        medium_q = [q for q in self.math_data if q['category'] == 'medium']
        hard_q = [q for q in self.math_data if q['category'] == 'difficult']
        
        selected = []
        if easy_q:
            selected.extend(random.sample(easy_q, min(distribution[0], len(easy_q))))
        if medium_q:
            selected.extend(random.sample(medium_q, min(distribution[1], len(medium_q))))
        if hard_q:
            selected.extend(random.sample(hard_q, min(distribution[2], len(hard_q))))
        
        # If not enough questions, fill with available ones
        if len(selected) < 5:
            all_questions = self.math_data.copy()
            random.shuffle(all_questions)
            selected.extend(all_questions[:5 - len(selected)])
        
        random.shuffle(selected)
        return selected[:5]
    
    def get_session_summary(self, user_id):
        """Get summary of current session"""
        if user_id not in self.user_sessions:
            return None
        
        session = self.user_sessions[user_id]
        accuracy = round((session['correct_answers'] / session['questions_answered'] * 100), 2) if session['questions_answered'] > 0 else 0
        
        return {
            'questions_answered': session['questions_answered'],
            'correct_answers': session['correct_answers'],
            'accuracy': accuracy,
            'points_earned': session['points_earned'],
            'current_difficulty': session['current_difficulty'],
            'questions_remaining': len(session['questions']) - session['current_question_index'],
            'current_streak': session['current_streak'],
            'stress_level': session['stress_level'],
            'real_time_metrics': self.get_real_time_metrics(user_id)
        }

# Global math service instance
math_service = MathService()