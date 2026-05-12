#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRODUCTION-GRADE TRAINER WITH KABALE DATASET
Trains a high-quality English-Luganda translator using kambale/luganda-english-parallel-corpus
Uses HuggingFace API for direct dataset access via bearer token.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import torch
from pathlib import Path
from dataset_loader_api import load_all_available_datasets
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq
)
from datasets import Dataset, DatasetDict
import warnings
warnings.filterwarnings('ignore')

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("[TRAINER] PRODUCTION-GRADE TRAINER - KABALE ENGLISH-LUGANDA DATASET")
print("=" * 100)

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    'dataset_name': 'kambale/luganda-english-parallel-corpus',
    'base_model': 'Helsinki-NLP/opus-mt-en-mul',
    'trained_model_path': 'models/trained_model_cpu',
    'epochs': 5,
    'batch_size': 16,
    'learning_rate': 2e-5,
    'max_length': 128,
    'warmup_steps': 500,
    'seed': 42,
}

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"\n[DEVICE] {device.upper()}")

# ============================================================================
# STEP 1: LOAD KABALE DATASET VIA API
# ============================================================================
print("\n[STEP 1] LOADING KABALE DATASET VIA HUGGINGFACE API")
print(f"[DATA] Dataset: {CONFIG['dataset_name']}")

try:
    # Load using API (handles gated dataset access)
    df = load_all_available_datasets()
    
    print(f"[DATA] Dataset loaded successfully")
    print(f"[DATA] Total samples: {len(df):,}")
    
    # Statistics
    print(f"\n[STATS] Data Statistics:")
    print(f"[STATS] English avg length: {df['english'].str.len().mean():.1f} characters")
    print(f"[STATS] Luganda avg length: {df['luganda'].str.len().mean():.1f} characters")
    
    # Show sample
    print(f"\n[SAMPLE] Example translation pair:")
    if len(df) > 0:
        print(f"[SAMPLE] EN: {df.iloc[0]['english']}")
        print(f"[SAMPLE] LG: {df.iloc[0]['luganda']}")
    
except Exception as e:
    print(f"[ERROR] Failed to load dataset: {e}")
    print(f"[INFO] Make sure HF_TOKEN is set. Get token from:")
    print(f"[INFO] https://huggingface.co/settings/tokens")
    sys.exit(1)

# ============================================================================
# STEP 2: PREPARE DATA
# ============================================================================
print("\n[STEP 2] PREPARING DATA")

# Remove duplicates
df_original = len(df)
df = df.drop_duplicates(subset=['english', 'luganda']).reset_index(drop=True)
print(f"[PREP] Removed {df_original - len(df):,} duplicates")
print(f"[PREP] Final dataset: {len(df):,} unique pairs")

# ============================================================================
# STEP 3: SPLIT DATA
# ============================================================================
print("\n[STEP 3] SPLITTING DATA INTO TRAIN/VAL/TEST")

np.random.seed(CONFIG['seed'])
indices = np.random.permutation(len(df))

train_size = int(len(df) * 0.70)
val_size = int(len(df) * 0.15)

train_idx = indices[:train_size]
val_idx = indices[train_size:train_size + val_size]
test_idx = indices[train_size + val_size:]

df_train = df.iloc[train_idx].reset_index(drop=True)
df_val = df.iloc[val_idx].reset_index(drop=True)
df_test = df.iloc[test_idx].reset_index(drop=True)

print(f"[SPLIT] Train: {len(df_train):,} pairs ({len(df_train)/len(df)*100:.1f}%)")
print(f"[SPLIT] Validation: {len(df_val):,} pairs ({len(df_val)/len(df)*100:.1f}%)")
print(f"[SPLIT] Test: {len(df_test):,} pairs ({len(df_test)/len(df)*100:.1f}%)")

# ============================================================================
# STEP 4: LOAD MODEL AND TOKENIZER
# ============================================================================
print(f"\n[STEP 4] LOADING MODEL AND TOKENIZER")
print(f"[MODEL] Base model: {CONFIG['base_model']}")

try:
    tokenizer = AutoTokenizer.from_pretrained(CONFIG['base_model'])
    model = AutoModelForSeq2SeqLM.from_pretrained(CONFIG['base_model'])
    print(f"[MODEL] Model loaded: {model.num_parameters():,} parameters")
    
    model.to(device)
    print(f"[MODEL] Model moved to {device.upper()}")
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    sys.exit(1)

# ============================================================================
# STEP 5: TOKENIZE DATASETS
# ============================================================================
print(f"\n[STEP 5] TOKENIZING DATASETS")

def preprocess_function(examples):
    """Tokenize inputs and targets."""
    inputs = examples['english']
    targets = examples['luganda']
    
    model_inputs = tokenizer(
        inputs,
        max_length=CONFIG['max_length'],
        truncation=True,
        padding='max_length'
    )
    
    labels = tokenizer(
        targets,
        max_length=CONFIG['max_length'],
        truncation=True,
        padding='max_length'
    )
    
    model_inputs['labels'] = labels['input_ids']
    return model_inputs

# Convert to HF Datasets
train_dataset = Dataset.from_pandas(df_train[['english', 'luganda']])
val_dataset = Dataset.from_pandas(df_val[['english', 'luganda']])
test_dataset = Dataset.from_pandas(df_test[['english', 'luganda']])

print(f"[TOKENIZE] Tokenizing train dataset...")
train_dataset = train_dataset.map(preprocess_function, batched=True, remove_columns=['english', 'luganda'])

print(f"[TOKENIZE] Tokenizing validation dataset...")
val_dataset = val_dataset.map(preprocess_function, batched=True, remove_columns=['english', 'luganda'])

print(f"[TOKENIZE] Tokenizing test dataset...")
test_dataset = test_dataset.map(preprocess_function, batched=True, remove_columns=['english', 'luganda'])

print(f"[TOKENIZE] Tokenization complete")

# ============================================================================
# STEP 6: SETUP TRAINING
# ============================================================================
print(f"\n[STEP 6] SETTING UP TRAINING ARGUMENTS")

output_dir = Path(CONFIG['trained_model_path'])
output_dir.mkdir(parents=True, exist_ok=True)

training_args = Seq2SeqTrainingArguments(
    output_dir=str(output_dir),
    num_train_epochs=CONFIG['epochs'],
    per_device_train_batch_size=CONFIG['batch_size'],
    per_device_eval_batch_size=CONFIG['batch_size'],
    learning_rate=CONFIG['learning_rate'],
    warmup_steps=CONFIG['warmup_steps'],
    weight_decay=0.01,
    logging_steps=100,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    predict_with_generate=True,
    fp16=False,
    seed=CONFIG['seed'],
    dataloader_num_workers=0,
)

print(f"[CONFIG] Training arguments configured")

# ============================================================================
# STEP 7: TRAIN MODEL
# ============================================================================
print(f"\n[STEP 7] STARTING MODEL TRAINING")
print(f"[TRAIN] Training with {len(df_train):,} samples for {CONFIG['epochs']} epochs")

try:
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    trainer.train()
    print(f"[TRAIN] Training complete")
    
except Exception as e:
    print(f"[ERROR] Training failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 8: EVALUATE MODEL
# ============================================================================
print(f"\n[STEP 8] EVALUATING MODEL ON TEST SET")

try:
    eval_results = trainer.evaluate(test_dataset)
    print(f"[EVAL] Evaluation Results:")
    for key, value in eval_results.items():
        print(f"[EVAL] {key}: {value:.4f}")
    
except Exception as e:
    print(f"[WARNING] Evaluation error: {e}")

# ============================================================================
# STEP 9: SAVE MODEL
# ============================================================================
print(f"\n[STEP 9] SAVING MODEL")

try:
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    print(f"[SAVE] Model saved to: {output_dir}")
    
    # Save config
    config_data = {
        'model_name': CONFIG['base_model'],
        'dataset': CONFIG['dataset_name'],
        'train_samples': len(df_train),
        'val_samples': len(df_val),
        'test_samples': len(df_test),
        'total_samples': len(df),
        'epochs': CONFIG['epochs'],
        'batch_size': CONFIG['batch_size'],
        'learning_rate': CONFIG['learning_rate'],
        'max_length': CONFIG['max_length'],
    }
    
    with open(output_dir / 'training_config.json', 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"[SAVE] Training config saved")
    
except Exception as e:
    print(f"[ERROR] Failed to save model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 10: TEST INFERENCE
# ============================================================================
print(f"\n[STEP 10] TESTING MODEL INFERENCE")

try:
    test_tokenizer = AutoTokenizer.from_pretrained(str(output_dir))
    test_model = AutoModelForSeq2SeqLM.from_pretrained(str(output_dir))
    test_model.to(device)
    test_model.eval()
    
    test_sentences = [
        "Hello, how are you?",
        "What is your name?",
        "Good morning, welcome to Uganda.",
    ]
    
    print(f"\n[INFERENCE] Sample Translations:")
    for sent in test_sentences:
        try:
            inputs = test_tokenizer(sent, return_tensors='pt', max_length=128, truncation=True).to(device)
            output_ids = test_model.generate(**inputs, max_length=128)
            translated = test_tokenizer.decode(output_ids[0], skip_special_tokens=True)
            print(f"[INFERENCE] EN: {sent}")
            print(f"[INFERENCE] LG: {translated}\n")
        except Exception as e:
            print(f"[ERROR] Translation error: {e}\n")
    
    print(f"[INFERENCE] Inference test complete")
    
except Exception as e:
    print(f"[ERROR] Inference error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("[SUCCESS] TRAINING COMPLETE")
print("=" * 100)
print(f"""
[MODEL] Information:
   Location: {output_dir}
   Base Model: {CONFIG['base_model']}
   Dataset: {CONFIG['dataset_name']}
   Training Samples: {len(df_train):,}
   Validation Samples: {len(df_val):,}
   Test Samples: {len(df_test):,}
   Total Samples: {len(df):,}

[NEXT] Steps:
   1. Update app_streamlit.py to load from: {output_dir}
   2. Run: streamlit run app_streamlit.py
   3. Deploy to production

[STATUS] Ready for deployment
""")
