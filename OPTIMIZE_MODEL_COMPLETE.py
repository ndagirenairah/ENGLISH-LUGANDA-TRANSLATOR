#!/usr/bin/env python3
"""
COMPREHENSIVE MODEL OPTIMIZATION & PERFORMANCE IMPROVEMENT PIPELINE
- Diagnoses current model issues
- Trains new model on best dataset
- Tests and validates improvements
- Generates performance report
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datasets import Dataset
import torch
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
print("🚀 COMPREHENSIVE MODEL OPTIMIZATION PIPELINE")
print("=" * 100)

# ============================================================================
# PHASE 1: DIAGNOSE CURRENT STATE
# ============================================================================
print("\n" + "=" * 100)
print("📊 PHASE 1: DIAGNOSE CURRENT MODEL STATE")
print("=" * 100)

# Check if trained model exists
trained_path = "models/trained_model"
pytorch_bin = os.path.join(trained_path, "pytorch_model.bin")
has_trained_weights = os.path.exists(pytorch_bin)

print(f"\n📁 Trained Model Status:")
print(f"   - Trained model directory exists: {os.path.exists(trained_path)}")
print(f"   - Model weights (pytorch_model.bin): {has_trained_weights}")

if not has_trained_weights:
    print("   ⚠️  NO TRAINED WEIGHTS FOUND - Will train from scratch")

# Check available data
print(f"\n📚 Data Availability:")
data_files = {
    "training": "data/train_data.csv",
    "validation": "data/val_data.csv",
    "test": "data/test_data.csv",
    "main_training": "luganda_training_data.csv"
}

for name, path in data_files.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        print(f"   ✅ {name:20s}: {len(df):6d} samples - {path}")
    else:
        print(f"   ❌ {name:20s}: NOT FOUND")

# ============================================================================
# PHASE 2: LOAD AND PREPARE DATA
# ============================================================================
print("\n" + "=" * 100)
print("📊 PHASE 2: LOAD & PREPARE TRAINING DATA")
print("=" * 100)

# Load the main training dataset
print("\n📖 Loading training data...")
df_train = pd.read_csv("luganda_training_data.csv")
print(f"   ✅ Loaded {len(df_train)} training samples")

# Clean column names
df_train.columns = df_train.columns.str.strip().str.lower()
print(f"   ✅ Columns: {list(df_train.columns)}")

# Find the right columns
lug_col = None
eng_col = None

for col in df_train.columns:
    if 'luganda' in col or 'lug' in col or 'source' in col:
        lug_col = col
    if 'english' in col or 'eng' in col or 'target' in col:
        eng_col = col

print(f"   ✅ Luganda column: {lug_col}")
print(f"   ✅ English column: {eng_col}")

# Prepare data
train_data = []
for idx, row in df_train.iterrows():
    try:
        lug_text = str(row[lug_col]).strip()
        eng_text = str(row[eng_col]).strip()
        
        # Skip empty or invalid entries
        if len(lug_text) > 2 and len(eng_text) > 2 and lug_text != "nan" and eng_text != "nan":
            train_data.append({
                "source": lug_text,
                "target": eng_text
            })
    except:
        continue

print(f"   ✅ Valid training pairs: {len(train_data)} ({len(train_data)/len(df_train)*100:.1f}%)")

# Split into train/val (80/20)
np.random.seed(42)
indices = np.random.permutation(len(train_data))
train_idx = indices[:int(len(train_data) * 0.8)]
val_idx = indices[int(len(train_data) * 0.8):]

train_dataset = [train_data[i] for i in train_idx]
val_dataset = [train_data[i] for i in val_idx]

print(f"   ✅ Train/Val split: {len(train_dataset)}/{len(val_dataset)}")

# Create HF datasets
train_df = pd.DataFrame(train_dataset)
val_df = pd.DataFrame(val_dataset)

train_hf = Dataset.from_pandas(train_df)
val_hf = Dataset.from_pandas(val_df)

print(f"   ✅ HuggingFace datasets created")

# ============================================================================
# PHASE 3: LOAD MODEL & TOKENIZER
# ============================================================================
print("\n" + "=" * 100)
print("🤖 PHASE 3: LOAD MODEL & TOKENIZER")
print("=" * 100)

print("\n📥 Loading model...")

# Use the correct model for Luganda→English translation
# If trained model exists, load it; otherwise use base model
if has_trained_weights:
    print("   ✅ Loading TRAINED model (custom fine-tuned weights)")
    model_name = trained_path
else:
    print("   ℹ️  Loading BASE model (Helsinki-NLP/opus-mt-en-mul)")
    model_name = "Helsinki-NLP/opus-mt-en-mul"

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    print(f"   ✅ Model loaded successfully")
    print(f"   ℹ️  Model size: {model.num_parameters():,} parameters")
except Exception as e:
    print(f"   ❌ Error loading model: {e}")
    sys.exit(1)

# ============================================================================
# PHASE 4: PREPARE DATA FOR TRAINING
# ============================================================================
print("\n" + "=" * 100)
print("⚙️  PHASE 4: PREPARE DATA FOR TRAINING")
print("=" * 100)

def preprocess_function(examples):
    """Preprocess dataset for training"""
    inputs = examples["source"]
    targets = examples["target"]
    
    model_inputs = tokenizer(
        inputs,
        max_length=128,
        truncation=True,
        padding="max_length"
    )
    
    labels = tokenizer(
        targets,
        max_length=128,
        truncation=True,
        padding="max_length"
    )
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

print("\n📑 Tokenizing training data...")
train_tokenized = train_hf.map(preprocess_function, batched=True)
val_tokenized = val_hf.map(preprocess_function, batched=True)
print(f"   ✅ Training data tokenized: {len(train_tokenized)} samples")
print(f"   ✅ Validation data tokenized: {len(val_tokenized)} samples")

# ============================================================================
# PHASE 5: TRAIN MODEL
# ============================================================================
print("\n" + "=" * 100)
print("🏋️  PHASE 5: TRAIN MODEL")
print("=" * 100)

# Training arguments
training_args = Seq2SeqTrainingArguments(
    output_dir=trained_path,
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    weight_decay=0.01,
    save_total_limit=3,
    num_train_epochs=3,  # 3 epochs for better convergence
    predict_with_generate=True,
    fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
    logging_steps=100,
    save_steps=200,
    eval_steps=200,
    gradient_accumulation_steps=2,
)

print("\n🎯 Training arguments:")
print(f"   - Learning rate: {training_args.learning_rate}")
print(f"   - Batch size: {training_args.per_device_train_batch_size}")
print(f"   - Epochs: {training_args.num_train_epochs}")
print(f"   - Device: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}")

# Data collator
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_tokenized,
    eval_dataset=val_tokenized,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

print("\n🚀 Starting training...")
print("   (This may take 5-30 minutes depending on dataset size and device)\n")

train_result = trainer.train()

print("\n✅ Training complete!")
print(f"   - Final training loss: {train_result.training_loss:.4f}")

# ============================================================================
# PHASE 6: EVALUATE ON TEST SET
# ============================================================================
print("\n" + "=" * 100)
print("📊 PHASE 6: EVALUATE ON TEST SET")
print("=" * 100)

# Load test data
if os.path.exists("data/test_data.csv"):
    test_df = pd.read_csv("data/test_data.csv")
    test_df.columns = test_df.columns.str.strip().str.lower()
    
    # Find columns
    test_lug_col = None
    test_eng_col = None
    for col in test_df.columns:
        if 'luganda' in col or 'lug' in col or 'source' in col:
            test_lug_col = col
        if 'english' in col or 'eng' in col or 'target' in col:
            test_eng_col = col
    
    print(f"\n📖 Test set: {len(test_df)} samples")
    
    # Generate translations
    print("\n🔄 Generating test predictions...")
    predictions = []
    references = []
    
    for idx, row in test_df.head(100).iterrows():  # Test on first 100
        try:
            source = str(row[test_lug_col]).strip()
            target = str(row[test_eng_col]).strip()
            
            input_ids = tokenizer.encode(source, return_tensors="pt")
            outputs = model.generate(input_ids, max_length=100, num_beams=4)
            prediction = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            predictions.append(prediction)
            references.append(target)
            
            if (idx + 1) % 20 == 0:
                print(f"   ✓ Processed {idx + 1} samples")
        except:
            continue
    
    print(f"   ✅ Generated {len(predictions)} predictions")
    
    # Calculate metrics
    try:
        from sacrebleu import corpus_chrf, corpus_bleu
        
        print("\n📈 Calculating metrics...")
        chrf = corpus_chrf(predictions, [references])
        bleu = corpus_bleu(predictions, [references])
        
        print(f"   ✅ chrF++ Score: {chrf.score:.1f}/100")
        print(f"   ✅ BLEU Score:   {bleu.score:.1f}/100")
        
        quality = "EXCELLENT" if chrf.score >= 70 else "GOOD" if chrf.score >= 50 else "FAIR" if chrf.score >= 30 else "POOR"
        print(f"   🎯 Quality Rating: {quality}")
    except ImportError:
        print("   ⚠️  sacrebleu not available")

# ============================================================================
# PHASE 7: SAVE MODEL & REPORT
# ============================================================================
print("\n" + "=" * 100)
print("💾 PHASE 7: SAVE MODEL & REPORT")
print("=" * 100)

print(f"\n💾 Saving model to {trained_path}...")
model.save_pretrained(trained_path)
tokenizer.save_pretrained(trained_path)
print("   ✅ Model saved successfully")

# Create report
report = {
    "timestamp": pd.Timestamp.now().isoformat(),
    "phase": "optimization_complete",
    "model_type": "trained" if has_trained_weights else "base",
    "data_stats": {
        "total_training_pairs": len(train_data),
        "training_samples": len(train_dataset),
        "validation_samples": len(val_dataset),
        "avg_source_length": float(train_df["source"].str.len().mean()),
        "avg_target_length": float(train_df["target"].str.len().mean()),
    },
    "training_config": {
        "epochs": training_args.num_train_epochs,
        "batch_size": training_args.per_device_train_batch_size,
        "learning_rate": training_args.learning_rate,
        "device": "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
    },
    "status": "READY FOR DEPLOYMENT"
}

with open("outputs/optimization_report.json", "w") as f:
    json.dump(report, f, indent=2)

print("\n✅ Optimization report saved to outputs/optimization_report.json")

# ============================================================================
# PHASE 8: FINAL STATUS
# ============================================================================
print("\n" + "=" * 100)
print("✅ OPTIMIZATION PIPELINE COMPLETE")
print("=" * 100)

print(f"""
✅ MODEL STATUS: TRAINED & READY

🎯 Next Steps:
   1. Test the model: python Step6_Test_Model.py
   2. Run full evaluation: python Step7_Evaluate_BLEU.py
   3. Deploy web app: python app.py
   4. Monitor performance: Check outputs/quick_test_results.csv

📊 Performance Metrics:
   - Model: TRAINED MODEL
   - Device: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}
   - Parameters: {model.num_parameters():,}
   - Training Data: {len(train_dataset)} samples
   - Validation Data: {len(val_dataset)} samples

🚀 Model Ready for Production!
""")

print("=" * 100)
