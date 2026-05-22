# 🔍 Google Colab Testing - Quick Reference

## Which File Should I Use?

### Option 1: **COLAB_COPY_PASTE_READY.py** ✨ BEST FOR QUICK TESTING
- **Use this if:** You want to start testing RIGHT NOW
- **How:** Copy each section into separate Colab cells
- **Time:** 30 minutes total
- **Best for:** Quick validation and testing

**👉 START HERE IF YOU'RE IN A HURRY**

### Option 2: **COLAB_TESTING_GUIDE.md** 📖 BEST FOR DETAILED LEARNING
- **Use this if:** You want to understand what each step does
- **How:** Read the guide, then copy-paste code sections
- **Time:** 1 hour
- **Best for:** Learning and understanding the model

### Option 3: **COLAB_TESTING_NOTEBOOK.py** 🎓 MOST COMPREHENSIVE
- **Use this if:** You want the complete testing suite
- **How:** Copy all cells, or use as reference
- **Time:** 1.5 hours
- **Best for:** Full evaluation and metrics

---

## ⚡ Fastest Way to Test (5 Minutes)

1. **Open Google Colab:** https://colab.research.google.com
2. **Click:** New notebook
3. **Copy these 5 cells from COLAB_COPY_PASTE_READY.py:**
   - SETUP (runs dependencies)
   - LOAD THE MODEL
   - TEST 1: ENGLISH → LUGANDA
   - TEST 2: LUGANDA → ENGLISH
   - TEST 4: YOUR OWN EXAMPLES (modify this!)
4. **Done!** Model is tested and working

---

## Step-by-Step Instructions

### 1️⃣ Create New Colab Notebook
```
https://colab.research.google.com → New notebook
```

### 2️⃣ Add First Cell - Setup & Dependencies
Press `Ctrl+M` then `B` to add new cell. Copy this:

```python
!pip install -q torch transformers datasets pandas numpy scikit-learn sacrebleu flask requests tqdm python-dotenv SpeechRecognition gTTS
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
import os
os.chdir('/content/translator')
import sys
sys.path.insert(0, '/content/translator')
print("✓ Setup complete!")
```

Click ▶️ to run. **Wait 2-3 minutes.**

### 3️⃣ Add Second Cell - Load Model
```python
from inference import TransformerTranslator
print("Loading models...")
translator = TransformerTranslator()
print(f"✓ Ready! Device: {translator.device}")
```

Click ▶️ to run. **Wait 3-5 minutes (first time only).**

### 4️⃣ Add Third Cell - Test English to Luganda
```python
result = translator.translate("Hello, how are you?", source_lang="english", target_lang="luganda")
print(f"EN: Hello, how are you?")
print(f"LG: {result['translation']}")
```

Click ▶️ to run. **Should be instant!**

### 5️⃣ Add Fourth Cell - Test Your Own Text
```python
# Edit these lines with YOUR text:
my_text = "God bless Uganda"

result = translator.translate(my_text)
print(f"EN: {my_text}")
print(f"LG: {result['translation']}")
```

Click ▶️ to run.

---

## 🧪 Ready-to-Run Code Snippets

### Simple English to Luganda
```python
from inference import TransformerTranslator
translator = TransformerTranslator()

# Test
result = translator.translate("I love Luganda", source_lang="english", target_lang="luganda")
print(result['translation'])
```

### Simple Luganda to English
```python
result = translator.translate("Webale nnyo", source_lang="luganda", target_lang="english")
print(result['translation'])
```

### Auto-Detect Language
```python
result = translator.translate("Hello")  # Model figures it out!
print(f"Detected: {result['source_lang']}")
print(f"Translation: {result['translation']}")
```

### Batch Translation
```python
texts = ["Hello", "Good morning", "Thank you"]

for text in texts:
    result = translator.translate(text)
    print(f"{text} → {result['translation']}")
```

### Measure Speed
```python
import time

start = time.time()
result = translator.translate("Hello, how are you?")
elapsed = time.time() - start

print(f"Translation: {result['translation']}")
print(f"Time: {elapsed*1000:.2f}ms")
```

---

## ⏱️ Timing Guide

| Step | Time | Notes |
|------|------|-------|
| Setup & Install | 2-3 min | One time only |
| Model Download | 3-5 min | One time only |
| First Translation | 1-2 sec | After model loads |
| Subsequent Translations | 100-500ms | Depends on text length |

---

## 🆘 Common Issues & Fixes

### "No module named 'torch'"
👉 **Fix:** Go back to cell 1 and re-run the pip install

### "Model download is stuck"
👉 **Fix:** This is normal. Wait 5+ minutes. Watch the progress bar.

### "Out of memory error"
👉 **Fix:** Model uses CPU automatically. It's slower but works fine.

### "Translation looks weird"
👉 **Fix:** Try different text. Some phrases work better than others.

---

## 📥 How to Save Results

### Save to File:
```python
import json
from datetime import datetime

results = {
    "device": str(translator.device),
    "timestamp": datetime.now().isoformat(),
    "translations": {
        "hello": translator.translate("Hello")['translation'],
    }
}

with open('results.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Download to Computer:
```python
from google.colab import files
files.download('results.json')
```

---

## 📊 Expected Results

When everything works, you should see:

```
✓ Setup complete!
✓ Ready! Device: cuda (or cpu)

EN: Hello, how are you?
✨ LG: Habari yako uvivu?

LG: Webale nnyo
✨ EN: Thank you very much

Translation: ...
Time: 150.23ms
```

---

## 🚀 Next Steps

After you've verified the model works:

1. **Test with your own data** - Modify the text and see translations
2. **Batch process** - Translate multiple sentences
3. **Measure performance** - Check speed and accuracy
4. **Save results** - Download JSON file to your computer
5. **Deploy** - Use in your own projects

---

## 💡 Pro Tips

1. **First translation is slower** - Model is warming up. Subsequent ones are faster.
2. **Use specific language codes** - "english" and "luganda" work best
3. **Pre-process text** - Clean up spelling/punctuation for better results
4. **Batch process** - Translate multiple items together for speed
5. **Keep session alive** - Model stays loaded between cells

---

## 🎯 TL;DR (Too Long; Didn't Read)

**Just want it to work?**

1. Open https://colab.research.google.com
2. Create new notebook
3. Copy CELL 1, 2, 3 from COLAB_COPY_PASTE_READY.py
4. Run each cell (wait for downloads)
5. Test with your own text
6. Done! 🎉

---

## 📚 More Resources

- **GitHub:** https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR
- **Full Guide:** See COLAB_TESTING_GUIDE.md
- **All Cells:** See COLAB_COPY_PASTE_READY.py
- **Main Notebook:** See COLAB_TESTING_NOTEBOOK.py

---

**Questions?** Check the GitHub repository or the detailed COLAB_TESTING_GUIDE.md

**Ready?** Open Google Colab and start testing! 🌍
