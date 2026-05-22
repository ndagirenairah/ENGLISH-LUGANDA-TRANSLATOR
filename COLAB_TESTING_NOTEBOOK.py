# English-Luganda Translator - Complete Colab Testing Notebook
# Copy all cells below into your Google Colab notebook

# ============================================================
# CELL 1: Install Dependencies (Run First!)
# ============================================================
!pip install -q torch transformers datasets pandas numpy scikit-learn sacrebleu flask requests tqdm python-dotenv SpeechRecognition gTTS

# ============================================================
# CELL 2: Clone Repository from GitHub
# ============================================================
import os
from pathlib import Path

# Clone the project
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
os.chdir('/content/translator')

print("✓ Repository cloned successfully")
print(f"Current directory: {os.getcwd()}")

# ============================================================
# CELL 3: Verify Setup
# ============================================================
import sys
sys.path.insert(0, '/content/translator')

from pathlib import Path

# Check all critical files exist
critical_files = [
    'inference.py',
    'app.py',
    'train.py',
    'evaluate.py',
    'preprocess.py',
    'requirements.txt',
    'README.md'
]

print("[SETUP VERIFICATION]")
print("=" * 60)

all_good = True
for file in critical_files:
    if Path(file).exists():
        print(f"✓ {file}")
    else:
        print(f"✗ {file} - MISSING")
        all_good = False

print("=" * 60)
if all_good:
    print("✓ All files verified!")
else:
    print("✗ Some files missing!")

# ============================================================
# CELL 4: Load Inference Module
# ============================================================
from inference import TransformerTranslator

print("[LOADING TRANSLATION MODELS]")
print("This will download ~600MB from Hugging Face Hub...")
print("This takes 2-5 minutes on first run...")
print("=" * 60)

translator = TransformerTranslator()

print("✓ Models loaded successfully!")
print(f"✓ Device: {translator.device}")
print(f"✓ Available directions: {list(translator.models.keys())}")

# ============================================================
# CELL 5: Test Language Detection
# ============================================================
print("[LANGUAGE DETECTION TEST]")
print("=" * 60)

test_cases = [
    ("Hello, how are you?", "english"),
    ("Oli otya?", "luganda"),
    ("Thank you very much", "english"),
    ("Webale nnyo", "luganda"),
]

for text, expected in test_cases:
    detected = translator.detect_language(text)
    status = "✓" if detected == expected else "✗"
    print(f"{status} '{text}' -> {detected}")

# ============================================================
# CELL 6: English to Luganda Translation
# ============================================================
print("[ENGLISH → LUGANDA TRANSLATION]")
print("=" * 60)

english_samples = [
    "Hello, how are you?",
    "Thank you very much",
    "I love Luganda language",
    "Good morning",
    "What is your name?",
    "The weather is beautiful today",
    "I am learning Luganda",
]

results = []
for text in english_samples:
    result = translator.translate(text, source_lang="english", target_lang="luganda")
    print(f"\n✓ EN: {text}")
    print(f"  LG: {result['translation']}")
    results.append(result)

# ============================================================
# CELL 7: Luganda to English Translation
# ============================================================
print("[LUGANDA → ENGLISH TRANSLATION]")
print("=" * 60)

luganda_samples = [
    "Oli otya?",
    "Webale nnyo",
    "Ndi muganda",
    "Kabaka wa Buganda",
    "Abantu bammwe",
]

results_lg = []
for text in luganda_samples:
    result = translator.translate(text, source_lang="luganda", target_lang="english")
    print(f"\n✓ LG: {text}")
    print(f"  EN: {result['translation']}")
    results_lg.append(result)

# ============================================================
# CELL 8: Auto-Detection (Smart Direction)
# ============================================================
print("[AUTO-DETECTION TEST - Let Model Detect Language]")
print("=" * 60)

auto_samples = [
    "Hello world",
    "Oli otya?",
    "Good afternoon",
    "Webale",
]

for text in auto_samples:
    result = translator.translate(text)
    print(f"\n✓ Text: '{text}'")
    print(f"  Detected: {result['source_lang']}")
    print(f"  Direction: {result['direction']}")
    print(f"  Translation: {result['translation']}")

# ============================================================
# CELL 9: Batch Translation
# ============================================================
print("[BATCH TRANSLATION TEST]")
print("=" * 60)

sentences = [
    "I am happy",
    "You are strong",
    "We are brothers",
    "They are sisters",
]

print("Translating batch of English sentences to Luganda:")
for i, sentence in enumerate(sentences, 1):
    result = translator.translate(sentence)
    print(f"{i}. {sentence} -> {result['translation']}")

# ============================================================
# CELL 10: Performance Metrics
# ============================================================
import time
import torch

print("[PERFORMANCE METRICS]")
print("=" * 60)

# Measure inference time
test_text = "Hello, I am learning Luganda language"
device_info = f"Device: {translator.device}"
print(device_info)

times = []
for i in range(5):
    start = time.time()
    result = translator.translate(test_text)
    elapsed = time.time() - start
    times.append(elapsed)

avg_time = sum(times) / len(times)
print(f"✓ Text: '{test_text}'")
print(f"✓ Average inference time: {avg_time*1000:.2f}ms")
print(f"✓ Min: {min(times)*1000:.2f}ms, Max: {max(times)*1000:.2f}ms")
print(f"✓ Translation: {result['translation']}")

# ============================================================
# CELL 11: Create Interactive Test Function
# ============================================================
def translate_text(text, source_lang=None):
    """
    Easy-to-use translation function
    
    Args:
        text (str): Text to translate
        source_lang (str): "english" or "luganda" or None for auto-detect
    
    Returns:
        dict: Translation result
    """
    result = translator.translate(text, source_lang=source_lang)
    return result

# Test the function
print("[INTERACTIVE TRANSLATION FUNCTION]")
print("=" * 60)

# Test 1
result1 = translate_text("I love programming")
print(f"EN: I love programming")
print(f"LG: {result1['translation']}\n")

# Test 2
result2 = translate_text("Ndi Muganda nnyo")
print(f"LG: Ndi Muganda nnyo")
print(f"EN: {result2['translation']}\n")

# Test 3 (auto-detect)
result3 = translate_text("How is your family?")
print(f"Text: How is your family?")
print(f"Auto-detected source: {result3['source_lang']}")
print(f"Translation: {result3['translation']}")

# ============================================================
# CELL 12: Custom Translation Examples
# ============================================================
print("[CUSTOM EXAMPLES - Try Your Own!]")
print("=" * 60)
print("\nModify the text below and run to test:\n")

# CUSTOMIZE THESE:
custom_english = "God bless Uganda"
custom_luganda = "Katonda amuwe Uganda"

result_en = translate_text(custom_english)
result_lg = translate_text(custom_luganda)

print(f"English: {custom_english}")
print(f"  → Luganda: {result_en['translation']}\n")

print(f"Luganda: {custom_luganda}")
print(f"  → English: {result_lg['translation']}")

# ============================================================
# CELL 13: Load Evaluation Data
# ============================================================
import pandas as pd

print("[EVALUATE ON TEST DATA]")
print("=" * 60)

# Load test dataset
test_data = pd.read_csv('data/processed/test.csv')
print(f"✓ Loaded {len(test_data)} test samples")
print(f"\nFirst 5 test samples:")
print(test_data.head())

# ============================================================
# CELL 14: Quick Evaluation
# ============================================================
print("[QUICK EVALUATION ON TEST SET]")
print("=" * 60)

# Take first 10 samples
sample_size = min(10, len(test_data))
test_sample = test_data.head(sample_size)

print(f"\nTranslating {sample_size} test samples:\n")

for idx, (_, row) in enumerate(test_sample.iterrows(), 1):
    en_text = str(row.get('english', row.get('en', 'N/A')))
    result = translator.translate(en_text)
    print(f"{idx}. EN: {en_text[:50]}...")
    print(f"   LG: {result['translation']}")
    print()

# ============================================================
# CELL 15: Save Test Results
# ============================================================
import json
from datetime import datetime

print("[SAVING TEST RESULTS]")
print("=" * 60)

test_results = {
    "timestamp": datetime.now().isoformat(),
    "device": str(translator.device),
    "test_samples": 10,
    "sample_translations": [
        {
            "english": "Hello, how are you?",
            "luganda": results[0]['translation'] if results else "N/A"
        },
        {
            "english": "Thank you very much",
            "luganda": results[1]['translation'] if len(results) > 1 else "N/A"
        }
    ]
}

with open('colab_test_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)

print("✓ Test results saved to colab_test_results.json")
print(json.dumps(test_results, indent=2))

# ============================================================
# CELL 16: Download Results
# ============================================================
from google.colab import files

print("[DOWNLOAD TEST RESULTS]")
print("=" * 60)

# Download the test results file
files.download('colab_test_results.json')

print("\n✓ colab_test_results.json downloaded to your computer")
print("\nTo access and keep your results:")
print("1. The file is now saved in your Downloads folder")
print("2. You can also mount Google Drive to save there")

# ============================================================
# CELL 17: Mount Google Drive (Optional)
# ============================================================
# from google.colab import drive
# 
# drive.mount('/content/drive')
# print("✓ Google Drive mounted at /content/drive")
# print("You can now save files to your Drive!")

print("\nColab Testing Setup Complete!")
print("=" * 60)
print("Next Steps:")
print("1. Run each cell from top to bottom")
print("2. Wait for model download on first run (2-5 min)")
print("3. Test translations with your own examples")
print("4. Download results to your computer")
print("\nFeel free to modify CELL 12 with your own English/Luganda text!")
