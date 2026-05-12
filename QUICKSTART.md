# 🚀 QUICK START GUIDE - Kabale English-Luganda Translator

## Overview
This guide walks you through setting up and training the English-Luganda translator using the **Kabale English-Luganda Parallel Corpus**.

**IMPORTANT**: The Kabale dataset is GATED, meaning you need to request access first.

---

## 📋 Prerequisites

Make sure you have the following installed:

```bash
pip install -r requirements.txt
```

Key packages:
- `transformers>=4.35.2` - HuggingFace transformers
- `datasets>=2.14.5` - HuggingFace datasets
- `torch>=2.0.0` - PyTorch
- `streamlit` - Web interface (if deploying the app)

---

## ⚠️ Step 0: Access the Kabale Dataset (CRITICAL!)

The Kabale dataset requires manual approval. Follow these steps:

### 1. Go to the dataset page:
https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus

### 2. Request Access:
- Click the "Access repository" button
- Read the terms
- Accept and submit your request
- Wait for approval (usually instant to a few hours)

### 3. Authenticate Locally:

Once approved, authenticate with HuggingFace:

**Option A - Interactive CLI (Recommended):**
```bash
huggingface-cli login
# Paste your token when prompted
```

**Option B - Set Environment Variable:**
```bash
set HF_TOKEN=your_token_here
```

**Option C - Python:**
```python
from huggingface_hub import login
login(token="your_token_here")
```

### 4. Get Your HuggingFace Token:
- Visit: https://huggingface.co/settings/tokens
- Click "New token"
- Name it: "Luganda Translator"
- Select "Read" permission
- Click "Create token"
- Copy and save it

---

## ✅ Step 1: Validate Your Setup

First, verify that everything is configured correctly:

```bash
python validate_setup.py
```

This script will check:
- ✅ Kabale dataset access
- ✅ Data normalization
- ✅ Model loading capability
- ✅ Tokenization
- ✅ Inference capability

**Expected output**: All checks pass

**Troubleshooting**:
- If "gated dataset" error: You haven't requested access yet (Step 0)
- If "authentication failed": Make sure you've run `huggingface-cli login`
- If model download fails: Check internet connection

---

## 🎯 Step 2: Train the Model

Now train the translator with the Kabale dataset:

```bash
python train_with_kabale_dataset.py
```

### What this script does:
1. **Loads** the Kabale English-Luganda corpus (100k+ pairs)
2. **Normalizes** the data (removes duplicates, validates)
3. **Splits** into train/val/test (70%/15%/15%)
4. **Fine-tunes** a MarianMT model for 5 epochs
5. **Saves** the trained model to `models/trained_model_cpu/`
6. **Tests** inference on sample sentences

### Training Configuration:
- **Model**: Helsinki-NLP/opus-mt-en-mul (200M parameters)
- **Epochs**: 5
- **Batch Size**: 16
- **Learning Rate**: 2e-5
- **Max Sequence Length**: 128
- **Warmup Steps**: 500
- **Device**: CPU or CUDA (auto-detected)

### Training Time Estimate:
- **CPU**: 4-8 hours (depends on dataset size)
- **GPU (CUDA)**: 30-60 minutes

### Progress Indicators:
- Each epoch shows: loss, validation loss, training progress
- Model saves best checkpoint automatically
- Final inference test shows sample translations

**Output**: Trained model in `models/trained_model_cpu/`

---

## 🧪 Step 3: Test the Trained Model

After training, verify the model works:

```bash
python test_translator_quality.py
```

This tests:
- Model loading
- Translation quality
- Confidence scoring
- Batch processing

---

## 🌐 Step 4: Deploy the Streamlit App

Once training is complete, deploy the interactive app:

```bash
streamlit run app_streamlit.py
```

### Features:
- 🔤 **Translator Tab**: Translate English ↔ Luganda with confidence scores
- 📚 **Phrasebook Tab**: 60+ common phrases with audio
- 📊 **History Tab**: Track all translations with SQLite
- ℹ️ **About Tab**: ML pipeline information

### App Usage:
1. Select source language (or Auto-Detect)
2. Enter text to translate
3. Click "Translate"
4. View translation with confidence score
5. Optional: Click "Play Audio" for text-to-speech

---

## 📁 Project Structure

```
d:\ENGLISH-LUGANDA TRANSLATOR\
├── train_with_kabale_dataset.py  ← Main training script (NEW)
├── validate_setup.py              ← Setup validation (NEW)
├── app_streamlit.py               ← Streamlit deployment (UPDATED)
├── requirements.txt               ← All dependencies
├── data/
│   ├── raw/                       ← Original datasets
│   ├── processed/                 ← Processed data
│   └── tokenized/                 ← Tokenized datasets
├── models/
│   └── trained_model_cpu/         ← Your trained model (OUTPUT)
├── outputs/
│   ├── evaluation_results.json
│   └── training_summary.json
└── ...
```

---

## 🔍 Configuration Details

### Training Script Configuration

Edit `train_with_kabale_dataset.py` to customize:

```python
CONFIG = {
    'dataset_name': 'kambale/luganda-english-parallel-corpus',  # Dataset
    'base_model': 'Helsinki-NLP/opus-mt-en-mul',                # Base model
    'trained_model_path': 'models/trained_model_cpu',           # Output path
    'epochs': 5,                                                 # Training epochs
    'batch_size': 16,                                            # Batch size
    'learning_rate': 2e-5,                                       # Learning rate
    'max_length': 128,                                           # Max sequence length
    'warmup_steps': 500,                                         # Warmup steps
    'seed': 42,                                                  # Random seed
}
```

---

## 🛠️ Troubleshooting

### Issue: "Dataset is a gated dataset"
**Solution**: You need to request access at https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus

### Issue: "Authentication failed"
**Solution**: Run `huggingface-cli login` and paste your HuggingFace token

### Issue: Out of memory (OOM) during training
**Solution**:
- Reduce `batch_size`: Change from 16 to 8
- Reduce `max_length`: Change from 128 to 64
- Increase warmup steps

### Issue: Model not found when running Streamlit app
**Solution**:
- Ensure training completed successfully
- Check `models/trained_model_cpu/` directory exists
- App will auto-fallback to base model if trained model not found

### Issue: Slow inference on CPU
**Solution**:
- For GPU acceleration, install CUDA-enabled PyTorch
- Use quantized model for faster inference (optional)

---

## 📊 Dataset Information

### Kabale English-Luganda Parallel Corpus
- **Source**: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
- **Size**: 100k+ English-Luganda translation pairs (RECOMMENDED)
- **Quality**: High-quality curated parallel corpus
- **Language Codes**: `en` (English), `lg` (Luganda)
- **Column Structure**: Nested `translation` dict with language keys
- **Access**: GATED - Requires approval

### Why Kabale?
- ✅ Largest publicly available Luganda-English corpus
- ✅ High-quality curated data
- ✅ Well-maintained by Kabale team
- ✅ Ideal for production-grade translation

---

## 📈 Expected Performance

After training with Kabale dataset:

- **Training Loss**: ~1-2 (decreases over epochs)
- **Validation Loss**: ~1-2 (lower indicates better fit)
- **Inference Speed**: 
  - CPU: ~500ms per sentence
  - GPU: ~50ms per sentence
- **Translation Quality**: 
  - BLEU Score: Calculated during evaluation
  - Coverage: Near 100% on seen phrases
  - Accuracy: 70-85% on semantic preservation

---

## 🎓 Learning Resources

- **HuggingFace Documentation**: https://huggingface.co/docs/transformers/
- **MarianMT Model**: https://huggingface.co/Helsinki-NLP/opus-mt-en-mul
- **Streamlit Docs**: https://docs.streamlit.io/
- **Kabale Dataset**: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
- **Luganda Language**: https://en.wikipedia.org/wiki/Luganda

---

## ❓ FAQ

**Q: Do I have to use the Kabale dataset?**
A: For best quality, yes. It's the highest quality Luganda-English corpus available.

**Q: How long does it take to get dataset access?**
A: Usually instant to a few hours. Just request and wait.

**Q: Can I use a different dataset?**
A: Yes, but Kabale is recommended. See AVAILABLE_DATASETS.py for alternatives.

**Q: How do I improve translation quality?**
A: Train for more epochs, increase batch size, or use more data.

**Q: Can I export the model for mobile?**
A: Yes! Convert to ONNX or TensorFlow format using HuggingFace tools.

**Q: Does the app work offline?**
A: Once trained, inference works offline. Only dataset loading requires internet.

---

## 🚀 Next Steps

1. ✅ Request access to Kabale dataset (Step 0)
2. ✅ Authenticate with `huggingface-cli login`
3. ✅ Run `validate_setup.py` to verify everything
4. ✅ Run `train_with_kabale_dataset.py` to train
5. ✅ Run `app_streamlit.py` to deploy
6. ✅ Share your translations!

---

## 📞 Support

If you encounter issues:
1. Check the Troubleshooting section above
2. Run `DATASET_ACCESS_GUIDE.py` for dataset help
3. Run `AVAILABLE_DATASETS.py` to see all options
4. Review error messages in the terminal
5. Verify all dependencies are installed

---

**For more information, run:**
```bash
python DATASET_ACCESS_GUIDE.py
python AVAILABLE_DATASETS.py
```

**Happy translating!**
