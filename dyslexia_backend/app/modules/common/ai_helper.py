class AIHelper:
    def __init__(self):
        self.encouragement_messages = [
            "Great job! You're doing amazing!",
            "Well done! Keep up the good work!",
            "Excellent! You're learning so fast!",
            "Fantastic! You're a star learner!",
            "Awesome work! You're getting better every day!"
        ]
        
        self.help_messages = {
            'math': {
                'easy': "Let me help you! Try counting on your fingers.",
                'medium': "Think step by step. You can do this!",
                'hard': "This is challenging! Break it down into smaller parts."
            },
            'spelling': {
                'easy': "Sound it out slowly. What sounds do you hear?",
                'medium': "Try breaking the word into syllables.",
                'hard': "This is a tricky word! Let's practice it together."
            },
            'reading': {
                'easy': "Listen carefully and try to repeat after me.",
                'medium': "Read it slowly, one word at a time.",
                'hard': "Let's break this down into smaller parts."
            }
        }
    
    def get_encouragement(self):
        """Get random encouragement message"""
        import random
        return random.choice(self.encouragement_messages)
    
    def get_help_message(self, module, difficulty, stress_level=0.5):
        """Get context-specific help message based on stress"""
        base_message = self.help_messages[module][difficulty]
        
        if stress_level > 0.7:
            return f"Don't worry! {base_message} Take your time."
        elif stress_level > 0.5:
            return f"You're doing great! {base_message}"
        else:
            return base_message
    
    def get_spelling_help(self, word, attempt_count):
        """Get spelling-specific help"""
        if attempt_count == 1:
            return f"Let me spell it for you: {' '.join(list(word.upper()))}"
        elif attempt_count == 2:
            return f"Try sounding it out: {self._get_phonetic_help(word)}"
        else:
            return f"The word is '{word}'. Let's try another one!"
    
    def get_reading_help(self, text, mode, attempt_count):
        """Get reading-specific help"""
        if attempt_count == 1:
            return f"Listen carefully: {text}"
        elif attempt_count == 2:
            if mode in ['sentences', 'paragraphs']:
                words = text.split()
                return f"Let's go word by word: {'... '.join(words)}"
            else:
                return f"Say it slowly: {text}"
        else:
            return f"Let me show you: {text}"
    
    def _get_phonetic_help(self, word):
        """Generate phonetic help for spelling"""
        vowels = 'aeiou'
        help_text = []
        for char in word:
            if char in vowels:
                help_text.append(f"{char}(vowel)")
            else:
                help_text.append(f"{char}(consonant)")
        return ' '.join(help_text)
    
    def generate_stuck_message(self, module):
        """Generate message when user is stuck"""
        messages = {
            'math': "I see this is challenging. Let me give you an easier question... Don't worry!",
            'spelling': "This word seems tricky. Let's try an easier one together!",
            'reading': "Let's practice with something simpler. You're doing great!"
        }
        return messages.get(module, "Let me help you with this!")

# Global AI helper instance
ai_helper = AIHelper()