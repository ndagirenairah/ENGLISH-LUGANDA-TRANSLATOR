# Testing English-Luganda Translator in Google Colab - Complete Guide

## Overview
This guide shows you how to quickly test the English-Luganda Translator model in Google Colab with step-by-step instructions.

---

## Quick Start (5 Minutes)

### Step 1: Create New Colab Notebook
1. Go to [Google Colab](https://colab.research.google.com)
2. Click "New notebook"

### Step 2: Copy-Paste the Cells

In your new Colab notebook, create cells by pressing `Ctrl+M` then `B` (or click `+ Code`)

Copy each section below into a separate cell and run them in order:

---

## Cell 1: Install Dependencies

```python
!pip install -q torch transformers datasets pandas numpy scikit-learn sacrebleu flask requests tqdm python-dotenv SpeechRecognition gTTS
```

**What it does:** Installs all required packages
**Expected time:** 2-3 minutes
**When done:** You'll see ✓ without errors

---

## Cell 2: Clone Repository

```python
import os
from pathlib import Path

!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
os.chdir('/content/translator')

print("✓ Repository cloned successfully")
print(f"Current directory: {os.getcwd()}")
```

**What it does:** Downloads your project from GitHub
**Expected time:** 30 seconds
**When done:** Shows current directory path

---

## Cell 3: Verify Files

```python
import sys
sys.path.insert(0, '/content/translator')
from pathlib import Path

critical_files = [
    'inference.py', 'app.py', 'train.py',
    'evaluate.py', 'preprocess.py', 'requirements.txt'
]

print("[SETUP VERIFICATION]")
print("=" * 60)

for file in critical_files:
    status = "✓" if Path(file).exists() else "✗"
    print(f"{status} {file}")
```

**What it does:** Verifies all project files are present
**When done:** All files should show ✓

---

## Cell 4: Load Translation Models

```python
from inference import TransformerTranslator

print("[LOADING TRANSLATION MODELS]")
print("This downloads ~600MB from Hugging Face...")
print("=" * 60)

translator = TransformerTranslator()

print("✓ Models loaded successfully!")
print(f"✓ Device: {translator.device}")
print(f"✓ Available: {list(translator.models.keys())}")
```

**What it does:** Initializes the translation models
**Expected time:** 2-5 minutes (first time only)
**When done:** Shows device type and available models
**Note:** This is the slowest step. Be patient!

---

## Cell 5: Test English → Luganda

```python
print("[ENGLISH → LUGANDA TRANSLATION]")
print("=" * 60)

samples = [
    "Hello, how are you?",
    "Thank you very much",
    "I love Luganda language",
    "Good morning",
]

for text in samples:
    result = translator.translate(text, source_lang="english", target_lang="luganda")
    print(f"EN: {text}")
    print(f"LG: {result['translation']}\n")
```

**What it does:** Translates English sentences to Luganda
**Expected time:** 10-20 seconds
**When done:** See translations below each English sentence

---

## Cell 6: Test Luganda → English

```python
print("[LUGANDA → ENGLISH TRANSLATION]")
print("=" * 60)

samples = [
    "Oli otya?",
    "Webale nnyo",
    "Ndi muganda",
]

for text in samples:
    result = translator.translate(text, source_lang="luganda", target_lang="english")
    print(f"LG: {text}")
    print(f"EN: {result['translation']}\n")
```

**What it does:** Translates Luganda sentences to English
**When done:** See English translations

---

## Cell 7: Auto-Detection (Smart Test)

```python
print("[AUTO-DETECTION - Model Detects Language]")
print("=" * 60)

samples = [
    "Hello world",
    "Oli otya?",
    "Good afternoon",
]

for text in samples:
    result = translator.translate(text)  # No language specified!
    print(f"Text: '{text}'")
    print(f"Detected: {result['source_lang']}")
    print(f"Direction: {result['direction']}")
    print(f"Translation: {result['translation']}\n")
```

**What it does:** Model automatically detects which language is being used
**When done:** Shows detected language and translation

---

## Cell 8: Create Translation Function

```python
def translate_text(text, source_lang=None):
    """Easy translation function"""
    result = translator.translate(text, source_lang=source_lang)
    return result

# Test it
print("[INTERACTIVE TESTING]")
print("=" * 60)

# Try your own examples:
result1 = translate_text("I am happy")
print(f"EN: I am happy")
print(f"LG: {result1['translation']}")
```

**What it does:** Creates a simple function for easy translation
**Usage:** Modify `text` parameter to test anything you want

---

## Cell 9: Test with Your Own Examples

```python
# 👇 MODIFY THESE LINES WITH YOUR OWN TEXT 👇

my_english = "God bless Uganda"
my_luganda = "Katonda amuwe Uganda"

result1 = translate_text(my_english)
result2 = translate_text(my_luganda)

print(f"English: {my_english}")
print(f"  → {result1['translation']}\n")

print(f"Luganda: {my_luganda}")
print(f"  → {result2['translation']}")
```

**What it does:** Tests your custom English and Luganda text
**How to use:** 
1. Edit `my_english` with any English text
2. Edit `my_luganda` with any Luganda text
3. Run the cell to see translations

---

## Cell 10: Load Test Data

```python
import pandas as pd

print("[LOAD TEST DATA]")
print("=" * 60)

test_data = pd.read_csv('data/processed/test.csv')
print(f"✓ Loaded {len(test_data)} test samples")
print("\nFirst 5 samples:")
print(test_data.head())
```

**What it does:** Loads the test dataset
**When done:** Shows the first 5 test samples

---

## Cell 11: Evaluate on Test Set

```python
print("[QUICK EVALUATION]")
print("=" * 60)

sample_size = min(10, len(test_data))
test_sample = test_data.head(sample_size)

print(f"Translating {sample_size} test samples:\n")

for idx, (_, row) in enumerate(test_sample.iterrows(), 1):
    en_text = str(row.get('english', row.get('en', 'N/A')))
    result = translator.translate(en_text)
    print(f"{idx}. EN: {en_text[:60]}...")
    print(f"   LG: {result['translation']}\n")
```

**What it does:** Tests model on real test data
**When done:** Shows 10 sample translations

---

## Cell 12: Performance Measurement

```python
import time

print("[PERFORMANCE METRICS]")
print("=" * 60)

test_text = "Hello, I am learning Luganda language"
print(f"Device: {translator.device}")
print(f"Text: '{test_text}'\n")

times = []
for i in range(5):
    start = time.time()
    result = translator.translate(test_text)
    elapsed = time.time() - start
    times.append(elapsed)

avg_time = sum(times) / len(times)
print(f"Average time: {avg_time*1000:.2f}ms")
print(f"Min: {min(times)*1000:.2f}ms")
print(f"Max: {max(times)*1000:.2f}ms")
print(f"\nTranslation: {result['translation']}")
```

**What it does:** Measures how fast the model translates
**Shows:** Average time in milliseconds

---

## Cell 13: Save Results

```python
import json
from datetime import datetime

test_results = {
    "timestamp": datetime.now().isoformat(),
    "device": str(translator.device),
    "test_samples": 10,
    "translations": {
        "hello": translate_text("Hello")['translation'],
        "thank_you": translate_text("Thank you")['translation'],
    }
}

with open('test_results.json', 'w') as f:
    json.dump(test_results, f, indent=2)

print("✓ Results saved!")
print(json.dumps(test_results, indent=2))
```

**What it does:** Saves test results to a JSON file

---

## Cell 14: Download Results

```python
from google.colab import files

files.download('test_results.json')
print("✓ File downloaded to your computer!")
```

**What it does:** Downloads results to your computer
**When done:** Check your Downloads folder

---

## Common Issues & Solutions

### Issue 1: Model Download Hangs
**Solution:** This is normal. The model is ~600MB. Wait 5+ minutes. Watch the progress bar.

### Issue 2: CUDA Out of Memory
**Solution:** The model will automatically use CPU, which is slower but works fine.

### Issue 3: "No module named 'torch'"
**Solution:** Re-run Cell 1 (dependency installation).

### Issue 4: "File not found" error
**Solution:** Make sure you ran Cell 2 (clone repository).

### Issue 5: Translation is gibberish
**Solution:** This happens sometimes. Try a different sentence or wait for model fine-tuning.

---

## Quick Reference

### Test English to Luganda:
```python
result = translator.translate("Hello", source_lang="english", target_lang="luganda")
print(result['translation'])
```

### Test Luganda to English:
```python
result = translator.translate("Oli otya?", source_lang="luganda", target_lang="english")
print(result['translation'])
```

### Auto-detect language:
```python
result = translator.translate("Hello world")  # Model figures out the language
print(f"Detected: {result['source_lang']}, Translation: {result['translation']}")
```

### Batch translation:
```python
texts = ["Hello", "Thank you", "Good morning"]
for text in texts:
    result = translator.translate(text)
    print(f"{text} → {result['translation']}")
```

---

## File Locations

Inside Colab, your files are at:
- Code: `/content/translator/`
- Models cache: `/root/.cache/huggingface/hub/`
- Test data: `/content/translator/data/processed/test.csv`

---

## Next Steps

1. ✓ Run all cells above to verify everything works
2. Test with your own English/Luganda text (Cell 9)
3. Check translation quality on test data (Cell 11)
4. Save and download results (Cells 13-14)
5. Share results with team members

---

## Performance Expectations

| Metric | Expected |
|--------|----------|
| First load time | 3-5 minutes |
| Per-translation time | 100-500ms |
| Model size | ~600MB download |
| Memory needed | 4-8GB RAM |
| Device | GPU (faster) or CPU (slower but works) |

---

## Advanced: Custom Fine-tuning

If you want to fine-tune the model with your own data:

```python
# Coming soon - see train.py in your repository
!python train.py --epochs 5 --batch_size 16
```

---

## Questions?

- Check: [GitHub Repository](https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR)
- See: `/content/translator/README.md`
- Review: `/content/translator/docs/ML_PIPELINE_GUIDE.md`

---

**Happy Translating! 🌍**
