from googletrans import Translator

translator = Translator()

def translate_to_english(text):
    try:
        result = translator.translate(text, dest='en')
        return result.text
    except Exception as e:
        print("Translation error:", e)
        return text  # Fallback to original
