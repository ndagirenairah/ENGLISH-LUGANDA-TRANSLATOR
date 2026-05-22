# English-Luganda Translator

Neural Machine Translation model for English to Luganda translation using the Kambale corpus and multiple high-quality datasets.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Local Testing
```bash
python test_translation_interactive.py
```

### 3. Train in Google Colab

Open Google Colab and run:
```python
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
import os
os.chdir('/content/translator')
exec(open('COLAB_TRAIN_KAMBALE_COMBINED.py').read())
```

When prompted, enter your HuggingFace token from https://huggingface.co/settings/tokens

### 4. Run Flask Server
```bash
python app.py
```

Access at http://localhost:5000

## Files

- COLAB_TRAIN_KAMBALE_COMBINED.py - Google Colab training script
- combine_datasets_with_token.py - Dataset combination with HuggingFace authentication
- app.py - Flask web interface
- test_translation_interactive.py - Interactive local testing
- train.py - Local training
- evaluate.py - Model evaluation
- inference.py - Inference utilities
- preprocess.py - Data preprocessing
- requirements.txt - Dependencies

## Model

Base: Helsinki-NLP/opus-mt-en-mul (300M parameters)

Training:
- Epochs: 3
- Batch size: 8
- Learning rate: 2e-5
- Expected BLEU: 25-35

## Dataset

Combines:
- Kambale Luganda-English Parallel Corpus (100k+ pairs)
- Cultural dictionary
- JW300 parallel corpus
- Makerere NLP corpus
- Sunbird Salt dataset

## Requirements

- Python 3.8+
- PyTorch 2.2.0+
- Transformers 4.41.0+
- Google Colab GPU (Tesla T4 recommended)
- HuggingFace token for dataset access

