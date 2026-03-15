import re
import numpy as np
from collections import Counter

class WordAnalyzer:
    def __init__(self):
        self.common_patterns = {
            'cvc': r'^[bcdfghjklmnpqrstvwxyz][aeiou][bcdfghjklmnpqrstvwxyz]$',  # consonant-vowel-consonant
            'cvce': r'^[bcdfghjklmnpqrstvwxyz][aeiou][bcdfghjklmnpqrstvwxyz]e$',  # consonant-vowel-consonant-silent e
            'vowel_teams': ['ai', 'ay', 'ea', 'ee', 'ie', 'oa', 'oe', 'ue', 'ui'],
            'r_controlled': ['ar', 'er', 'ir', 'or', 'ur'],
            'digraphs': ['ch', 'sh', 'th', 'wh', 'ph', 'ck'],
            'blends': ['bl', 'br', 'cl', 'cr', 'dr', 'fl', 'fr', 'gl', 'gr', 'pl', 'pr', 'sc', 'sk', 'sl', 'sm', 'sn', 'sp', 'st', 'sw', 'tr', 'tw']
        }
        
        self.difficulty_factors = {
            'length': {3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6},
            'pattern_complexity': {'cvc': 1, 'cvce': 2, 'vowel_teams': 3, 'r_controlled': 3, 'digraphs': 2, 'blends': 2},
            'irregularity': 5
        }
    
    def analyze_word(self, word):
        """
        Comprehensive analysis of a word for spelling instruction
        """
        word_lower = word.lower().strip()
        
        analysis = {
            'word': word,
            'length': len(word_lower),
            'letters': list(word_lower),
            'patterns': self._identify_patterns(word_lower),
            'syllables': self._estimate_syllables(word_lower),
            'phonetic_breakdown': self._phonetic_breakdown(word_lower),
            'difficulty_score': 0,
            'difficulty_level': 'easy',
            'learning_suggestions': [],
            'common_mistakes': self._predict_common_mistakes(word_lower),
            'word_family': self._identify_word_family(word_lower)
        }
        
        # Calculate difficulty
        analysis['difficulty_score'] = self._calculate_difficulty_score(analysis)
        analysis['difficulty_level'] = self._determine_difficulty_level(analysis['difficulty_score'])
        
        # Generate learning suggestions
        analysis['learning_suggestions'] = self._generate_learning_suggestions(analysis)
        
        return analysis
    
    def analyze_spelling_attempt(self, attempted_word, correct_word, context=None):
        """
        Analyze a spelling attempt and provide detailed feedback
        """
        attempted_lower = attempted_word.lower().strip()
        correct_lower = correct_word.lower().strip()
        
        analysis = {
            'attempted': attempted_word,
            'correct': correct_word,
            'is_correct': attempted_lower == correct_lower,
            'error_type': None,
            'error_details': [],
            'phonetic_similarity': self._calculate_phonetic_similarity(attempted_lower, correct_lower),
            'visual_similarity': self._calculate_visual_similarity(attempted_lower, correct_lower),
            'feedback': '',
            'practice_suggestions': []
        }
        
        if not analysis['is_correct']:
            analysis['error_type'] = self._classify_spelling_error(attempted_lower, correct_lower)
            analysis['error_details'] = self._analyze_error_details(attempted_lower, correct_lower)
            analysis['feedback'] = self._generate_error_feedback(analysis)
            analysis['practice_suggestions'] = self._generate_practice_suggestions(analysis)
        
        return analysis
    
    def _identify_patterns(self, word):
        """Identify spelling patterns in the word"""
        patterns = []
        
        # Check basic patterns
        for pattern_name, pattern in self.common_patterns.items():
            if isinstance(pattern, str):  # Regex pattern
                if re.match(pattern, word):
                    patterns.append(pattern_name)
            else:  # List of patterns
                for p in pattern:
                    if p in word:
                        patterns.append(f"{pattern_name}:{p}")
        
        # Check for silent letters
        silent_letters = self._identify_silent_letters(word)
        if silent_letters:
            patterns.append(f"silent_letters:{','.join(silent_letters)}")
        
        # Check for double letters
        double_letters = self._find_double_letters(word)
        if double_letters:
            patterns.append(f"double_letters:{','.join(double_letters)}")
        
        return patterns
    
    def _identify_silent_letters(self, word):
        """Identify silent letters in the word"""
        silent_patterns = {
            'k': ['kn'],    # knee, know
            'w': ['wr'],    # write, wrong
            'g': ['gn'],    # gnome, sign
            'b': ['mb'],    # comb, thumb
            'l': ['lk', 'lm'], # walk, calm
            'e': ['e$']     # silent e at end
        }
        
        silent_letters = []
        for letter, patterns in silent_patterns.items():
            for pattern in patterns:
                if pattern in word:
                    silent_letters.append(letter)
        
        return silent_letters
    
    def _find_double_letters(self, word):
        """Find double letters in the word"""
        doubles = []
        for i in range(len(word) - 1):
            if word[i] == word[i+1]:
                doubles.append(word[i])
        return doubles
    
    def _estimate_syllables(self, word):
        """Estimate number of syllables"""
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
    
    def _phonetic_breakdown(self, word):
        """Break down word into phonetic components"""
        breakdown = []
        i = 0
        
        while i < len(word):
            # Check for multi-letter patterns first
            found_pattern = False
            
            # Check digraphs and blends (2 letters)
            if i < len(word) - 1:
                two_letters = word[i:i+2]
                for pattern_type in ['digraphs', 'blends', 'vowel_teams', 'r_controlled']:
                    if two_letters in self.common_patterns[pattern_type]:
                        breakdown.append({
                            'segment': two_letters,
                            'type': pattern_type[:-1],  # Remove 's'
                            'position': i
                        })
                        i += 2
                        found_pattern = True
                        break
            
            # If no pattern found, add single letter
            if not found_pattern:
                char_type = 'vowel' if word[i] in 'aeiou' else 'consonant'
                breakdown.append({
                    'segment': word[i],
                    'type': char_type,
                    'position': i
                })
                i += 1
        
        return breakdown
    
    def _calculate_difficulty_score(self, analysis):
        """Calculate spelling difficulty score"""
        score = 0
        
        # Length factor
        length = analysis['length']
        score += self.difficulty_factors['length'].get(length, 7)
        
        # Pattern complexity
        for pattern in analysis['patterns']:
            base_pattern = pattern.split(':')[0]  # Get base pattern name
            if base_pattern in self.difficulty_factors['pattern_complexity']:
                score += self.difficulty_factors['pattern_complexity'][base_pattern]
        
        # Syllable complexity
        syllables = analysis['syllables']
        score += max(0, syllables - 1) * 2
        
        # Irregularity penalty
        if analysis['common_mistakes']:
            score += 2
        
        return score
    
    def _determine_difficulty_level(self, score):
        """Determine difficulty level based on score"""
        if score <= 5:
            return 'easy'
        elif score <= 10:
            return 'medium'
        else:
            return 'difficult'
    
    def _predict_common_mistakes(self, word):
        """Predict common spelling mistakes for this word"""
        common_mistakes = []
        
        # Phonetically similar substitutions
        phonetic_subs = {
            'c': ['k', 's'],
            'k': ['c'],
            's': ['c'],
            'f': ['ph'],
            'ph': ['f'],
            'ee': ['ea'],
            'ea': ['ee'],
            'ai': ['ay'],
            'ay': ['ai']
        }
        
        # Common omissions
        if any(pattern.startswith('silent_letters') for pattern in self._identify_patterns(word)):
            common_mistakes.append("omitting_silent_letters")
        
        # Common additions
        if not word.endswith('e') and any(vowel in word for vowel in 'aeiou'):
            common_mistakes.append("adding_final_e")
        
        return common_mistakes
    
    def _identify_word_family(self, word):
        """Identify word family/rhyming pattern"""
        # Simple rhyming pattern based on last 2-3 letters
        if len(word) >= 3:
            return word[-3:]
        elif len(word) == 2:
            return word
        else:
            return word
    
    def _calculate_phonetic_similarity(self, attempted, correct):
        """Calculate phonetic similarity between attempted and correct spelling"""
        # Simple character-based similarity for now
        return self._levenshtein_similarity(attempted, correct)
    
    def _calculate_visual_similarity(self, attempted, correct):
        """Calculate visual similarity between attempted and correct spelling"""
        # Consider visually similar letters
        visual_similar = {
            'i': ['l', '1'],
            'l': ['i', '1'],
            'o': ['0'],
            'e': ['c'],
            'c': ['e'],
            'm': ['n'],
            'n': ['m'],
            'u': ['v'],
            'v': ['u']
        }
        
        if len(attempted) != len(correct):
            return 0.0
        
        similar_count = 0
        for a, c in zip(attempted, correct):
            if a == c:
                similar_count += 1
            elif a in visual_similar.get(c, []):
                similar_count += 0.5
        
        return similar_count / len(correct)
    
    def _levenshtein_similarity(self, s1, s2):
        """Calculate Levenshtein similarity between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_similarity(s2, s1)
        
        if len(s2) == 0:
            return 0.0
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        distance = previous_row[-1]
        max_len = max(len(s1), len(s2))
        
        if max_len == 0:
            return 1.0
        
        return 1.0 - (distance / max_len)
    
    def _classify_spelling_error(self, attempted, correct):
        """Classify the type of spelling error"""
        if len(attempted) != len(correct):
            return "length_mismatch"
        
        errors = []
        for a, c in zip(attempted, correct):
            if a != c:
                # Check if phonetic substitution
                phonetic_groups = [
                    ['c', 'k', 's'],
                    ['f', 'ph'],
                    ['ee', 'ea'],
                    ['ai', 'ay']
                ]
                
                for group in phonetic_groups:
                    if a in group and c in group:
                        errors.append("phonetic_substitution")
                        break
                else:
                    errors.append("letter_substitution")
        
        if errors:
            return max(set(errors), key=errors.count)
        
        return "unknown_error"
    
    def _analyze_error_details(self, attempted, correct):
        """Analyze specific error details"""
        details = []
        
        for i, (a, c) in enumerate(zip(attempted, correct)):
            if a != c:
                details.append({
                    'position': i,
                    'attempted_letter': a,
                    'correct_letter': c,
                    'error_type': 'substitution'
                })
        
        # Handle length mismatches
        if len(attempted) > len(correct):
            details.append({
                'position': len(correct),
                'attempted_letter': 'extra_letters',
                'correct_letter': '',
                'error_type': 'addition'
            })
        elif len(attempted) < len(correct):
            details.append({
                'position': len(attempted),
                'attempted_letter': '',
                'correct_letter': correct[len(attempted)],
                'error_type': 'omission'
            })
        
        return details
    
    def _generate_error_feedback(self, analysis):
        """Generate specific feedback for the spelling error"""
        error_type = analysis['error_type']
        
        if error_type == 'phonetic_substitution':
            return "Good try! You used a different spelling for the same sound. Remember the correct letter pattern."
        elif error_type == 'letter_substitution':
            return "Close! Pay attention to the specific letters in this word."
        elif error_type == 'length_mismatch':
            return "Check the number of letters in your spelling compared to the correct word."
        elif error_type == 'addition':
            return "You have an extra letter in your spelling. Try sounding it out carefully."
        elif error_type == 'omission':
            return "You're missing a letter. Listen for all the sounds in the word."
        else:
            return "Let's practice this word some more. Focus on each sound and letter."
    
    def _generate_learning_suggestions(self, analysis):
        """Generate learning suggestions based on word analysis"""
        suggestions = []
        word = analysis['word']
        difficulty = analysis['difficulty_level']
        
        # General suggestions based on difficulty
        if difficulty == 'easy':
            suggestions.extend([
                f"Practice writing '{word}' 3 times",
                f"Say the word aloud while looking at it",
                "Create a mental picture of the word"
            ])
        elif difficulty == 'medium':
            suggestions.extend([
                f"Break '{word}' into syllables: {self._break_into_syllables(word)}",
                "Practice spelling the word without looking",
                "Use the word in a sentence"
            ])
        else:  # difficult
            suggestions.extend([
                f"Study the spelling pattern: {', '.join(analysis['patterns'][:2])}",
                "Practice with similar words from the same word family",
                "Create a mnemonic device to remember the spelling"
            ])
        
        # Pattern-specific suggestions
        for pattern in analysis['patterns'][:2]:  # Limit to 2 patterns
            if pattern.startswith('silent_letters'):
                suggestions.append("Remember which letters are silent in this word")
            elif pattern.startswith('double_letters'):
                suggestions.append("Pay attention to the double letters")
            elif 'digraph' in pattern:
                suggestions.append("Practice the special two-letter sound")
        
        return suggestions
    
    def _break_into_syllables(self, word):
        """Break word into estimated syllables"""
        syllables = []
        current = ""
        
        for i, char in enumerate(word):
            current += char
            if char in 'aeiou' and i < len(word) - 1 and word[i+1] not in 'aeiou':
                syllables.append(current)
                current = ""
        
        if current:
            syllables.append(current)
        
        return '-'.join(syllables) if syllables else word
    
    def _generate_practice_suggestions(self, analysis):
        """Generate practice suggestions for spelling errors"""
        suggestions = []
        error_type = analysis['error_type']
        
        if error_type == 'phonetic_substitution':
            suggestions.extend([
                "Practice words with similar sounds but different spellings",
                "Learn spelling rules for different sound patterns",
                "Use word sorting activities by sound-spelling patterns"
            ])
        elif error_type in ['letter_substitution', 'addition', 'omission']:
            suggestions.extend([
                "Practice visualizing the word with your eyes closed",
                "Write the word multiple times while saying each letter",
                "Use tactile methods like writing in sand or with magnetic letters"
            ])
        elif error_type == 'length_mismatch':
            suggestions.extend([
                "Clap the syllables while spelling",
                "Count the letters before and after writing",
                "Practice with words of similar length"
            ])
        
        # Add general practice suggestions
        suggestions.extend([
            "Try the 'Look, Say, Cover, Write, Check' method",
            "Practice spelling in different contexts (sentences, stories)",
            "Use spelling games and apps for reinforcement"
        ])
        
        return suggestions[:3]  # Return top 3 suggestions

# Global word analyzer instance
word_analyzer = WordAnalyzer()
