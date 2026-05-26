# Download Trained Model from Colab

After you finish training in Colab, use this simple script to download your trained model.

## Quick Steps:

1. **In Google Colab:**
   - Go to your COLAB_TRAINING_ML_PIPELINE.ipynb notebook
   - After STEP 7 (Results) finishes
   - Create a NEW CELL and paste this code:

```python
import shutil
from pathlib import Path
from google.colab import files

model_path = Path("models/trained_model")
if model_path.exists():
    shutil.make_archive("trained_model", "zip", model_path.parent, model_path.name)
    print("[SUCCESS] Downloading trained_model.zip...")
    files.download("trained_model.zip")
else:
    print("[ERROR] Model not found! Make sure training completed.")
```

   - Run the cell
   - Your browser will download `trained_model.zip` automatically

2. **On Your Local Machine:**
   - Extract `trained_model.zip` to your `models/` folder:
     ```
     d:\English-Luganda-Translator\ENGLISH-LUGANDA-TRANSLATOR\models\
     ```
   - The folder should look like:
     ```
     models/
     └── trained_model/
         ├── config.json
         ├── pytorch_model.bin
         ├── tokenizer_config.json
         ├── source.spm
         └── target.spm
     ```

3. **Run the Web Server:**
   ```powershell
   cd d:\English-Luganda-Translator\ENGLISH-LUGANDA-TRANSLATOR
   python web_server_flask.py
   ```

4. **Open in Browser:**
   - Go to: http://localhost:5000
   - Translate English to Luganda!

## Alternative (If ZIP doesn't download):

Copy-paste this into Colab instead:

```python
!zip -r /tmp/trained_model.zip models/trained_model/
from google.colab import files
files.download("/tmp/trained_model.zip")
```

---

**Questions?** The trained model files are located at `models/trained_model/` after training completes.
