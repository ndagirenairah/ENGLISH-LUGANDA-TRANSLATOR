# ============================================================================
# ENGLISH-LUGANDA TRANSLATOR - CLEAN CORRECTED TRAINING NOTEBOOK FOR COLAB
# ============================================================================
# This is a production-ready training notebook optimized for Google Colab
# All file paths are corrected and tested
# ============================================================================

# CELL 1: MOUNT GOOGLE DRIVE
# ============================================================================
from google.colab import drive
drive.mount('/content/drive')
print("✓ Google Drive mounted at /content/drive")

# CELL 2: VERIFY GPU
# ============================================================================
import torch
import os

print("\n[SYSTEM CHECK]")
print("=" * 60)
print(f"PyTorch: {torch.__version__}")
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# CELL 3: INSTALL DEPENDENCIES
# ============================================================================
!pip install -q torch transformers datasets pandas scikit-learn sacrebleu evaluate tqdm matplotlib seaborn

import transformers
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
from datetime import datetime

print("✓ All dependencies installed")

# CELL 4: CLONE REPOSITORY
# ============================================================================
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator 2>/dev/null || echo "Repo already cloned"

os.chdir('/content/translator')
import sys
sys.path.insert(0, '/content/translator')

print("✓ Repository cloned to /content/translator")
print(f"Current directory: {os.getcwd()}")

# CELL 5: LIST AVAILABLE DATA FILES
# ============================================================================
print("\n[CHECKING DATA FILES]")
print("=" * 60)

data_path = '/content/translator/data/processed'
if os.path.exists(data_path):
    files = os.listdir(data_path)
    print(f"Files in {data_path}:")
    for f in files:
        filepath = os.path.join(data_path, f)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / 1024
            print(f"  - {f} ({size:.1f} KB)")
else:
    print(f"❌ Data directory not found: {data_path}")

# CELL 6: LOAD TRAINING DATA
# ============================================================================
print("\n[LOADING DATA]")
print("=" * 60)

try:
    train_df = pd.read_csv('/content/translator/data/processed/train.csv')
    val_df = pd.read_csv('/content/translator/data/processed/val.csv')
    test_df = pd.read_csv('/content/translator/data/processed/test.csv')
    
    print(f"✓ Training samples: {len(train_df)}")
    print(f"✓ Validation samples: {len(val_df)}")
    print(f"✓ Test samples: {len(test_df)}")
    
    print("\nFirst 3 samples:")
    print(train_df.head(3).to_string())
    
except FileNotFoundError as e:
    print(f"❌ Error loading data: {e}")
    print("\nAlternative: Using data from /content/drive")
    
    # Try loading from Google Drive if local path doesn't work
    drive_data_path = '/content/drive/MyDrive/ENGLISH-LUGANDA TRANSLATOR/data/processed'
    if os.path.exists(drive_data_path):
        train_df = pd.read_csv(f'{drive_data_path}/train.csv')
        val_df = pd.read_csv(f'{drive_data_path}/val.csv')
        test_df = pd.read_csv(f'{drive_data_path}/test.csv')
        print(f"✓ Loaded from Google Drive")
    else:
        print(f"❌ Data not found in Google Drive either")
        print("Please ensure you have data/processed/train.csv, val.csv, test.csv")

# CELL 7: LOAD MODEL
# ============================================================================
print("\n[LOADING MODEL]")
print("=" * 60)

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Use multilingual model
MODEL_NAME = "Helsinki-NLP/opus-mt-en-mul"
print(f"Loading model: {MODEL_NAME}")
print("(This may take 2-3 minutes for first download...)")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
model = model.to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"✓ Model loaded successfully")
print(f"✓ Parameters: {total_params:,}")
print(f"✓ Device: {device}")

# CELL 8: TEST BASE MODEL (BEFORE TRAINING)
# ============================================================================
print("\n[BASE MODEL TEST (BEFORE TRAINING)]")
print("=" * 60)

def translate_batch(texts, model, tokenizer, device):
    """Translate a batch of texts"""
    inputs = tokenizer(
        texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        generated = model.generate(
            **inputs,
            max_length=120,
            num_beams=5,
            no_repeat_ngram_size=3
        )
    
    return tokenizer.batch_decode(generated, skip_special_tokens=True)

# Test with 3 samples
test_samples = train_df['english'].head(3).tolist()
print("\nBefore Training Translations:\n")

before_translations = translate_batch(test_samples, model, tokenizer, device)
for i, (en, lg) in enumerate(zip(test_samples, before_translations), 1):
    print(f"{i}. EN: {en}")
    print(f"   LG: {lg}\n")

# CELL 9: PREPARE TRAINING DATA
# ============================================================================
print("\n[PREPARING TRAINING DATA]")
print("=" * 60)

from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
from datasets import Dataset

def create_dataset(df):
    """Create HuggingFace dataset from dataframe"""
    # Handle both 'english'/'luganda' and 'en'/'lg' column names
    source_col = 'english' if 'english' in df.columns else 'en'
    target_col = 'luganda' if 'luganda' in df.columns else 'lg'
    
    dataset = Dataset.from_dict({
        'source': df[source_col].fillna('').tolist(),
        'target': df[target_col].fillna('').tolist(),
    })
    return dataset

train_dataset = create_dataset(train_df)
val_dataset = create_dataset(val_df)
test_dataset = create_dataset(test_df)

def preprocess_function(examples):
    """Tokenize input and target texts"""
    inputs = tokenizer(
        examples['source'],
        text_target=examples['target'],
        max_length=128,
        truncation=True,
        padding="max_length"
    )
    return inputs

print("Tokenizing datasets...")
train_dataset = train_dataset.map(preprocess_function, batched=True, batch_size=100, desc="train")
val_dataset = val_dataset.map(preprocess_function, batched=True, batch_size=100, desc="val")
test_dataset = test_dataset.map(preprocess_function, batched=True, batch_size=100, desc="test")

print(f"✓ Data prepared for training")
print(f"✓ Train: {len(train_dataset)} | Val: {len(val_dataset)} | Test: {len(test_dataset)}")

# CELL 10: SETUP TRAINING PARAMETERS
# ============================================================================
print("\n[TRAINING SETUP]")
print("=" * 60)

EPOCHS = 3
BATCH_SIZE = 8
LEARNING_RATE = 2e-5

training_args = Seq2SeqTrainingArguments(
    output_dir="/content/translator/results",
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    learning_rate=LEARNING_RATE,
    warmup_steps=500,
    weight_decay=0.01,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    logging_steps=50,
    predict_with_generate=True,
    report_to="none",
    seed=42,
)

print(f"Epochs: {EPOCHS}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Learning rate: {LEARNING_RATE}")
print(f"Output dir: {training_args.output_dir}")

# CELL 11: START TRAINING 🚀
# ============================================================================
print("\n[STARTING TRAINING]")
print("=" * 60)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("This will take ~15-20 minutes...\n")

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

training_result = trainer.train()

print(f"\n✓ Training completed!")
print(f"Final training loss: {training_result.training_loss:.4f}")
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# CELL 12: EVALUATE ON TEST SET
# ============================================================================
print("\n[EVALUATING ON TEST SET]")
print("=" * 60)

from sacrebleu import corpus_bleu

predictions = trainer.predict(test_dataset)
decoded_preds = tokenizer.batch_decode(predictions.predictions, skip_special_tokens=True)
decoded_labels = tokenizer.batch_decode(predictions.label_ids, skip_special_tokens=True)

bleu = corpus_bleu(decoded_preds, [decoded_labels])

print(f"\n🎯 TEST SET BLEU SCORE: {bleu.score:.2f}")
print(f"\nSample Predictions (first 5):")
print("=" * 60)

for i in range(min(5, len(decoded_preds))):
    print(f"\nSample {i+1}:")
    print(f"  Reference: {decoded_labels[i]}")
    print(f"  Predicted: {decoded_preds[i]}")

# CELL 13: COMPARE BEFORE vs AFTER TRAINING
# ============================================================================
print("\n[COMPARING BASE vs FINE-TUNED MODEL]")
print("=" * 60)

after_translations = translate_batch(test_samples, model, tokenizer, device)

for i, (en, before, after) in enumerate(zip(test_samples, before_translations, after_translations), 1):
    print(f"\n{i}. Input: {en}")
    print(f"   Base:      {before}")
    print(f"   Fine-tuned: {after}")

# CELL 14: SAVE MODEL
# ============================================================================
print("\n[SAVING MODEL]")
print("=" * 60)

model_save_path = '/content/translator/models/colab_trained_model'
os.makedirs(model_save_path, exist_ok=True)

model.save_pretrained(model_save_path)
tokenizer.save_pretrained(model_save_path)

print(f"✓ Model saved to {model_save_path}")

# CELL 15: SAVE METRICS
# ============================================================================
print("\n[SAVING METRICS]")
print("=" * 60)

metrics = {
    "model": MODEL_NAME,
    "training_samples": len(train_dataset),
    "validation_samples": len(val_dataset),
    "test_samples": len(test_dataset),
    "epochs": EPOCHS,
    "batch_size": BATCH_SIZE,
    "learning_rate": LEARNING_RATE,
    "bleu_score": float(bleu.score),
    "training_loss": float(training_result.training_loss),
    "device": str(device),
    "timestamp": datetime.now().isoformat(),
}

metrics_path = '/content/translator/training_metrics.json'
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"✓ Metrics saved to {metrics_path}")
print("\nTraining Summary:")
print(json.dumps(metrics, indent=2))

# CELL 16: DOWNLOAD RESULTS
# ============================================================================
print("\n[DOWNLOADING RESULTS]")
print("=" * 60)

from google.colab import files

try:
    files.download(metrics_path)
    print("✓ training_metrics.json downloaded")
except:
    print("⚠ Could not download metrics file")

# CELL 17: FINAL SUMMARY
# ============================================================================
print("\n" + "=" * 60)
print("🎉 TRAINING COMPLETE!")
print("=" * 60)

print(f"""
✓ Model trained successfully
✓ BLEU Score: {bleu.score:.2f}
✓ Training Loss: {training_result.training_loss:.4f}
✓ Model saved: {model_save_path}
✓ Metrics saved: {metrics_path}

BLEU Score Interpretation:
  0-10:  Poor
  10-20: Acceptable
  20-30: Good
  30-40: Very Good
  40+:   Excellent

Next Steps:
1. Review your BLEU score above
2. If score < 25: Collect more training data
3. If score 25-30: Good! Ready for some testing
4. If score > 30: Excellent! Deploy with confidence

For improvements, consider:
- More training data (most important!)
- More epochs (3→5→10)
- Larger model (opus-mt-en-lg instead of mul)
- Data quality improvements
- Fine-tuning hyperparameters

Happy Translating! 🌍
""")
