#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRODUCTION-GRADE TRAINER WITH KABALE DATASET
Trains a high-quality English-Luganda translator using kambale/luganda-english-parallel-corpus
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import torch
from pathlib import Path
from datasets import load_dataset, Dataset, DatasetDict
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq
)
import warnings
warnings.filterwarnings('ignore')

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 100)
print("[TRAINER] PRODUCTION-GRADE TRAINER WITH KABALE ENGLISH-LUGANDA DATASET")
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

# Device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"\n🖥️  Device: {device.upper()}")

# ============================================================================
# STEP 1: LOAD KABALE DATASET
# ============================================================================
print("\n[STEP 1] LOADING KABALE ENGLISH-LUGANDA DATASET...")
print(f"  📥 Dataset: {CONFIG['dataset_name']}")

try:
    # Load the dataset
    dataset = load_dataset(CONFIG['dataset_name'])
    print(f"  ✅ Dataset loaded successfully!")
    print(f"  📊 Available splits: {list(dataset.keys())}")
    
    # Get the main split
    if 'train' in dataset:
        main_data = dataset['train']
    else:
        main_data = dataset[list(dataset.keys())[0]]
    
    print(f"  📈 Total samples: {len(main_data):,}")
    
    # Inspect the structure
    print(f"  🔍 Column structure: {main_data.column_names}")
    print(f"  📋 Sample entry:")
    sample = main_data[0]
    print(f"     {json.dumps(sample, indent=2, default=str)}")
    
except Exception as e:
    print(f"  ❌ Error loading dataset: {e}")
    print(f"  💡 Make sure you have internet connection and the dataset is accessible")
    sys.exit(1)

# ============================================================================
# STEP 2: NORMALIZE AND PREPARE DATA
# ============================================================================
print("\n[STEP 2] NORMALIZING AND PREPARING DATA...")

def normalize_dataset(hf_dataset):
    """Convert HF dataset to DataFrame with 'english' and 'luganda' columns."""
    rows = []
    
    for item in hf_dataset:
        try:
            # Handle nested translation column
            if 'translation' in item and isinstance(item['translation'], dict):
                eng = item['translation'].get('en') or item['translation'].get('eng') or item['translation'].get('english') or ''
                lug = item['translation'].get('lg') or item['translation'].get('lug') or item['translation'].get('luganda') or ''
            # Handle flat columns
            elif 'english' in item and 'luganda' in item:
                eng = item['english']
                lug = item['luganda']
            else:
                continue
            
            # Clean
            eng = str(eng).strip() if eng else ''
            lug = str(lug).strip() if lug else ''
            
            # Validate
            if len(eng) > 3 and len(lug) > 3 and eng != 'nan' and lug != 'nan':
                rows.append({'english': eng, 'luganda': lug})
        except Exception as e:
            continue
    
    return pd.DataFrame(rows)

# Normalize
try:
    df = normalize_dataset(main_data)
    print(f"  ✅ Normalized {len(df):,} valid translation pairs")
    
    # Show statistics
    print(f"\n  📊 Data Statistics:")
    print(f"     • English avg length: {df['english'].str.len().mean():.1f} chars")
    print(f"     • Luganda avg length: {df['luganda'].str.len().mean():.1f} chars")
    print(f"     • Unique pairs: {df.drop_duplicates().shape[0]:,}")
    
except Exception as e:
    print(f"  ❌ Error normalizing dataset: {e}")
    sys.exit(1)

# Remove duplicates
df = df.drop_duplicates().reset_index(drop=True)
print(f"  ✅ After deduplication: {len(df):,} pairs")

# ============================================================================
# STEP 3: SPLIT DATA
# ============================================================================
print("\n[STEP 3] SPLITTING DATA INTO TRAIN/VAL/TEST...")

np.random.seed(CONFIG['seed'])
indices = np.random.permutation(len(df))

# 70% train, 15% val, 15% test
train_size = int(len(df) * 0.70)
val_size = int(len(df) * 0.15)

train_idx = indices[:train_size]
val_idx = indices[train_size:train_size + val_size]
test_idx = indices[train_size + val_size:]

df_train = df.iloc[train_idx].reset_index(drop=True)
df_val = df.iloc[val_idx].reset_index(drop=True)
df_test = df.iloc[test_idx].reset_index(drop=True)

print(f"  ✅ Train: {len(df_train):,} pairs ({len(df_train)/len(df)*100:.1f}%)")
print(f"  ✅ Val:   {len(df_val):,} pairs ({len(df_val)/len(df)*100:.1f}%)")
print(f"  ✅ Test:  {len(df_test):,} pairs ({len(df_test)/len(df)*100:.1f}%)")

# ============================================================================
# STEP 4: LOAD MODEL AND TOKENIZER
# ============================================================================
print(f"\n[STEP 4] LOADING MODEL AND TOKENIZER...")
print(f"  📦 Base model: {CONFIG['base_model']}")

try:
    tokenizer = AutoTokenizer.from_pretrained(CONFIG['base_model'])
    model = AutoModelForSeq2SeqLM.from_pretrained(CONFIG['base_model'])
    print(f"  ✅ Model loaded: {model.num_parameters():,} parameters")
    
    model.to(device)
    print(f"  ✅ Model moved to {device.upper()}")
except Exception as e:
    print(f"  ❌ Error loading model: {e}")
    sys.exit(1)

# ============================================================================
# STEP 5: TOKENIZE DATASETS
# ============================================================================
print(f"\n[STEP 5] TOKENIZING DATASETS...")

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

print(f"  🔄 Tokenizing train dataset...")
train_dataset = train_dataset.map(preprocess_function, batched=True, remove_columns=['english', 'luganda'])

print(f"  🔄 Tokenizing val dataset...")
val_dataset = val_dataset.map(preprocess_function, batched=True, remove_columns=['english', 'luganda'])

print(f"  🔄 Tokenizing test dataset...")
test_dataset = test_dataset.map(preprocess_function, batched=True, remove_columns=['english', 'luganda'])

print(f"  ✅ Tokenization complete")

# ============================================================================
# STEP 6: SETUP TRAINING
# ============================================================================
print(f"\n[STEP 6] SETTING UP TRAINING ARGUMENTS...")

# Create output directory
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
    fp16=False,  # Disable for CPU compatibility
    seed=CONFIG['seed'],
    dataloader_num_workers=0,
)

print(f"  ✅ Training config ready")

# ============================================================================
# STEP 7: TRAIN MODEL
# ============================================================================
print(f"\n[STEP 7] STARTING MODEL TRAINING...")
print(f"  ⏱️  This may take a while depending on dataset size and device...")

try:
    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    # Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    # Train
    trainer.train()
    print(f"  ✅ Training complete!")
    
except Exception as e:
    print(f"  ❌ Error during training: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 8: EVALUATE MODEL
# ============================================================================
print(f"\n[STEP 8] EVALUATING MODEL ON TEST SET...")

try:
    eval_results = trainer.evaluate(test_dataset)
    print(f"  📊 Evaluation Results:")
    for key, value in eval_results.items():
        print(f"     • {key}: {value:.4f}")
    
except Exception as e:
    print(f"  ⚠️  Evaluation error: {e}")

# ============================================================================
# STEP 9: SAVE MODEL
# ============================================================================
print(f"\n[STEP 9] SAVING MODEL...")

try:
    # Save using HF method (handles CPU conversion automatically)
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    print(f"  ✅ Model saved to: {output_dir}")
    
    # Also save config
    config_data = {
        'model_name': CONFIG['base_model'],
        'dataset': CONFIG['dataset_name'],
        'train_samples': len(df_train),
        'val_samples': len(df_val),
        'test_samples': len(df_test),
        'epochs': CONFIG['epochs'],
        'batch_size': CONFIG['batch_size'],
        'learning_rate': CONFIG['learning_rate'],
        'max_length': CONFIG['max_length'],
    }
    
    with open(output_dir / 'training_config.json', 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"  ✅ Training config saved")
    
except Exception as e:
    print(f"  ❌ Error saving model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 10: TEST INFERENCE
# ============================================================================
print(f"\n[STEP 10] TESTING MODEL INFERENCE...")

try:
    # Reload model for testing
    test_tokenizer = AutoTokenizer.from_pretrained(str(output_dir))
    test_model = AutoModelForSeq2SeqLM.from_pretrained(str(output_dir))
    test_model.to(device)
    test_model.eval()
    
    # Test translations
    test_sentences = [
        "Hello, how are you?",
        "What is your name?",
        "Good morning, welcome to Uganda.",
    ]
    
    print(f"\n  🌐 Sample Translations:")
    for sent in test_sentences:
        try:
            inputs = test_tokenizer(sent, return_tensors='pt', max_length=128, truncation=True).to(device)
            output_ids = test_model.generate(**inputs, max_length=128)
            translated = test_tokenizer.decode(output_ids[0], skip_special_tokens=True)
            print(f"     EN: {sent}")
            print(f"     LG: {translated}\n")
        except Exception as e:
            print(f"     ❌ Translation error: {e}\n")
    
    print(f"  ✅ Inference test complete!")
    
except Exception as e:
    print(f"  ❌ Error during inference: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 100)
print("✅ TRAINING COMPLETE!")
print("=" * 100)
print(f"""
📦 Model Information:
   • Location: {output_dir}
   • Base Model: {CONFIG['base_model']}
   • Dataset: {CONFIG['dataset_name']}
   • Training Samples: {len(df_train):,}
   • Validation Samples: {len(df_val):,}
   • Test Samples: {len(df_test):,}

🚀 Next Steps:
   1. Update app_streamlit.py to load from: {output_dir}
   2. Test the Streamlit app: streamlit run app_streamlit.py
   3. Deploy to production

✨ Ready for deployment!
""")
