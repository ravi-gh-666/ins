import configparser
import openai
import re

# Read OpenAI API key from config.ini
config = configparser.ConfigParser()
config.read('config.ini')
if 'openai' in config and 'api_key' in config['openai']:
    openai.api_key = config['openai']['api_key']
else:
    raise RuntimeError('OpenAI API key not found in config.ini')

# 1. Extract all user-facing strings from test_home.html
with open("templates/test_home.html", "r", encoding="utf-8") as f:
    html = f.read()

# Regex to find all text between >...< that is not a tag or variable
text_matches = re.findall(r">([^<{%}][^<]*)<", html)
# Remove whitespace and deduplicate
unique_texts = sorted(set([t.strip() for t in text_matches if t.strip()]))

# 2. Function to translate a list of strings

def batch_translate(texts, target_language):
    translations = {}
    client = openai.OpenAI(api_key=openai.api_key)
    for text in texts:
        prompt = (
            f"You are a professional translator. Translate the following website UI text to {target_language}. "
            f"Use natural, clear, and concise language suitable for a website. Do not transliterate. "
            f"If the text is a button, heading, or label, use the most natural equivalent. "
            f"If the text is a sentence, keep the meaning and tone.\n"
            f"Examples:\n"
            f"English: Go to Scorecard\nHindi: स्कोरकार्ड देखें\nKannada: ಸ್ಕೋರ್ಕಾರ್ಡ್ ನೋಡಿ\n"
            f"English: Compare Policies\nHindi: पॉलिसी तुलना करें\nKannada: ಪಾಲಿಸಿ ಹೋಲಿಸಿ\n"
            f"English: Best Health Insurance Plans in India 2025\nHindi: भारत में सर्वश्रेष्ठ स्वास्थ्य बीमा योजनाएँ 2025\nKannada: ಭಾರತದ ಅತ್ಯುತ್ತಮ ಆರೋಗ್ಯ ವಿಮಾ ಯೋಜನೆಗಳು 2025\n"
            f"\nText: {text}\nTranslation:"
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        translated = response.choices[0].message.content.strip()
        translations[text] = translated
        print(f"{target_language}: {text} => {translated}")
    return translations

# 3. Translate to Hindi and Kannada
print("Translating to Hindi...")
hi_translations = batch_translate(unique_texts, "Hindi")
print("Translating to Kannada...")
kn_translations = batch_translate(unique_texts, "Kannada")

# 4. Print the mapping (copy-paste into your JS or template)
print("\n# Hindi Translations")
for k, v in hi_translations.items():
    print(f'"{k}": "{v}",')

print("\n# Kannada Translations")
for k, v in kn_translations.items():
    print(f'"{k}": "{v}",')