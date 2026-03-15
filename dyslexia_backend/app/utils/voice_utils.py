import pyttsx3
import speech_recognition as sr
import tempfile
import os
import time
import random  # ADDED IMPORT

class VoiceUtils:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.recognizer = sr.Recognizer()
            
            # Configure voice properties
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)  # Female voice
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.8)
            
        except Exception as e:
            print(f"Voice utils initialization warning: {e}")
    
    def speak(self, text, slow=False, word_by_word=False):
        """AI speaks text with optional slow speed or word-by-word"""
        try:
            if slow:
                self.engine.setProperty('rate', 100)
            else:
                self.engine.setProperty('rate', 150)
            
            if word_by_word:
                words = text.split()
                for word in words:
                    self.engine.say(word)
                    self.engine.runAndWait()
                    time.sleep(0.3)  # Pause between words
            else:
                self.engine.say(text)
                self.engine.runAndWait()
                
        except Exception as e:
            print(f"Speech error: {e}")
    
    def speak_word_with_letters(self, word):
        """Spell out a word letter by letter"""
        try:
            self.engine.setProperty('rate', 120)
            self.engine.say(f"The word is {word}")
            self.engine.runAndWait()
            
            time.sleep(0.5)
            
            self.engine.say("Let me spell it for you")
            self.engine.runAndWait()
            
            for letter in word:
                self.engine.say(letter)
                self.engine.runAndWait()
                time.sleep(0.2)
                
            time.sleep(0.5)
            self.engine.say(f"Again, the word is {word}")
            self.engine.runAndWait()
            
        except Exception as e:
            print(f"Word spelling error: {e}")
    
    def speak_sentence_with_highlight(self, sentence, current_word=None):
        """Speak a sentence with emphasis on current word"""
        try:
            if current_word:
                self.engine.say(f"Let's focus on this word: {current_word}")
                self.engine.runAndWait()
                time.sleep(0.5)
                
                self.engine.say(f"In the sentence: {sentence}")
                self.engine.runAndWait()
            else:
                self.engine.say(sentence)
                self.engine.runAndWait()
                
        except Exception as e:
            print(f"Sentence speaking error: {e}")
    
    def get_encouragement(self):
        """Get random encouragement message"""
        encouragements = [
            "Excellent work! You're doing amazing!",
            "Fantastic job! Keep it up!",
            "Wonderful! You're learning so fast!",
            "Perfect! You're a star student!",
            "Amazing! You're getting better every day!",
            "Brilliant! I'm so proud of you!",
            "Outstanding! You're a quick learner!",
            "Superb! You're mastering this!",
            "Terrific! You're doing great!",
            "Magnificent! Keep up the good work!"
        ]
        return random.choice(encouragements)
    
    def get_help_message(self, module, difficulty):
        """Get context-specific help message"""
        help_messages = {
            'math': {
                'easy': "Let me help you! Try counting on your fingers.",
                'medium': "Think step by step. Break it down into smaller parts.",
                'hard': "This is challenging! Let's work through it together."
            },
            'spelling': {
                'easy': "Sound it out slowly. What sounds do you hear?",
                'medium': "Try breaking the word into syllables.",
                'hard': "This is a tricky word! Let me spell it for you."
            },
            'reading': {
                'easy': "Listen carefully and try to repeat after me.",
                'medium': "Read it slowly, one word at a time.",
                'hard': "Let's break this down into smaller parts and practice."
            }
        }
        return help_messages[module][difficulty]    

# Global voice utils instance
voice_utils = VoiceUtils()
