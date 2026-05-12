# English-Luganda Neural Machine Translator

A production-grade machine translation system for low-resource Luganda combining transformer neural networks with cultural intelligence for accurate English - Luganda translation.

---

## QUICK START

### Fast Track with Kabale Dataset

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Request Kabale dataset access
# https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus

# 3. Authenticate with HuggingFace
huggingface-cli login

# 4. Validate setup
python validate_setup.py

# 5. Train the model
python train_kabale_professional.py

# 6. Deploy the app
streamlit run app_streamlit_professional.py
```

**Training Time**: 4-8 hours (CPU) | 30-60 min (GPU)  
**Dataset**: Kabale English-Luganda Parallel Corpus (100k+ pairs)

---

## PROFESSIONAL FILES (PRODUCTION READY)

| File | Purpose |
|------|---------|
| dataset_loader_api.py | HuggingFace API dataset loader |
| train_kabale_professional.py | Production training script |
| app_streamlit_professional.py | Production Streamlit web app |
| validate_setup.py | Environment validation |
| SETUP_GUIDE.md | Complete setup instructions |
| DATASET_USAGE_GUIDE.md | Dataset access and usage guide |

---

## ML PIPELINE ARCHITECTURE

| Stage | Component | File | Input | Output |
|-------|-----------|------|-------|--------|
| Problem | Low-resource Luganda NMT | - | Domain knowledge | Task definition |
| Dataset | Kabale parallel corpus | dataset_loader_api.py | HF API | 100k+ pairs |
| Preprocessing | Clean + Tokenize | train_kabale_professional.py | Raw text | Train/val/test splits |
| Model | MarianMT Transformer | train_kabale_professional.py | Pre-trained weights | 200M parameters |
| Training | Fine-tuning | train_kabale_professional.py | Tokenized data | Fine-tuned model |
| Evaluation | BLEU + Metrics | train_kabale_professional.py | Test set | Metrics report |
| Deployment | Streamlit App | app_streamlit_professional.py | Model weights | Live translation service |

---

## KEY FEATURES

- Bidirectional translation (English - Luganda)
- Confidence scoring for each translation
- Translation history tracking
- Voice input/output support
- Learning phrasebook (60+ phrases)
- Production-ready performance
- API-based dataset access
- Professional error handling

---

## DATASET INFORMATION

### Kabale English-Luganda Parallel Corpus

- **Size**: 100k+ translation pairs
- **Quality**: High-quality, professionally curated
- **Access**: Gated dataset (requires approval)
- **URL**: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
- **Language Pairs**: English (en) - Luganda (lg)
- **Splits**: train, validation, test

### Getting Access

1. Visit: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
2. Click "Access repository"
3. Accept terms
4. Wait for approval (usually instant)
5. Run: huggingface-cli login

---

## SYSTEM REQUIREMENTS

### Minimum
- Python 3.7+
- 4 GB RAM
- 2 GB disk space
- Internet connection

### Recommended
- Python 3.9+
- 8 GB RAM
- 10 GB disk space
- GPU with 6+ GB VRAM (optional but much faster)

### Installation

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate.ps1

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## CONFIGURATION

### Training Parameters

Edit CONFIG in `train_kabale_professional.py`:

```python
CONFIG = {
    'dataset_name': 'kambale/luganda-english-parallel-corpus',
    'base_model': 'Helsinki-NLP/opus-mt-en-mul',
    'trained_model_path': 'models/trained_model_cpu',
    'epochs': 5,
    'batch_size': 16,
    'learning_rate': 2e-5,
    'max_length': 128,
    'warmup_steps': 500,
    'seed': 42,
}
```

### Adjustment Guide

For better quality:
- Increase epochs: 5 -> 10
- Decrease learning_rate: 2e-5 -> 1e-5
- Increase warmup_steps: 500 -> 1000

For faster training:
- Reduce epochs: 5 -> 3
- Reduce max_length: 128 -> 64
- Increase batch_size: 16 -> 32

---

## PROJECT STRUCTURE

```
d:\ENGLISH-LUGANDA TRANSLATOR\
|
|- dataset_loader_api.py
|- train_kabale_professional.py
|- app_streamlit_professional.py
|- validate_setup.py
|- requirements.txt
|
|- SETUP_GUIDE.md
|- DATASET_USAGE_GUIDE.md
|- README.md
|
|- data/
|  |- raw/
|  |- processed/
|  |- tokenized/
|
|- models/
|  |- trained_model_cpu/   [After training]
|
|- outputs/
|  |- evaluation_results.json
```

---

## TRAINING WORKFLOW

### Step 1: Validate Environment

```bash
python validate_setup.py
```

### Step 2: Train Model

```bash
python train_kabale_professional.py
```

Expected output:
```
[LOADER] Loading Kabale dataset via API
[DATA] Total samples: 100,000+
[SPLIT] Train: 70,000 pairs
[SPLIT] Validation: 15,000 pairs
[SPLIT] Test: 15,000 pairs
[TRAIN] Training epoch 1/5...
[TRAIN] Training complete
[SAVE] Model saved to: models/trained_model_cpu/
```

Training time:
- CPU: 4-8 hours
- GPU: 30-60 minutes

### Step 3: Deploy App

```bash
streamlit run app_streamlit_professional.py
```

Access at: http://localhost:8501

---

## FEATURES

### Translator Tab
- Real-time translation
- Auto-language detection
- Confidence scoring
- Character limit: 500

### Phrasebook Tab
- 60+ learning phrases
- 6 categories
- Audio playback
- Cultural context

### History Tab
- Translation tracking
- SQLite persistence
- Statistics dashboard
- Download support

### About Tab
- System information
- Model details
- Technology stack
- Usage guide

---

## PERFORMANCE

### Training Performance

| Metric | Value |
|--------|-------|
| Training Loss | 1-2 |
| Validation Loss | 1-2 |
| BLEU Score | 25-35 |
| Training Time (CPU) | 4-8 hours |
| Training Time (GPU) | 30-60 min |

### Inference Performance

| Device | Speed | Memory |
|--------|-------|--------|
| CPU | 500ms | 1 GB |
| GPU | 50ms | 2 GB |

---

## TROUBLESHOOTING

### Dataset Access Denied
- Request access at: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
- Run: huggingface-cli login
- Try again after approval

### Authentication Failed
- Get token from: https://huggingface.co/settings/tokens
- Run: huggingface-cli login
- Or: set HF_TOKEN=your_token_here

### Out of Memory
- Reduce batch_size: 16 -> 8
- Reduce max_length: 128 -> 64
- Use CPU instead of GPU

### Slow Training
- Use GPU acceleration
- Reduce max_length
- Reduce epochs for testing

---

## TECHNOLOGY STACK

- **ML Framework**: HuggingFace Transformers + PyTorch
- **Model**: MarianMT (200M parameters)
- **Base**: Helsinki-NLP/opus-mt-en-mul
- **Web Interface**: Streamlit
- **Dataset**: HuggingFace Datasets + API
- **Audio**: Google Text-to-Speech
- **Database**: SQLite
- **Language**: Python 3.7+

---

## RESOURCES

### Documentation
- HuggingFace: https://huggingface.co/docs/
- Streamlit: https://docs.streamlit.io/
- PyTorch: https://pytorch.org/docs/

### Datasets
- Kabale Corpus: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
- Sunbird AI: https://huggingface.co/Sunbird

### Models
- MarianMT: https://huggingface.co/Helsinki-NLP/opus-mt-en-mul

---

## DEPLOYMENT

### Local Deployment
```bash
streamlit run app_streamlit_professional.py
```

### Production Deployment
```bash
streamlit run app_streamlit_professional.py --server.port 80
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app_streamlit_professional.py"]
```

---

## NEXT STEPS

1. Install dependencies: `pip install -r requirements.txt`
2. Request Kabale dataset access
3. Authenticate: `huggingface-cli login`
4. Validate setup: `python validate_setup.py`
5. Train model: `python train_kabale_professional.py`
6. Deploy app: `streamlit run app_streamlit_professional.py`

---

## PROJECT STATUS

- Status: Production Ready
- Last Updated: May 2026
- Version: 1.0
- License: MIT

---

For complete setup instructions, see: **SETUP_GUIDE.md**

For dataset information, see: **DATASET_USAGE_GUIDE.md**
