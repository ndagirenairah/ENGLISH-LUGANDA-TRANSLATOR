# QUICK REFERENCE - KABALE DATASET & TRAINING COMMANDS

## 📌 KEY FILES (USE THESE)

```
luganda_dataset.csv              ← 50,012 rows downloaded and ready
train_with_kabale_csv.py         ← Use this to train (RECOMMENDED)
app_streamlit_professional.py    ← Use this to deploy web app
```

---

## ⚡ THREE ESSENTIAL COMMANDS

### Command 1: TRAIN THE MODEL
```bash
python train_with_kabale_csv.py
```
- Loads 50,012 Kabale dataset rows
- Trains MarianMT for 5 epochs
- Takes 4-8 hours (CPU) or 30-60 min (GPU)
- Output: `models/trained_model_kabale/`

### Command 2: DEPLOY WEB APP
```bash
streamlit run app_streamlit_professional.py
```
- Starts Streamlit server
- Access at: `http://localhost:8501`
- Features: Translation, History, Phrasebook, About

### Command 3: TEST DATA (OPTIONAL)
```bash
python test_dataset.py
```
- Verifies dataset loads correctly
- Shows first 20 rows
- Confirms 50,012 pairs available

---

## 📊 DATASET SUMMARY

| Field | Value |
|-------|-------|
| **File** | luganda_dataset.csv |
| **Rows** | 50,012 |
| **Size** | 5.69 MB |
| **Columns** | english, luganda |
| **Source** | kambale/luganda-english-parallel-corpus |
| **Status** | ✓ READY |

---

## 📈 TRAINING SUMMARY

| Parameter | Value |
|-----------|-------|
| **Model** | Helsinki-NLP/opus-mt-en-mul |
| **Epochs** | 5 |
| **Batch Size** | 16 |
| **Learning Rate** | 2e-5 |
| **Max Length** | 128 |
| **Output Dir** | models/trained_model_kabale/ |

---

## ⏱️ TIME ESTIMATES

| Device | Training Time |
|--------|---------------|
| **CPU** | 4-8 hours |
| **GPU (GTX 1080)** | 30-60 minutes |
| **GPU (RTX 4090)** | 5-10 minutes |

---

## 🚀 FASTEST PATH TO WORKING TRANSLATOR

```bash
# Step 1: Start training (takes time)
python train_with_kabale_csv.py

# Step 2: (After training completes) Start web app
streamlit run app_streamlit_professional.py

# Step 3: Use translator at http://localhost:8501
```

---

## ✅ WHAT'S READY NOW

| Item | Status |
|------|--------|
| Dataset (CSV) | ✓ READY |
| Training Script | ✓ READY |
| Web App Script | ✓ READY |
| Documentation | ✓ READY |
| Trained Model | ⏳ PENDING (run training) |

---

## 🎯 SAMPLE DATA

**English**: "Eggplants always grow best under warm conditions."  
**Luganda**: "Bbiringanya lubeerera asinga kukulira mu mbeera ya bugumu"

---

## 📁 FILE LOCATIONS

```
d:\ENGLISH-LUGANDA TRANSLATOR\
├── luganda_dataset.csv              [50,012 rows - READY]
├── train_with_kabale_csv.py         [Training script - READY]
├── app_streamlit_professional.py    [Web app - READY]
└── models/
    └── trained_model_kabale/        [Will be created after training]
```

---

## 🔧 TROUBLESHOOTING

**Problem**: "File not found: luganda_dataset.csv"  
**Fix**: Run `python test_dataset.py`

**Problem**: Training is slow  
**Fix**: Use GPU or reduce max_length to 64

**Problem**: "CUDA out of memory"  
**Fix**: Reduce batch_size to 8

---

## 📱 FEATURES AFTER TRAINING

- Real-time English ↔ Luganda translation
- Confidence scoring
- Translation history
- 60+ learning phrases
- Voice input/output support
- Professional web interface

---

## 🎓 LEARNING PATH

1. Run training: `python train_with_kabale_csv.py` (4-8h)
2. Deploy app: `streamlit run app_streamlit_professional.py`
3. Use translator: Visit `http://localhost:8501`
4. Customize: Edit config in scripts as needed

---

## 💡 PRO TIPS

- Training on GPU is 10x faster
- Start training overnight (CPU), use app next day
- Save model paths for production deployment
- Monitor training logs for issues

---

## 📚 DOCUMENTATION FILES

| File | Purpose |
|------|---------|
| TRAINING_READY_STATUS.md | Complete status report |
| KABALE_DATASET_DOWNLOADED.md | Dataset quick start |
| DATASET_ACCESS_OPTIONS.md | 3 ways to access data |
| SETUP_GUIDE.md | Installation & setup |
| DATASET_USAGE_GUIDE.md | Detailed reference |

---

## ✨ YOU ARE HERE

```
✓ Dataset downloaded
✓ Training scripts ready
✓ Web app ready
→ READY TO TRAIN (run command below)
→ READY TO DEPLOY (after training)
```

---

## 🎬 START HERE

```bash
python train_with_kabale_csv.py
```

This single command will:
- Load 50,012 training pairs
- Train model for 5 epochs
- Evaluate performance
- Save trained model
- Test inference

**Then after training**, deploy with:
```bash
streamlit run app_streamlit_professional.py
```

---

**Everything is ready. Run the training command above to begin!** ✨
