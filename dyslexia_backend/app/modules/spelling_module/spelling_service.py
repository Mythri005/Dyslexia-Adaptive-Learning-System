from app.data.data_loader import data_loader
from app.modules.common.adaptive_algorithm import AdaptiveAlgorithm
from app.utils.voice_utils import voice_utils
from app.utils.camera_utils import camera_utils
from app.utils.speech_utils import speech_utils
import random
from datetime import datetime
import logging
from app.modules.common.reward_system import reward_system
from app.models.progress import Progress
from app import db

logger = logging.getLogger(__name__)

class SpellingService:
    # Use class-level variable to persist sessions across instances
    _user_sessions = {}
    
    def __init__(self):
        self.adaptive_algo = AdaptiveAlgorithm()
        self.words_data = data_loader.load_spelling_words()
        self.quiz_data = data_loader.load_spelling_quiz()
        
        # Use class-level sessions to persist across requests
        self.user_sessions = SpellingService._user_sessions
        
        logger.info(f"Spelling service initialized with {len(self.words_data)} words and {len(self.quiz_data)} quiz items")
    
    def start_session(self, user_id, mode='missing_letters'):
        """Start a new spelling session with real-time monitoring"""
        logger.info(f"Starting spelling session for user {user_id}, mode: {mode}")
        
        # Select initial questions based on mode
        questions = self._select_initial_questions(mode)
        
        session_data = {
            'mode': mode,
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
            'current_word_attempts': 0,
            'questions': questions,
            'session_started': True,
            'start_time': datetime.now(),
            'stress_history': [],
            'help_count': 0,
            'current_expected_answer': None  # NEW: Track current expected answer
        }
        
        self.user_sessions[user_id] = session_data
        
        # Start real-time monitoring (camera, pulse sensor, mic)
        camera_utils.start_real_time_monitoring(user_id)
        speech_utils.start_voice_monitoring(user_id)
        
        # AI welcome message based on mode
        if mode == 'missing_letters':
            voice_utils.speak("Welcome to Spelling practice! Complete the missing letters in the words.")
        else:
            voice_utils.speak("Welcome to Spelling practice! I'll say a word and you spell it.")
        
        logger.info(f"Spelling session started for user {user_id} with {len(questions)} questions")
        return session_data
    
    def _select_initial_questions(self, mode):
        """Select initial set of 10 questions based on mode"""
        if mode == 'missing_letters':
            data_source = self.quiz_data
        else:
            data_source = self.words_data
        
        if not data_source:
            logger.error(f"❌ Spelling dataset EMPTY for mode: {mode}")
            return [{
                "question": "⚠ No spelling data available. Upload dataset.",
                "answer": "",
                "category": "easy",
                "complete_word": ""
            }]
            
        # Start with easy questions
        easy_questions = [q for q in data_source if q['category'] == 'easy']
        medium_questions = [q for q in data_source if q['category'] == 'medium']
        
        selected = []
        if easy_questions:
            selected.extend(random.sample(easy_questions, min(8, len(easy_questions))))
        if medium_questions:
            selected.extend(random.sample(medium_questions, min(2, len(medium_questions))))
        
        # If not enough questions, use whatever is available
        if len(selected) < 5:
            all_questions = data_source.copy()
            random.shuffle(all_questions)
            selected.extend(all_questions[:5 - len(selected)])
        
        random.shuffle(selected)
        return selected[:5]
    
    def get_next_question(self, user_id, stress_data=None):
        """Get the next spelling question with adaptive difficulty"""
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        # Check if session has questions
        if not session['questions']:
            return {
                "error": True,
                "message": "Spelling dataset is empty. Please upload data."
            }
        
        # Update stress level from camera/pulse monitoring
        if stress_data:
            session['stress_level'] = stress_data.get('stress_level', 0.0)
            session['stress_history'].append(session['stress_level'])
            
            # Check if user needs help due to high stress
            if (session['stress_level'] > 0.7 and 
                not session['needs_help'] and 
                session['help_count'] < 3):
                session['needs_help'] = True
                session['help_count'] += 1
                voice_utils.speak("I can see you're finding this challenging. Let me give you an easier question!")
                
                # Replace current question with easier one
                easier_questions = self._get_easier_questions(session['mode'])
                if easier_questions and session['current_question_index'] < len(session['questions']):
                    session['questions'][session['current_question_index']] = random.choice(easier_questions)
        
        if session['current_question_index'] >= len(session['questions']):
            return {'session_complete': True, 'message': 'Spelling session completed'}
        
        current_question = session['questions'][session['current_question_index']]
        question = current_question.copy()
        
        # FIXED: Properly set expected answer based on mode
        if session['mode'] == 'complete_words':
            # COMPLETE WORDS MODE: AI speaks the word, user spells complete word
            word = question.get('word', '')
            question['ai_instruction'] = f"Please spell the word: {word}"
            question['speak_word'] = word
            question['expected_answer'] = word  # User should enter the complete word
            question['display_text'] = f"Spell the word: {word}"
            question['type'] = 'complete_word'
            
            # Store expected answer in session for comparison
            session['current_expected_answer'] = word
            
            # AI speaks the word
            voice_utils.speak(f"Spell the word: {word}")
            
        else:
            # MISSING LETTERS MODE: Show pattern, user enters missing letter only
            word_pattern = question.get('question', '')
            missing_letter = question.get('answer', '')  # This is the missing letter user should enter
            complete_word = question.get('complete_word', '')
            
            question['ai_instruction'] = f"Complete the word: {word_pattern}. Enter the missing letter."
            question['display_text'] = word_pattern
            question['expected_answer'] = missing_letter  # User should enter the missing letter only
            question['complete_word'] = complete_word  # For reference
            question['word_pattern'] = word_pattern
            question['type'] = 'missing_letter'
            
            # Store expected answer in session for comparison
            session['current_expected_answer'] = missing_letter
            
            # AI speaks the instruction
            voice_utils.speak(f"Complete the word: {word_pattern}. What letter is missing?")
        
        return question
    
    def _get_easier_questions(self, mode):
        """Get easier questions when user is stressed"""
        if mode == 'missing_letters':
            data_source = self.quiz_data
        else:
            data_source = self.words_data
        
        return [q for q in data_source if q['category'] == 'easy']
    
    def _answers_match(self, user_answer, correct_answer):
        """
        FIXED: Robust answer comparison for spelling
        Handles different cases and whitespace
        """
        if user_answer is None:
            return False
            
        user_str = str(user_answer).strip().lower()
        correct_str = str(correct_answer).strip().lower()
        
        print(f"🔍 DEBUG _answers_match: user='{user_str}', correct='{correct_str}'")
        
        # Exact match
        if user_str == correct_str:
            return True
        
        # For single letters, allow case-insensitive comparison
        if len(user_str) == 1 and len(correct_str) == 1:
            return user_str == correct_str
        
        # For complete words, allow minor formatting differences
        return user_str == correct_str
    
    def get_real_time_metrics(self, user_id):
        """Get real-time monitoring metrics from camera"""
        if user_id not in self.user_sessions:
            return None
        
        camera_metrics = camera_utils.get_real_time_metrics(user_id)
        
        return {
            'camera': camera_metrics
        }
    
    def save_progress_to_db(self, user_id):
        """Save session progress to database"""
        session = self.user_sessions.get(user_id)
        
        if not session:
            return
        
        progress = Progress.query.filter_by(
            user_id=user_id,
            module='spelling'
        ).first()
        
        if not progress:
            progress = Progress(
                user_id=user_id,
                module='spelling',
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
        logger.info(f"Saved spelling progress for user {user_id}: {session['correct_answers']}/{session['questions_answered']} correct, {session['points_earned']} points")
    
    def submit_answer(self, user_id, answer, response_time, stress_data=None):
        """Submit an answer with adaptive feedback and stress monitoring"""
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        if session['current_question_index'] >= len(session['questions']):
            return {'error': 'No current question'}
            
        current_question = session['questions'][session['current_question_index']]
        
        # Update stress level
        if stress_data:
            session['stress_level'] = stress_data.get('stress_level', 0.0)
        
        # FIXED: Get expected answer from session storage (more reliable)
        expected_answer = session.get('current_expected_answer', '')
        if not expected_answer:
            # Fallback to question data
            if session['mode'] == 'missing_letters':
                expected_answer = current_question.get('answer', '')
            else:
                expected_answer = current_question.get('word', '')
        
        user_answer = str(answer).strip().lower() if answer is not None else ""
        expected_answer = str(expected_answer).strip().lower()
        
        print(f"🔍 DEBUG SPELLING: mode={session['mode']}, user_answer='{user_answer}', expected_answer='{expected_answer}'")
        
        # FIXED: Use robust answer comparison
        is_correct = self._answers_match(user_answer, expected_answer)
        
        # Get complete word for display
        complete_word = current_question.get('complete_word', '')
        if not complete_word and session['mode'] == 'complete_words':
            complete_word = expected_answer
        
        print(f"🎯 FINAL RESULT: is_correct={is_correct}")
        
        # Update session data
        session['questions_answered'] += 1
        
        if is_correct:
            session['correct_answers'] += 1
            session['current_streak'] += 1
            session['consecutive_wrong'] = 0
            session['current_word_attempts'] = 0
            session['current_question_index'] += 1
            session['current_expected_answer'] = None  # Clear for next question
            
            # Calculate points with bonuses
            points, reward_message = reward_system.calculate_reward(
                session['current_difficulty'],
                True,
                response_time,
                session['stress_level'],
                session['current_streak']
            )
            session['points_earned'] += points
            
            # AI encouragement based on performance
            if session['current_streak'] >= 3:
                encouragement = f"Amazing streak! {session['current_streak']} in a row! 🎉"
            elif session['stress_level'] > 0.7:
                encouragement = "Great job overcoming that challenge! You're doing amazing!"
            else:
                encouragement = voice_utils.get_encouragement()
            
            voice_utils.speak(encouragement)
            
            # Adaptive difficulty adjustment with real-time metrics
            accuracy = session['correct_answers'] / session['questions_answered'] if session['questions_answered'] > 0 else 0
            
            # Get real-time camera metrics
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
                'correct_answer': expected_answer,
                'user_answer': answer,
                'points_earned': points,
                'reward_message': f"{encouragement} You earned {points} points!",
                'ai_feedback': encouragement,
                'total_points': session['points_earned'],
                'current_streak': session['current_streak'],
                'session_complete': session['questions_answered'] >= 5,
                'mode': session['mode'],
                'level_up': level_up,
                'new_difficulty': new_difficulty if level_up else None
            }
            
            if session['mode'] == 'missing_letters' and complete_word:
                feedback['complete_word'] = complete_word
            
        else:
            session['current_streak'] = 0
            session['consecutive_wrong'] += 1
            session['current_word_attempts'] += 1
            
            # Adaptive help based on mode and attempts
            if session['mode'] == 'complete_words':
                if session['current_word_attempts'] < 2:
                    # Stay on same question for another attempt
                    feedback_msg = "Let's try that again. Listen carefully."
                    move_to_next = False
                    
                    # On second attempt, spell the word letter by letter
                    if session['current_word_attempts'] >= 1:
                        word = current_question.get('word', expected_answer)
                        voice_utils.speak_word_with_letters(word)
                        feedback_msg = f"Let me spell it for you. The word is {word}. Now you try!"
                else:
                    # After 2 attempts, move to next
                    session['current_question_index'] += 1
                    session['current_word_attempts'] = 0
                    session['current_expected_answer'] = None
                    feedback_msg = f"Good effort! The correct spelling is {expected_answer}."
                    move_to_next = True
                    
            else:  # missing_letters mode
                if session['current_word_attempts'] < 2:
                    # Stay on same question, provide hint
                    move_to_next = False
                    if session['current_word_attempts'] == 1:
                        # On second attempt, tell them the missing letter
                        voice_utils.speak(f"The missing letter is {expected_answer}. Try again!")
                        feedback_msg = f"The missing letter is {expected_answer}. Please enter it."
                    else:
                        feedback_msg = "That's not quite right. Try again!"
                else:
                    # After 2 attempts, move to next and show correct answer
                    session['current_question_index'] += 1
                    session['current_word_attempts'] = 0
                    session['current_expected_answer'] = None
                    feedback_msg = f"The missing letter was {expected_answer}. The complete word is {complete_word}."
                    move_to_next = True
            
            # If high stress and multiple wrong answers, offer easier question
            if (session['stress_level'] > 0.8 and 
                session['consecutive_wrong'] >= 2 and 
                session['help_count'] < 3):
                feedback_msg = "Let me give you an easier question... don't worry!"
                voice_utils.speak(feedback_msg)
                session['help_count'] += 1
                # Replace next question with easier one
                easier_questions = self._get_easier_questions(session['mode'])
                if easier_questions and session['current_question_index'] < len(session['questions']):
                    session['questions'][session['current_question_index']] = random.choice(easier_questions)
            
            feedback = {
                'is_correct': False,
                'correct_answer': expected_answer,
                'user_answer': answer,
                'points_earned': 0,
                'reward_message': "Good try! Let's practice this word.",
                'ai_feedback': feedback_msg,
                'total_points': session['points_earned'],
                'current_streak': session['current_streak'],
                'session_complete': session['questions_answered'] >= 5,
                'needs_practice': True,
                'move_to_next': move_to_next,
                'mode': session['mode'],
                'attempts_remaining': 2 - session['current_word_attempts'] if not move_to_next else 0,
                'stress_level': session['stress_level']
            }
            
            if session['mode'] == 'missing_letters' and complete_word:
                feedback['complete_word'] = complete_word
        
        # Check if session is complete (10 questions)
        if session['questions_answered'] >= 5:
            from app.utils.report_generator import report_generator
            report = report_generator.generate_spelling_report(user_id, session)
            feedback['session_complete'] = True
            feedback['report'] = report
            feedback['continue_available'] = True
            
            # Save progress to database
            self.save_progress_to_db(user_id)
            
            # Stop monitoring
            camera_utils.stop_real_time_monitoring(user_id)
            speech_utils.stop_voice_monitoring(user_id)
            
            # Final encouragement based on performance
            if session['correct_answers'] >= 3:
                final_msg = f"Outstanding work! You got {session['correct_answers']} out of 5 correct and earned {session['points_earned']} points!"
            else:
                final_msg = f"Great job completing the session! You earned {session['points_earned']} points!"
            voice_utils.speak(final_msg)
        
        return feedback
    
    def continue_session(self, user_id):
        """Continue with next set of 10 questions"""
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        # Calculate accuracy for difficulty adjustment
        accuracy = session['correct_answers'] / session['questions_answered'] if session['questions_answered'] > 0 else 0
        
        # Get real-time camera metrics
        metrics = self.get_real_time_metrics(user_id)
        
        attention = 0.5
        pulse = 75
        
        if metrics and metrics.get('camera'):
            attention = metrics['camera'].get('current_attention', 0.5)
            pulse = metrics['camera'].get('current_pulse', 75)
        
        # Adjust difficulty based on performance and metrics
        new_difficulty = self.adaptive_algo.adjust_difficulty(
            session['current_difficulty'],
            accuracy,
            session['stress_level'],
            attention,
            pulse
        )
        
        session['current_difficulty'] = new_difficulty
        
        # Select new questions based on current difficulty
        session['questions'] = self._select_questions_based_on_difficulty(session['current_difficulty'], session['mode'])
        session['current_question_index'] = 0
        session['questions_answered'] = 0
        session['correct_answers'] = 0
        session['help_provided'] = False
        session['current_word_attempts'] = 0
        session['stress_history'] = []
        session['current_expected_answer'] = None
        
        voice_utils.speak(f"Great! Let's continue with more {session['current_difficulty']} spelling practice!")
        
        return {'message': 'Session continued', 'new_difficulty': session['current_difficulty']}
    
    def _select_questions_based_on_difficulty(self, difficulty, mode):
        """Select questions based on current difficulty level"""
        if mode == 'missing_letters':
            data_source = self.quiz_data
        else:
            data_source = self.words_data
        
        if not data_source:
            return []
            
        if difficulty == 'easy':
            distribution = [8, 2, 0]  # 8 easy, 2 medium, 0 hard
        elif difficulty == 'medium':
            distribution = [5, 4, 1]  # 5 easy, 4 medium, 1 hard
        else:  # hard
            distribution = [3, 4, 3]  # 3 easy, 4 medium, 3 hard
        
        easy_q = [q for q in data_source if q['category'] == 'easy']
        medium_q = [q for q in data_source if q['category'] == 'medium']
        hard_q = [q for q in data_source if q['category'] == 'difficult']
        
        selected = []
        if easy_q:
            selected.extend(random.sample(easy_q, min(distribution[0], len(easy_q))))
        if medium_q:
            selected.extend(random.sample(medium_q, min(distribution[1], len(medium_q))))
        if hard_q:
            selected.extend(random.sample(hard_q, min(distribution[2], len(hard_q))))
        
        # If not enough questions, fill with available ones
        if len(selected) < 5:
            all_questions = data_source.copy()
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
            'mode': session['mode'],
            'questions_answered': session['questions_answered'],
            'correct_answers': session['correct_answers'],
            'accuracy': accuracy,
            'points_earned': session['points_earned'],
            'current_difficulty': session['current_difficulty'],
            'questions_remaining': len(session['questions']) - session['current_question_index'],
            'current_streak': session['current_streak'],
            'stress_level': session['stress_level'],
            'help_count': session['help_count']
        }

# Singleton instance to ensure sessions persist
_spelling_service_instance = None

def get_spelling_service():
    global _spelling_service_instance
    if _spelling_service_instance is None:
        _spelling_service_instance = SpellingService()
    return _spelling_service_instance

# Global spelling service instance
spelling_service = get_spelling_service()