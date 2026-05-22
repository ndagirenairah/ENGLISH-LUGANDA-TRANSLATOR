#!/usr/bin/env python3
# ============================================================================
# COMBINE DATASETS WITH KAMBALE (USING HF TOKEN)
# ============================================================================
# This script:
# 1. Uses HF token to load gated Kambale dataset
# 2. Loads all local datasets
# 3. Cleans and deduplicates
# 4. Combines and splits train/val/test
# ============================================================================

import os
import json
import pandas as pd
import random
from datetime import datetime
from collections import Counter

print("\n" + "="*80)
print("  📚 COMBINING KAMBALE + LOCAL DATASETS")
print("="*80)

# ============================================================================
# LOGIN WITH HF TOKEN
# ============================================================================
print("\n[STEP 1: AUTHENTICATING WITH HUGGING FACE]")
print("="*80)

try:
    from huggingface_hub import login
    # Token from environment variable (set in Colab or local environment)
    hf_token = os.environ.get('HF_TOKEN')
    if not hf_token:
        print("⚠ HF_TOKEN not found in environment variables")
        print("To authenticate, set HF_TOKEN or use: huggingface-cli login")
    else:
        login(token=hf_token)
        print("✓ Successfully authenticated with Hugging Face")
except Exception as e:
    print(f"⚠ Authentication note: {e}")

# ============================================================================
# LOAD KAMBALE DATASET
# ============================================================================
print("\n[STEP 2: LOADING KAMBALE DATASET]")
print("="*80)

kambale_data = []
try:
    from datasets import load_dataset
    
    print("Loading: kambale/luganda-english-parallel-corpus")
    dataset = load_dataset(
        "kambale/luganda-english-parallel-corpus",
        trust_remote_code=True
    )
    
    print(f"Available splits: {list(dataset.keys())}")
    
    for split_name in dataset.keys():
        print(f"\nProcessing split: {split_name} ({len(dataset[split_name])} samples)")
        
        for idx, example in enumerate(dataset[split_name]):
            try:
                en_text = str(example.get('english', '')).strip()
                lg_text = str(example.get('luganda', '')).strip()
                
                if en_text and lg_text:
                    kambale_data.append({
                        'english': en_text,
                        'luganda': lg_text,
                        'source': 'kambale'
                    })
            except Exception as e:
                if idx < 5:  # Only show first few errors
                    print(f"  Note: Skipped sample {idx}: {e}")
                continue
    
    print(f"\n✓ Loaded {len(kambale_data)} samples from Kambale")
    
except Exception as e:
    print(f"❌ Error loading Kambale dataset: {e}")
    print("\nTroubleshooting:")
    print("1. Ensure you've accepted the dataset terms:")
    print("   https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus")
    print("2. Your HF token has been set correctly")
    print("3. You have internet connection")
    kambale_data = []

# ============================================================================
# LOAD LOCAL DATASETS
# ============================================================================
print("\n[STEP 3: LOADING LOCAL DATASETS]")
print("="*80)

local_data = []
data_dir = 'data/raw'

datasets_to_load = {
    'cultural_training.csv': 'cultural',
    'jw300_parallel.csv': 'jw300',
    'makerere_nlp.csv': 'makerere',
    'sunbird_salt.csv': 'sunbird'
}

for filename, source_name in datasets_to_load.items():
    filepath = os.path.join(data_dir, filename)
    
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            
            # Detect column names
            en_col = None
            lg_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if 'english' in col_lower or col_lower == 'en':
                    en_col = col
                if 'luganda' in col_lower or col_lower == 'lg':
                    lg_col = col
            
            if en_col and lg_col:
                source_count = 0
                for _, row in df.iterrows():
                    en_text = str(row[en_col]).strip()
                    lg_text = str(row[lg_col]).strip()
                    
                    if en_text and lg_text and len(en_text) > 3 and len(lg_text) > 3:
                        local_data.append({
                            'english': en_text,
                            'luganda': lg_text,
                            'source': source_name
                        })
                        source_count += 1
                
                print(f"✓ {source_name}: {source_count} samples")
            else:
                print(f"⚠ {source_name}: Could not find English/Luganda columns")
                print(f"  Available columns: {list(df.columns)}")
        
        except Exception as e:
            print(f"❌ {source_name}: {e}")
    else:
        print(f"⚠ {source_name}: File not found")

print(f"\n✓ Total local samples: {len(local_data)}")

# ============================================================================
# COMBINE & CLEAN
# ============================================================================
print("\n[STEP 4: COMBINING & CLEANING DATA]")
print("="*80)

all_data = kambale_data + local_data
print(f"Total before cleaning: {len(all_data)}")

# Remove duplicates
unique_pairs = {}
duplicates_removed = 0
for item in all_data:
    key = (item['english'].lower().strip(), item['luganda'].lower().strip())
    if key not in unique_pairs:
        unique_pairs[key] = item
    else:
        duplicates_removed += 1

cleaned_data = list(unique_pairs.values())
print(f"After removing duplicates: {len(cleaned_data)} (removed {duplicates_removed})")

# Remove very short sentences
before = len(cleaned_data)
cleaned_data = [
    x for x in cleaned_data 
    if len(x['english'].split()) >= 2 and len(x['luganda'].split()) >= 2
]
print(f"After removing short sentences: {len(cleaned_data)} (removed {before - len(cleaned_data)})")

# Remove very long sentences (>50 words)
before = len(cleaned_data)
cleaned_data = [
    x for x in cleaned_data 
    if len(x['english'].split()) <= 50 and len(x['luganda'].split()) <= 50
]
print(f"After removing long sentences: {len(cleaned_data)} (removed {before - len(cleaned_data)})")

# Source breakdown
source_counts = Counter([x['source'] for x in cleaned_data])
print(f"\nFinal source breakdown:")
for source, count in source_counts.most_common():
    percentage = (count / len(cleaned_data)) * 100
    print(f"  {source}: {count} ({percentage:.1f}%)")

# ============================================================================
# SPLIT DATA
# ============================================================================
print("\n[STEP 5: SPLITTING DATA]")
print("="*80)

random.seed(42)
random.shuffle(cleaned_data)

total = len(cleaned_data)
train_size = int(total * 0.8)
val_size = int(total * 0.1)

train_data = cleaned_data[:train_size]
val_data = cleaned_data[train_size:train_size + val_size]
test_data = cleaned_data[train_size + val_size:]

print(f"Total: {total}")
print(f"  Train: {len(train_data)} ({len(train_data)/total*100:.1f}%)")
print(f"  Val:   {len(val_data)} ({len(val_data)/total*100:.1f}%)")
print(f"  Test:  {len(test_data)} ({len(test_data)/total*100:.1f}%)")

# ============================================================================
# SAVE
# ============================================================================
print("\n[STEP 6: SAVING DATASETS]")
print("="*80)

os.makedirs('data/combined_kambale', exist_ok=True)

train_df = pd.DataFrame(train_data)
val_df = pd.DataFrame(val_data)
test_df = pd.DataFrame(test_data)

train_df.to_csv('data/combined_kambale/train.csv', index=False)
val_df.to_csv('data/combined_kambale/val.csv', index=False)
test_df.to_csv('data/combined_kambale/test.csv', index=False)

print(f"✓ train.csv: {len(train_df)} rows")
print(f"✓ val.csv: {len(val_df)} rows")
print(f"✓ test.csv: {len(test_df)} rows")

# ============================================================================
# STATISTICS
# ============================================================================
print("\n[STEP 7: DATASET STATISTICS]")
print("="*80)

stats = {
    "total_samples": len(cleaned_data),
    "kambale_samples": len(kambale_data),
    "local_samples": len(local_data),
    "duplicates_removed": duplicates_removed,
    "train_samples": len(train_df),
    "val_samples": len(val_df),
    "test_samples": len(test_df),
    "sources": dict(source_counts),
    "avg_english_tokens": float(train_df['english'].str.split().str.len().mean()),
    "avg_luganda_tokens": float(train_df['luganda'].str.split().str.len().mean()),
    "created_at": datetime.now().isoformat()
}

with open('data/combined_kambale/stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print(f"\nAverage tokens:")
print(f"  English: {stats['avg_english_tokens']:.1f}")
print(f"  Luganda: {stats['avg_luganda_tokens']:.1f}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("  ✅ DATASET COMBINATION COMPLETE!")
print("="*80)

print(f"""
📊 COMBINED DATASET:
   • Kambale dataset: {len(kambale_data):,} samples
   • Local datasets: {len(local_data):,} samples
   • Total: {len(cleaned_data):,} samples

📁 OUTPUT:
   ✓ data/combined_kambale/train.csv
   ✓ data/combined_kambale/val.csv
   ✓ data/combined_kambale/test.csv
   ✓ data/combined_kambale/stats.json

🎯 NEXT STEP:
   Run training with this combined dataset!
""")

print("="*80)
