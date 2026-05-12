# PROFESSIONAL SETUP GUIDE - ENGLISH-LUGANDA TRANSLATOR

## Quick Start (5 Minutes)

### Prerequisites
- Python 3.7+
- Virtual environment (recommended)
- Internet connection
- HuggingFace account (free)

### Installation

```bash
# 1. Navigate to project
cd d:\ENGLISH-LUGANDA TRANSLATOR

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Get HuggingFace token
# https://huggingface.co/settings/tokens

# 5. Authenticate
huggingface-cli login
# Paste token when prompted

# 6. Validate setup
python validate_setup.py

# 7. Train model
python train_kabale_professional.py

# 8. Run app
streamlit run app_streamlit_professional.py
```

---

## DETAILED SETUP GUIDE

### Step 1: Environment Setup

Create Python virtual environment:

```bash
# Create venv
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows Command Prompt)
.\.venv\Scripts\activate.bat

# Activate (Linux/Mac)
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install from requirements
pip install -r requirements.txt

# Verify installation
pip list
```

### Step 3: HuggingFace Authentication

Get token:
1. Visit: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "Luganda Translator"
4. Permission: "Read"
5. Create and copy token

Authenticate locally:

```bash
# Interactive login
huggingface-cli login

# Or set environment variable
set HF_TOKEN=your_token_here

# Or in Python
from huggingface_hub import login
login(token="your_token_here")
```

### Step 4: Verify Setup

```bash
python validate_setup.py
```

Expected output:
- Dataset API accessible
- Model can load
- Tokenization works
- Inference functional

### Step 5: Access Kabale Dataset

1. Visit: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
2. Click "Access repository"
3. Accept terms
4. Request approval
5. Wait for email confirmation
6. Re-authenticate with: `huggingface-cli login`

---

## TRAINING THE MODEL

### Option A: Professional Training (Recommended)

```bash
python train_kabale_professional.py
```

This script:
- Loads 100k+ Kabale dataset pairs
- Validates and normalizes data
- Splits into train/val/test (70/15/15)
- Fine-tunes MarianMT for 5 epochs
- Saves to models/trained_model_cpu/
- Tests inference automatically

**Expected time**: 4-8 hours (CPU) | 30-60 min (GPU)

### Training Stages

```
[STEP 1] Load Dataset via API
  - Fetches all splits
  - Validates data
  
[STEP 2] Prepare Data
  - Removes duplicates
  - Normalizes text
  
[STEP 3] Split Data
  - Train: 70%
  - Validation: 15%
  - Test: 15%
  
[STEP 4] Load Model
  - Helsinki-NLP/opus-mt-en-mul
  - 200M parameters
  
[STEP 5] Tokenize
  - Encode sentences
  - Create attention masks
  
[STEP 6] Setup Training
  - Configure optimization
  - Set learning rate schedule
  
[STEP 7] Train
  - Fine-tune on Luganda data
  - Monitor validation loss
  
[STEP 8] Evaluate
  - Test on held-out set
  - Calculate metrics
  
[STEP 9] Save
  - Model weights
  - Tokenizer
  - Config
  
[STEP 10] Test Inference
  - Sample translations
  - Verify outputs
```

### Monitoring Training

During training, you'll see:

```
[TRAIN] Epoch 1/5
[TRAIN] Loss: 1.234  Validation Loss: 1.156
[TRAIN] Epoch 2/5
[TRAIN] Loss: 0.987  Validation Loss: 0.956
...
[SUCCESS] Training complete
```

---

## DEPLOYMENT

### Start Streamlit App

```bash
streamlit run app_streamlit_professional.py
```

Access at: http://localhost:8501

### Features

- **Translator Tab**: Real-time translation
- **Phrasebook Tab**: 60+ learning phrases
- **History Tab**: Translation tracking
- **About Tab**: System information

### Configuration

Edit in `app_streamlit_professional.py`:

```python
confidence_threshold = 40  # Show if confidence > 40%
max_history = 50          # Store last 50 translations
batch_size = 1            # Process 1 at a time
```

---

## PROJECT STRUCTURE

```
d:\ENGLISH-LUGANDA TRANSLATOR\
|
|- dataset_loader_api.py          [API-based dataset loader]
|- train_kabale_professional.py   [Main training script]
|- app_streamlit_professional.py  [Production web app]
|- validate_setup.py              [Setup validator]
|
|- requirements.txt               [Dependencies]
|- DATASET_USAGE_GUIDE.md         [Dataset guide]
|- SETUP_GUIDE.md                 [This file]
|
|- data/                          [Data directory]
|  |- raw/                        [Original datasets]
|  |- processed/                  [Preprocessed data]
|  |- tokenized/                  [Tokenized data]
|
|- models/                        [Model directory]
|  |- trained_model_cpu/          [Trained model]
|
|- outputs/                       [Results directory]
|  |- evaluation_results.json     [Metrics]
|  |- training_summary.json       [Summary]
```

---

## CONFIGURATION PARAMETERS

### Training Configuration

```python
CONFIG = {
    # Data
    'dataset_name': 'kambale/luganda-english-parallel-corpus',
    
    # Model
    'base_model': 'Helsinki-NLP/opus-mt-en-mul',
    'trained_model_path': 'models/trained_model_cpu',
    
    # Training
    'epochs': 5,              # Number of training epochs
    'batch_size': 16,         # Batch size per device
    'learning_rate': 2e-5,    # Adam learning rate
    'max_length': 128,        # Max token sequence length
    'warmup_steps': 500,      # Learning rate warmup steps
    'seed': 42,              # Random seed for reproducibility
}
```

### Adjustment Guide

**For better quality:**
- Increase epochs: 5 -> 7 or 10
- Decrease learning_rate: 2e-5 -> 1e-5
- Increase warmup_steps: 500 -> 1000
- Increase batch_size: 16 -> 24 (if GPU available)

**For faster training:**
- Reduce epochs: 5 -> 3
- Reduce max_length: 128 -> 64
- Increase batch_size: 16 -> 32 (if GPU available)
- Reduce warmup_steps: 500 -> 100

**For memory constraints:**
- Reduce batch_size: 16 -> 8
- Reduce max_length: 128 -> 64
- Increase gradient_accumulation_steps

---

## TROUBLESHOOTING

### Problem 1: Dataset Access Denied

```
Error: "Dataset is a gated dataset"
```

Solution:
1. Request access: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
2. Wait for approval
3. Run: huggingface-cli login
4. Try again

### Problem 2: Authentication Failed

```
Error: "HuggingFace token not found" or "Authentication error"
```

Solution:
1. Get new token: https://huggingface.co/settings/tokens
2. Run: huggingface-cli login
3. Paste token when prompted
4. Or set: set HF_TOKEN=your_token_here

### Problem 3: Out of Memory

```
Error: "CUDA out of memory" or "MemoryError"
```

Solution:
- Reduce batch_size: 16 -> 8
- Reduce max_length: 128 -> 64
- Use CPU instead of GPU (slower but works)

### Problem 4: Slow Training

Training is taking too long (> 12 hours on CPU)

Solution:
- Use GPU acceleration (much faster)
- Reduce dataset size (use subset)
- Reduce max_length
- Reduce epochs

### Problem 5: Model Not Found on App Startup

```
Warning: Local model not found. Loading base model from HuggingFace
```

Solution:
1. Ensure training completed successfully
2. Check models/trained_model_cpu/ exists
3. Restart app after training
4. App will use base model as fallback

### Problem 6: Poor Translation Quality

Translations are not accurate

Solution:
1. Retrain with more epochs (5 -> 10)
2. Use larger batch size
3. Use more/better data
4. Fine-tune learning rate

---

## PERFORMANCE OPTIMIZATION

### Enable GPU Training

```bash
# Check if GPU available
python -c "import torch; print(torch.cuda.is_available())"

# Install GPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Speed Comparison

| Device | Training Time (5 epochs) | Inference Time |
|--------|--------------------------|-----------------|
| CPU | 4-8 hours | 500ms |
| GPU (GTX 1080) | 30-60 min | 50ms |
| GPU (A100) | 5-10 min | 10ms |

### Memory Requirements

| Stage | CPU RAM | GPU VRAM |
|-------|---------|---------|
| Data Loading | 2-4 GB | 0 GB |
| Model Loading | 1 GB | 4 GB |
| Training | 8 GB | 6-8 GB |
| Inference | 1 GB | 2 GB |

---

## DATASET INFORMATION

### Kabale Dataset

- **Size**: 100k+ parallel sentence pairs
- **Languages**: English - Luganda
- **Quality**: High (professionally curated)
- **Format**: JSON with translation dicts
- **Splits**: train, validation, test
- **Access**: Gated (approval required)

### Data Statistics

After loading:
- English sentences: 100,000+
- Luganda sentences: 100,000+
- Avg English length: 50-100 chars
- Avg Luganda length: 50-100 chars
- No significant quality issues

---

## DEVELOPMENT WORKFLOW

### Local Development

```bash
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Make changes to code
# (Edit files in text editor)

# 3. Test changes
python validate_setup.py

# 4. Run training
python train_kabale_professional.py

# 5. Test app
streamlit run app_streamlit_professional.py
```

### Git Workflow

```bash
# Track changes
git add .
git commit -m "Update training script"

# Push to repository
git push origin main
```

---

## PRODUCTION DEPLOYMENT

### Server Deployment

```bash
# Clone repository
git clone <repo>
cd ENGLISH-LUGANDA\ TRANSLATOR

# Setup
pip install -r requirements.txt
huggingface-cli login

# Train (one-time)
python train_kabale_professional.py

# Run app
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

## RESOURCES

### Official Documentation
- HuggingFace: https://huggingface.co/docs/
- Streamlit: https://docs.streamlit.io/
- PyTorch: https://pytorch.org/docs/

### Datasets
- Kabale: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
- Sunbird: https://huggingface.co/Sunbird

### Models
- MarianMT: https://huggingface.co/Helsinki-NLP/opus-mt-en-mul

---

## SUPPORT

For issues:
1. Check DATASET_USAGE_GUIDE.md
2. Review troubleshooting section
3. Check error message carefully
4. Verify all steps completed
5. Check internet connection
6. Verify authentication

---

## NEXT STEPS

1. [FIRST] Install requirements: `pip install -r requirements.txt`
2. [SECOND] Authenticate: `huggingface-cli login`
3. [THIRD] Request Kabale access: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
4. [FOURTH] Validate: `python validate_setup.py`
5. [FIFTH] Train: `python train_kabale_professional.py`
6. [SIXTH] Deploy: `streamlit run app_streamlit_professional.py`

---

**Professional English-Luganda Translation System**

Setup completed and ready for production use.
