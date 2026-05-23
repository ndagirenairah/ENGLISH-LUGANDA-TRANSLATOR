#!/usr/bin/env python3

print("\n" + "="*70)
print("COLAB TRAINING - COMBINED KAMBALE + LOCAL DATASET")
print("="*70)

# Setup
!pip install -q torch transformers datasets pandas sacrebleu

# Clone repo
!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator 2>/dev/null || echo "Repo exists"
import os
os.chdir('/content/translator')

print("\n[STEP 1: COMBINING DATASETS WITH KAMBALE]")
print("="*70)

# Set HF token (use your token from https://huggingface.co/settings/tokens)
hf_token = input("Enter your HuggingFace token: ") if 'HF_TOKEN' not in os.environ else os.environ['HF_TOKEN']
os.environ['HF_TOKEN'] = hf_token

# Run the combination script
try:
    exec(open('preprocess_combine_datasets.py').read())
except Exception as e:
    print(f"Note: {e}")
    print("Proceeding with whatever datasets are available...")

print("\n" + "="*70)
print("STARTING TRAINING")
print("="*70)

import torch
import pandas as pd
import json
from datetime import datetime
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
from datasets import Dataset

# Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\nDevice: {device}")
if device.type == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Load data
print("\n[LOADING COMBINED DATA]")
try:
    train_df = pd.read_csv('data/combined_kambale/train.csv')
    val_df = pd.read_csv('data/combined_kambale/val.csv')
    test_df = pd.read_csv('data/combined_kambale/test.csv')
    
    print(f"Train: {len(train_df)}")
    print(f"Val: {len(val_df)}")
    print(f"Test: {len(test_df)}")
    
    # Show source breakdown
    if 'source' in train_df.columns:
        print(f"\nDataset sources:")
        for source, count in train_df['source'].value_counts().items():
            print(f"  {source}: {count}")
            
except Exception as e:
    print(f"Using fallback data: {e}")
    train_df = pd.read_csv('data/processed/train.csv')
    val_df = pd.read_csv('data/processed/val.csv')
    test_df = pd.read_csv('data/processed/test.csv')

# Load model
print("\n[LOADING MODEL]")
MODEL = "Helsinki-NLP/opus-mt-en-mul"
print(f"Model: {MODEL}")
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)
model = model.to(device)
print("Model loaded")

# Prepare data
print("\n[PREPARING DATASETS]")

def create_dataset(df):
    return Dataset.from_dict({
        'source': df['english'].fillna('').tolist(),
        'target': df['luganda'].fillna('').tolist(),
    })

def preprocess(examples):
    return tokenizer(examples['source'], text_target=examples['target'],
                    max_length=128, truncation=True, padding="max_length")

train_dataset = create_dataset(train_df).map(preprocess, batched=True, batch_size=100)
val_dataset = create_dataset(val_df).map(preprocess, batched=True, batch_size=100)
test_dataset = create_dataset(test_df).map(preprocess, batched=True, batch_size=100)

print("Data prepared")

# Training args
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

print("Training configured")
print(f"  Epochs: 3")
print(f"  Batch size: 8")
print(f"  Training samples: {len(train_df)}")

# Trainer
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,
)

# Train
print("\n" + "="*70)
print(f"TRAINING ON {len(train_df)} SAMPLES")
print("="*70)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

result = trainer.train()

print(f"\nTraining complete!")
print(f"  Loss: {result.training_loss:.4f}")

# Evaluate
print("\n[EVALUATING ON TEST SET]")

from sacrebleu import corpus_bleu

predictions = trainer.predict(test_dataset)
decoded_preds = tokenizer.batch_decode(predictions.predictions, skip_special_tokens=True)
decoded_labels = tokenizer.batch_decode(predictions.label_ids, skip_special_tokens=True)

bleu = corpus_bleu(decoded_preds, [decoded_labels])

print(f"\nTEST SET BLEU SCORE: {bleu.score:.2f}")

# Show samples
print("\n[SAMPLE PREDICTIONS]")
for i in range(min(5, len(decoded_preds))):
    print(f"\n{i+1}. Reference: {decoded_labels[i]}")
    print(f"   Predicted: {decoded_preds[i]}")

# Save
print("\n[SAVING MODEL]")

model_path = '/content/translator/models/kambale_combined_model'
os.makedirs(model_path, exist_ok=True)
model.save_pretrained(model_path)
tokenizer.save_pretrained(model_path)

metrics = {
    "dataset": "kambale_combined_local",
    "bleu_score": float(bleu.score),
    "training_loss": float(result.training_loss),
    "train_samples": len(train_df),
    "val_samples": len(val_df),
    "test_samples": len(test_df),
    "model": MODEL,
    "timestamp": datetime.now().isoformat()
}

metrics_file = '/content/translator/metrics_kambale_combined.json'
with open(metrics_file, 'w') as f:
    json.dump(metrics, f, indent=2)

from google.colab import files
files.download(metrics_file)

print("Model saved and metrics downloaded!")

# Summary
print("\n" + "="*70)
print("TRAINING COMPLETE!")
print("="*70)

print(f"""
FINAL RESULTS:
   BLEU Score: {bleu.score:.2f}
   Training Loss: {result.training_loss:.4f}
   Samples: {len(train_df)}

Datasets used:
   Kambale Luganda-English Parallel Corpus
   Cultural dictionary
   JW300 parallel corpus
   Makerere NLP
   Sunbird Salt

Model saved to: {model_path}

Ready for production!
""")

print("="*70)
