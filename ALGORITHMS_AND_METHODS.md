# Machine Learning Algorithms and Methods Used

## English-Luganda Neural Machine Translation Project

This document lists the 10+ algorithms and machine learning methods implemented in this project.

---

## 1. Transformer Architecture (Seq2Seq)

**Purpose**: Core neural network architecture for sequence-to-sequence translation

**Implementation**: Helsinki-NLP/opus-mt-en-mul (MarianMT)

**Details**:
- Multi-head self-attention mechanism
- Encoder-decoder architecture
- Positional encoding for word positions
- Feed-forward networks with ReLU activation
- Layer normalization for training stability

**Files**: train_colab_kambale_combined.py, train_local_gpu.py, translate_english_luganda.py

---

## 2. Beam Search Decoding

**Purpose**: Generate high-quality translations by exploring multiple hypotheses

**Parameters Used**:
- num_beams=5: Maintains 5 best hypotheses
- max_length=120: Maximum token output length
- no_repeat_ngram_size=3: Prevents 3-gram repetition

**Implementation**: transformers.AutoModelForSeq2SeqLM.generate()

**Files**: train_colab_kambale_combined.py, translate_english_luganda.py, test_translator_interactive.py

---

## 3. Byte-Pair Encoding (BPE) Tokenization

**Purpose**: Subword tokenization for efficient handling of rare words

**Details**:
- SentencePiece tokenizer for multilingual support
- Converts text to tokens for model input
- Vocabulary size optimized for 300+ languages
- Handles unknown characters gracefully

**Implementation**: transformers.AutoTokenizer

**Files**: translate_english_luganda.py, train_colab_kambale_combined.py

---

## 4. Data Deduplication Algorithm

**Purpose**: Remove duplicate sentence pairs from dataset

**Method**: 
- Lowercase both English and Luganda text
- Remove exact duplicate (english, luganda) pairs
- Preserves data quality and prevents model bias

**Implementation**: pandas DataFrame drop_duplicates()

**Files**: preprocess_combine_datasets.py, data_quality_validator.py

---

## 5. Stratified Train-Test Split

**Purpose**: Ensure representative data distribution across train/validation/test sets

**Split Ratio**: 80% train, 10% validation, 10% test

**Details**:
- Fixed seed=42 for reproducibility
- Maintains class balance
- Prevents data leakage

**Implementation**: sklearn.model_selection.train_test_split()

**Files**: preprocess_combine_datasets.py, train_colab_kambale_combined.py

---

## 6. BLEU Score Evaluation Metric

**Purpose**: Quantify translation quality on test set

**Details**:
- Corpus-level BLEU score (sacreBLEU)
- Precision of n-grams (1-gram to 4-gram)
- Reference-based evaluation
- Score range: 0-100 (higher is better)

**Expected Results**: 25-35 BLEU after 3 epochs on Tesla T4 GPU

**Implementation**: sacrebleu.corpus_bleu()

**Files**: train_colab_kambale_combined.py, evaluate_model_performance.py

---

## 7. Pattern-Based Text Cleaning

**Purpose**: Remove broken or noisy Luganda sentences

**Patterns Removed**:
- Broken constructions: "ere gye", "werebwamu"
- Placeholders: "xxx", "xxxx"
- Long numbers (>5 digits)
- Non-alphabetic characters
- Sentences <2 words or >25 words

**Implementation**: regex pattern matching in LugandaDataCleaner

**Files**: data_quality_validator.py, preprocess_text_data.py

---

## 8. Vowel Ratio Analysis

**Purpose**: Validate Luganda authenticity based on phonetic patterns

**Method**:
- Luganda languages have 40-60% vowels
- Check vowel-to-consonant ratio
- Reject text with unusual ratios (e.g., 3% or 95% vowels)
- Identifies machine-generated or corrupted text

**Implementation**: vowel counting in is_clean_luganda()

**Files**: data_quality_validator.py

---

## 9. Regex-Based Cultural Term Replacement

**Purpose**: Apply domain-specific post-processing for cultural accuracy

**Replacements**:
- Clan names: "Mamba" -> "ekika kya mbwa"
- Royal titles: "king" -> "Kabaka"
- Cultural terms: "totem" -> "muzizo"
- Kingdom references: "Buganda" -> "Buganda"

**Implementation**: re.sub() with case-insensitive matching

**Files**: postprocess_cultural_correction.py

---

## 10. Adaptive Learning Rate Scheduling

**Purpose**: Optimize training convergence and prevent overfitting

**Configuration**:
- Initial learning rate: 2e-5 (fine-tuning rate)
- Warmup steps: 500 (gradual learning rate increase)
- Linear warmup schedule
- Prevents early instability in training

**Implementation**: Seq2SeqTrainingArguments warmup_steps

**Files**: train_colab_kambale_combined.py, train_local_gpu.py

---

## 11. Multi-Dataset Aggregation

**Purpose**: Combine multiple data sources for improved model robustness

**Datasets Combined**:
1. Kambale Parallel Corpus (100k+ high-quality pairs, gated access)
2. Cultural Terminology Dataset (custom domain-specific pairs)
3. JW300 Parallel Corpus (Jw Org translation data)
4. Makerere NLP Dataset (academic institution data)
5. Sunbird SALT Dataset (low-resource language data)

**Process**:
- Normalize column names (en/lg vs english/luganda)
- Concatenate datasets
- Remove cross-dataset duplicates
- Apply quality filters
- Split into train/val/test

**Implementation**: pandas concat() + deduplication

**Files**: preprocess_combine_datasets.py

---

## 12. Token Padding and Truncation

**Purpose**: Ensure uniform input tensor sizes for batch processing

**Parameters**:
- Padding: "max_length" to longest sequence
- Truncation: max_length=128 tokens for input, 120 for output
- Padding token: 0 (reserved)
- Special tokens: <s> (start), </s> (end), <unk> (unknown)

**Implementation**: AutoTokenizer with pad_token_id

**Files**: train_colab_kambale_combined.py, translate_english_luganda.py

---

## 13. Cross-Entropy Loss Function

**Purpose**: Optimize model weights during training

**Details**:
- Language modeling loss at each token position
- Compares model predictions vs. ground truth
- Backpropagation updates 300M+ parameters
- Combined with label smoothing (default=0.1 in transformers)

**Implementation**: PyTorch native cross_entropy_loss in Seq2SeqTrainer

**Files**: train_colab_kambale_combined.py, train_local_gpu.py

---

## Summary of Algorithms

| # | Algorithm | Category | Purpose |
|---|-----------|----------|---------|
| 1 | Transformer (Seq2Seq) | Neural Architecture | Translation modeling |
| 2 | Beam Search | Decoding | High-quality translation generation |
| 3 | BPE Tokenization | Preprocessing | Text tokenization |
| 4 | Deduplication | Data Cleaning | Remove duplicates |
| 5 | Stratified Split | Data Management | Train/Val/Test partition |
| 6 | BLEU Score | Evaluation | Quantify translation quality |
| 7 | Pattern Cleaning | Data Quality | Remove broken sentences |
| 8 | Vowel Analysis | Validation | Detect corrupted text |
| 9 | Cultural Replacement | Post-processing | Domain-specific correction |
| 10 | Learning Rate Scheduling | Training | Optimize convergence |
| 11 | Multi-Dataset Aggregation | Feature Engineering | Combine data sources |
| 12 | Token Padding/Truncation | Preprocessing | Uniform tensor sizes |
| 13 | Cross-Entropy Loss | Optimization | Model weight updates |

---

## Expected Performance

**Training Configuration**:
- Model: Helsinki-NLP/opus-mt-en-mul (300M parameters)
- GPU: Tesla T4 (Google Colab)
- Epochs: 3
- Batch Size: 8
- Training Time: 15-20 minutes

**Baseline (Pretrained Model)**:
- BLEU Score: 20-25

**After Fine-tuning**:
- BLEU Score: 25-35 (Good to Excellent)

---

## Technology Stack

- **PyTorch** (>=2.2.0): Tensor operations, GPU acceleration
- **Transformers** (>=4.41.0): Pretrained models, tokenizers, trainers
- **HuggingFace Datasets**: Dataset loading and management
- **SacreBLEU**: BLEU score computation
- **Pandas**: Data manipulation and analysis

---

**Last Updated**: May 23, 2026
**Project**: English-Luganda Neural Machine Translator
**Status**: Production-Ready
