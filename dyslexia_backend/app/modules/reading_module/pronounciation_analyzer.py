import numpy as np
import random  # ADDED IMPORT
from app.utils.speech_utils import speech_utils  # FIXED IMPORT PATH

class PronunciationAnalyzer:
    def __init__(self):
        self.phonetic_patterns = {
            'short_vowels': ['a', 'e', 'i', 'o', 'u'],
            'long_vowels': ['ay', 'ee', 'eye', 'oh', 'you'],
            'consonant_blends': ['bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'sc', 'sk', 'sl', 'sm', 'sn', 'sp', 'st', 'sw', 'tr', 'tw'],
            'digraphs': ['ch', 'sh', 'th', 'wh', 'ph']
        }
    
    def analyze_word_pronunciation(self, audio_data, word, context=None):
        """
        Analyze pronunciation of a single word with detailed feedback
        """
        # Use the speech utils for basic analysis
        basic_analysis = speech_utils.analyze_pronunciation(audio_data, word)
        
        if not basic_analysis['success']:
            return basic_analysis
        
        # Add detailed phonetic analysis
        detailed_analysis = self._analyze_phonetic_patterns(word, basic_analysis)
        
        # Combine results
        result = {**basic_analysis, **detailed_analysis}
        
        # Add word-specific feedback
        result['word_feedback'] = self._generate_word_specific_feedback(word, result)
        
        return result
    
    def analyze_sentence_pronunciation(self, audio_data, sentence, current_word=None, word_index=0):
        """
        Analyze pronunciation within sentence context
        """
        basic_analysis = speech_utils.analyze_pronunciation(audio_data, sentence)
        
        if not basic_analysis['success']:
            return basic_analysis
        
        # If we're focusing on a specific word in the sentence
        if current_word and word_index >= 0:
            words = sentence.split()
            if word_index < len(words):
                target_word = words[word_index]
                
                # Analyze the specific word within context
                word_analysis = self.analyze_word_pronunciation(audio_data, target_word, context=sentence)
                
                # Update the basic analysis with word-specific details
                basic_analysis['word_analysis'] = word_analysis
                basic_analysis['current_word'] = target_word
                basic_analysis['word_index'] = word_index
                basic_analysis['total_words'] = len(words)
                
                # Adjust overall score based on word performance
                if 'pronunciation_score' in word_analysis:
                    word_weight = 0.6  # Weight for current word
                    sentence_weight = 0.4  # Weight for full sentence
                    
                    basic_analysis['pronunciation_score'] = (
                        word_analysis['pronunciation_score'] * word_weight +
                        basic_analysis['pronunciation_score'] * sentence_weight
                    )
        
        return basic_analysis
    
    def _analyze_phonetic_patterns(self, word, basic_analysis):
        """
        Analyze phonetic patterns in the word for detailed feedback
        """
        word_lower = word.lower()
        patterns_found = []
        potential_issues = []
        
        # Check for common phonetic patterns
        for pattern_type, patterns in self.phonetic_patterns.items():
            for pattern in patterns:
                if pattern in word_lower:
                    patterns_found.append({
                        'type': pattern_type,
                        'pattern': pattern,
                        'position': word_lower.find(pattern)
                    })
        
        # Identify potentially difficult sounds
        difficult_sounds = self._identify_difficult_sounds(word_lower)
        if difficult_sounds:
            potential_issues.extend(difficult_sounds)
        
        # Analyze syllable structure
        syllables = self._estimate_syllables(word_lower)
        syllable_feedback = self._analyze_syllable_structure(word_lower, syllables)
        
        return {
            'phonetic_patterns': patterns_found,
            'potential_issues': potential_issues,
            'syllable_count': syllables,
            'syllable_feedback': syllable_feedback,
            'difficulty_level': self._assess_difficulty_level(word_lower, patterns_found)
        }
    
    def _identify_difficult_sounds(self, word):
        """Identify sounds that are commonly challenging"""
        difficult_patterns = {
            'th': 'voiced/unvoiced "th" sound (think/this)',
            'ch': '"ch" sound (church)',
            'sh': '"sh" sound (shoe)',
            'wh': '"wh" sound (what)',
            'ph': '"f" sound (phone)',
            'gh': 'silent or "f" sound (enough, ghost)',
            'kn': 'silent "k" (knee)',
            'wr': 'silent "w" (write)',
            'ng': 'nasal sound (sing)',
            'qu': '"kw" sound (queen)'
        }
        
        issues = []
        for pattern, description in difficult_patterns.items():
            if pattern in word:
                issues.append({
                    'sound': pattern,
                    'description': description,
                    'examples': self._get_sound_examples(pattern)
                })
        
        return issues
    
    def _get_sound_examples(self, sound):
        """Get example words for difficult sounds"""
        examples = {
            'th': ['the', 'this', 'that', 'think', 'thumb'],
            'ch': ['chat', 'church', 'cheese', 'chocolate'],
            'sh': ['shoe', 'ship', 'wish', 'fishing'],
            'wh': ['what', 'when', 'where', 'whale'],
            'ph': ['phone', 'photo', 'elephant', 'alphabet'],
            'gh': ['enough', 'laugh', 'ghost', 'night'],
            'kn': ['knee', 'knife', 'know', 'knight'],
            'wr': ['write', 'wrong', 'wrap', 'wrist'],
            'ng': ['sing', 'long', 'ring', 'song'],
            'qu': ['queen', 'quick', 'question', 'square']
        }
        return examples.get(sound, [])
    
    def _estimate_syllables(self, word):
        """Estimate number of syllables in a word"""
        vowels = 'aeiouy'
        count = 0
        prev_char_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_vowel:
                    count += 1
                prev_char_vowel = True
            else:
                prev_char_vowel = False
        
        # Adjust for words ending with 'e'
        if word.endswith('e') and count > 1:
            count -= 1
        
        return max(1, count)
    
    def _analyze_syllable_structure(self, word, syllable_count):
        """Analyze syllable structure for feedback"""
        if syllable_count == 1:
            return "This is a one-syllable word. Focus on clear pronunciation of all sounds."
        elif syllable_count == 2:
            return "This is a two-syllable word. Pay attention to syllable stress."
        elif syllable_count >= 3:
            return f"This is a {syllable_count}-syllable word. Break it down into parts and practice each syllable."
        
        return "Focus on clear articulation of each sound."
    
    def _assess_difficulty_level(self, word, patterns_found):
        """Assess the difficulty level of the word"""
        difficulty_score = 0
        
        # Length factor
        if len(word) <= 3:
            difficulty_score += 1
        elif len(word) <= 5:
            difficulty_score += 2
        else:
            difficulty_score += 3
        
        # Syllable factor
        syllables = self._estimate_syllables(word)
        difficulty_score += min(3, syllables)
        
        # Complex patterns factor
        complex_patterns = ['th', 'ch', 'sh', 'wh', 'ph', 'gh', 'kn', 'wr']
        for pattern in complex_patterns:
            if pattern in word:
                difficulty_score += 2
        
        # Determine level
        if difficulty_score <= 3:
            return "easy"
        elif difficulty_score <= 6:
            return "medium"
        else:
            return "difficult"
    
    def _generate_word_specific_feedback(self, word, analysis):
        """Generate specific feedback for the word"""
        feedback_parts = []
        
        # Basic accuracy feedback
        accuracy = analysis.get('accuracy', 0)
        if accuracy >= 0.9:
            feedback_parts.append("Perfect! 🎉")
        elif accuracy >= 0.7:
            feedback_parts.append("Well done!")
        elif accuracy >= 0.5:
            feedback_parts.append("Good attempt!")
        else:
            feedback_parts.append("Let's try again.")
        
        # Phonetic pattern feedback
        patterns = analysis.get('phonetic_patterns', [])
        if patterns:
            for pattern in patterns[:2]:  # Limit to 2 patterns
                if pattern['type'] == 'digraphs':
                    feedback_parts.append(f"Remember the '{pattern['pattern']}' sound.")
        
        # Difficulty-specific feedback
        difficulty = analysis.get('difficulty_level', 'easy')
        if difficulty == 'difficult':
            feedback_parts.append("This is a challenging word. Break it into smaller parts.")
        
        # Syllable feedback
        syllable_feedback = analysis.get('syllable_feedback', '')
        if syllable_feedback:
            feedback_parts.append(syllable_feedback)
        
        return " ".join(feedback_parts)
    
    def get_practice_suggestions(self, word, analysis):
        """Get practice suggestions based on analysis"""
        suggestions = []
        difficulty = analysis.get('difficulty_level', 'easy')
        
        if difficulty == 'easy':
            suggestions.extend([
                "Practice saying the word slowly and clearly",
                "Repeat the word 3-5 times",
                "Use the word in a simple sentence"
            ])
        elif difficulty == 'medium':
            suggestions.extend([
                "Break the word into syllables and practice each part",
                "Say the word at different speeds",
                "Practice with similar sounding words"
            ])
        else:  # difficult
            suggestions.extend([
                "Practice each syllable separately, then combine",
                "Record yourself and compare with correct pronunciation",
                "Use the word in different sentences for context"
            ])
        
        # Add pattern-specific suggestions
        issues = analysis.get('potential_issues', [])
        for issue in issues[:2]:  # Limit to 2 issues
            sound = issue['sound']
            suggestions.append(f"Focus on the '{sound}' sound. Practice words like: {', '.join(issue['examples'][:2])}")
        
        return suggestions

# Global pronunciation analyzer instance
pronunciation_analyzer = PronunciationAnalyzer()
