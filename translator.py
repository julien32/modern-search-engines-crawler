from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from langdetect import detect

class Trans: 
    
    def is_english(text):
        try:
            language = detect(text)
            return language == 'en'
        except:
            return False