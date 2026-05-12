#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRODUCTION TRAINER - PUBLIC DATASETS VERSION
Uses publicly available Luganda-English datasets (Sunbird SALT + JW300)
For users without access to the gated Kabale dataset
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
print("[TRAINER] PRODUCTION TRAINER WITH PUBLIC LUGANDA-ENGLISH DATASETS")
print("=" * 100)

# ============================================================================
# CONFIGURATION
# ============================================================================
CONFIG = {
    'datasets': ['sunbird', 'jw300'],  # Public datasets to use
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
print(f"\n🖥️  Device: {device.upper()}")

# ============================================================================
# STEP 1: LOAD PUBLIC DATASETS
# ============================================================================
print("\n[STEP 1] LOADING PUBLIC LUGANDA-ENGLISH DATASETS...")

all_data = []

# Load Sunbird SALT Dataset
print(f"\n  [1/2] Loading Sunbird AI SALT Dataset...")
try:
    dataset_sunbird = load_dataset("Sunbird/salt", "lug-eng", split="train")
    print(f"  ✅ Sunbird loaded: {len(dataset_sunbird):,} samples")
    
    for item in dataset_sunbird:
        try:
            eng = item['translation'].get('eng') or item['translation'].get('en') or ''
            lug = item['translation'].get('lug') or item['translation'].get('lg') or ''
            
            eng = str(eng).strip() if eng else ''
            lug = str(lug).strip() if lug else ''
            
            if len(eng) > 3 and len(lug) > 3:
                all_data.append({'english': eng, 'luganda': lug, 'source': 'Sunbird SALT'})
        except:
            continue
    
    print(f"     ✅ Extracted {len([d for d in all_data if d['source'] == 'Sunbird SALT']):,} valid pairs")
    
except Exception as e:
    print(f"  ⚠️  Sunbird SALT: {e}")

# Load JW300 Corpus
print(f"\n  [2/2] Loading JW300 Parallel Corpus (en-lg)...")
try:
    dataset_jw300 = load_dataset("opus_100", "en-lg", split="train", trust_remote_code=True)
    print(f"  ✅ JW300 loaded: {len(dataset_jw300):,} samples (will use subset)")
    
    # Limit to avoid excessive memory usage
    jw300_limit = min(10000, len(dataset_jw300))
    
    for i, item in enumerate(dataset_jw300):
        if i >= jw300_limit:
            break
        
        try:
            eng = item['translation'].get('en') or ''
            lug = item['translation'].get('lg') or ''
            
            eng = str(eng).strip() if eng else ''
            lug = str(lug).strip() if lug else ''
            
            if len(eng) > 3 and len(lug) > 3:
                all_data.append({'english': eng, 'luganda': lug, 'source': 'JW300'})
        except:
            continue
    
    print(f"     ✅ Extracted {len([d for d in all_data if d['source'] == 'JW300']):,} valid pairs")
    
except Exception as e:
    print(f"  ⚠️  JW300: {e}")

# Verify we have data
if len(all_data) == 0:
    print("\n❌ ERROR: No data loaded from any dataset!")
    print("Make sure you have internet connection and the datasets are accessible.")
    sys.exit(1)

print(f"\n  ✅ Total combined: {len(all_data):,} translation pairs")

# ============================================================================
# STEP 2: PREPARE DATA
# ============================================================================
print("\n[STEP 2] PREPARING DATA...")

df = pd.DataFrame(all_data)

# Remove duplicates
df_original_len = len(df)
df = df.drop_duplicates(subset=['english', 'luganda']).reset_index(drop=True)
print(f"  ✅ Removed {df_original_len - len(df):,} duplicates")
print(f"  ✅ Final dataset: {len(df):,} unique pairs")

# Data statistics
print(f"\n  📊 Data Statistics:")
print(f"     • English avg length: {df['english'].str.len().mean():.1f} chars")
print(f"     • Luganda avg length: {df['luganda'].str.len().mean():.1f} chars")

# Source distribution
print(f"\n  📚 Data Sources:")
for source in df['source'].unique():
    count = (df['source'] == source).sum()
    pct = count / len(df) * 100
    print(f"     • {source}: {count:,} pairs ({pct:.1f}%)")

# ============================================================================
# STEP 3: SPLIT DATA
# ============================================================================
print(f"\n[STEP 3] SPLITTING DATA INTO TRAIN/VAL/TEST...")

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

print(f"  ✅ Training config ready")

# ============================================================================
# STEP 7: TRAIN MODEL
# ============================================================================
print(f"\n[STEP 7] STARTING MODEL TRAINING...")
print(f"  ⏱️  Training with {len(df_train):,} samples...")

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
    print(f"  ✅ Training complete!")
    
except Exception as e:
    print(f"  ❌ Error during training: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# STEP 8: EVALUATE
# ============================================================================
print(f"\n[STEP 8] EVALUATING MODEL...")

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
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    print(f"  ✅ Model saved to: {output_dir}")
    
    config_data = {
        'model_name': CONFIG['base_model'],
        'datasets_used': CONFIG['datasets'],
        'train_samples': len(df_train),
        'val_samples': len(df_val),
        'test_samples': len(df_test),
        'epochs': CONFIG['epochs'],
        'batch_size': CONFIG['batch_size'],
        'learning_rate': CONFIG['learning_rate'],
    }
    
    with open(output_dir / 'training_config.json', 'w') as f:
        json.dump(config_data, f, indent=2)
    
    print(f"  ✅ Training config saved")
    
except Exception as e:
    print(f"  ❌ Error saving model: {e}")
    sys.exit(1)

# ============================================================================
# STEP 10: TEST INFERENCE
# ============================================================================
print(f"\n[STEP 10] TESTING MODEL INFERENCE...")

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
    
    print(f"\n  🌐 Sample Translations:")
    for sent in test_sentences:
        try:
            inputs = test_tokenizer(sent, return_tensors='pt', max_length=128, truncation=True).to(device)
            output_ids = test_model.generate(**inputs, max_length=128)
            translated = test_tokenizer.decode(output_ids[0], skip_special_tokens=True)
            print(f"     EN: {sent}")
            print(f"     LG: {translated}\n")
        except Exception as e:
            print(f"     ❌ Error: {e}\n")
    
    print(f"  ✅ Inference test complete!")
    
except Exception as e:
    print(f"  ❌ Error during inference: {e}")

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
   • Datasets: Sunbird SALT + JW300 (Public)
   • Training Samples: {len(df_train):,}
   • Validation Samples: {len(df_val):,}
   • Test Samples: {len(df_test):,}

💡 Note:
   For better results, consider requesting access to the Kabale dataset:
   https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus
   (See DATASET_ACCESS_GUIDE.py for instructions)

🚀 Next Steps:
   1. Update app_streamlit.py to load from: {output_dir}
   2. Test the Streamlit app: streamlit run app_streamlit.py
   3. Deploy to production

✨ Ready for deployment!
""")
