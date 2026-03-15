import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_folder='app/data/datasets'):
        self.data_folder = data_folder
    
    def load_math_data(self):
        """Load math questions dataset from Excel with correct column mapping"""
        try:
            file_path = os.path.join(self.data_folder, 'math1.xlsx')
            if not os.path.exists(file_path):
                logger.error(f"Math data file not found: {file_path}")
                return []
                
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = df.columns.str.strip().str.lower()  # Normalize column names
            
            logger.info(f"✅ Loaded math data: {len(df)} records")
            print(f"Math columns: {df.columns.tolist()}")
            
            math_data = []
            for _, row in df.iterrows():
                # Handle category conversion safely
                category = str(row['category']).lower() if 'category' in row and pd.notna(row['category']) else 'easy'
                
                math_data.append({
                    'id': int(row['id']) if 'id' in row and pd.notna(row['id']) else len(math_data) + 1,
                    'question': str(row['question']) if 'question' in row and pd.notna(row['question']) else '',
                    'answer': str(row['answer']) if 'answer' in row and pd.notna(row['answer']) else '',
                    'category': category,
                    'explanation': str(row['explanation']) if 'explanation' in row and pd.notna(row['explanation']) else 'No explanation available'
                })
            return self._validate_dataset(math_data, "Math")
        except Exception as e:
            logger.error(f"Error loading math data: {e}")
            print(f"❌ Math data loading error: {e}")
            return []
    
    def load_spelling_words(self):
        """Load complete spelling words dataset from Excel - for COMPLETE WORDS mode"""
        try:
            file_path = os.path.join(self.data_folder, 'word_dataset1.xlsx')
            if not os.path.exists(file_path):
                logger.error(f"Spelling words file not found: {file_path}")
                return []
                
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = df.columns.str.strip().str.lower()  # Normalize column names
            
            logger.info(f"✅ Loaded spelling words: {len(df)} records")
            print(f"Spelling words columns: {df.columns.tolist()}")
            
            spelling_data = []
            for _, row in df.iterrows():
                spelling_data.append({
                    'id': int(row['id']) if 'id' in row and pd.notna(row['id']) else len(spelling_data) + 1,
                    'word': str(row['word']) if 'word' in row and pd.notna(row['word']) else '',
                    'meaning': "Word for spelling practice",
                    'category': self._map_level_to_category(row['level'] if 'level' in row else 'easy')
                })
            return self._validate_dataset(spelling_data, "Spelling Words")
        except Exception as e:
            logger.error(f"Error loading spelling words: {e}")
            print(f"❌ Spelling words loading error: {e}")
            return []
    
    def load_spelling_quiz(self):
        """Load spelling quiz dataset (missing letters) from Excel - for MISSING LETTERS mode"""
        try:
            file_path = os.path.join(self.data_folder, 'word_quiz1.xlsx')
            if not os.path.exists(file_path):
                logger.error(f"Spelling quiz file not found: {file_path}")
                return []
                
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = df.columns.str.strip().str.lower()  # Normalize column names
            
            logger.info(f"✅ Loaded spelling quiz: {len(df)} records")
            print(f"Spelling quiz columns: {df.columns.tolist()}")
            
            quiz_data = []
            valid_count = 0
            skipped_count = 0
            
            for _, row in df.iterrows():
                # Skip rows with missing critical data
                if (pd.isna(row.get('word_pattern')) or 
                    pd.isna(row.get('missing_letters')) or 
                    pd.isna(row.get('answer'))):
                    skipped_count += 1
                    continue
                    
                word_pattern = str(row['word_pattern']).strip() if 'word_pattern' in row and pd.notna(row['word_pattern']) else ''
                missing_letter = str(row['missing_letters']).strip() if 'missing_letters' in row and pd.notna(row['missing_letters']) else ''
                
                # FIX: Clean the missing_letter - remove any extra spaces or special characters
                missing_letter = missing_letter.replace(' ', '').lower()
                
                # If missing_letters is empty or invalid, extract from answer column
                if not missing_letter or len(missing_letter) != 1:
                    answer_from_excel = str(row['answer']).strip() if 'answer' in row and pd.notna(row['answer']) else ''
                    missing_letter = self._extract_missing_letter(word_pattern, answer_from_excel)
                
                # Skip if we still don't have a valid single letter
                if not missing_letter or len(missing_letter) != 1:
                    skipped_count += 1
                    continue
                
                complete_word = self._get_complete_word(word_pattern, missing_letter)
                
                # FIX: Convert ID to integer properly
                try:
                    question_id = int(float(row['id'])) if 'id' in row and pd.notna(row['id']) else len(quiz_data) + 1
                except (ValueError, TypeError):
                    question_id = len(quiz_data) + 1
                
                quiz_data.append({
                    'id': question_id,
                    'question': word_pattern,
                    'answer': missing_letter,  # This is the MISSING LETTER that user should enter
                    'complete_word': complete_word,  # The full word for reference
                    'meaning': "Complete the word",
                    'category': self._map_level_to_category(row['level'] if 'level' in row else 'easy')
                })
                valid_count += 1
            
            print(f"✅ Processed {valid_count} valid spelling quiz items (skipped {skipped_count} invalid rows)")
            return self._validate_dataset(quiz_data, "Spelling Quiz")
        except Exception as e:
            logger.error(f"Error loading spelling quiz: {e}")
            print(f"❌ Spelling quiz loading error: {e}")
            return []
    
    def _extract_missing_letter(self, word_pattern, answer_from_excel):
        """Extract the missing letter from word pattern and answer (fallback)"""
        if not word_pattern or not answer_from_excel:
            return ""
        
        # If answer_from_excel is already a single letter, use it
        if len(answer_from_excel.strip()) == 1:
            return answer_from_excel.strip().lower()
        
        # If answer_from_excel is the complete word, find what letter replaces the underscore
        complete_word = answer_from_excel.replace(' ', '').lower()
        pattern_without_spaces = word_pattern.replace(' ', '').lower()
        
        # Find the position of underscore in pattern
        underscore_pos = pattern_without_spaces.find('_')
        if underscore_pos != -1 and underscore_pos < len(complete_word):
            return complete_word[underscore_pos]
        
        return ""
    
    def _get_complete_word(self, word_pattern, missing_letter):
        """Convert word pattern with missing letters to complete word"""
        if not word_pattern or not missing_letter:
            return ""
        
        # Replace underscore with missing letter and remove spaces
        complete_word = word_pattern.replace('_', missing_letter).replace(' ', '')
        return complete_word
    
    def load_reading_sentences(self):
        """Load reading sentences dataset from Excel"""
        try:
            file_path = os.path.join(self.data_folder, 'sentences1.xlsx')
            if not os.path.exists(file_path):
                logger.error(f"Sentences file not found: {file_path}")
                return []
                
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = df.columns.str.strip().str.lower()  # Normalize column names
            
            logger.info(f"✅ Loaded reading sentences: {len(df)} records")
            print(f"Sentences columns: {df.columns.tolist()}")
            
            sentences_data = []
            for _, row in df.iterrows():
                sentences_data.append({
                    'id': int(row['id']) if 'id' in row and pd.notna(row['id']) else len(sentences_data) + 1,
                    'sentence': str(row['sentence']) if 'sentence' in row and pd.notna(row['sentence']) else '',
                    'category': self._map_level_to_category(row['level'] if 'level' in row else 'easy')
                })
            return self._validate_dataset(sentences_data, "Reading Sentences")
        except Exception as e:
            logger.error(f"Error loading reading sentences: {e}")
            print(f"❌ Sentences loading error: {e}")
            return []
    
    def load_reading_paragraphs(self):
        """Load reading paragraphs dataset from Excel"""
        try:
            file_path = os.path.join(self.data_folder, 'paragraphs1.xlsx')
            if not os.path.exists(file_path):
                logger.error(f"Paragraphs file not found: {file_path}")
                return []
                
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = df.columns.str.strip().str.lower()  # Normalize column names
            
            logger.info(f"✅ Loaded reading paragraphs: {len(df)} records")
            print(f"Paragraphs columns: {df.columns.tolist()}")
            
            paragraphs_data = []
            for _, row in df.iterrows():
                paragraphs_data.append({
                    'id': int(row['id']) if 'id' in row and pd.notna(row['id']) else len(paragraphs_data) + 1,
                    'paragraph': str(row['paragraph']) if 'paragraph' in row and pd.notna(row['paragraph']) else '',
                    'category': self._map_level_to_category(row['level'] if 'level' in row else 'easy')
                })
            return self._validate_dataset(paragraphs_data, "Reading Paragraphs")
        except Exception as e:
            logger.error(f"Error loading reading paragraphs: {e}")
            print(f"❌ Paragraphs loading error: {e}")
            return []
    
    def _map_level_to_category(self, level):
        """Map your level system to the expected category system"""
        if pd.isna(level):
            return 'easy'
            
        level_str = str(level).lower()
        if 'easy' in level_str or level == 1:
            return 'easy'
        elif 'medium' in level_str or level == 2:
            return 'medium'
        elif 'hard' in level_str or 'difficult' in level_str or level == 3:
            return 'difficult'
        else:
            return 'easy'
    
    def _validate_dataset(self, data, dataset_name):
        """Ensure dataset is not empty"""
        if not data or len(data) == 0:
            logger.error(f"❌ {dataset_name} dataset is EMPTY")
            print(f"⚠️ {dataset_name} dataset is empty. Upload valid Excel data.")
            return []  # MUST return list to avoid breaking services
        
        return data

# Global data loader instance
data_loader = DataLoader()
