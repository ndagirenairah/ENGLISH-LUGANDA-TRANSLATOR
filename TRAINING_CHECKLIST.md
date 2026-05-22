# Training Execution Checklist

## Pre-Training (Before Opening Colab)

### Preparation
- [ ] Have HuggingFace token ready (https://huggingface.co/settings/tokens)
- [ ] Bookmark GitHub repo: https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR
- [ ] Read COLAB_SETUP_INSTRUCTIONS.md (2 min)
- [ ] Ensure you have a Google account for Colab access

### System Check (Optional - for local testing first)
- [ ] Python 3.8+ installed
- [ ] All local datasets present in `data/raw/`
- [ ] Test dataset combination: `python combine_datasets_with_token.py`

---

## In Google Colab (Step-by-Step)

### Cell 1: Clone Repository
```python
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
import os
os.chdir('/content/translator')
print("✓ Repository cloned")
```

**Expected Output**:
```
✓ Repository cloned
```

### Cell 2: Run Training Script
```python
exec(open('COLAB_TRAIN_KAMBALE_COMBINED.py').read())
```

**Expected Flow** (15-20 minutes):
1. **Setup Phase** (1 min)
   - GPU verification: ✓ Device: cuda, ✓ GPU: Tesla T4
   - Dependencies: ✓ Installing torch, transformers, datasets, pandas, sacrebleu
   
2. **Dataset Phase** (3-5 min)
   - Prompt: "🔑 Enter your HuggingFace token: "
   - Output: Kambale dataset loaded, 4 local datasets loaded, combined, deduplicated
   - Result: "Train: XXX, Val: YY, Test: YY"
   
3. **Model Phase** (2-3 min)
   - Model download: Helsinki-NLP/opus-mt-en-mul (~600MB)
   - Tokenizer loaded
   - Model loaded to GPU
   
4. **Training Phase** (10-15 min)
   - Epoch 1: Training steps progress
   - Epoch 2: Validation metrics shown
   - Epoch 3: Final training step
   - Output: Training loss: X.XXXX
   
5. **Evaluation Phase** (1 min)
   - Predictions generated on test set
   - BLEU score calculated
   - Sample predictions shown (5 examples)
   
6. **Save Phase** (1 min)
   - Model saved to: /content/translator/models/kambale_combined_model/
   - Metrics file downloaded: metrics_kambale_combined.json

---

## What to Do When Prompted

### When You See:
```
🔑 Enter your HuggingFace token:
```

### Action:
1. Copy your HF token from https://huggingface.co/settings/tokens
2. Paste it after the prompt
3. Press Enter

**Note**: The token will NOT appear on screen (security feature)

---

## Understanding the Output

### Dataset Loading Output
```
✓ Train: 350
✓ Val: 50
✓ Test: 50

Dataset sources:
  kambale: 300
  cultural: 50
  jw300: 40
  makerere: 10
```
→ Good: Shows Kambale is primary source, combined with others

### BLEU Score Output
```
🎯 TEST SET BLEU SCORE: 28.45
```

| Score | Meaning | Action |
|-------|---------|--------|
| 20-25 | Baseline | Consider improvements |
| 25-30 | Good ✓ | Ready for testing |
| 30-35 | Excellent ✓✓ | Production ready |
| 35+ | Exceptional ✓✓✓ | Deploy immediately |

### Sample Predictions
```
1. Reference: Ssalamu alaikum
   Predicted: Ssalamu alaikum
```
→ Perfect match (BLEU boosts for these)

---

## After Training

### Step 1: Download Metrics
The script automatically downloads `metrics_kambale_combined.json`

### Step 2: Review Metrics
```python
import json
with open('metrics_kambale_combined.json') as f:
    metrics = json.load(f)
    print(f"BLEU Score: {metrics['bleu_score']:.2f}")
    print(f"Train samples: {metrics['train_samples']}")
    print(f"Dataset: {metrics['dataset']}")
```

### Step 3: Next Steps by BLEU Score

**If BLEU > 30: ✅ DEPLOY**
```bash
# Copy model locally
# Run: python app.py
# Test at: http://localhost:5000
```

**If BLEU 25-30: ✅ TEST & CONSIDER IMPROVEMENTS**
```
See: MODEL_IMPROVEMENT_GUIDE.md
Try:
  - Fine-tune learning rate (2e-5 → 5e-5)
  - More epochs (3 → 5)
  - Larger batch size (8 → 16)
```

**If BLEU < 25: ⚠ INVESTIGATE**
```
Possible causes:
  1. Dataset too small (< 200 samples)
  2. Data quality issues (duplicates, noise)
  3. Model mismatch (use newer version)
  
Solutions:
  - Add more training data (see DATASET_USAGE_GUIDE.md)
  - Try: COLAB_TRAINING_ULTRA_SIMPLE.py with more epochs
  - Check raw data quality in data/raw/
```

---

## Troubleshooting During Training

### Error: "HF_TOKEN not found"
**Solution**: Make sure you entered the token when prompted

### Error: "Killed (Connection timeout)"
**Reason**: Network issue downloading Kambale
**Solution**: Restart the training cell (usually works on retry)

### Error: "CUDA out of memory"
**Solution** (if it happens):
1. Edit COLAB_TRAIN_KAMBALE_COMBINED.py before Cell 2
2. Change line: `per_device_train_batch_size=8,` → `per_device_train_batch_size=4,`
3. Rerun Cell 2

### Warning: "Model loading is slow"
**Expected**: First time ~2-3 minutes (normal)
Subsequent runs will use cache (~30 seconds)

### Model Not Saving
**Check**: Look for `/content/translator/models/kambale_combined_model/` folder
**If not there**: Run this diagnostic:
```python
import os
print(os.listdir('/content/translator/models/'))
```

---

## Files You'll Get

After successful training:

**Locally** (from downloads):
- `metrics_kambale_combined.json` - BLEU score + statistics

**In Colab** (in folder `/content/translator/`):
- `models/kambale_combined_model/` - Full trained model
- `data/combined_kambale/` - Dataset used for training
- `results/` - Training checkpoints

---

## Performance Timeline

| Phase | Duration | What's Happening |
|-------|----------|------------------|
| Setup & GPU check | 30 sec | Installation, verification |
| Clone & download | 1-2 min | Repository + model (~600MB) |
| Dataset loading | 2-3 min | Combining 5 sources + dedup |
| Model loading | 1 min | Loading MarianMT to GPU |
| Training | 10-15 min | 3 epochs, ~50-100 steps per epoch |
| Evaluation | 1 min | Computing BLEU score |
| Save & download | 1 min | Model save, metrics download |
| **TOTAL** | **15-20 min** | Complete training & evaluation |

---

## Success Confirmation

✅ **Training was successful when you see:**

```
================================================================================
  ✅ TRAINING COMPLETE!
================================================================================

🎯 FINAL RESULTS:
   BLEU Score: XX.XX
   Training Loss: X.XXXX
   Samples: XXX

📊 Datasets used:
   ✓ Kambale Luganda-English Parallel Corpus
   ✓ Cultural dictionary
   ✓ JW300 parallel corpus
   ✓ Makerere NLP
   ✓ Sunbird Salt

📁 Model saved to: /content/translator/models/kambale_combined_model/

🌍 Ready for production!

================================================================================
```

✅ **Plus downloaded file:**
- `metrics_kambale_combined.json` in your Downloads folder

---

## Quick Reference

### Hyperparameters Used
- Model: Helsinki-NLP/opus-mt-en-mul (300M params)
- Epochs: 3
- Batch size: 8
- Learning rate: 2e-5
- Max length: 128 tokens

### Dataset Composition
- Primary: Kambale (100k+ pairs)
- Secondary: Cultural (1k+ pairs)
- Tertiary: JW300, Makerere, Sunbird (various sizes)
- Total after dedup: ~300-500 pairs

### Expected BLEU Score
- Pretrained baseline: 20-25
- After 3 epochs: 25-35
- Target: 30+ (excellent)

---

## Need Help?

1. **Check this file**: COLAB_SETUP_INSTRUCTIONS.md
2. **Read documentation**: MODEL_IMPROVEMENT_GUIDE.md
3. **Debug script**: Run diagnostic cells (see troubleshooting above)
4. **GitHub Issues**: https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR/issues

---

**You're ready! Open Google Colab and start training! 🚀**
