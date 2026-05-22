#!/usr/bin/env python3
# ============================================================================
# ENGLISH-LUGANDA TRANSLATOR - SIMPLIFIED COLAB TRAINING
# ============================================================================
# Ultra-simple version with minimal parameters (works with all versions)
# ============================================================================

print("\n" + "="*70)
print("  🚀 TRAINING - SIMPLIFIED VERSION")
print("="*70)

# SETUP
!pip install -q torch transformers datasets pandas sacrebleu
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator 2>/dev/null || echo "Repo exists"

import os
os.chdir('/content/translator')

import torch
import pandas as pd
import json
from datetime import datetime
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
from datasets import Dataset

# ============================================================================
# DEVICE
# ============================================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n✓ Device: {device}")

# ============================================================================
# DATA
# ============================================================================
print("\n[LOADING DATA]")
train_df = pd.read_csv('data/processed/train.csv')
val_df = pd.read_csv('data/processed/val.csv')
test_df = pd.read_csv('data/processed/test.csv')
print(f"✓ Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

# ============================================================================
# MODEL
# ============================================================================
print("\n[LOADING MODEL]")
MODEL = "Helsinki-NLP/opus-mt-en-mul"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)
model = model.to(device)
print(f"✓ Model loaded")

# ============================================================================
# PREPARE DATASETS
# ============================================================================
print("\n[PREPARING DATA]")

def create_dataset(df):
    col_src = 'english' if 'english' in df.columns else 'en'
    col_tgt = 'luganda' if 'luganda' in df.columns else 'lg'
    return Dataset.from_dict({
        'source': df[col_src].fillna('').tolist(),
        'target': df[col_tgt].fillna('').tolist(),
    })

def preprocess(examples):
    return tokenizer(examples['source'], text_target=examples['target'],
                    max_length=128, truncation=True, padding="max_length")

train_dataset = create_dataset(train_df).map(preprocess, batched=True, batch_size=100)
val_dataset = create_dataset(val_df).map(preprocess, batched=True, batch_size=100)
test_dataset = create_dataset(test_df).map(preprocess, batched=True, batch_size=100)
print(f"✓ Data prepared")

# ============================================================================
# TRAINING ARGUMENTS
# ============================================================================
print("\n[SETUP TRAINING]")

training_args = Seq2SeqTrainingArguments(
    output_dir="results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    warmup_steps=500,
    save_strategy="epoch",
    eval_strategy="epoch",
    logging_steps=50,
    predict_with_generate=True,
    report_to="none",
)

print(f"✓ Training configured (3 epochs, batch 8)")

# ============================================================================
# TRAINER - SIMPLIFIED (no tokenizer parameter)
# ============================================================================
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,
)

# ============================================================================
# TRAIN
# ============================================================================
print("\n" + "="*70)
print("  🚀 STARTING TRAINING NOW (15-20 minutes)")
print("="*70)
print(f"Start: {datetime.now().strftime('%H:%M:%S')}\n")

result = trainer.train()

print(f"\n✓ Training complete!")
print(f"  Loss: {result.training_loss:.4f}")

# ============================================================================
# EVALUATE
# ============================================================================
print("\n[EVALUATING]")

from sacrebleu import corpus_bleu

predictions = trainer.predict(test_dataset)
decoded_preds = tokenizer.batch_decode(predictions.predictions, skip_special_tokens=True)
decoded_labels = tokenizer.batch_decode(predictions.label_ids, skip_special_tokens=True)

bleu = corpus_bleu(decoded_preds, [decoded_labels])

print(f"\n🎯 BLEU SCORE: {bleu.score:.2f}")
print("\n[SAMPLE PREDICTIONS]")
for i in range(min(3, len(decoded_preds))):
    print(f"\n{i+1}. Ref: {decoded_labels[i]}")
    print(f"   Pred: {decoded_preds[i]}")

# ============================================================================
# SAVE
# ============================================================================
print("\n[SAVING MODEL]")

model_path = '/content/translator/models/colab_trained_model'
os.makedirs(model_path, exist_ok=True)
model.save_pretrained(model_path)
tokenizer.save_pretrained(model_path)
print(f"✓ Model saved")

metrics = {
    "bleu": float(bleu.score),
    "loss": float(result.training_loss),
    "samples": len(train_df),
    "time": datetime.now().isoformat()
}

metrics_file = '/content/translator/metrics.json'
with open(metrics_file, 'w') as f:
    json.dump(metrics, f, indent=2)

from google.colab import files
files.download(metrics_file)

print(f"✓ Metrics downloaded!")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("  ✅ TRAINING COMPLETE!")
print("="*70)
print(f"""
🎯 BLEU Score: {bleu.score:.2f}

📊 Interpretation:
   15-20: Acceptable
   20-30: Good!
   30+:   Excellent!

✨ Model saved and ready to use!
""")
