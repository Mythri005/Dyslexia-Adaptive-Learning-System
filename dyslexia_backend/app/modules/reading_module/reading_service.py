from app.data.data_loader import data_loader
from app.modules.common.adaptive_algorithm import AdaptiveAlgorithm
from app.utils.voice_utils import voice_utils
from app.utils.speech_utils import speech_utils
from app.utils.camera_utils import camera_utils
from app.models.progress import Progress
from app import db
import random
from datetime import datetime
import logging
import difflib
from app.modules.common.reward_system import reward_system

logger = logging.getLogger(__name__)

class ReadingService:
    def __init__(self):
        self.adaptive_algo = AdaptiveAlgorithm()
        self.words_data = data_loader.load_spelling_words()
        self.sentences_data = data_loader.load_reading_sentences()
        self.paragraphs_data = data_loader.load_reading_paragraphs()
        self.user_sessions = {}
        logger.info(f"Reading service initialized with {len(self.words_data)} words, {len(self.sentences_data)} sentences, {len(self.paragraphs_data)} paragraphs")
    
    def _parse_user_id(self, user_id):
        """Helper method to parse user_id from various formats"""
        # Handle frontend string IDs like user_12345
        if isinstance(user_id, str) and user_id.startswith("user_"):
            return int(user_id.split("_")[1])
        else:
            return int(user_id)
    
    def start_session(self, user_id, mode='words'):
        """Start a new reading session"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)
        
        # RESET previous session completely
        self.user_sessions[user_id] = {}
        
        # Normalize mode name
        if mode == "paragraph":
            mode = "paragraphs"
        
        logger.info(f"Starting reading session for user {user_id}, mode: {mode}")
        
        session_data = {
            'mode': mode,
            'current_item_index': 0,
            'items_attempted': 0,
            'correct_pronunciations': 0,
            'session_items_attempted': 0,
            'session_correct': 0,
            'current_difficulty': 'easy',
            'stress_level': 0.0,
            'points_earned': 0,
            'current_streak': 0,
            'consecutive_errors': 0,
            'needs_help': False,
            'help_provided': False,
            'current_word_index': 0,
            'current_sentence_index': 0,
            'word_attempts': 0,
            'current_expected_text': '',
            'items': self._select_initial_items(mode),
            'session_started': True,
            'start_time': datetime.now()
        }
        
        self.user_sessions[user_id] = session_data
        
        # Start real-time monitoring
        camera_utils.start_real_time_monitoring(user_id)
        speech_utils.start_voice_monitoring(user_id)
        
        # AI welcome message based on mode
        if mode == 'words':
            voice_utils.speak("Welcome to Reading practice! I'll say a word and you repeat it after me.")
        elif mode == 'sentences':
            voice_utils.speak("Welcome to Reading practice! We'll practice reading sentences together.")
        else:  # paragraphs
            voice_utils.speak("Welcome to Reading practice! Let's practice reading paragraphs.")
        
        logger.info(f"Reading session started for user {user_id}")
        return session_data
    
    def _select_initial_items(self, mode):
        """Select initial set of 10 items"""
        if mode == 'words':
            data_source = self.words_data
        elif mode == 'sentences':
            data_source = self.sentences_data
        else:  # paragraphs
            data_source = self.paragraphs_data
        
        if not data_source:
            logger.error(f"❌ Reading dataset EMPTY for mode: {mode}")
            return [{
                "display_text": "⚠ No reading data available. Upload dataset.",
                "expected_pronunciation": "",
                "category": "easy"
            }]
            
        easy_items = [q for q in data_source if q['category'] == 'easy']
        medium_items = [q for q in data_source if q['category'] == 'medium']
        
        selected = []
        if easy_items:
            selected.extend(random.sample(easy_items, min(8, len(easy_items))))
        if medium_items:
            selected.extend(random.sample(medium_items, min(2, len(medium_items))))
        
        # If not enough items, use whatever is available
        if len(selected) < 5:
            all_items = data_source.copy()
            random.shuffle(all_items)
            selected.extend(all_items[:5 - len(selected)])
        
        random.shuffle(selected)
        return selected[:5]
    
    def get_next_item(self, user_id, stress_data=None):
        """Get the next reading item with AI voice instructions"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)
        
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        # Check if session has items
        if not session['items']:
            return {
                "error": True,
                "message": "Reading dataset is empty. Please upload data."
            }
        
        # Update stress level if provided
        if stress_data:
            session['stress_level'] = stress_data.get('stress_level', 0.0)
            session['needs_help'] = stress_data.get('needs_help', False)
            
            if session['needs_help'] and not session['help_provided']:
                voice_utils.speak(stress_data.get('help_message', "Let me help you with this reading."))
                session['help_provided'] = True
        
        if session['current_item_index'] >= len(session['items']):
            return {'session_complete': True, 'message': 'Reading session completed'}
        
        current_item = session['items'][session['current_item_index']].copy()
        
        # Format response based on mode with AI instructions
        if session['mode'] == 'words':
            # ✅ CORRECT WORD MODE CODE - Get word directly, not from sentence splitting
            word = str(current_item.get('word') or current_item.get('display_text') or '').strip()

            current_item['type'] = 'word'
            current_item['display_text'] = word
            current_item['full_text'] = word
            current_item['expected_pronunciation'] = word.lower()
            current_item['ai_instruction'] = f"Please repeat the word: {word}"
            current_item['speak_text'] = word

            session['current_expected_text'] = word.lower()

            voice_utils.speak(f"Repeat after me: {word}")
            
        elif session['mode'] == 'sentences':
            sentence = str(current_item.get('sentence', '')).strip()

            current_item['type'] = 'sentence'
            current_item['display_text'] = sentence
            current_item['full_text'] = sentence
            current_item['expected_pronunciation'] = sentence.lower()
            current_item['ai_instruction'] = f"Please repeat the sentence: {sentence}"
            current_item['speak_text'] = sentence

            session['current_expected_text'] = sentence.lower()

            # AI speaks full sentence
            voice_utils.speak(f"Repeat after me: {sentence}")
                
        else:  # paragraphs mode
            paragraph = str(current_item.get('paragraph', '')).strip()

            current_item['type'] = 'paragraph'
            current_item['display_text'] = paragraph
            current_item['full_text'] = paragraph
            current_item['expected_pronunciation'] = paragraph.lower()
            current_item['ai_instruction'] = "Please read the full paragraph aloud."
            current_item['speak_text'] = paragraph

            session['current_expected_text'] = paragraph.lower()

            # AI speaks full paragraph
            voice_utils.speak("Listen carefully, then repeat the paragraph.")
            voice_utils.speak(paragraph)
        
        return current_item
    
    def _highlight_current_word(self, text, word_index):
        """Highlight the current word in the text"""
        words = text.split()
        if word_index < len(words):
            highlighted_words = []
            for i, word in enumerate(words):
                if i == word_index:
                    highlighted_words.append(f"**{word}**")
                else:
                    highlighted_words.append(word)
            return ' '.join(highlighted_words)
        return text
    
    def evaluate_pronunciation(self, user_id, audio_data, transcribed_text=""):
        """Evaluate user's pronunciation with adaptive feedback"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)
        
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        if session['current_item_index'] >= len(session['items']):
            return {'error': 'No current item'}
            
        current_item = session['items'][session['current_item_index']]
        
        # Get expected pronunciation from session (stored in get_next_item)
        expected_text = session.get('current_expected_text', '')
        
        # Fallback to item data if session doesn't have it
        if not expected_text:
            expected_text = current_item.get('expected_pronunciation', '')
        
        # Use frontend text if provided, otherwise use speech recognition
        if transcribed_text:
            # 💛 CHILD-FRIENDLY RELAXED EVALUATION
            spoken_clean = transcribed_text.lower().strip()
            expected_clean = expected_text.lower().strip()

            accuracy = self._calculate_text_similarity(spoken_clean, expected_clean)

            spoken_words = spoken_clean.split()
            expected_words = expected_clean.split()

            word_match_count = sum(
                1 for s, e in zip(spoken_words, expected_words) if s == e
            )

            word_accuracy = word_match_count / max(len(expected_words), 1)

            pronunciation_score = (accuracy + word_accuracy) / 2

            # 💛 Child-friendly relaxed thresholds
            if pronunciation_score >= 0.75:
                is_correct = True
            elif pronunciation_score >= 0.65 and len(spoken_words) == len(expected_words):
                # Accept small pronunciation variations
                is_correct = True
            else:
                is_correct = False
            
            result = {
                'success': True,
                'pronunciation_score': pronunciation_score,
                'accuracy': pronunciation_score,
                'spoken_text': transcribed_text,
                'expected_text': expected_text,
                'is_correct': is_correct,
                'feedback': self._generate_text_feedback(pronunciation_score, transcribed_text, expected_text)
            }
        else:
            # Fall back to audio analysis
            result = speech_utils.analyze_pronunciation(audio_data, expected_text)
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', 'Pronunciation analysis failed'),
                'needs_help': True
            }
        
        is_correct = result.get('is_correct', False)
        pronunciation_score = result.get('pronunciation_score', 0)
        
        # DO NOT increment items_attempted here - wait for item completion
        
        if is_correct:
            # FIX 1: Reorder counters - session counters first for report
            session['session_correct'] += 1
            session['session_items_attempted'] += 1
            
            # cumulative counters (for total progress)
            session['correct_pronunciations'] += 1
            session['items_attempted'] += 1
            
            session['current_streak'] += 1
            session['consecutive_errors'] = 0
            session['word_attempts'] = 0
            
            # Calculate points
            response_time = 10
            points, reward_message = reward_system.calculate_reward(
                session['current_difficulty'],
                True,
                response_time,
                session['stress_level'],
                session['current_streak']
            )
            session['points_earned'] += points
            # Move to next item based on mode
            if session['mode'] == 'words':
                # In word mode, one word = one item - no sentence splitting
                session['current_item_index'] += 1
                    
            elif session['mode'] == 'sentences':
                # Move to next sentence
                session['current_item_index'] += 1
                
            elif session['mode'] == 'paragraphs':
                # Move to next paragraph
                session['current_item_index'] += 1
            
            # ===== REAL-TIME DIFFICULTY UPDATE =====
            accuracy = (
                session['correct_pronunciations'] /
                session['items_attempted']
                if session['items_attempted'] > 0 else 0
            )
            
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
            
            # AI encouragement
            encouragement = voice_utils.get_encouragement()
            voice_utils.speak(encouragement)
            
            feedback = {
                'success': True,
                'is_correct': True,
                'pronunciation_score': pronunciation_score,
                'points_earned': points,
                'reward_message': f"{encouragement} You earned {points} points!",
                'ai_feedback': encouragement,
                'total_points': session['points_earned'],
                'current_streak': session['current_streak'],
                'session_complete': False,
                'move_to_next': True,
                'level_up': level_up,
                'new_difficulty': new_difficulty if level_up else None,
                'session_progress': {
                    'attempted': session['session_items_attempted'],
                    'correct': session['session_correct']
                }
            }
            
        else:
            session['current_streak'] = 0
            session['consecutive_errors'] += 1
            session['word_attempts'] += 1
            
            # Adaptive help based on consecutive errors
            if session['consecutive_errors'] >= 2 or session['word_attempts'] >= 2:
                # AI speaks slowly
                text_to_speak = current_item.get('speak_text', '')
                voice_utils.speak("Let me say it slower for you.", slow=True)
                voice_utils.speak(text_to_speak, slow=True)
                feedback_msg = "Listen carefully and try again. You can do it!"
            else:
                help_msg = voice_utils.get_help_message('reading', current_item.get('category', 'easy'))
                voice_utils.speak(help_msg)
                feedback_msg = f"{help_msg} Try repeating after me again."
            
            # ===== REAL-TIME DIFFICULTY UPDATE (for wrong answers too) =====
            accuracy = (
                session['correct_pronunciations'] /
                session['items_attempted']
                if session['items_attempted'] > 0 else 0
            )
            
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
                level_message = f"Let's try some easier words to build confidence."
                voice_utils.speak(level_message)
            
            feedback = {
                'success': True,
                'is_correct': False,
                'pronunciation_score': pronunciation_score,
                'points_earned': 0,
                'reward_message': "Good attempt! Let's practice this one more time.",
                'ai_feedback': feedback_msg,
                'total_points': session['points_earned'],
                'current_streak': session['current_streak'],
                'session_complete': False,
                'needs_practice': True,
                'try_again': True,
                'level_down': level_down,
                'new_difficulty': new_difficulty if level_down else None,
                'session_progress': {
                    'attempted': session['session_items_attempted'],
                    'correct': session['session_correct']
                }
            }
            
            # Don't move to next if needs practice
            if session['word_attempts'] < 3:  # Max 3 attempts per item
                feedback['move_to_next'] = False
            else:
                # After 3 attempts, move to next item
                if session['mode'] == 'words':
                    # In word mode, one word = one item
                    session['current_item_index'] += 1
                    session['items_attempted'] += 1
                    session['session_items_attempted'] += 1
                        
                elif session['mode'] == 'sentences':
                    session['current_item_index'] += 1
                    session['items_attempted'] += 1
                    session['session_items_attempted'] += 1
                    
                elif session['mode'] == 'paragraphs':
                    session['current_item_index'] += 1
                    session['items_attempted'] += 1
                    session['session_items_attempted'] += 1
                
                session['word_attempts'] = 0
                feedback['move_to_next'] = True
                feedback['ai_feedback'] = "Let's try a different item. You can come back to this one later."
        
        # Check if session has reached a checkpoint (every 5 items in current session)
        if session['session_items_attempted'] >= 5:
            from app.utils.report_generator import report_generator
            feedback['checkpoint_reached'] = True
            feedback['continue_available'] = True
            
            # Only generate final report when user explicitly ends session
            # Not automatically at checkpoint
            
            # Stop monitoring if user chooses to end (handled separately)
        
        return feedback
    
    def _calculate_text_similarity(self, spoken, expected):
        """Calculate similarity between spoken and expected text"""
        if spoken == expected:
            return 1.0
        
        # Calculate character-based similarity using difflib
        return difflib.SequenceMatcher(None, spoken, expected).ratio()
    
    def _generate_text_feedback(self, accuracy, spoken, expected):
        """Generate encouraging feedback based on text comparison"""
        # 💛 Child-friendly encouraging feedback
        if accuracy >= 0.85:
            return "Excellent reading! 🌟"
        elif accuracy >= 0.7:
            return "Very good! Just a tiny improvement needed."
        elif accuracy >= 0.55:
            return "Nice try! Let's practice it once more."
        else:
            return "Good effort! Let's try that again together."
    
    def provide_help(self, user_id):
        """Provide help for current reading item"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)
        
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        if session['current_item_index'] >= len(session['items']):
            return {'error': 'No current item'}
        
        current_item = session['items'][session['current_item_index']]
        
        # Provide context-specific help based on mode
        if session['mode'] == 'words':
            word = current_item.get('speak_text', '')
            help_message = f"Let me help you with the word '{word}'. Listen carefully and repeat after me."
            voice_utils.speak(help_message)
            voice_utils.speak(word, slow=True)
            
        elif session['mode'] == 'sentences':
            sentence = current_item.get('full_text', '')
            help_message = f"Let's practice this sentence: {sentence}"
            voice_utils.speak(help_message)
            voice_utils.speak(sentence, slow=True)
            
        else:  # paragraphs
            paragraph = current_item.get('full_text', '')
            help_message = "Let's read this paragraph together. I'll read it first."
            voice_utils.speak(help_message)
            voice_utils.speak(paragraph, slow=True)
        
        session['help_provided'] = True
        
        return {
            'help_provided': True,
            'message': help_message,
            'full_text': current_item.get('full_text', '')
        }
    
    def continue_session(self, user_id):
        """Continue with next set of 5 items"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)
        
        if user_id not in self.user_sessions:
            return {'error': 'No active session'}
        
        session = self.user_sessions[user_id]
        
        # Select new items based on performance
        accuracy = session['correct_pronunciations'] / session['items_attempted'] if session['items_attempted'] > 0 else 0
        
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
        
        session['current_difficulty'] = new_difficulty
        session['items'] = self._select_items_based_on_difficulty(new_difficulty, session['mode'])
        session['current_item_index'] = 0
        # Reset session counters for new set of 5 items
        session['session_items_attempted'] = 0
        session['session_correct'] = 0
        # Keep items_attempted and correct_pronunciations to accumulate totals
        session['help_provided'] = False
        session['current_word_index'] = 0
        session['current_sentence_index'] = 0
        session['word_attempts'] = 0
        session['current_expected_text'] = ''
        
        voice_utils.speak(f"Excellent! Let's continue with more {new_difficulty} reading practice!")
        
        return {'message': 'Session continued', 'new_difficulty': new_difficulty}
    
    def _select_items_based_on_difficulty(self, difficulty, mode):
        """Select items based on current difficulty level"""
        if mode == 'words':
            data_source = self.words_data
        elif mode == 'sentences':
            data_source = self.sentences_data
        else:  # paragraphs
            data_source = self.paragraphs_data
        
        if not data_source:
            return []
            
        if difficulty == 'easy':
            distribution = [8, 2, 0]
        elif difficulty == 'medium':
            distribution = [5, 4, 1]
        else:  # hard
            distribution = [3, 4, 3]
        
        easy_items = [q for q in data_source if q['category'] == 'easy']
        medium_items = [q for q in data_source if q['category'] == 'medium']
        hard_items = [q for q in data_source if q['category'] == 'difficult']
        
        selected = []
        if easy_items:
            selected.extend(random.sample(easy_items, min(distribution[0], len(easy_items))))
        if medium_items:
            selected.extend(random.sample(medium_items, min(distribution[1], len(medium_items))))
        if hard_items:
            selected.extend(random.sample(hard_items, min(distribution[2], len(hard_items))))
        
        # If not enough items, fill with available ones
        if len(selected) < 5:
            all_items = data_source.copy()
            random.shuffle(all_items)
            selected.extend(all_items[:5 - len(selected)])
        
        random.shuffle(selected)
        return selected[:5]
    
    def get_session_summary(self, user_id):
        """Get summary of current session"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)
        
        if user_id not in self.user_sessions:
            return None
        
        session = self.user_sessions[user_id]
        accuracy = round((session['correct_pronunciations'] / session['items_attempted'] * 100), 2) if session['items_attempted'] > 0 else 0
        
        return {
            'mode': session['mode'],
            'items_attempted': session['items_attempted'],
            'correct_pronunciations': session['correct_pronunciations'],
            'accuracy': accuracy,
            'points_earned': session['points_earned'],
            'current_difficulty': session['current_difficulty'],
            'items_remaining': len(session['items']) - session['current_item_index'],
            'current_streak': session['current_streak'],
            'stress_level': session['stress_level'],
            'current_word_index': session['current_word_index'],
            'session_progress': {
                'attempted': session['session_items_attempted'],
                'correct': session['session_correct']
            }
        }
    
    def get_real_time_metrics(self, user_id):
        """Get real-time monitoring metrics from camera"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)
        
        if user_id not in self.user_sessions:
            return None
        
        camera_metrics = camera_utils.get_real_time_metrics(user_id)
        
        return {
            'camera': camera_metrics
        }
    
    # 🔥 COMPLETELY FIXED: Get progress with proper session vs cumulative handling
    def get_progress(self, user_id):
        """Get progress - returns session counters for active session, cumulative for reports"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)

        # First check active session
        session = self.user_sessions.get(user_id)

        if session:
            # 🔥 CRITICAL FIX: Check if this is a brand new session (no items attempted yet)
            if session.get('session_items_attempted', 0) == 0:
                logger.info(f"New session detected for user {user_id} - returning zeros")
                return {
                    'items_attempted': 0,
                    'correct_pronunciations': 0,
                    'accuracy': 0,
                    'points_earned': 0,
                    'current_streak': 0,
                    'session_progress': {
                        'attempted': 0,
                        'correct': 0
                    }
                }
            
            # Active session with progress - return session counters for the results page
            attempted = session.get('session_items_attempted', 0)
            correct = session.get('session_correct', 0)
            points = session.get('points_earned', 0)  # Session points only
            streak = session.get('current_streak', 0)

            accuracy = round((correct / attempted) * 100, 2) if attempted > 0 else 0

            logger.info(f"Active session progress for user {user_id}: {correct}/{attempted} correct, {points} points")

            return {
                'items_attempted': attempted,
                'correct_pronunciations': correct,
                'accuracy': accuracy,
                'points_earned': points,
                'current_streak': streak,
                'session_progress': {
                    'attempted': session.get('session_items_attempted', 0),
                    'correct': session.get('session_correct', 0)
                }
            }

        # ✅ If no session, fetch from database (for progress report page)
        progress = Progress.query.filter_by(
            user_id=user_id,
            module='reading'
        ).first()

        if progress:
            logger.info(f"Database progress for user {user_id}: {progress.questions_correct}/{progress.questions_attempted} correct, {progress.total_points} total points")
            return {
                'items_attempted': progress.questions_attempted,
                'correct_pronunciations': progress.questions_correct,
                'accuracy': round(
                    (progress.questions_correct / progress.questions_attempted * 100), 2
                ) if progress.questions_attempted > 0 else 0,
                'points_earned': progress.total_points,
                'current_streak': progress.questions_correct,
                'session_progress': {
                    'attempted': 0,
                    'correct': 0
                }
            }

        # If nothing found
        logger.info(f"No progress found for user {user_id}")
        return {
            'items_attempted': 0,
            'correct_pronunciations': 0,
            'accuracy': 0,
            'points_earned': 0,
            'current_streak': 0,
            'session_progress': {
                'attempted': 0,
                'correct': 0
            }
        }
    
    # 🔥 FIXED: Save session progress to database with proper accumulation
    def save_progress_to_db(self, user_id):
        """Save session progress to database"""
        # Parse user_id to handle string formats
        user_id = self._parse_user_id(user_id)
        session = self.user_sessions.get(user_id)
        
        if not session:
            logger.warning(f"No session found for user {user_id} to save to DB")
            return
        
        try:
            # Find existing progress record
            progress = Progress.query.filter_by(
                user_id=user_id,
                module='reading'
            ).first()
            
            if not progress:
                # Create new progress record
                progress = Progress(
                    user_id=user_id,
                    module='reading',
                    total_points=session['points_earned'],  # Session points only
                    questions_attempted=session['items_attempted'],  # Cumulative attempted
                    questions_correct=session['correct_pronunciations'],  # Cumulative correct
                    current_level=session['current_difficulty']
                )
                db.session.add(progress)
                logger.info(f"Created new progress record for user {user_id} with {session['points_earned']} points")
            else:
                # Update existing progress record
                progress.total_points += session['points_earned']  # Add session points
                progress.questions_attempted += session['items_attempted']  # Add cumulative
                progress.questions_correct += session['correct_pronunciations']  # Add cumulative
                progress.current_level = session['current_difficulty']
                progress.updated_at = datetime.now()
                logger.info(f"Updated progress record for user {user_id}: +{session['points_earned']} points, +{session['items_attempted']} items")
            
            db.session.commit()
            logger.info(f"Successfully saved progress to DB for user {user_id}")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving progress to DB: {str(e)}")

# Global reading service instance
reading_service = ReadingService()