# Google Colab Training Setup - Quick Start

## Overview
Train the English-Luganda translator in Google Colab using the **Kambale dataset** combined with all available local datasets (cultural, jw300, makerere, sunbird).

## Prerequisites
1. **Google Colab Account** - Free tier with Tesla T4 GPU
2. **HuggingFace Token** - For accessing the gated Kambale dataset
   - Get yours at: https://huggingface.co/settings/tokens
   - Save it securely (you'll need it during training)

## Step 1: Setup Colab Notebook

Open Google Colab: https://colab.research.google.com

Create a new cell and run:

```python
# Clone repository
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
import os
os.chdir('/content/translator')
```

## Step 2: Run Training Script

Create a new cell with this command:

```python
exec(open('COLAB_TRAIN_KAMBALE_COMBINED.py').read())
```

## Step 3: Provide HuggingFace Token

When prompted:
```
🔑 Enter your HuggingFace token: [PASTE YOUR TOKEN HERE]
```

The script will:
1. ✓ Authenticate with HuggingFace
2. ✓ Download Kambale dataset (100k+ pairs)
3. ✓ Combine with local datasets (cultural, jw300, makerere, sunbird)
4. ✓ Deduplicate and clean
5. ✓ Train for 3 epochs on combined data
6. ✓ Compute BLEU score on test set
7. ✓ Save trained model
8. ✓ Download metrics

## Expected Results

**Training Time**: 15-20 minutes (Tesla T4 GPU)

**BLEU Score**:
- Baseline (pre-trained): 20-25
- After training: 25-35+ (goal: good translation quality)

**Output Files**:
- Model: `models/kambale_combined_model/`
- Metrics: `metrics_kambale_combined.json` (downloaded automatically)

## What the Script Does

### Phase 1: Dataset Combination
```
Load: Kambale corpus (100k+ pairs from HF)
Load: 4 local datasets (cultural, jw300, makerere, sunbird)
Combine: Merge all sources
Deduplicate: Remove duplicate (english, luganda) pairs
Clean: Remove <2 word or >50 word sentences
Split: 80% train, 10% val, 10% test
```

### Phase 2: Training
```
Model: Helsinki-NLP/opus-mt-en-mul
Epochs: 3
Batch size: 8
Learning rate: 2e-5
Max length: 128 tokens
Optimization: Adam with warmup
```

### Phase 3: Evaluation
```
Metric: BLEU score (sacrebleu)
Dataset: Test set (10% of combined data)
Output: metrics_kambale_combined.json
```

## Key Improvements

The combined dataset approach provides:

1. **Large Scale**: 100k+ pairs from Kambale + local data
2. **Better Quality**: Kambale is professionally curated
3. **Better Coverage**: Cultural phrases, religious texts, parallel corpora
4. **Deduplication**: No redundant training data
5. **Reproducibility**: Fixed random seed (42)

## Troubleshooting

### Issue: "HF_TOKEN not found in environment variables"
**Solution**: Make sure to enter your token when prompted

### Issue: "Model loading is slow"
**Expected**: First time loading ~10 minutes, subsequent ~1 minute (cached)

### Issue: "Out of memory"
**Solution**: Google Colab usually has enough VRAM, but if it fails:
- Reduce batch_size from 8 to 4 in the script
- Reduce num_train_epochs from 3 to 2

### Issue: "Network timeout downloading Kambale"
**Solution**: Retry the script (usually temporary)

## Next Steps After Training

1. **Review BLEU Score**
   - Read metrics_kambale_combined.json
   - If BLEU > 30: Good quality, ready for use
   - If BLEU 25-30: Acceptable, consider improvements
   - If BLEU < 25: Need more data or tuning

2. **Plan Improvements** (see MODEL_IMPROVEMENT_GUIDE.md)
   - Strategy 1: Add more training data
   - Strategy 2: Fine-tune hyperparameters
   - Strategy 3: Try larger model (Helsinki-NLP/opus-mt-en-mul-large)
   - Strategy 4: Data augmentation

3. **Deploy Model**
   - Copy trained model to local
   - Run: `python app.py` (Flask interface)
   - Or: `streamlit run app_streamlit_professional.py` (Web UI)

## Files Reference

- `COLAB_TRAIN_KAMBALE_COMBINED.py` - Main training script
- `combine_datasets_with_token.py` - Dataset combination logic
- `COLAB_TRAINING_ULTRA_SIMPLE.py` - Alternative minimal version
- `MODEL_IMPROVEMENT_GUIDE.md` - Improvement strategies
- `TRAINING_WORKFLOW.md` - Detailed workflow documentation

## Contact

For issues or questions:
- GitHub: https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR
- Check issues/discussions first

---

**Ready to train?** Start with Step 1 above in Google Colab!
