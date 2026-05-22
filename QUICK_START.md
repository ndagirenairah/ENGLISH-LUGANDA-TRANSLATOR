# QUICK START - TRAIN IN COLAB IN 3 STEPS

## Step 1️⃣: Get Your Token (1 minute)
Go to: https://huggingface.co/settings/tokens
- Click "New token"
- Name: "Luganda Translator"
- Type: Read access
- Click "Generate"
- Copy the token (starts with `hf_`)

## Step 2️⃣: Open Google Colab
Go to: https://colab.research.google.com

Create new notebook → Cell 1:
```python
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
import os
os.chdir('/content/translator')
```
**Run** (Ctrl+Enter)

## Step 3️⃣: Train Cell 2:
```python
exec(open('COLAB_TRAIN_KAMBALE_COMBINED.py').read())
```
**Run** → When prompted, paste your token

---

# WHAT HAPPENS NEXT

| Time | Phase | What's Running |
|------|-------|-----------------|
| 1 min | Setup | Install packages, verify GPU |
| 2 min | Clone | Download model (~600MB) |
| 3 min | Dataset | Combine 5 sources (Kambale + local) |
| 1 min | Load | Load model to GPU |
| 12 min | **TRAINING** | 3 epochs on combined data |
| 1 min | Evaluate | Calculate BLEU score |
| **~20 min** | **DONE** | Download metrics + save model |

---

# WHAT YOU GET

- **Trained Model** → `models/kambale_combined_model/`
- **BLEU Score** → `metrics_kambale_combined.json` (downloaded)
- **Prediction Samples** → Shown in output

---

# EXPECTED RESULTS

**BLEU Score ≥ 25 = Success! ✅**

| Score | Quality | Status |
|-------|---------|--------|
| 20-25 | Baseline | Good start |
| 25-30 | **Good ✓** | Ready to use |
| 30+ | **Excellent ✓✓** | Production ready |

---

# IF SOMETHING GOES WRONG

### "Token not recognized"
→ Check you copied the whole token (including `hf_` at start)

### "Model downloading is slow"
→ Normal! First time is slow (~2-3 min), cached after

### "Out of memory"
→ Edit line in COLAB_TRAIN_KAMBALE_COMBINED.py:
   Change `per_device_train_batch_size=8` → `per_device_train_batch_size=4`

### "Network timeout"
→ Just rerun the cell (usually temporary)

---

# THEN WHAT?

After training:

1. **Check BLEU score** in metrics file
2. **If > 25**: Use the model! Copy to local:
   ```bash
   # On your local machine after downloading from Colab
   cp -r models/kambale_combined_model ~/translator/
   python app.py
   ```
3. **If < 25**: Try improvements:
   - Add more epochs (3 → 5)
   - Lower learning rate (2e-5 → 1e-5)
   - Use TRAINING_CHECKLIST.md for options

---

# LINKS YOU NEED

- **Colab**: https://colab.research.google.com
- **HF Token**: https://huggingface.co/settings/tokens
- **GitHub**: https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR
- **Full Guide**: See COLAB_SETUP_INSTRUCTIONS.md

---

# THAT'S IT! 🚀

Your Kambale-trained English-Luganda translator will be ready in ~20 minutes!

Questions? Check:
- SESSION_COMPLETE_SUMMARY.md
- TRAINING_CHECKLIST.md
- COLAB_SETUP_INSTRUCTIONS.md
