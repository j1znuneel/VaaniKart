from googletrans import Translator

def translate_to_english(text):
    translator = Translator()
    try:
        result = translator.translate(text, dest='en')
        print(f"📥 Original ({result.src}): {text}")
        print(f"📤 Translated: {result.text}\n")
        return result.text
    except Exception as e:
        print("❌ Translation Error:", e)
        return text

# 🧪 Test with sample inputs in Malayalam, Hindi, Tamil, Bengali
samples = [
    "ചക്ക ചിപ്‌സ്, വീട്ടിൽ ഉണ്ടാക്കിയത്, 250 ഗ്രാം, 80 രൂപ",  # Malayalam
    "आम का अचार, घर का बना, 500 ग्राम, ₹120",                # Hindi
    "தயிர், உள்ளூர் பண்ணையிலிருந்து, 1 லிட்டர், ₹40",          # Tamil
    "ঘৃত, বাড়িতে তৈরি, 250 গ্রাম, ১০০ টাকা",                   # Bengali
]

for sample in samples:
    translate_to_english(sample)
