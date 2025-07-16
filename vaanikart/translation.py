from googletrans import Translator

translator = Translator()

def translate_text(text, lang_code):
    if lang_code == "en":
        return text  # No need to translate
    try:
        translated = translator.translate(text, dest=lang_code)
        return translated.text
    except Exception as e:
        print(f"Translation error for '{text}':", e)
        return text  # Fallback
