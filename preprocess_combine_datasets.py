#!/usr/bin/env python3

import os
import json
import pandas as pd
import random
from datetime import datetime
from collections import Counter

print("\n" + "="*80)
print("COMBINING KAMBALE + LOCAL DATASETS WITH CULTURAL BALANCING")
print("="*80)

print("\n[STEP 0: CULTURAL BALANCING CONFIGURATION]")
print("="*80)

DATASET_WEIGHTS = {
    "cultural_training": 3.0,
    "makerere_nlp": 1.5,
    "jw300_parallel": 1.0,
    "sunbird_salt": 1.0,
    "kambale": 2.0
}

print("Dataset weighting for cultural emphasis:")
for source, weight in DATASET_WEIGHTS.items():
    print(f"  {source}: {weight}x")

CULTURAL_PHRASES = {
    "how are you": "oli otya",
    "i am fine": "ndi bulungi",
    "thank you": "webale nnyo",
    "welcome": "tukusanyuse",
    "sit down": "tuula wansi",
    "come here": "jangu wano",
    "good morning": "ku makya",
    "good evening": "ku wakati",
    "my name is": "erinnya lyange",
    "what is your name": "erinnya lyo ggwe ani",
    "i love luganda": "njagala nnyo olulimi oluggya",
    "respect elders": "okwata abalala nti abakulu",
    "greet with respect": "kwagala n'okuddamu",
    "our culture": "ensikirize yaffe",
    "traditional values": "ebigenderezamu by'ennono"
}

print(f"\nCultural phrases injected: {len(CULTURAL_PHRASES)}")

print("\n[STEP 1: AUTHENTICATING WITH HUGGING FACE]")
print("="*80)

try:
    from huggingface_hub import login
    
    hf_token = os.environ.get('HF_TOKEN')
    if not hf_token:
        hf_token = input("Enter your HuggingFace token (from https://huggingface.co/settings/tokens): ").strip()
    
    if hf_token:
        os.environ['HF_TOKEN'] = hf_token
        login(token=hf_token)
        print(f"Successfully authenticated with Hugging Face")
        print(f"Token starts with: {hf_token[:20]}...")
    else:
        print("WARNING: No HF_TOKEN provided. Kambale dataset requires authentication.")
except Exception as e:
    print(f"Authentication note: {e}")

print("\n[STEP 2: LOADING KAMBALE DATASET]")
print("="*80)

kambale_data = []

kambale_local_path = "data/raw/kambale_train.csv"

if os.path.exists(kambale_local_path):
    print(f"\nLoading from local file: {kambale_local_path}")
    try:
        kambale_df = pd.read_csv(kambale_local_path)
        print(f"  Columns: {list(kambale_df.columns)}")
        print(f"  Rows: {len(kambale_df)}")
        
        for _, row in kambale_df.iterrows():
            en_text = str(row.get('english', '')).strip()
            lg_text = str(row.get('luganda', '')).strip()
            
            if en_text and lg_text and len(en_text) > 3 and len(lg_text) > 3:
                kambale_data.append({
                    'english': en_text,
                    'luganda': lg_text,
                    'source': 'kambale'
                })
        
        print(f"✓ Loaded {len(kambale_data)} valid samples from Kambale (local)")
    
    except Exception as e:
        print(f"Error loading local Kambale file: {e}")
        print("Falling back to HuggingFace download...")
        kambale_data = []

if not kambale_data:
    print(f"\nKambale local file not found. Trying HuggingFace download...")
    try:
        from datasets import load_dataset
        
        print("Loading: kambale/luganda-english-parallel-corpus from HuggingFace")
        dataset = load_dataset(
            "kambale/luganda-english-parallel-corpus"
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
                    if idx < 5:
                        print(f"  Note: Skipped sample {idx}: {e}")
                    continue
        
        print(f"\n✓ Loaded {len(kambale_data)} samples from Kambale (HuggingFace)")
    
    except Exception as e:
        print(f"Error loading Kambale from HuggingFace: {e}")
        print("\nTroubleshooting:")
        print("1. To download locally, run: python download_kambale_dataset.py")
        print("2. Or accept dataset terms at:")
        print("   https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus")
    print("3. You have internet connection")
    kambale_data = []

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
                
                print(f"{source_name}: {source_count} samples")
            else:
                print(f"{source_name}: Could not find English/Luganda columns")
                print(f"  Available columns: {list(df.columns)}")
        
        except Exception as e:
            print(f"{source_name}: {e}")
    else:
        print(f"{source_name}: File not found")

print(f"\nTotal local samples: {len(local_data)}")

print("\n[STEP 4: COMBINING & CLEANING DATA WITH CULTURAL BALANCING]")
print("="*80)

all_data = kambale_data + local_data

print(f"\nBefore balancing:")
print(f"  Kambale: {len(kambale_data)}")
print(f"  Local: {len(local_data)}")
print(f"  Total: {len(all_data)}")

print(f"\nApplying dataset weighting for cultural emphasis...")
balanced_data = []

for source, items in [
    ("kambale", kambale_data),
    ("cultural_training", [x for x in local_data if x['source'] == 'cultural']),
    ("jw300_parallel", [x for x in local_data if x['source'] == 'jw300']),
    ("makerere_nlp", [x for x in local_data if x['source'] == 'makerere']),
    ("sunbird_salt", [x for x in local_data if x['source'] == 'sunbird']),
]:
    if not items:
        continue
    
    weight = DATASET_WEIGHTS.get(source, 1.0)
    repeat_count = int(weight)
    
    print(f"  {source}: {len(items)} samples × {weight}x = {len(items) * repeat_count} weighted samples")
    
    for _ in range(repeat_count):
        balanced_data.extend(items)

print(f"\nAfter balancing: {len(balanced_data)} total samples")

print(f"\nInjecting cultural phrases for semantic grounding...")
cultural_pairs = []
for en_phrase, lg_phrase in CULTURAL_PHRASES.items():
    cultural_pairs.append({
        'english': en_phrase,
        'luganda': lg_phrase,
        'source': 'cultural_injection'
    })

balanced_data.extend(cultural_pairs)
print(f"  Added {len(cultural_pairs)} cultural phrases")
print(f"  Total after injection: {len(balanced_data)}")

all_data = balanced_data
print(f"\nTotal before deduplication: {len(all_data)}")

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

before = len(cleaned_data)
cleaned_data = [
    x for x in cleaned_data 
    if len(x['english'].split()) >= 2 and len(x['luganda'].split()) >= 2
]
print(f"After removing short sentences: {len(cleaned_data)} (removed {before - len(cleaned_data)})")

before = len(cleaned_data)
cleaned_data = [
    x for x in cleaned_data 
    if len(x['english'].split()) <= 50 and len(x['luganda'].split()) <= 50
]
print(f"After removing long sentences: {len(cleaned_data)} (removed {before - len(cleaned_data)})")

source_counts = Counter([x['source'] for x in cleaned_data])
print(f"\nFinal source breakdown:")
for source, count in source_counts.most_common():
    percentage = (count / len(cleaned_data)) * 100
    print(f"  {source}: {count} ({percentage:.1f}%)")

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

print("\n[STEP 6: SAVING DATASETS]")
print("="*80)

os.makedirs('data/combined_kambale', exist_ok=True)

train_df = pd.DataFrame(train_data)
val_df = pd.DataFrame(val_data)
test_df = pd.DataFrame(test_data)

train_df.to_csv('data/combined_kambale/train.csv', index=False)
val_df.to_csv('data/combined_kambale/val.csv', index=False)
test_df.to_csv('data/combined_kambale/test.csv', index=False)

print(f"train.csv: {len(train_df)} rows")
print(f"val.csv: {len(val_df)} rows")
print(f"test.csv: {len(test_df)} rows")

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

print("\n" + "="*80)
print("DATASET COMBINATION COMPLETE!")
print("="*80)

print(f"""
Combined dataset summary:
   - Kambale dataset: {len(kambale_data):,} samples
   - Local datasets: {len(local_data):,} samples
   - Total: {len(cleaned_data):,} samples

Output files:
   - data/combined_kambale/train.csv
   - data/combined_kambale/val.csv
   - data/combined_kambale/test.csv
   - data/combined_kambale/stats.json

Next step: Run training with this combined dataset!
""")

print("="*80)
