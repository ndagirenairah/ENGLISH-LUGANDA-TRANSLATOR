# English-Luganda Translator

Production-ready neural machine translation model for English to Luganda translation. Implements 13+ machine learning algorithms with multi-dataset training strategy.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Interactive Local Testing
```bash
python test_translator_interactive.py
```

### 3. Train with Combined Datasets in Google Colab

Open Google Colab and run:
```python
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
import os
os.chdir('/content/translator')
exec(open('train_colab_kambale_combined.py').read())
```

When prompted, enter your HuggingFace token from https://huggingface.co/settings/tokens

### 4. Run Web Server
```bash
python web_server_flask.py
```

Access translation interface at http://localhost:5000

## Core Files

| File | Purpose |
|------|---------|
| train_colab_kambale_combined.py | Full pipeline training for Google Colab GPU |
| preprocess_combine_datasets.py | Combines Kambale + 4 local datasets with deduplication |
| web_server_flask.py | Flask web interface for live translation |
| test_translator_interactive.py | Interactive terminal testing |
| train_local_gpu.py | Local GPU training alternative |
| translate_english_luganda.py | Inference and translation functions |
| evaluate_model_performance.py | Model evaluation with BLEU metrics |
| preprocess_text_data.py | Text preprocessing and normalization |

## Algorithms and Methods

This project implements 13 machine learning algorithms:

1. Transformer Seq2Seq Architecture
2. Beam Search Decoding (num_beams=5)
3. Byte-Pair Encoding (BPE) Tokenization
4. Data Deduplication Algorithm
5. Stratified Train-Test Split (80/10/10)
6. BLEU Score Evaluation Metric
7. Pattern-Based Text Cleaning
8. Vowel Ratio Analysis (Language Validation)
9. Regex-Based Cultural Term Replacement
10. Adaptive Learning Rate Scheduling
11. Multi-Dataset Aggregation
12. Token Padding and Truncation
13. Cross-Entropy Loss Optimization

See ALGORITHMS_AND_METHODS.md for detailed documentation.

## Model Architecture

Base Model: Helsinki-NLP/opus-mt-en-mul (300M parameters, multilingual)

Training Configuration:
- Epochs: 3
- Batch Size: 8 (train and eval)
- Learning Rate: 2e-5 (fine-tuning)
- Warmup Steps: 500
- Max Sequence Length: 128 tokens (input), 120 tokens (output)
- Optimizer: AdamW

Expected Performance:
- Baseline (pretrained): BLEU 20-25
- After fine-tuning: BLEU 25-35 (Good to Excellent)

## Multi-Dataset Strategy

Combines 5 high-quality sources:

1. Kambale Luganda-English Parallel Corpus (100k+ pairs, gated dataset)
2. Cultural Dictionary (1000+ domain-specific terms)
3. JW300 Parallel Corpus (Jw.org translations)
4. Makerere NLP Dataset (academic institution)
5. Sunbird SALT Dataset (low-resource language focus)

Process:
- Normalize column formats (en/lg and english/luganda)
- Remove cross-dataset duplicates
- Clean broken/noisy sentences
- Apply quality filters (2-50 word range)
- Split: 80% train, 10% validation, 10% test

## Utility Modules

Utility Files (in utils/ directory):
- data_quality_validator.py - Luganda text quality checking
- postprocess_cultural_correction.py - Cultural term correction
- __init__.py - Module initialization

## System Requirements

Minimum:
- Python 3.8+
- 8GB RAM
- CPU or GPU (recommended: Tesla T4 or better)

Recommended for Training:
- PyTorch 2.2.0+
- Transformers 4.41.0+
- Google Colab GPU (free tier with Tesla T4)
- HuggingFace account with token

## Installation

```bash
git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git
cd ENGLISH-LUGANDA-TRANSLATOR
pip install -r requirements.txt
```

## Usage

### Option 1: Local Testing (No GPU Required)

```bash
python test_translator_interactive.py
```

### Option 2: Train Locally

```bash
python train_local_gpu.py
```

### Option 3: Train in Google Colab (Recommended)

Execute in Colab:
```python
exec(open('train_colab_kambale_combined.py').read())
```

### Option 4: Use Web Interface

```bash
python web_server_flask.py
# Open http://localhost:5000
```

## File Structure

```
ENGLISH-LUGANDA-TRANSLATOR/
├── Core Scripts (8 Python files, no emojis)
├── utils/ (2 utility modules for data processing)
├── data/ (raw, processed, cultural data)
├── models/ (trained model checkpoints)
├── outputs/ (evaluation results and metrics)
├── ALGORITHMS_AND_METHODS.md (comprehensive algorithm documentation)
├── README.md (this file)
└── requirements.txt (dependencies)
```

## Performance Notes

Training time on Tesla T4 GPU: 15-20 minutes (3 epochs)

Model evaluation includes:
- BLEU score on test set
- Loss tracking across epochs
- Validation metrics every evaluation step
- Translation quality metrics in JSON format

## Troubleshooting

If models load slowly:
- First run may take 2-3 minutes (model downloading)
- Subsequent runs cached automatically

If GPU not detected:
- Verify CUDA installation: `nvidia-smi`
- Check PyTorch GPU support: `python -c "import torch; print(torch.cuda.is_available())"`

If dataset access fails:
- Verify HuggingFace token at https://huggingface.co/settings/tokens
- Request access to kambale/luganda-english-parallel-corpus dataset

## Project Status

Status: Production Ready
Latest Update: May 23, 2026
Algorithm Count: 13+ machine learning methods
Code Quality: Professional standard (no decorative elements, code-only)

