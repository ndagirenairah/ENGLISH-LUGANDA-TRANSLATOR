@ -1,355 +0,0 @@
# Three ML Enhancements for 28+/30 BLEU Score

This guide documents three major enhancements implemented to improve the English-Luganda translator model to achieve a BLEU score of 28+/30 (Grade A).

## Overview

| Enhancement | Status | Impact | Implementation |
|---|---|---|---|
| **Stronger Base Model** | ✅ Complete | +2-3 BLEU | src/config.py |
| **Validation BLEU Tracking** | ✅ Complete | Enables Optimization | src/train.py |
| **Back-Translation Augmentation** | ✅ Complete | +3-5 BLEU | src/augmentation.py + Notebook STEP 4.5 |

---

## Enhancement 1: Stronger Base Model Selection

### Problem
Original model was general-purpose multilingual, not optimized for English-Luganda translation.

### Solution
Changed from `Helsinki-NLP/opus-mt-en-mul` → `Helsinki-NLP/opus-mt-en-lg`

- **opus-mt-en-mul**: General multilingual (trained on many language pairs)
- **opus-mt-en-lg**: English→Luganda specific (optimized for this exact task)

### Expected Impact
**+2-3 BLEU points** - Language-specific models consistently outperform general models.

### Configuration
**File**: `src/config.py`
```python
MODEL_NAME = "Helsinki-NLP/opus-mt-en-lg"  # Stronger: English-to-Luganda specific
BACK_TRANSLATION_MODEL = "Helsinki-NLP/opus-mt-lg-en"  # For augmentation
```

---

## Enhancement 2: Validation BLEU Tracking During Training

### Problem
No visibility into validation BLEU improvement during training. Couldn't monitor overfitting or convergence.

### Solution
Implemented `compute_metrics` callback in training loop.

**Features**:
- Computes BLEU score after **each epoch** on validation set
- Uses 200 validation samples for speed (configurable)
- Logs to console during training
- Enables early stopping based on BLEU progress

### Implementation Details

**File**: `src/train.py`

Two key functions added:
1. **`compute_bleu_metrics()`** - Computes BLEU on validation set
2. **`compute_metrics()` callback** - Integrated with Seq2SeqTrainer

```python
def compute_bleu_metrics(eval_dataset, model, tokenizer, sample_size=BLEU_EVAL_SAMPLES):
    """Compute BLEU score on validation set during training"""
    # Samples 200 validation examples
    # Generates predictions with model
    # Computes BLEU using sacrebleu
    # Returns {"bleu": score}

# In Seq2SeqTrainer:
trainer = Seq2SeqTrainer(
    ...,
    compute_metrics=compute_metrics if COMPUTE_BLEU_ON_VALIDATION else None,
)
```

### Configuration
**File**: `src/config.py`
```python
COMPUTE_BLEU_ON_VALIDATION = True   # Enable BLEU tracking
BLEU_EVAL_SAMPLES = 200              # Use 200 samples per epoch
TRAINING_METRICS_FILE = "outputs/training_metrics.json"  # Save results
```

### Expected Output During Training
```
Epoch 1/8: 
  BLEU: 18.42
  Loss: 2.15
  
Epoch 2/8:
  BLEU: 20.67 (+2.25)
  Loss: 1.89
  
...continues each epoch...
```

---

## Enhancement 3: Back-Translation Data Augmentation

### Problem
Limited training data diversity. Model sees same English→Luganda patterns repeatedly.

### Solution
Generate synthetic training pairs using back-translation:
1. Take existing Luganda translations
2. Translate Luganda → English using reverse model
3. Create synthetic pairs: (back-translated EN → original LU)
4. Double training dataset size
5. Train on mixed original + synthetic data

### Process Flow
```
Original Pair:
  English: "Hello world"
  Luganda: "Habari dunia"
  
Back-Translation Step 1 (LU→EN):
  Input: "Habari dunia"
  Back-Translated EN: "Hello universe"
  
Synthetic Pair Created:
  English: "Hello universe" (back-translated)
  Luganda: "Habari dunia" (original)
  
Result: Dataset size ~2x, more diverse patterns
```
