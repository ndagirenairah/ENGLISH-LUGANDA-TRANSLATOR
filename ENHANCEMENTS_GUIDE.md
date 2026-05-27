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

