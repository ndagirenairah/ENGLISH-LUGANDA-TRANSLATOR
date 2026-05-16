# English <-> Luganda Transformer NMT System

This project implements a full Neural Machine Translation workflow using Transformer models and Hugging Face.

It supports:
- English -> Luganda translation
- Luganda -> English translation
- Data collection and preprocessing
- Tokenization and train/val/test splitting
- Fine-tuning with checkpoints
- BLEU-based evaluation
- Inference API
- Voice input (speech-to-text) and text-to-speech
- Optional attention visualization

## 1) Transformer Architecture

The system uses pretrained sequence-to-sequence Transformer models from Hugging Face and fine-tunes them on Luganda-English parallel data.

Default model choices:
- `Helsinki-NLP/opus-mt-en-lg` for English -> Luganda
- `Helsinki-NLP/opus-mt-lg-en` for Luganda -> English

Fallback models (if needed):
- `Helsinki-NLP/opus-mt-en-mul`
- `Helsinki-NLP/opus-mt-mul-en`

Why Transformers:
- Encoder-decoder attention for long-range dependencies
- Strong transfer learning from pretrained multilingual corpora
- Better quality than traditional phrase-based systems in low-resource setups

## 2) Project Structure

- `preprocess.py`: data collection, cleaning, deduplication, train/val/test split
- `train.py`: tokenization, fine-tuning, BLEU evaluation, checkpointing, model saving
- `inference.py`: bidirectional inference, language detection, hallucination reduction, attention plotting
- `app.py`: production Flask API with translation + STT + TTS + attention endpoint
- `requirements.txt`: dependencies for training and deployment

Important folders:
- `data/raw/`: raw parallel datasets
- `data/processed/`: split datasets (`train.csv`, `val.csv`, `test.csv`)
- `models/en-lg/` and `models/lg-en/`: checkpoints and final trained models
- `outputs/`: summaries, generated files (attention plot, TTS audio)
- `tests/`: validation scripts for post-training quality checks
- `docs/`: documentation (`ML_PIPELINE_GUIDE.md`) and archived legacy notes
- `scripts/legacy/`: archived older step-by-step training scripts

## 3) Dataset Pipeline

The preprocessing script merges parallel corpora from local CSV files and can optionally augment with online Hugging Face datasets.

Expected normalized columns:
- `english`
- `luganda`

Pipeline steps in `preprocess.py`:
1. Load local sources
2. Optionally load Hugging Face sources
3. Normalize columns
4. Clean text (whitespace, URL removal)
5. Filter noisy/empty pairs by length
6. Deduplicate parallel pairs
7. Split into train/val/test (80/10/10)
8. Save statistics JSON

## 4) Training Workflow (PyTorch + Hugging Face)

`train.py` performs true Transformer fine-tuning using `Seq2SeqTrainer` and `AutoModelForSeq2SeqLM`.

Includes:
- tokenization using model tokenizer
- epoch-based validation
- checkpoint saving each epoch
- BLEU scoring (`sacrebleu` via `evaluate`)
- best-checkpoint selection
- final model export

Google Colab GPU optimizations included:
- `fp16` auto-enabled when CUDA is available
- gradient checkpointing
- gradient accumulation
- beam search generation during evaluation

## 5) Inference and Hallucination Reduction

`inference.py` provides:
- automatic language direction selection
- beam search decoding
- `no_repeat_ngram_size` and repetition penalty
- simple post-generation repetition cleanup

This helps reduce repetitive and hallucinatory outputs in low-resource conditions.

## 6) Voice Features

`app.py` includes:
- `POST /api/stt`: speech-to-text (audio upload)
- `POST /api/tts`: text-to-speech (returns MP3)

Note: gTTS has limited direct support for Luganda, so `lang` is configurable and falls back to English when unsupported.

## 7) Attention Visualization

If supported by the loaded model, `inference.py` can export encoder attention heatmaps:
- `POST /api/attention`
- saves an image to `outputs/attention.png`

## 8) Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 9) Usage

### Step A: Preprocess data
```bash
python preprocess.py --output-dir data/processed
```

Optional with online dataset augmentation:
```bash
python preprocess.py --use-hf --output-dir data/processed
```

### Step B: Train both directions
```bash
python train.py --direction both --data-dir data/processed --output-dir models --epochs 3
```

Train one direction only:
```bash
python train.py --direction en-lg --data-dir data/processed --output-dir models
python train.py --direction lg-en --data-dir data/processed --output-dir models
```

### Step C: Run API
```bash
python app.py
```

API base URL:
- `http://localhost:5000`

Frontend page:
- `http://localhost:5000/`

API info endpoint:
- `http://localhost:5000/api`

### Step D: Run automatic post-training quality test
```bash
python tests/test_after_training.py --test-csv data/processed/test.csv --max-samples 200
```

This runs:
- corpus BLEU for EN -> LG
- corpus BLEU for LG -> EN
- sample translation checks
- JSON report output at `outputs/post_training_test_report.json`

### Example translation request
```bash
curl -X POST http://localhost:5000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "How are you?", "source_lang": "english", "target_lang": "luganda"}'
```

## 10) Evaluation Metrics

Primary metric:
- BLEU score on held-out test split

Training artifacts:
- `models/<direction>/checkpoints/`
- `models/<direction>/final/`
- `models/<direction>/metrics.json`
- `outputs/training_summary_transformer.json`

## 11) Production Notes

- Keep preprocessing and training deterministic using fixed seeds.
- Store checkpoints regularly and archive best model versions.
- Validate BLEU and run human evaluation on culturally sensitive terms.
- For stronger STT quality, you can replace SpeechRecognition backend with a Whisper model.

## 12) Beginner-Friendly Tips

- Start with local CSV preprocessing first.
- Train only one direction (`en-lg`) before training both.
- Keep epochs low initially (1-2) to verify pipeline end-to-end.
- Use attention plots to inspect whether the model is focusing on relevant tokens.
