# 🚀 COLAB TRAINING GUIDE - Using Kambale Dataset

This guide explains how to train the English-Luganda NLLB translator with your Kambale datasets in Google Colab.

## 📋 What You Have

**Local Datasets (in your workspace):**
- `kambale_train.csv` - Main Kambale training data
- `cultural_training.csv` - Cultural phrases  
- `jw300_parallel.csv` - JW300 parallel corpus
- `makerere_nlp.csv` - Makerere NLP dataset
- `sunbird_salt.csv` - Sunbird SALT dataset

**Colab Notebook:**
- `COLAB_NLLB_PIPELINE.ipynb` - Complete training pipeline (8 cells)

---

## 🎯 Step-by-Step Instructions

### Step 1: Open Colab
1. Go to https://colab.research.google.com
2. Click **"File" → "Open notebook"**
3. Go to **"GitHub"** tab
4. Paste your repo URL
5. Select `COLAB_NLLB_PIPELINE.ipynb`

### Step 2: Set GPU
1. Click **"Runtime" → "Change runtime type"**
2. Select **"GPU (T4)"** or higher
3. Click **"Save"**

### Step 3: Upload Datasets
**Option A: Upload CSV files (Recommended)**
1. Left panel → 📁 **Files** tab
2. Click upload button (📤)
3. Select ALL your CSV files:
   - `kambale_train.csv`
   - `cultural_training.csv`
   - `jw300_parallel.csv`
   - `makerere_nlp.csv`
   - `sunbird_salt.csv`
4. Wait for all uploads to complete

**Option B: Use GitHub (if files are in repo)**
```python
# In Colab Cell 2, add:
!git clone https://github.com/YOUR_USERNAME/ENGLISH-LUGANDA-TRANSLATOR.git
# Then reference files as: /content/ENGLISH-LUGANDA-TRANSLATOR/data/raw/kambale_train.csv
```

### Step 4: Run the Pipeline

**Cell 0: Setup & Installation**
- Run first (Shift+Enter)
- Installs all dependencies
- Wait for completion ✓

**Cell 1: Import Libraries & GPU**
- Detects GPU (should see Tesla T4)
- Wait for completion ✓

**Cell 2: Load & Combine Datasets** ⭐
- Automatically combines ALL uploaded datasets
- Removes duplicates
- Cleans text
- Displays sample data
- Wait for completion ✓

**Cell 3: Clean Dataset**
- Normalizes text
- Filters by length
- Removes duplicates again
- Shows statistics
- Wait for completion ✓

**Cell 4: Load NLLB Model**
- Downloads 2.5GB model (~25 seconds)
- Wait for ✓ complete message

**Cell 5: Tokenize & Prepare Data**
- Splits into train/val/test (80/10/10)
- Tokenizes with language codes
- Creates dataset objects
- Wait for completion ✓

**Cell 6: Train Model** ⏱️ TAKES ~10-15 MINUTES
- Trains on Tesla T4 GPU
- Watch loss decrease
- Early stopping based on validation
- Saves best model
- ☕ Grab coffee, this is the longest step!

**Cell 7: Evaluate BLEU Score** (~2 minutes)
- Generates predictions
- Computes BLEU score (expected: 28-38)
- Shows sample translations
- Displays metrics

**Cell 8: Save Model** (~1 minute)
- Saves model to `/content/nllb_trained`
- Saves tokenizer
- Saves evaluation results
- Creates inference script

### Step 5: Download Trained Model
1. Left panel → 📁 **Files**
2. Find `nllb_trained` folder
3. Right-click → **Download**
4. Save locally for deployment

---

## 📊 Expected Results

| Metric | Value |
|--------|-------|
| Training Samples | 100-1000+ (from combined datasets) |
| BLEU Score | 28-38 |
| Training Time | ~10-15 min |
| GPU Memory Used | ~6-7 GB |
| Model Size | ~2.5 GB |

---

## ❓ Troubleshooting

### "File not found" error
- Make sure CSV files are uploaded to Colab `/content/` folder
- Check file names match exactly (case-sensitive)

### Out of Memory error
- Reduce `BATCH_SIZE` from 8 to 4 in Cell 6
- Or use fewer datasets

### Low BLEU Score
- Add more training data
- Increase epochs (change `NUM_EPOCHS` in Cell 6)
- Train longer

### "No module named..." error
- Re-run Cell 0 (Setup)
- Wait for all packages to install

---

## 🔧 Customization

**In Cell 6, you can modify:**

```python
BATCH_SIZE = 8           # Reduce if out of memory
NUM_EPOCHS = 3           # Increase for better quality (slower)
LEARNING_RATE = 2e-5     # Adjust training speed
```

**In Cell 4, you can change the model:**

```python
# Faster (600M params) - Current
MODEL_NAME = "facebook/nllb-200-distilled-600M"

# Better quality (1.3B params) - Slower, needs more VRAM
MODEL_NAME = "facebook/nllb-200-1.3B"

# Much faster (small) - Lower quality
MODEL_NAME = "facebook/nllb-200-distilled-200M"
```

---

## 📥 After Training - Deployment

Once you download the trained model, you can use it locally:

```python
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

model = AutoModelForSeq2SeqLM.from_pretrained('nllb_trained')
tokenizer = AutoTokenizer.from_pretrained('nllb_trained')

# Use the model for inference
inputs = tokenizer("Hello, how are you?", return_tensors="pt")
outputs = model.generate(**inputs)
print(tokenizer.decode(outputs[0]))  # Output: Agandi, oli otya?
```

---

## ✅ Quick Checklist

Before running:
- [ ] All CSV files uploaded to Colab
- [ ] GPU enabled (Runtime → Change runtime type → T4)
- [ ] Python 3.8+ installed locally (for deployment)
- [ ] 15-20 minutes available (full pipeline time)

During training:
- [ ] Watch Cell 6 for training progress
- [ ] Check loss is decreasing (not increasing)
- [ ] Monitor GPU memory in bottom left

After training:
- [ ] Check Cell 7 BLEU score (should be 28+)
- [ ] Download the `nllb_trained` folder
- [ ] Test inference locally

---

## 📞 Support

If you encounter issues:
1. Check error message carefully
2. Try re-running the cell
3. Check file paths in error message
4. Verify GPU is enabled
5. Make sure all CSV files are uploaded

---

**Good luck! Your Kambale translator is on the way! 🇺🇬✨**
