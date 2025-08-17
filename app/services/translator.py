# app/services/translator.py
from app.locales import en, ru, uz

# A dictionary to hold all our language packs
translations = {
    'en': en.lexicon,
    'ru': ru.lexicon,
    'uz': uz.lexicon,
}

# Default to Uzbek if a language or key is not found
DEFAULT_LANG = 'uz'

def get_text(key: str, lang: str = DEFAULT_LANG) -> str:
    """
    Retrieves a translated text string for a given key and language.
    Falls back to the default language if the key is not found in the target language.
    """
    if lang not in translations:
        lang = DEFAULT_LANG
    
    # Get the text, falling back to the default language's version of the key
    return translations.get(lang, translations[DEFAULT_LANG]).get(key, translations[DEFAULT_LANG].get(key, f"_{key}_"))