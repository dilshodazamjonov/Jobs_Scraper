from deep_translator import GoogleTranslator
import re

# Function to preprocess and translate text
def translate_to_english(text):
    try:
        # Allow commas in the cleaned text
        cleaned_text = re.sub(r'[^\w\s가-힣,]', '', text)  # Keeps commas
        # Translate the cleaned text
        translated = GoogleTranslator(source='auto', target='en').translate(cleaned_text).strip('"')
        return translated if translated.strip() else text
    except Exception as e:
        print(f"Error during translation: {e}")
        return text  # Return original text in case of any error

# Function to translate a list of texts
def translate_list(text_list):
    return [translate_to_english(text) for text in text_list]

# Test case
texts = ["(주)오래", "개발자", "서울, 경기도"]
translated_texts = translate_list(texts)
print(translated_texts)  # Should translate the list correctly, preserving commas
