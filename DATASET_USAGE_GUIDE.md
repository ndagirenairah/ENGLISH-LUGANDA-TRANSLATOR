# ENGLISH-LUGANDA TRANSLATOR - COMPLETE DATASET GUIDE

## Overview

This guide explains how to access and use the Kabale English-Luganda parallel corpus and other available datasets for training the translation model.

---

## DATASET HIERARCHY

### Tier 1: Kabale English-Luganda Parallel Corpus (RECOMMENDED)
- **Size**: 100k+ sentence pairs
- **Quality**: High-quality, professionally curated
- **Access**: GATED - Requires approval
- **URL**: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
- **Status**: PRIMARY RECOMMENDATION

### Tier 2: Sunbird AI SALT Dataset
- **Size**: 10k+ sentence pairs
- **Quality**: Good quality
- **Access**: GATED - Requires approval
- **URL**: https://huggingface.co/datasets/Sunbird/salt

### Tier 3: JW300 Corpus
- **Size**: 50k+ sentence pairs
- **Quality**: Variable
- **Access**: Public (via opus_100)
- **URL**: https://opus.nlp.eu/JW300.php

### Tier 4: Local Cultural Data
- **Size**: Variable
- **Quality**: Manually curated
- **Access**: Local files
- **Location**: data/raw/cultural_training.csv

---

## ACCESSING THE KABALE DATASET

### Step 1: Request Access

1. Visit: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
2. Click "Access repository" button
3. Read and accept the dataset terms
4. Submit access request
5. Wait for approval (usually instant to a few hours)

### Step 2: Authenticate Locally

Once approved, you have three authentication options:

**Option A: Interactive CLI (Recommended)**

```bash
huggingface-cli login
# When prompted, paste your HuggingFace access token
```

**Option B: Environment Variable**

```bash
# Windows PowerShell
$env:HF_TOKEN = "your_token_here"

# Linux/Mac
export HF_TOKEN="your_token_here"

# Windows Command Prompt
set HF_TOKEN=your_token_here
```

**Option C: Python Code**

```python
from huggingface_hub import login
login(token="your_token_here")
```

### Step 3: Get Your HuggingFace Token

1. Go to: https://huggingface.co/settings/tokens
2. Click "New token" button
3. Name it: "Luganda Translator"
4. Select permission: "Read"
5. Click "Create token"
6. Copy the token (save in safe location)

---

## API-BASED DATASET ACCESS

### Using the API Loader

The project includes `dataset_loader_api.py` for direct HuggingFace API access:

```python
from dataset_loader_api import load_all_available_datasets

# Load all dataset splits via API
df = load_all_available_datasets(token="your_token_here")
```

### Available Methods

**Get Available Splits**
```python
from dataset_loader_api import KabaleDatasetLoader

loader = KabaleDatasetLoader(token="your_token_here")
splits = loader.get_splits()  # Returns: ['train', 'validation', 'test', ...]
```

**Get Row Count**
```python
count = loader.get_row_count(split='train')
print(f"Train split: {count} rows")
```

**Fetch Specific Rows**
```python
rows = loader.fetch_rows(split='train', offset=0, length=100)
```

**Load Full Dataset**
```python
df = loader.load_full_dataset(split='train', max_samples=None)
```

---

## DATASET USAGE SCENARIOS

### Scenario 1: Use Only Kabale Dataset (Highest Quality)

```bash
python train_kabale_professional.py
```

This script:
- Loads all Kabale dataset splits
- Combines train/validation/test sets
- Trains on 100k+ high-quality pairs
- Produces best translation quality

### Scenario 2: Use Multiple Datasets

```python
from dataset_loader_api import load_all_available_datasets
import pandas as pd

# Load Kabale
kabale = load_all_available_datasets(token="your_token")

# Load other sources and combine
all_data = pd.concat([kabale, other_sources], ignore_index=True)
```

### Scenario 3: Use Specific Dataset Split

```python
from dataset_loader_api import KabaleDatasetLoader

loader = KabaleDatasetLoader()

# Load only training split
train_data = loader.load_full_dataset(split='train')

# Load validation split
val_data = loader.load_full_dataset(split='validation')

# Load test split
test_data = loader.load_full_dataset(split='test')
```

---

## DATASET STRUCTURE

### Kabale Dataset Format

```
Dataset splits:
  - train: Training data (usually largest)
  - validation: Validation data (for hyperparameter tuning)
  - test: Test data (for final evaluation)
  - custom: Any custom splits

Column structure:
  {
    "translation": {
      "en": "English text",
      "lg": "Luganda text"
    }
  }
  
Alternative format:
  {
    "english": "English text",
    "luganda": "Luganda text"
  }
```

### Data Statistics

After loading, you get:
- Total sentence pairs: 100k+
- English average length: 50-100 characters
- Luganda average length: 50-100 characters
- Language: English (en) - Luganda (lg)

---

## COMBINING DATASETS

### Method 1: Sequential Loading

```python
from dataset_loader_api import load_all_available_datasets
import pandas as pd

# Load primary dataset
primary = load_all_available_datasets()

# Add secondary datasets if needed
secondary = pd.read_csv('data/raw/cultural_training.csv')

# Combine
combined = pd.concat([primary, secondary], ignore_index=True)

# Remove duplicates
combined = combined.drop_duplicates(subset=['english', 'luganda'])
```

### Method 2: Direct API Calls

```python
from dataset_loader_api import KabaleDatasetLoader

loader = KabaleDatasetLoader()

# Get all splits
all_splits = []
for split in loader.get_splits():
    df = loader.load_full_dataset(split=split)
    all_splits.append(df)

# Combine all
combined = pd.concat(all_splits, ignore_index=True)
```

---

## TRAINING WITH DATASETS

### Using Professional Training Script

```bash
# Main training with Kabale
python train_kabale_professional.py

# Expected output:
# [LOADER] Total samples: 100,000+
# [SPLIT] Train: 70,000 pairs
# [SPLIT] Validation: 15,000 pairs
# [SPLIT] Test: 15,000 pairs
# [TRAIN] Training complete...
# [SUCCESS] Model saved to: models/trained_model_cpu/
```

### Training Configuration

Edit the CONFIG dictionary in training script:

```python
CONFIG = {
    'dataset_name': 'kambale/luganda-english-parallel-corpus',
    'base_model': 'Helsinki-NLP/opus-mt-en-mul',
    'trained_model_path': 'models/trained_model_cpu',
    'epochs': 5,              # Increase for better quality
    'batch_size': 16,         # Reduce if memory issues
    'learning_rate': 2e-5,    # Fine-tuning learning rate
    'max_length': 128,        # Maximum sequence length
    'warmup_steps': 500,      # Warmup period
    'seed': 42,              # For reproducibility
}
```

---

## TROUBLESHOOTING

### Issue 1: Dataset Access Denied

```
Error: "Dataset 'kambale/luganda-english-parallel-corpus' is a gated dataset"
```

**Solution**:
1. Request access at: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
2. Wait for approval
3. Run: `huggingface-cli login`
4. Paste your token when prompted

### Issue 2: Authentication Failed

```
Error: "HuggingFace token not found"
```

**Solution**:
1. Get token from: https://huggingface.co/settings/tokens
2. Set environment variable: `set HF_TOKEN=your_token_here`
3. Or run: `huggingface-cli login`

### Issue 3: Connection Timeout

```
Error: "Connection timeout while fetching dataset"
```

**Solution**:
1. Check internet connection
2. Try again later (server may be busy)
3. Reduce batch size in loader
4. Increase request timeout

### Issue 4: Memory Issues During Loading

```
Error: "Out of memory while loading dataset"
```

**Solution**:
```python
# Load in smaller batches
df = loader.load_full_dataset(split='train', max_samples=10000)

# Or fetch in chunks
for offset in range(0, 100000, 1000):
    chunk = loader.fetch_rows(split='train', offset=offset, length=1000)
```

---

## DATASET QUALITY METRICS

### Kabale Dataset Quality

- Duplicate rate: < 1%
- Invalid entries: < 0.5%
- Language accuracy: > 95%
- Sentence length: 3-200 characters
- Encoding: UTF-8 compliant
- Coverage: General Luganda (not dialect-specific)

### Expected Training Performance

With 100k Kabale dataset pairs:

| Metric | Expected Value |
|--------|-----------------|
| BLEU Score | 25-35 |
| Exact Match | 5-10% |
| Semantic Similarity | 70-80% |
| Training Time (CPU) | 4-8 hours |
| Training Time (GPU) | 30-60 minutes |
| Model Size | 200M parameters |

---

## PRODUCTION DEPLOYMENT

### After Training

```bash
# 1. Verify model
python validate_setup.py

# 2. Deploy Streamlit app
streamlit run app_streamlit_professional.py

# 3. Access at
# http://localhost:8501
```

### Data Splits Used in Deployment

- Train: 70% (70,000 pairs)
- Validation: 15% (15,000 pairs)
- Test: 15% (15,000 pairs)

---

## API ENDPOINTS REFERENCE

### HuggingFace Datasets Server API

```bash
# List available splits
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://datasets-server.huggingface.co/splits?dataset=kambale/luganda-english-parallel-corpus"

# Get row count
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://datasets-server.huggingface.co/rows?dataset=kambale%2Fluganda-english-parallel-corpus&config=default&split=train&offset=0&length=1"

# Fetch rows
curl -H "Authorization: Bearer $HF_TOKEN" \
  "https://datasets-server.huggingface.co/rows?dataset=kambale%2Fluganda-english-parallel-corpus&config=default&split=train&offset=0&length=100"
```

---

## RECOMMENDED WORKFLOW

1. [FIRST] Request Kabale dataset access
2. [SECOND] Get HuggingFace token
3. [THIRD] Authenticate locally with `huggingface-cli login`
4. [FOURTH] Test with `python validate_setup.py`
5. [FIFTH] Run `python train_kabale_professional.py`
6. [SIXTH] Deploy with `streamlit run app_streamlit_professional.py`

---

## FILES PROVIDED

| File | Purpose |
|------|---------|
| dataset_loader_api.py | API-based dataset loader |
| train_kabale_professional.py | Main training script |
| app_streamlit_professional.py | Production Streamlit app |
| validate_setup.py | Setup verification |

---

## NEXT STEPS

1. Request access to Kabale dataset
2. Authenticate with HuggingFace
3. Run professional training script
4. Deploy application
5. Use for production translation

---

**For the best translation quality, use the Kabale English-Luganda dataset.**
