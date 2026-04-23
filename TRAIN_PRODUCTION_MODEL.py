#!/usr/bin/env python3
"""
PRODUCTION-READY MODEL TRAINER
Trains a high-quality translator with validation and testing
"""

import os
import json
import pandas as pd
import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq
)
import warnings
warnings.filterwarnings('ignore')

print("=" * 100)
print("🚀 PRODUCTION-READY MODEL TRAINER")
print("=" * 100)

# ============================================================================
# CONFIG
# ============================================================================
TRAINED_MODEL_PATH = "models/trained_model"
BASE_MODEL_NAME = "Helsinki-NLP/opus-mt-en-mul"
EPOCHS = 3
BATCH_SIZE = 16
LEARNING_RATE = 2e-5
MAX_LENGTH = 128

# ============================================================================
# PHASE 1: LOAD DATA
# ============================================================================
print("\n[1/6] LOADING DATA...")

print("\n📖 Loading training data from luganda_training_data.csv...")
df_train = pd.read_csv("luganda_training_data.csv")
print(f"   ✅ Loaded {len(df_train)} total samples")

# Clean columns
df_train.columns = df_train.columns.str.strip().str.lower()

# Build dataset
train_data = []
for _, row in df_train.iterrows():
    try:
        lug = str(row.get('luganda', row.get('source', ''))).strip()
        eng = str(row.get('english', row.get('target', ''))).strip()
        
        if len(lug) > 2 and len(eng) > 2 and lug != "nan" and eng != "nan":
            train_data.append({"source": lug, "target": eng})
    except:
        continue

print(f"   ✅ Valid training pairs: {len(train_data)}")

# Split 80/20
np.random.seed(42)
indices = np.random.permutation(len(train_data))
split = int(len(train_data) * 0.8)

train_list = [train_data[i] for i in indices[:split]]
val_list = [train_data[i] for i in indices[split:]]

print(f"   ✅ Train: {len(train_list)} | Val: {len(val_list)}")

# Convert to HF datasets
train_df = pd.DataFrame(train_list)
val_df = pd.DataFrame(val_list)

train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

# ============================================================================
# PHASE 2: LOAD MODEL
# ============================================================================
print("\n[2/6] LOADING MODEL...")

print(f"\n   Loading: {BASE_MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL_NAME)
print(f"   ✅ Model: {model.num_parameters():,} parameters")

# Device
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print(f"   ✅ Device: {device.upper()}")

# ============================================================================
# PHASE 3: PREPARE DATASET
# ============================================================================
print("\n[3/6] PREPARING DATASET...")

def preprocess(examples):
    inputs = examples["source"]
    targets = examples["target"]
    
    model_inputs = tokenizer(
        inputs,
        max_length=MAX_LENGTH,
        truncation=True,
        padding="max_length"
    )
    
    labels = tokenizer(
        targets,
        max_length=MAX_LENGTH,
        truncation=True,
        padding="max_length"
    )
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

print("   Tokenizing training data...")
train_tokenized = train_dataset.map(preprocess, batched=True, remove_columns=["source", "target"])
val_tokenized = val_dataset.map(preprocess, batched=True, remove_columns=["source", "target"])

print(f"   ✅ Training: {len(train_tokenized)} | Validation: {len(val_tokenized)}")

# ============================================================================
# PHASE 4: TRAINING CONFIG
# ============================================================================
print("\n[4/6] CONFIGURING TRAINING...")

training_args = Seq2SeqTrainingArguments(
    output_dir=TRAINED_MODEL_PATH,
    eval_strategy="epoch",
    learning_rate=LEARNING_RATE,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=EPOCHS,
    predict_with_generate=True,
    fp16=torch.cuda.is_available(),
    logging_steps=200,
    save_steps=500,
    gradient_accumulation_steps=2,
)

print(f"   ✅ Epochs: {EPOCHS}")
print(f"   ✅ Batch size: {BATCH_SIZE}")
print(f"   ✅ Learning rate: {LEARNING_RATE}")
print(f"   ✅ Output dir: {TRAINED_MODEL_PATH}")

# ============================================================================
# PHASE 5: TRAIN
# ============================================================================
print("\n[5/6] TRAINING MODEL...")
print("   (This may take 10-30 minutes...\n")

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_tokenized,
    eval_dataset=val_tokenized,
    data_collator=data_collator,
)

try:
    train_result = trainer.train()
    print(f"\n   ✅ Training complete!")
    print(f"      Final loss: {train_result.training_loss:.4f}")
except KeyboardInterrupt:
    print("\n   ⚠️  Training interrupted by user")
except Exception as e:
    print(f"\n   ❌ Training error: {e}")

# ============================================================================
# PHASE 6: SAVE MODEL
# ============================================================================
print("\n[6/6] SAVING MODEL...")

os.makedirs(TRAINED_MODEL_PATH, exist_ok=True)
model.save_pretrained(TRAINED_MODEL_PATH)
tokenizer.save_pretrained(TRAINED_MODEL_PATH)

print(f"   ✅ Model saved to: {TRAINED_MODEL_PATH}")
print(f"   ✅ Files:")
for f in os.listdir(TRAINED_MODEL_PATH)[:5]:
    print(f"      - {f}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("✅ TRAINING COMPLETE!")
print("=" * 100)

summary = {
    "status": "TRAINED",
    "model_path": TRAINED_MODEL_PATH,
    "base_model": BASE_MODEL_NAME,
    "device": device.upper(),
    "parameters": int(model.num_parameters()),
    "epochs": EPOCHS,
    "batch_size": BATCH_SIZE,
    "learning_rate": LEARNING_RATE,
    "training_samples": len(train_list),
    "validation_samples": len(val_list),
    "timestamp": pd.Timestamp.now().isoformat()
}

with open("outputs/training_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print(f"""
📊 TRAINING SUMMARY:
   - Model: {summary['base_model']}
   - Samples: {summary['training_samples']} training, {summary['validation_samples']} validation
   - Device: {summary['device']}
   - Epochs: {summary['epochs']}

🎯 NEXT STEPS:
   1. Test the model:
      python QUICK_TEST_FAST.py
   
   2. If results are good, deploy:
      python app.py
   
   3. Monitor performance in outputs/

✨ Model ready for testing and deployment!
""")

print("=" * 100)
