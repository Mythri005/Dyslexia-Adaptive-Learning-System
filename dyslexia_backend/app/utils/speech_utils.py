import speech_recognition as sr
import librosa
import numpy as np
import tempfile
import os
from pydub import AudioSegment
import base64
import time
from collections import deque
from datetime import datetime
import logging
import difflib

logger = logging.getLogger(__name__)

class SpeechUtils:
    def __init__(self):
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            
            # Real-time voice monitoring
            self.voice_metrics = {}
            self.monitoring_active = False
            
        except Exception as e:
            print(f"Speech utils initialization warning: {e}")
    
    def start_voice_monitoring(self, user_id):
        """Start real-time voice monitoring for user"""
        self.voice_metrics[user_id] = {
            'energy_levels': deque(maxlen=50),
            'speech_rates': deque(maxlen=50),
            'pitch_levels': deque(maxlen=50),
            'clarity_scores': deque(maxlen=50),
            'last_audio_time': None,
            'is_speaking': False
        }
        print(f"✅ Voice monitoring started for user {user_id}")
    
    def stop_voice_monitoring(self, user_id):
        """Stop voice monitoring for user"""
        if user_id in self.voice_metrics:
            del self.voice_metrics[user_id]
        print(f"✅ Voice monitoring stopped for user {user_id}")
    
    def analyze_voice_metrics(self, audio_data, user_id):
        """Analyze voice metrics in real-time"""
        if user_id not in self.voice_metrics:
            self.start_voice_monitoring(user_id)
        
        try:
            # Create temporary file for analysis
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                if isinstance(audio_data, bytes):
                    temp_audio.write(audio_data)
                else:
                    audio_binary = base64.b64decode(audio_data.split(',')[1] if isinstance(audio_data, str) and audio_data.startswith('data:audio') else audio_data)
                    temp_audio.write(audio_binary)
                temp_audio_path = temp_audio.name
            
            # Load audio with librosa
            y, sr = librosa.load(temp_audio_path, sr=None)
            
            # Clean up
            os.unlink(temp_audio_path)
            
            # Extract voice metrics
            metrics = self._extract_voice_features(y, sr)
            
            # Update user metrics
            self.voice_metrics[user_id]['energy_levels'].append(metrics['energy'])
            self.voice_metrics[user_id]['speech_rates'].append(metrics['speech_rate'])
            self.voice_metrics[user_id]['pitch_levels'].append(metrics['pitch_mean'])
            self.voice_metrics[user_id]['clarity_scores'].append(metrics['clarity'])
            self.voice_metrics[user_id]['last_audio_time'] = datetime.now()
            self.voice_metrics[user_id]['is_speaking'] = metrics['is_speaking']
            
            return metrics
            
        except Exception as e:
            print(f"Voice metrics analysis error: {e}")
            return self._get_default_voice_metrics()
    
    def _extract_voice_features(self, y, sr):
        """Extract comprehensive voice features"""
        features = {}
        
        # Energy (volume)
        features['energy'] = np.mean(np.abs(y))
        
        # Speech rate estimation
        features['speech_rate'] = self._estimate_speech_rate(y, sr)
        
        # Pitch analysis
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=50, fmax=300, sr=sr)
            f0 = f0[voiced_flag]
            if len(f0) > 0:
                features['pitch_mean'] = np.mean(f0)
                features['pitch_std'] = np.std(f0)
            else:
                features['pitch_mean'] = 0
                features['pitch_std'] = 0
        except:
            features['pitch_mean'] = 0
            features['pitch_std'] = 0
        
        # Voice clarity (spectral centroid)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        features['clarity'] = np.mean(spectral_centroid) / 1000  # Normalize
        
        # Speech activity detection
        features['is_speaking'] = features['energy'] > 0.01 and features['speech_rate'] > 50
        
        # Confidence score
        features['confidence'] = min(1.0, features['energy'] * 10 + features['clarity'] * 2)
        
        return features
    
    def _estimate_speech_rate(self, y, sr):
        """Estimate speech rate from audio"""
        try:
            frame_length = int(0.025 * sr)
            hop_length = int(0.010 * sr)
            
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            rms_threshold = np.mean(rms) * 0.3
            
            speech_frames = np.sum(rms > rms_threshold)
            total_frames = len(rms)
            
            if total_frames == 0:
                return 0
            
            speech_ratio = speech_frames / total_frames
            wpm_estimate = speech_ratio * 180
            
            return min(200, wpm_estimate)
            
        except:
            return 0
    
    def get_voice_metrics(self, user_id):
        """Get current voice metrics for user"""
        if user_id not in self.voice_metrics:
            return None
        
        user_metrics = self.voice_metrics[user_id]
        
        # Check if data is stale
        if (user_metrics['last_audio_time'] and 
            (datetime.now() - user_metrics['last_audio_time']).seconds > 10):
            return {'status': 'inactive', 'message': 'No recent voice data'}
        
        if not user_metrics['energy_levels']:
            return {'status': 'no_data', 'message': 'No voice data available'}
        
        metrics = {
            'status': 'active',
            'current_energy': user_metrics['energy_levels'][-1],
            'current_speech_rate': user_metrics['speech_rates'][-1],
            'current_pitch': user_metrics['pitch_levels'][-1],
            'current_clarity': user_metrics['clarity_scores'][-1],
            'is_speaking': user_metrics['is_speaking'],
            'trends': {
                'energy_trend': self._calculate_voice_trend(user_metrics['energy_levels']),
                'speech_rate_trend': self._calculate_voice_trend(user_metrics['speech_rates']),
                'pitch_trend': self._calculate_voice_trend(user_metrics['pitch_levels'])
            },
            'last_update': user_metrics['last_audio_time'].isoformat() if user_metrics['last_audio_time'] else None
        }
        
        return metrics
    
    def _calculate_voice_trend(self, data):
        """Calculate trend from voice data"""
        if len(data) < 3:
            return 'stable'
        
        recent = list(data)[-3:]
        if len(recent) < 2:
            return 'stable'
        
        # Simple trend calculation
        if recent[-1] > recent[0] * 1.1:
            return 'increasing'
        elif recent[-1] < recent[0] * 0.9:
            return 'decreasing'
        else:
            return 'stable'
    
    def _get_default_voice_metrics(self):
        """Return default voice metrics"""
        return {
            'energy': 0.0,
            'speech_rate': 0,
            'pitch_mean': 0,
            'pitch_std': 0,
            'clarity': 0.0,
            'is_speaking': False,
            'confidence': 0.0
        }
    
    def speech_to_text(self, audio_data, language='en-US'):
        """
        Convert speech audio to text using Google Speech Recognition
        """
        try:
            # Handle different input formats
            if isinstance(audio_data, str):
                if audio_data.startswith('data:audio'):
                    audio_data = audio_data.split(',')[1]
                audio_binary = base64.b64decode(audio_data)
            elif isinstance(audio_data, bytes):
                audio_binary = audio_data
            else:
                raise ValueError("Invalid audio data format")
            
            # Create temporary audio file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_binary)
                temp_audio_path = temp_audio.name
            
            # Convert to WAV if needed and read with speech_recognition
            with sr.AudioFile(temp_audio_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Clean up temporary file
            os.unlink(temp_audio_path)
            
            # Perform speech recognition
            text = self.recognizer.recognize_google(audio, language=language)
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': 0.9  # Google doesn't provide confidence scores
            }
            
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Could not understand audio',
                'confidence': 0.0
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'Speech recognition service error: {e}',
                'confidence': 0.0
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {e}',
                'confidence': 0.0
            }
    
    def analyze_pronunciation(self, audio_data, expected_text):
        """
        Analyze pronunciation quality by comparing spoken text with expected text
        """
        try:
            # First, convert speech to text
            recognition_result = self.speech_to_text(audio_data)
            
            if not recognition_result['success']:
                return {
                    'success': False,
                    'error': recognition_result['error'],
                    'pronunciation_score': 0.0,
                    'accuracy': 0.0,
                    'matched_text': '',
                    'expected_text': expected_text
                }
            
            spoken_text = recognition_result['text'].lower()
            expected_text_lower = expected_text.lower()
            
            # Calculate text similarity (Levenshtein distance-based)
            accuracy = self._calculate_text_similarity(spoken_text, expected_text_lower)
            
            # STRICT WORD-LEVEL COMPARISON
            expected_words = expected_text_lower.split()
            spoken_words = spoken_text.split()
            
            # Calculate exact word match accuracy
            if len(expected_words) == 0:
                word_accuracy = 0
                all_words_match = False
            else:
                # Check if ALL words match exactly (for correctness)
                all_words_match = spoken_words == expected_words
                
                # Calculate word match percentage
                matches = 0
                for i in range(min(len(expected_words), len(spoken_words))):
                    if expected_words[i] == spoken_words[i]:
                        matches += 1
                
                word_accuracy = matches / len(expected_words)
            
            # Apply penalties for word count mismatch
            word_count_diff = abs(len(expected_words) - len(spoken_words))
            word_count_penalty = max(0, 1.0 - (0.5 * word_count_diff))
            
            # Combine scores - give heavy weight to word matching
            combined_accuracy = (accuracy * 0.2) + (word_accuracy * 0.8)
            combined_accuracy *= word_count_penalty
            
            # DETERMINE CORRECTNESS STRICTLY
            # Option 1: All words must match exactly (strictest)
            is_correct_strict = all_words_match and word_count_diff == 0
            
            # Option 2: Word accuracy threshold (allowing accent variations)
            # Uncomment if you want to allow minor accent differences
            is_correct = word_accuracy >= 0.8 and word_count_diff <= 1
            
            # Analyze audio features for pronunciation quality
            audio_features = self._analyze_audio_features(audio_data)
            
            # Calculate pronunciation score
            pronunciation_score = self._calculate_pronunciation_score(combined_accuracy, audio_features)
            
            return {
                'success': True,
                'pronunciation_score': pronunciation_score,
                'accuracy': combined_accuracy,
                'spoken_text': spoken_text,
                'expected_text': expected_text,
                'is_correct': is_correct,
                'all_words_match': all_words_match,
                'word_accuracy': word_accuracy,
                'word_count_diff': word_count_diff,
                'audio_features': audio_features,
                'feedback': self._generate_pronunciation_feedback(
                    combined_accuracy, 
                    audio_features, 
                    spoken_text, 
                    expected_text, 
                    word_accuracy, 
                    word_count_diff, 
                    is_correct
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pronunciation analysis error: {e}',
                'pronunciation_score': 0.0,
                'accuracy': 0.0
            }
    
    def analyze_pronunciation_with_text(self, transcribed_text, expected_text, audio_data=None):
        """
        Analyze pronunciation using transcribed text from frontend
        This method is specifically for the reading module
        """
        try:
            # Calculate text similarity
            accuracy = self._calculate_text_similarity(transcribed_text.lower(), expected_text.lower())
            
            # STRICT WORD-LEVEL COMPARISON
            expected_words = expected_text.lower().split()
            spoken_words = transcribed_text.lower().split()
            
            # Calculate exact word match accuracy
            if len(expected_words) == 0:
                word_accuracy = 0
                all_words_match = False
            else:
                # Check if ALL words match exactly (for correctness)
                all_words_match = spoken_words == expected_words
                
                # Calculate word match percentage
                matches = 0
                for i in range(min(len(expected_words), len(spoken_words))):
                    if expected_words[i] == spoken_words[i]:
                        matches += 1
                
                word_accuracy = matches / len(expected_words)
            
            # Apply penalties for word count mismatch
            word_count_diff = abs(len(expected_words) - len(spoken_words))
            word_count_penalty = max(0, 1.0 - (0.5 * word_count_diff))
            
            # Combine scores - give heavy weight to word matching
            combined_accuracy = (accuracy * 0.2) + (word_accuracy * 0.8)
            combined_accuracy *= word_count_penalty
            
            # DETERMINE CORRECTNESS STRICTLY
            # Word accuracy threshold (allowing accent variations)
            is_correct = word_accuracy >= 0.8 and word_count_diff <= 1
            
            # Pronunciation score
            pronunciation_score = combined_accuracy
            
            # If audio data is provided, enhance with audio analysis
            audio_enhancement = 0.0
            if audio_data:
                audio_features = self._analyze_audio_features(audio_data)
                audio_enhancement = min(0.2, audio_features.get('energy', 0) * 0.1 + audio_features.get('clarity', 0) * 0.1)
                pronunciation_score = min(1.0, combined_accuracy + audio_enhancement)
            
            return {
                'success': True,
                'pronunciation_score': pronunciation_score,
                'accuracy': combined_accuracy,
                'spoken_text': transcribed_text,
                'expected_text': expected_text,
                'is_correct': is_correct,
                'all_words_match': all_words_match,
                'word_accuracy': word_accuracy,
                'word_count_diff': word_count_diff,
                'audio_enhancement': audio_enhancement,
                'feedback': self._generate_pronunciation_feedback(
                    combined_accuracy, 
                    {}, 
                    transcribed_text, 
                    expected_text, 
                    word_accuracy, 
                    word_count_diff, 
                    is_correct
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Pronunciation analysis failed: {e}',
                'pronunciation_score': 0.0,
                'accuracy': 0.0
            }
    
    def _calculate_text_similarity(self, spoken, expected):
        """
        Calculate similarity between spoken and expected text using difflib
        """
        if spoken == expected:
            return 1.0
        
        # Use difflib for better text comparison
        return difflib.SequenceMatcher(None, spoken, expected).ratio()
    
    def _analyze_audio_features(self, audio_data):
        """
        Analyze audio features for pronunciation quality
        """
        try:
            # Create temporary file for audio analysis
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                if isinstance(audio_data, bytes):
                    temp_audio.write(audio_data)
                else:
                    audio_binary = base64.b64decode(audio_data.split(',')[1] if isinstance(audio_data, str) and audio_data.startswith('data:audio') else audio_data)
                    temp_audio.write(audio_binary)
                temp_audio_path = temp_audio.name
            
            # Load audio with librosa
            y, sr = librosa.load(temp_audio_path, sr=None)
            
            # Clean up
            os.unlink(temp_audio_path)
            
            # Extract features
            features = {}
            
            # Duration
            features['duration'] = len(y) / sr
            
            # Energy (volume)
            features['energy'] = np.mean(np.abs(y))
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            features['spectral_centroid_mean'] = np.mean(spectral_centroid)
            
            # Zero crossing rate (speech vs silence)
            zcr = librosa.feature.zero_crossing_rate(y)
            features['zero_crossing_rate'] = np.mean(zcr)
            
            return features
            
        except Exception as e:
            print(f"Audio feature analysis error: {e}")
            return {
                'duration': 0,
                'energy': 0,
                'spectral_centroid_mean': 0,
                'zero_crossing_rate': 0
            }
    
    def _calculate_pronunciation_score(self, accuracy, audio_features):
        """
        Calculate overall pronunciation score combining text accuracy and audio features
        """
        # Base score from text accuracy
        base_score = accuracy
        
        # Audio quality adjustments
        audio_score = 0.5  # Neutral base
        
        # Adjust based on duration (too short or too long is bad)
        duration = audio_features.get('duration', 0)
        if 0.5 <= duration <= 5.0:  # Reasonable speaking duration
            audio_score += 0.2
        else:
            audio_score -= 0.1
        
        # Adjust based on energy (volume)
        energy = audio_features.get('energy', 0)
        if energy > 0.01:  # Reasonable volume
            audio_score += 0.2
        else:
            audio_score -= 0.1
        
        # Combine scores
        final_score = (base_score * 0.7) + (audio_score * 0.3)
        
        return min(1.0, max(0.0, final_score))
    
    def _generate_pronunciation_feedback(self, accuracy, audio_features, spoken_text, expected_text, word_accuracy, word_count_diff, is_correct):
        """Generate helpful feedback for pronunciation improvement"""
        feedback = []
        
        if is_correct:
            if word_accuracy == 1.0 and word_count_diff == 0:
                feedback.append("Perfect! You said every word correctly! 🎉")
            elif word_accuracy >= 0.9:
                feedback.append("Excellent! Almost perfect! 🌟")
            else:
                feedback.append("Good job! You got most of the words right! 👍")
        else:
            feedback.append("Let's try again. Pay close attention to each word.")
        
        # Word count feedback
        if word_count_diff > 0:
            if word_count_diff == 1:
                if len(spoken_text.split()) > len(expected_text.split()):
                    feedback.append("You said one extra word.")
                else:
                    feedback.append("You missed one word.")
            else:
                if len(spoken_text.split()) > len(expected_text.split()):
                    feedback.append(f"You said {word_count_diff} too many words.")
                else:
                    feedback.append(f"You missed {word_count_diff} words.")
        
        # Specific word mismatch feedback
        if word_accuracy < 0.8 and word_count_diff <= 1:
            expected_words = expected_text.lower().split()
            spoken_words = spoken_text.lower().split()
            
            mismatches = []
            for i in range(min(len(expected_words), len(spoken_words))):
                if expected_words[i] != spoken_words[i]:
                    mismatches.append(f"'{expected_words[i]}' vs '{spoken_words[i]}'")
            
            if mismatches:
                feedback.append(f"Check these words: {', '.join(mismatches[:2])}")
        
        # Audio quality feedback
        duration = audio_features.get('duration', 0)
        if duration < 0.5:
            feedback.append("Try speaking a bit more slowly and clearly.")
        
        energy = audio_features.get('energy', 0)
        if energy < 0.005:
            feedback.append("Speak up a little so I can hear you better.")
        
        return " ".join(feedback)
    
    def _get_detailed_feedback(self, spoken, expected):
        """Generate detailed feedback about specific pronunciation issues"""
        if spoken == expected:
            return ""
        
        # Simple character-by-character comparison
        spoken_chars = list(spoken)
        expected_chars = list(expected)
        
        differences = []
        min_len = min(len(spoken_chars), len(expected_chars))
        
        for i in range(min_len):
            if spoken_chars[i] != expected_chars[i]:
                differences.append(f"'{spoken_chars[i]}' instead of '{expected_chars[i]}'")
        
        if differences:
            return f"Pay attention to these sounds: {', '.join(differences[:2])}"
        
        return ""

# Global speech utils instance
speech_utils = SpeechUtils()