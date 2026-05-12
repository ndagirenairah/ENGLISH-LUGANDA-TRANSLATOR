# KABALE DATASET DOWNLOADED - QUICK START GUIDE

## Dataset Information

**File**: `luganda_dataset.csv`  
**Size**: 5.69 MB  
**Rows**: 50,012 English-Luganda sentence pairs  
**Columns**: `english`, `luganda`  
**Location**: `d:\ENGLISH-LUGANDA TRANSLATOR\luganda_dataset.csv`

---

## TRAINING WITH DOWNLOADED DATASET

### Quick Start (3 Steps)

```bash
# Step 1: Run training
python train_with_kabale_csv.py

# Step 2: Wait for training (4-8 hours on CPU, 30-60 min on GPU)

# Step 3: Deploy the app
streamlit run app_streamlit_professional.py
```

---

## Training Script Details

**File**: `train_with_kabale_csv.py`

**12-Step Pipeline**:
1. Load CSV (luganda_dataset.csv)
2. Prepare and clean data
3. Split into 70% train / 15% val / 15% test
4. Convert to HuggingFace Datasets
5. Load MarianMT model
6. Tokenize with max_length=128
7. Configure training arguments
8. Initialize Seq2SeqTrainer
9. Train for 5 epochs
10. Evaluate on test set
11. Save model to `models/trained_model_kabale/`
12. Test inference on sample sentences

**Output Location**: `models/trained_model_kabale/`

---

## Data Split

| Set | Rows | Percentage |
|-----|------|-----------|
| Training | 35,008 | 70% |
| Validation | 7,502 | 15% |
| Test | 7,502 | 15% |
| **Total** | **50,012** | **100%** |

---

## Sample Data

**English**: "Eggplants always grow best under warm conditions."  
**Luganda**: "Bbiringanya lubeerera asinga kukulira mu mbeera ya bugumu"

---

## Model Information

**Model**: Helsinki-NLP/opus-mt-en-mul  
**Parameters**: 200 million  
**Max Length**: 128 tokens  
**Device**: Auto-detects CUDA or CPU

---

## Training Configuration

| Parameter | Value |
|-----------|-------|
| Epochs | 5 |
| Batch Size | 16 |
| Learning Rate | 2e-5 |
| Warmup Steps | 500 |
| Max Length | 128 |
| Optimizer | AdamW |

---

## Expected Results

**Training Time**:
- CPU: 4-8 hours
- GPU: 30-60 minutes

**Translation Quality**:
- BLEU Score: 25-35
- Training Loss: 1-2
- Validation Loss: 1-2

---

## After Training

### Deploy Streamlit App

```bash
streamlit run app_streamlit_professional.py
```

Access at: `http://localhost:8501`

### Use the Trained Model in Python

```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_path = "models/trained_model_kabale"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

text = "Hello, how are you?"
inputs = tokenizer(text, return_tensors="pt")
outputs = model.generate(**inputs)
translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(translation)
```

---

## Files Reference

| File | Purpose |
|------|---------|
| luganda_dataset.csv | Downloaded dataset (50,012 rows) |
| test_dataset.py | Dataset loading test |
| train_with_kabale_csv.py | Main training script (uses CSV) |
| train_kabale_professional.py | API-based training script |
| app_streamlit_professional.py | Production web interface |

---

## Troubleshooting

### Problem: "File not found: luganda_dataset.csv"

**Solution**: Run `python test_dataset.py` first to download and create the CSV file.

### Problem: "Out of memory" during training

**Solution**: 
1. Reduce batch_size: `per_device_train_batch_size=8`
2. Reduce max_length: `max_length=64`
3. Use GPU if available

### Problem: Training is very slow

**Solution**: Use GPU acceleration:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Problem: "CUDA out of memory"

**Solution**: Reduce batch size or max_length, or use CPU.

---

## Next Steps

1. **Run Test**: `python test_dataset.py` ✓ (Already done!)
2. **Train Model**: `python train_with_kabale_csv.py`
3. **Deploy App**: `streamlit run app_streamlit_professional.py`
4. **Use Translator**: Access at http://localhost:8501

---

## Dataset Column Reference

After loading from CSV, columns are:
- `english`: English text (50-200 characters typically)
- `luganda`: Luganda translation (50-200 characters typically)

Both columns are required for training.

---

**Status**: Dataset downloaded and ready for training! ✓
