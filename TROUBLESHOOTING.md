# 🔧 TROUBLESHOOTING GUIDE - Common Issues & Fixes

## Quick Navigation
- [Installation Issues](#installation-issues)
- [Dataset Loading Issues](#dataset-loading-issues)
- [GPU/Memory Issues](#gpumemory-issues)
- [Training Issues](#training-issues)
- [Testing Issues](#testing-issues)
- [Web App Issues](#web-app-issues)

---

## ⚡ Installation Issues

### Issue: "ModuleNotFoundError: No module named 'transformers'"

**Cause:** transformers library not installed

**Fix:**
```bash
pip install transformers
# or
pip install -r requirements.txt
```

**Verify:**
```bash
python -c "import transformers; print(transformers.__version__)"
```

---

### Issue: "ModuleNotFoundError: No module named 'datasets'"

**Cause:** datasets library not installed

**Fix:**
```bash
pip install datasets
```

**Verify:**
```bash
python -c "from datasets import load_dataset; print('✓ OK')"
```

---

### Issue: SSL Certificate Error / Network Error

**Cause:** Network/firewall issue when downloading datasets

**Fix Option 1: Set environment variables**
```bash
# Windows PowerShell
$env:HF_DATASETS_OFFLINE = "0"

# Windows CMD
set HF_DATASETS_OFFLINE=0

# Mac/Linux
export HF_DATASETS_OFFLINE=0
```

**Fix Option 2: Disable SSL verification (last resort)**
```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**Fix Option 3: Download manually**
- Use Google Colab (better internet)
- Download on different network
- Use VPN if blocked

---

## 📥 Dataset Loading Issues

### Issue: "Dataset not found: Sunbird/salt"

**Cause:** Dataset doesn't exist or HuggingFace is down

**What happens:** Script gracefully skips and uses other datasets

**Expected output:**
```
⚠️ Sunbird SALT: Failed to load
```

**This is OKAY!** Project works with any dataset that loads.

**Fix:** Don't worry - the script handles missing datasets!

---

### Issue: "opus_100 dataset not found"

**Cause:** JW300 might use different name

**Fix:** The script tries multiple names automatically
```python
# It tries: "opus_100", "JW300", etc.
# If all fail, it continues with other sources
```

---

### Issue: "Memory Error: dataset too large"

**Cause:** Trying to load all 300K pairs at once

**Fix: Limit dataset size (edit Step3)**
```python
# Instead of:
df = pd.read_csv('data/luganda_english_dataset_combined.csv')

# Do:
df = pd.read_csv('data/luganda_english_dataset_combined.csv')
df = df.head(100000)  # Use only first 100K for testing
```

---

## 💾 GPU/Memory Issues

### Issue: "CUDA out of memory"

**Cause:** Batch size too large for your GPU

**Fix (edit Step5_Train_Model.py):**
```python
# Change from:
per_device_train_batch_size=16

# To:
per_device_train_batch_size=8  # Smaller batches
```

**Tip:** Try these values:
```
GPU < 4GB:  batch_size = 4-8
GPU 4-8GB:  batch_size = 8-16
GPU > 8GB:  batch_size = 16-32
```

---

### Issue: "GPU not detected"

**Cause:** CUDA/PyTorch not properly configured

**Fix:**
```python
import torch
print(torch.cuda.is_available())  # Should be True
print(torch.cuda.get_device_name(0))  # Shows GPU name
```

**If False:**
Option 1: Install GPU version of PyTorch
```bash
# Visit: https://pytorch.org/get-started/locally/
# Follow their installation instructions
```

Option 2: Use Google Colab (has free GPU!)
```
Go to: https://colab.research.google.com
Runtime → Change Runtime Type → GPU
```

---

### Issue: "CPU is extremely slow"

**Expected:**
- GPU (Colab): 30-45 min
- CPU (laptop): 2-4 hours

**To make CPU faster:**
```python
# Edit Step5 - reduce data
df = pd.read_csv('...')
df = df.head(50000)  # Only use 50K pairs instead of 300K
```

---

## 🏋️ Training Issues

### Issue: "Training stopped / disconnected"

**Cause:** 
- Connection interrupted
- Colab session timed out
- Process killed

**Prevention:**
1. Use Google Colab (auto-saves checkpoints)
2. Run locally with screen/tmux
3. Save checkpoints frequently

**Recovery:**
- Model is saved in `models/trained_model/`
- If training was interrupted, can resume from checkpoint

---

### Issue: "Loss not decreasing (stuck at same value)"

**Cause:** Learning rate too low, or stuck in local minimum

**Fix:**
```python
# In Step5, increase learning rate:
learning_rate=2e-5  # Change to:
learning_rate=5e-5  # Higher
```

---

### Issue: "Loss suddenly jumps = NaN"

**Cause:** Learning rate too high, model exploding

**Fix:**
```python
# Reduce learning rate:
learning_rate=2e-5  # Change to:
learning_rate=1e-5  # Lower
```

---

### Issue: Training takes too long

**Normal times:**
```
GPU (Colab):  30-45 minutes
CPU (local):  2-4 hours
```

**To speed up (at cost of accuracy):**
```python
# Option 1: Fewer epochs
num_train_epochs=3  # Change to:
num_train_epochs=1

# Option 2: Less data
df = df.head(100000)  # Instead of 300K

# Option 3: Larger batches
per_device_train_batch_size=32  # Instead of 16
```

---

## 🧪 Testing Issues

### Issue: "No translations generated"

**Cause:** Model file missing or corrupted

**Fix:**
1. Verify Step 5 completed successfully
2. Check `models/trained_model/` exists
3. Re-run Step 5 if needed

---

### Issue: "Translation results are gibberish"

**Cause:** Model not properly trained or wrong language tags

**Expected:**
- Some translations are imperfect - that's normal!
- Check BLEU scores in Step 7
- 40-50% perfect matches is good for low-resource

**Fix:** More training data or epochs
```python
# In Step5:
num_train_epochs=5  # Instead of 3 (slower but better)
```

---

## 🌐 Web App Issues

### Issue: "ModuleNotFoundError: No module named 'gradio'"

**Fix:**
```bash
pip install gradio
```

---

### Issue: "Port 7860 already in use"

**Cause:** Another app using the same port

**Fix Option 1: Kill the process**
```bash
# Windows:
netstat -ano | findstr :7860
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :7860
kill -9 <PID>
```

**Fix Option 2: Use different port (edit Step8)**
```python
# Change from:
interface.launch(server_port=7860)

# To:
interface.launch(server_port=7861)  # Different port
```

---

### Issue: "Browser can't connect to localhost:7860"

**Cause:** Server not running or firewall blocking

**Fix:**
1. Check server is running (should see URL in console)
2. Try: http://127.0.0.1:7860 instead
3. Check firewall settings

---

## 📊 Debugging Steps

### If something fails:

**Step 1: Run DEBUG script**
```bash
python DEBUG_CHECK.py
```

**Step 2: Check outputs:**
```python
# Verify file exists
import os
print(os.path.exists('data/luganda_english_dataset_combined.csv'))

# Check file size
import os
size_mb = os.path.getsize('data/luganda_english_dataset_combined.csv') / (1024*1024)
print(f"File size: {size_mb:.1f} MB")
```

**Step 3: Check logs**
- `logs/` folder has training logs
- Look for ERROR messages

**Step 4: Reduce scope**
- Use smaller dataset
- Use fewer epochs
- Use smaller batches

---

## 🆘 Still Having Issues?

Try these in order:

### 1. **Use Google Colab** (Easiest)
```
- Go to: colab.research.google.com
- Has GPU built-in
- Most packages pre-installed
- Free!
```

### 2. **Try test datasets**
```bash
# Use smaller test to verify setup works:
python DEBUG_CHECK.py
```

### 3. **Read error messages carefully**
```
Most errors have helpful hints!
Look for: "did you mean...", "install:", etc.
```

### 4. **Check documentation files**
- `README.md` - Full guide
- `DATASETS.md` - Dataset info
- `QUICK_START.md` - Fast version

### 5. **Review the step files**
```
Step files have LOTS of comments
explaining what happens at each stage
```

---

## ⚠️ Common Mistakes

### Mistake 1: Running steps out of order
```
❌ WRONG:
python Step5_Train_Model.py  # Without Step 1-4

✅ RIGHT:
python Step1_Environment_Setup.py
python Step2_Load_Dataset.py
python Step3_Data_Preprocessing.py
python Step4_MarianMT_Setup.py
python Step5_Train_Model.py
```

---

### Mistake 2: Not installing requirements first
```
❌ WRONG:
python Step1_Environment_Setup.py  # Without pip install

✅ RIGHT:
pip install -r requirements.txt
python Step1_Environment_Setup.py
```

---

### Mistake 3: Using too much data on weak computer
```
❌ WRONG:
Training on 300K pairs on old laptop

✅ RIGHT:
Reduce to 50K pairs with:
df = df.head(50000)
```

---

### Mistake 4: Not checking GPU
```
❌ WRONG:
Starting 4-hour CPU training when GPU available

✅ RIGHT:
Check: python -c "import torch; print(torch.cuda.is_available())"
If True, GPU training (30 min instead of 4 hours!)
```

---

## ✅ How to Verify Everything Works

Run this checklist:

- [ ] `python DEBUG_CHECK.py` - All green ✓
- [ ] `python Step1_Environment_Setup.py` - No errors
- [ ] `python Step2_Load_Dataset.py` - CSV created
- [ ] Check `data/luganda_english_dataset_combined.csv` exists
- [ ] `python Step3_Data_Preprocessing.py` - No errors
- [ ] Check training/val/test files created
- [ ] `python Step4_MarianMT_Setup.py` - Model downloaded
- [ ] `python Step5_Train_Model.py` - Training starts
- [ ] After training, check `models/trained_model/` exists

---

## 💡 Pro Tips

### Tip 1: Save progress
```bash
# If training interrupted:
# Just re-run Step 5 - it loads last checkpoint
python Step5_Train_Model.py
```

### Tip 2: Monitor during training
```bash
# Keep separate terminal open:
ls -lh models/  # See updates in real-time
```

### Tip 3: Test early
```
# Don't wait for full training to test
# Use small dataset first to verify setup works
```

### Tip 4: Use Colab for GPU
```
Google Colab > Local CPU
- Free GPU (K80, T4, A100)
- Pre-installed packages
- Auto-saves to Google Drive
```

---

## 📞 Quick Reference

| Issue | Solution | Time to Fix |
|-------|----------|-------------|
| ModuleNotFoundError | pip install [module] | 1 min |
| CUDA out of memory | Reduce batch_size | 2 min |
| GPU not found | Use Colab / install CUDA | 5 min |
| Training slow | Use GPU instead of CPU | 50x faster |
| Dataset missing | Script handles gracefully | N/A |
| Connection interrupted | Save checkpoints | varies |

---

## 🎯 Remember

✅ Most issues are easy to fix
✅ Error messages are helpful - read them!
✅ Running on Google Colab avoids most issues
✅ Start small, scale up
✅ All steps can be re-run safely

**You've got this! 💪**

---

Created: April 17, 2026
Last updated: April 17, 2026
