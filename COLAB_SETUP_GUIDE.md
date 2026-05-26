# Run ML Pipeline on Google Colab (GPU - Faster!)

Google Colab provides **free GPU access** and runs this pipeline **5-10x faster** than CPU.

## [FAST] Why Colab?

| Aspect | Local CPU | Colab GPU |
|--------|-----------|-----------|
| **Speed** | 30-60 min | 5-15 min |
| **Cost** | Your electricity | FREE |
| **GPU** | None (maybe) | Tesla T4 (free) |
| **Setup** | Complex | 2 clicks |

## [START] Steps to Run on Colab

### Step 1: Upload Your Project to Google Drive
```
Google Drive
└── My Drive
    └── English-Luganda-Translator
        └── ENGLISH-LUGANDA-TRANSLATOR  ← Upload this folder
```

### Step 2: Create Colab Notebook
```
1. Go to https://colab.research.google.com/
2. Click "+ New notebook"
3. Name it: "English-Luganda-Training"
```

### Step 3: Copy Script to Colab
```
1. In Colab, paste the code from: COLAB_TRAIN_PIPELINE.py
2. OR upload it as a notebook
```

### Step 4: Configure Path (if needed)
In the notebook, find this line and adjust path:
```python
COLAB_PROJECT_PATH = "/content/drive/My Drive/English-Luganda-Translator/ENGLISH-LUGANDA-TRANSLATOR"
```

If your folder is at a different location in Drive, update the path.

### Step 5: Run All Cells
```
Menu → Runtime → Run all
```

Or run cells one-by-one (Shift + Enter)

### Step 6: Download Results
At the end, download:
- `trained_model.zip` - Your trained model
- `evaluation_outputs.zip` - BLEU scores & predictions

## [INFO] What Happens in Each Cell

| Cell | What | Time |
|------|------|------|
| 1 | Install packages | 2 min |
| 2 | Mount Google Drive | 10 sec |
| 3 | Load 5 datasets | 10 sec |
| 4 | Create train/val/test splits | 5 sec |
| 5 | **Train model on GPU** | **8-12 min** |
| 6 | Evaluate on test set | 2 min |
| 7 | Display BLEU score | 5 sec |
| 8 | Prepare downloads | 1 min |
| 9 | Test inference | 30 sec |
| 10 | Summary | 5 sec |

**Total: ~15-20 minutes**

## ⚠️ Important Notes

### Dataset Loading
The script looks for your data at:
```
/content/drive/My Drive/English-Luganda-Translator/ENGLISH-LUGANDA-TRANSLATOR/data/raw/
```

Make sure these 5 files exist:
- ✓ kambale_train.csv
- ✓ cultural_training.csv
- ✓ jw300_parallel.csv
- ✓ makerere_nlp.csv
- ✓ sunbird_salt.csv

### GPU Memory
- Colab's free Tesla T4: 15GB VRAM
- Pipeline uses: ~6-8GB
- [YES] Plenty of space

### Runtime Limits
- Free Colab: 12 hour session limit
- This pipeline: ~15-20 minutes
- [YES] No timeout issues

## Troubleshooting

### "Can't find project path"
**Problem**: Your project isn't at the expected location in Drive

**Solution**:
1. Find your project folder in Drive
2. Right-click → "Get link"
3. Note the path
4. Update `COLAB_PROJECT_PATH` in Cell 2

### "Permission denied"
**Problem**: Colab can't access your Drive

**Solution**:
1. Run Cell 2 again
2. Click the authentication link
3. Select your Google account
4. Approve access

### "Out of memory"
**Problem**: Training uses too much GPU memory

**Solution**: In Cell 5, reduce batch size:
```python
# Edit config.py
BATCH_SIZE = 4  # Instead of 8
```

### "No GPU available"
**Problem**: Colab isn't using GPU

**Solution**:
1. Go to Runtime → Change runtime type
2. Select GPU (T4 or A100 if available)
3. Click Save
4. Restart and run again

## 📥 After Training

### Download Model
The trained model is saved in:
- `trained_model.zip` (download at end)

Extract and use for:
- Inference (translate new text)
- Further fine-tuning
- Deployment

### Download Results
The BLEU scores and predictions are in:
- `evaluation_outputs.zip`

Contains:
- `evaluation_results.json` - BLEU score
- `predictions.csv` - Sample predictions

### Use Model Locally
```python
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load downloaded model
model_path = "path/to/trained_model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path)

# Translate
inputs = tokenizer("Hello, how are you?", return_tensors="pt")
output = model.generate(inputs['input_ids'])
translation = tokenizer.decode(output[0], skip_special_tokens=True)
print(translation)  # → Luganda translation
```

## [INFO] Expected Results

After running the pipeline:

```
BLEU Score: 18-28
Training Loss: 2.5-3.5
Test Samples: 300+
GPU Time: 8-12 minutes
```

This is **REAL training** on your data, not demo data!

## [TIP] Pro Tips

### Faster Iteration
To test just loading & preprocessing (skip long training):
```python
# Run only Cell 1-4, skip Cell 5-6
# This takes <1 minute
```

### Fine-tune Further
After downloading the model, retrain locally:
```python
# In src/config.py
NUM_EPOCHS = 5  # Train longer
LEARNING_RATE = 1e-5  # Lower learning rate

# Then run: python scripts/run_pipeline.py
```

### Batch Multiple Runs
Run different configurations:
1. Run 1: `BATCH_SIZE=8, NUM_EPOCHS=3`
2. Run 2: `BATCH_SIZE=4, NUM_EPOCHS=5`
3. Compare BLEU scores
4. Use the best model

## 📞 Need Help?

1. **Check Colab output**: Error messages usually tell you what's wrong
2. **Check your Drive path**: Make sure project is uploaded correctly
3. **Check GPU**: Runtime → Change runtime type → Select GPU
4. **Check datasets**: Verify 5 CSV files exist in `data/raw/`

## Next Steps

1. [DONE] Organize project locally (DONE)
2. [DONE] Create Colab script (DONE)
3. → Upload to Google Drive
4. → Run on Colab with GPU
5. → Download trained model
6. → Deploy or further train

Ready? Let's train!
