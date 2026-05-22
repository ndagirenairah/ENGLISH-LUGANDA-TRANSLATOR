#!/usr/bin/env python3
# ============================================================================
# ENGLISH-LUGANDA TRANSLATOR - CORRECTED COLAB TRAINING
# ============================================================================
# Fixed version with correct parameter names for latest transformers
# ============================================================================

print("\n" + "="*70)
print("  🚀 ENGLISH-LUGANDA TRAINING - CORRECTED VERSION")
print("="*70)

# SETUP: Install dependencies
!pip install -q torch transformers datasets pandas sacrebleu evaluate
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator 2>/dev/null || echo "Repo exists"

import os
os.chdir('/content/translator')

# ============================================================================
# IMPORTS
# ============================================================================
import torch
import pandas as pd
import json
from datetime import datetime
from transformers import (
    AutoModelForSeq2SeqLM, 
    AutoTokenizer, 
    Seq2SeqTrainingArguments, 
    Seq2SeqTrainer, 
    DataCollatorForSeq2Seq
)
from datasets import Dataset

# ============================================================================
# DEVICE CHECK
# ============================================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n✓ Device: {device}")
if device.type == "cuda":
    print(f"✓ GPU: {torch.cuda.get_device_name(0)}")

# ============================================================================
# LOAD DATA
# ============================================================================
print("\n[LOADING DATA]")
try:
    train_df = pd.read_csv('data/processed/train.csv')
    val_df = pd.read_csv('data/processed/val.csv')
    test_df = pd.read_csv('data/processed/test.csv')
    print(f"✓ Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    raise

# ============================================================================
# LOAD MODEL
# ============================================================================
print("\n[LOADING MODEL]")
MODEL = "Helsinki-NLP/opus-mt-en-mul"
print(f"Model: {MODEL}")

tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)
model = model.to(device)
print(f"✓ Model loaded successfully!")

# ============================================================================
# PREPARE DATA
# ============================================================================
print("\n[PREPARING DATA]")

def create_dataset(df):
    """Create HuggingFace dataset"""
    col_src = 'english' if 'english' in df.columns else 'en'
    col_tgt = 'luganda' if 'luganda' in df.columns else 'lg'
    return Dataset.from_dict({
        'source': df[col_src].fillna('').tolist(),
        'target': df[col_tgt].fillna('').tolist(),
    })

def preprocess_function(examples):
    """Tokenize input and target"""
    return tokenizer(
        examples['source'], 
        text_target=examples['target'],
        max_length=128, 
        truncation=True, 
        padding="max_length"
    )

# Create datasets
train_dataset = create_dataset(train_df).map(preprocess_function, batched=True, batch_size=100)
val_dataset = create_dataset(val_df).map(preprocess_function, batched=True, batch_size=100)
test_dataset = create_dataset(test_df).map(preprocess_function, batched=True, batch_size=100)

print(f"✓ Data prepared for training")

# ============================================================================
# TRAINING ARGUMENTS - FIXED VERSION
# ============================================================================
print("\n[SETUP TRAINING]")

training_args = Seq2SeqTrainingArguments(
    output_dir="results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    warmup_steps=500,
    weight_decay=0.01,
    save_strategy="epoch",
    eval_strategy="epoch",  # ✓ FIXED: Changed from evaluation_strategy
    logging_steps=50,
    predict_with_generate=True,
    report_to="none",
    seed=42,
)

print(f"✓ Training configured")
print(f"  - Epochs: 3")
print(f"  - Batch size: 8")
print(f"  - Learning rate: 2e-5")

# ============================================================================
# TRAINER
# ============================================================================
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

# ============================================================================
# START TRAINING
# ============================================================================
print("\n" + "="*70)
print("  🚀 STARTING TRAINING (this will take 15-20 minutes)")
print("="*70)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

result = trainer.train()

print(f"\n✓ Training complete!")
print(f"Training loss: {result.training_loss:.4f}")

# ============================================================================
# EVALUATE
# ============================================================================
print("\n[EVALUATING ON TEST SET]")

from sacrebleu import corpus_bleu

predictions = trainer.predict(test_dataset)
decoded_preds = tokenizer.batch_decode(predictions.predictions, skip_special_tokens=True)
decoded_labels = tokenizer.batch_decode(predictions.label_ids, skip_special_tokens=True)

bleu = corpus_bleu(decoded_preds, [decoded_labels])

print(f"\n🎯 TEST SET BLEU SCORE: {bleu.score:.2f}")

# Show samples
print("\n[SAMPLE PREDICTIONS]")
for i in range(min(5, len(decoded_preds))):
    print(f"\n{i+1}. Reference: {decoded_labels[i]}")
    print(f"   Predicted: {decoded_preds[i]}")

# ============================================================================
# SAVE MODEL
# ============================================================================
print("\n[SAVING MODEL]")

model_path = '/content/translator/models/colab_trained_model'
os.makedirs(model_path, exist_ok=True)
model.save_pretrained(model_path)
tokenizer.save_pretrained(model_path)

print(f"✓ Model saved to: {model_path}")

# ============================================================================
# SAVE METRICS
# ============================================================================
print("\n[SAVING METRICS]")

metrics = {
    "model": MODEL,
    "bleu_score": float(bleu.score),
    "training_loss": float(result.training_loss),
    "training_samples": len(train_dataset),
    "validation_samples": len(val_dataset),
    "test_samples": len(test_dataset),
    "epochs": 3,
    "batch_size": 8,
    "learning_rate": 2e-5,
    "device": str(device),
    "timestamp": datetime.now().isoformat(),
}

metrics_path = '/content/translator/training_metrics.json'
with open(metrics_path, 'w') as f:
    json.dump(metrics, f, indent=2)

print(f"✓ Metrics saved to: {metrics_path}")

# Download results
from google.colab import files
files.download(metrics_path)
print("✓ Metrics downloaded!")

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*70)
print("  ✅ TRAINING COMPLETE!")
print("="*70)

print(f"""
🎯 RESULTS:
   BLEU Score:        {bleu.score:.2f}
   Training Loss:     {result.training_loss:.4f}
   Model Saved:       {model_path}
   Metrics Saved:     {metrics_path}

📊 BLEU Score Interpretation:
   0-10:   Poor (needs more data)
   10-20:  Acceptable (low-resource)
   20-30:  Good! (production ready)
   30-40:  Very Good! (excellent quality)
   40+:    Outstanding!

✨ Next Steps:
   1. Check your BLEU score above
   2. Download metrics.json file
   3. Test translations with trained model
   4. Plan improvements if needed

🌍 Happy Translating!
""")

print("="*70)
