#!/usr/bin/env python3
# ============================================================================
# COMBINE ALL DATASETS - KAMBALE + LOCAL DATASETS
# ============================================================================
# This script:
# 1. Loads the gated Kambale Luganda-English Parallel Corpus
# 2. Loads all local datasets
# 3. Cleans and deduplicates
# 4. Combines properly
# 5. Splits into train/val/test
# ============================================================================

import pandas as pd
import os
import json
from datetime import datetime
from collections import Counter

print("\n" + "="*80)
print("  📚 COMBINING ALL DATASETS - KAMBALE + LOCAL")
print("="*80)

# ============================================================================
# STEP 1: LOGIN TO HUGGING FACE (REQUIRED FOR GATED DATASET)
# ============================================================================
print("\n[STEP 1: HUGGING FACE LOGIN]")
print("="*80)

print("""
⚠️  IMPORTANT: The Kambale dataset is GATED (requires authentication)

TO GET YOUR TOKEN:
1. Go to: https://huggingface.co/settings/tokens
2. Create a new token (READ access is enough)
3. Copy the token
4. Paste it when prompted below

Note: You only need to do this ONCE per machine
""")

try:
    from huggingface_hub import login
    # Try to login - this will prompt if needed
    login()
    print("✓ Logged in to Hugging Face!")
except Exception as e:
    print(f"Note: Login not available in this environment: {e}")
    print("You may need to set HF_TOKEN environment variable")

# ============================================================================
# STEP 2: LOAD KAMBALE DATASET
# ============================================================================
print("\n[STEP 2: LOADING KAMBALE DATASET]")
print("="*80)

kambale_data = []
try:
    from datasets import load_dataset
    
    print("Loading Kambale Luganda-English Parallel Corpus...")
    print("(This may take a few minutes on first download...)")
    
    dataset = load_dataset("kambale/luganda-english-parallel-corpus")
    
    # Extract all splits
    for split_name in dataset.keys():
        print(f"\nProcessing split: {split_name}")
        split = dataset[split_name]
        
        for example in split:
            kambale_data.append({
                'english': example.get('english', '').strip(),
                'luganda': example.get('luganda', '').strip(),
                'source': 'kambale'
            })
    
    print(f"\n✓ Loaded {len(kambale_data)} samples from Kambale dataset")
    
except Exception as e:
    print(f"❌ Could not load Kambale dataset: {e}")
    print("\nTo fix this:")
    print("1. Create Hugging Face account: https://huggingface.co/join")
    print("2. Accept dataset terms: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus")
    print("3. Get token: https://huggingface.co/settings/tokens")
    print("4. Run: huggingface-cli login")
    print("5. Paste your token when prompted")
    kambale_data = []

# ============================================================================
# STEP 3: LOAD LOCAL DATASETS
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
            
            # Detect column names (could be 'english'/'luganda' or 'en'/'lg' etc)
            en_col = None
            lg_col = None
            
            for col in df.columns:
                col_lower = col.lower()
                if 'english' in col_lower or col_lower == 'en':
                    en_col = col
                if 'luganda' in col_lower or col_lower == 'lg':
                    lg_col = col
            
            if en_col and lg_col:
                for _, row in df.iterrows():
                    en_text = str(row[en_col]).strip()
                    lg_text = str(row[lg_col]).strip()
                    
                    if en_text and lg_text and len(en_text) > 3 and len(lg_text) > 3:
                        local_data.append({
                            'english': en_text,
                            'luganda': lg_text,
                            'source': source_name
                        })
                
                print(f"✓ {source_name}: {len([x for x in local_data if x['source'] == source_name])} samples")
            else:
                print(f"⚠ {source_name}: Could not find English/Luganda columns")
        
        except Exception as e:
            print(f"❌ {source_name}: {e}")
    else:
        print(f"⚠ {source_name}: File not found ({filepath})")

print(f"\n✓ Total local samples: {len(local_data)}")

# ============================================================================
# STEP 4: COMBINE DATASETS
# ============================================================================
print("\n[STEP 4: COMBINING DATASETS]")
print("="*80)

all_data = kambale_data + local_data
print(f"Total before cleaning: {len(all_data)}")

# ============================================================================
# STEP 5: CLEANING & DEDUPLICATION
# ============================================================================
print("\n[STEP 5: CLEANING & DEDUPLICATION]")
print("="*80)

# Remove duplicates
unique_pairs = {}
for item in all_data:
    key = (item['english'].lower(), item['luganda'].lower())
    if key not in unique_pairs:
        unique_pairs[key] = item

cleaned_data = list(unique_pairs.values())
print(f"After removing duplicates: {len(cleaned_data)} (removed {len(all_data) - len(cleaned_data)})")

# Remove very short sentences
cleaned_data = [
    x for x in cleaned_data 
    if len(x['english'].split()) >= 2 and len(x['luganda'].split()) >= 2
]
print(f"After removing short sentences: {len(cleaned_data)}")

# Remove if too long (>50 words)
cleaned_data = [
    x for x in cleaned_data 
    if len(x['english'].split()) <= 50 and len(x['luganda'].split()) <= 50
]
print(f"After removing very long sentences: {len(cleaned_data)}")

# Show source breakdown
source_counts = Counter([x['source'] for x in cleaned_data])
print(f"\nSource breakdown:")
for source, count in source_counts.most_common():
    percentage = (count / len(cleaned_data)) * 100
    print(f"  {source}: {count} ({percentage:.1f}%)")

# ============================================================================
# STEP 6: SPLIT INTO TRAIN/VAL/TEST
# ============================================================================
print("\n[STEP 6: SPLITTING DATA]")
print("="*80)

# Shuffle
import random
random.seed(42)
random.shuffle(cleaned_data)

# Calculate splits (80% train, 10% val, 10% test)
total = len(cleaned_data)
train_size = int(total * 0.8)
val_size = int(total * 0.1)

train_data = cleaned_data[:train_size]
val_data = cleaned_data[train_size:train_size + val_size]
test_data = cleaned_data[train_size + val_size:]

print(f"Total samples: {total}")
print(f"  Train: {len(train_data)} ({len(train_data)/total*100:.1f}%)")
print(f"  Val:   {len(val_data)} ({len(val_data)/total*100:.1f}%)")
print(f"  Test:  {len(test_data)} ({len(test_data)/total*100:.1f}%)")

# ============================================================================
# STEP 7: SAVE DATASETS
# ============================================================================
print("\n[STEP 7: SAVING DATASETS]")
print("="*80)

os.makedirs('data/processed_combined', exist_ok=True)

train_df = pd.DataFrame(train_data)
val_df = pd.DataFrame(val_data)
test_df = pd.DataFrame(test_data)

train_df.to_csv('data/processed_combined/train.csv', index=False)
val_df.to_csv('data/processed_combined/val.csv', index=False)
test_df.to_csv('data/processed_combined/test.csv', index=False)

print(f"✓ train.csv saved ({len(train_df)} rows)")
print(f"✓ val.csv saved ({len(val_df)} rows)")
print(f"✓ test.csv saved ({len(test_df)} rows)")

# ============================================================================
# STEP 8: STATISTICS
# ============================================================================
print("\n[DATASET STATISTICS]")
print("="*80)

stats = {
    "total_samples": len(cleaned_data),
    "train_samples": len(train_df),
    "val_samples": len(val_df),
    "test_samples": len(test_df),
    "sources": dict(source_counts),
    "avg_english_length": train_df['english'].str.split().str.len().mean(),
    "avg_luganda_length": train_df['luganda'].str.split().str.len().mean(),
    "created_at": datetime.now().isoformat()
}

with open('data/processed_combined/stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print(f"\nAverage sentence length:")
print(f"  English: {stats['avg_english_length']:.1f} words")
print(f"  Luganda: {stats['avg_luganda_length']:.1f} words")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("  ✅ DATASET COMBINATION COMPLETE!")
print("="*80)

print(f"""
📊 SUMMARY:
   ✓ Kambale dataset: {len(kambale_data)} samples
   ✓ Local datasets: {len(local_data)} samples
   ✓ After cleaning: {len(cleaned_data)} samples
   ✓ Duplicates removed: {len(all_data) - len(cleaned_data)}

📁 OUTPUT FILES:
   ✓ data/processed_combined/train.csv ({len(train_df)} rows)
   ✓ data/processed_combined/val.csv ({len(val_df)} rows)
   ✓ data/processed_combined/test.csv ({len(test_df)} rows)
   ✓ data/processed_combined/stats.json

🎯 READY FOR TRAINING!

Next step: Use these files in your training script
   python COLAB_TRAINING_KAMBALE.py
""")

print("="*80)
