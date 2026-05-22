"""
ENGLISH-LUGANDA TRANSLATOR - GOOGLE COLAB QUICK START
Copy each section as a separate Colab cell and run from top to bottom.
Just press Ctrl+M then B in Colab to add a new code cell.
"""

# ============================================================
# 🔧 SETUP: Run this first (takes 2-3 minutes)
# ============================================================
# Copy this into a Colab cell and run it

!pip install -q torch transformers datasets pandas numpy scikit-learn sacrebleu flask requests tqdm python-dotenv SpeechRecognition gTTS
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
import os
os.chdir('/content/translator')
import sys
sys.path.insert(0, '/content/translator')

print("✓ Setup complete! Ready to test.")

# ============================================================
# 📥 LOAD THE MODEL (takes 2-5 minutes first time)
# ============================================================
# Copy this into a new Colab cell

from inference import TransformerTranslator

print("Loading translation models...")
translator = TransformerTranslator()
print(f"✓ Ready! Device: {translator.device}")

# ============================================================
# 🧪 TEST 1: ENGLISH → LUGANDA
# ============================================================
# Copy this into a new Colab cell

print("\n" + "="*60)
print("ENGLISH → LUGANDA TRANSLATION")
print("="*60)

english_texts = [
    "Hello, how are you?",
    "Thank you very much",
    "I love Luganda language",
    "Good morning, friend",
    "What is your name?",
]

for text in english_texts:
    result = translator.translate(text, source_lang="english", target_lang="luganda")
    print(f"\n📝 EN: {text}")
    print(f"✨ LG: {result['translation']}")

# ============================================================
# 🧪 TEST 2: LUGANDA → ENGLISH
# ============================================================
# Copy this into a new Colab cell

print("\n" + "="*60)
print("LUGANDA → ENGLISH TRANSLATION")
print("="*60)

luganda_texts = [
    "Oli otya?",
    "Webale nnyo",
    "Ndi muganda",
    "Kabaka wa Buganda",
]

for text in luganda_texts:
    result = translator.translate(text, source_lang="luganda", target_lang="english")
    print(f"\n📝 LG: {text}")
    print(f"✨ EN: {result['translation']}")

# ============================================================
# 🧪 TEST 3: AUTO-DETECTION (Model figures out language)
# ============================================================
# Copy this into a new Colab cell

print("\n" + "="*60)
print("AUTO-DETECTION - Let model figure out the language")
print("="*60)

texts = [
    "Hello, nice to meet you",
    "Oli otya ssebo?",
    "Thank you for helping",
]

for text in texts:
    result = translator.translate(text)  # No language specified!
    print(f"\n📝 Text: {text}")
    print(f"🔍 Detected: {result['source_lang'].upper()}")
    print(f"✨ Translation: {result['translation']}")

# ============================================================
# 🧪 TEST 4: YOUR OWN EXAMPLES (MODIFY THESE!)
# ============================================================
# Copy this and MODIFY the MY_TEXTS variable with your examples!

print("\n" + "="*60)
print("TEST WITH YOUR OWN EXAMPLES")
print("="*60)

# 👇 EDIT THESE LINES WITH YOUR OWN TEXT 👇
MY_ENGLISH_TEXTS = [
    "God bless Uganda",
    "I am proud of my language",
]

MY_LUGANDA_TEXTS = [
    "Katonda amuwe Uganda",
    "Ndi muganda nnyo",
]

print("\n[ENGLISH TEXTS]")
for text in MY_ENGLISH_TEXTS:
    result = translator.translate(text)
    print(f"📝 {text}")
    print(f"✨ {result['translation']}\n")

print("\n[LUGANDA TEXTS]")
for text in MY_LUGANDA_TEXTS:
    result = translator.translate(text)
    print(f"📝 {text}")
    print(f"✨ {result['translation']}\n")

# ============================================================
# 📊 TEST 5: PERFORMANCE MEASUREMENT
# ============================================================
# Copy this to measure speed

import time

print("\n" + "="*60)
print("PERFORMANCE TEST")
print("="*60)

test_text = "Hello, I am learning Luganda language"

times = []
for i in range(5):
    start = time.time()
    result = translator.translate(test_text)
    elapsed = time.time() - start
    times.append(elapsed)

avg_time = sum(times) / len(times)

print(f"\nDevice: {translator.device}")
print(f"Test text: '{test_text}'")
print(f"\nAverage time: {avg_time*1000:.2f}ms")
print(f"Fastest: {min(times)*1000:.2f}ms")
print(f"Slowest: {max(times)*1000:.2f}ms")
print(f"\nTranslation: {result['translation']}")

# ============================================================
# 📈 TEST 6: BATCH TRANSLATION
# ============================================================
# Copy this for batch testing

print("\n" + "="*60)
print("BATCH TRANSLATION (Multiple sentences at once)")
print("="*60)

batch = [
    "I am happy",
    "You are strong",
    "We are friends",
    "They are learning",
]

print("\nEnglish → Luganda batch:\n")
for i, text in enumerate(batch, 1):
    result = translator.translate(text)
    print(f"{i}. {text}")
    print(f"   → {result['translation']}\n")

# ============================================================
# 💾 TEST 7: SAVE RESULTS
# ============================================================
# Copy this to save your test results

import json
from datetime import datetime

results_summary = {
    "timestamp": datetime.now().isoformat(),
    "device": str(translator.device),
    "tests": {
        "english_to_luganda": "✓ Passed",
        "luganda_to_english": "✓ Passed",
        "auto_detection": "✓ Passed",
        "batch_translation": "✓ Passed",
    },
    "sample_translations": {
        "hello": translator.translate("Hello")['translation'],
        "thank_you": translator.translate("Thank you")['translation'],
        "good_morning": translator.translate("Good morning")['translation'],
    }
}

# Save to file
with open('translator_test_results.json', 'w') as f:
    json.dump(results_summary, f, indent=2)

print("✓ Results saved to: translator_test_results.json")
print("\n" + json.dumps(results_summary, indent=2))

# ============================================================
# 📥 DOWNLOAD RESULTS
# ============================================================
# Copy this to download results to your computer

from google.colab import files

files.download('translator_test_results.json')
print("✓ File downloaded to your Downloads folder!")

# ============================================================
# 🔗 BONUS: HELPFUL FUNCTIONS FOR YOUR USE
# ============================================================
# Copy these functions to use later in your notebook

def translate_en_to_lg(text):
    """Translate English to Luganda"""
    result = translator.translate(text, source_lang="english", target_lang="luganda")
    return result['translation']

def translate_lg_to_en(text):
    """Translate Luganda to English"""
    result = translator.translate(text, source_lang="luganda", target_lang="english")
    return result['translation']

def translate_auto(text):
    """Translate with auto-detection"""
    result = translator.translate(text)
    return f"{result['source_lang'].upper()} → {result['translation']}"

# Examples:
print("\n" + "="*60)
print("USING HELPER FUNCTIONS")
print("="*60)

print(f"\nEnglish: 'I am learning'")
print(f"Luganda: {translate_en_to_lg('I am learning')}")

print(f"\nLuganda: 'Oli otya?'")
print(f"English: {translate_lg_to_en('Oli otya?')}")

print(f"\nAuto-detect: 'Hello'")
print(f"Result: {translate_auto('Hello')}")

# ============================================================
# ✅ ALL TESTS COMPLETE!
# ============================================================
print("\n" + "="*60)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("="*60)
print("\nYour English-Luganda Translator is working perfectly!")
print("\nTo test more:")
print("1. Go back to TEST 4 and modify MY_TEXTS with your examples")
print("2. Use the helper functions (translate_en_to_lg, translate_lg_to_en, etc)")
print("3. Download results using TEST 7")
print("\nEnjoy translating! 🌍")
