#!/usr/bin/env python3
"""
Download Kambale Luganda-English Parallel Corpus
Saves dataset splits as CSV files locally
"""

import os
import sys
from pathlib import Path

print("\n" + "="*80)
print("DOWNLOADING KAMBALE LUGANDA-ENGLISH PARALLEL CORPUS")
print("="*80)

# Step 1: Set HF Token
print("\n[STEP 1: AUTHENTICATING WITH HUGGINGFACE]")
print("="*80)

hf_token = os.environ.get('HF_TOKEN')

if not hf_token:
    print("\n⚠️  HF_TOKEN not found in environment")
    hf_token = input("Enter your HuggingFace token: ").strip()
    
if not hf_token:
    print("\n✗ ERROR: No token provided. Exiting.")
    sys.exit(1)

os.environ['HF_TOKEN'] = hf_token
print(f"✓ Token set: {hf_token[:20]}...")

try:
    from huggingface_hub import login
    login(token=hf_token)
    print("✓ Authenticated with HuggingFace")
except Exception as e:
    print(f"⚠️  Authentication warning: {e}")

# Step 2: Load Dataset
print("\n[STEP 2: LOADING KAMBALE DATASET]")
print("="*80)

try:
    from datasets import load_dataset
    
    print("Loading dataset from: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus")
    print("(This may take 5-15 minutes on first download...)\n")
    
    dataset = load_dataset(
        "kambale/luganda-english-parallel-corpus",
        trust_remote_code=True
    )
    
    print(f"\n✓ Dataset loaded successfully!")
    print(f"\nDataset splits available:")
    for split, data in dataset.items():
        print(f"  - {split}: {len(data)} samples")
    
except Exception as e:
    print(f"\n✗ ERROR loading dataset: {e}")
    print("\nPossible causes:")
    print("  1. Token not accepted for gated dataset")
    print("  2. Dataset access not granted")
    print("  3. Internet connection issue")
    print("\nSolution:")
    print("  1. Visit: https://huggingface.co/datasets/kambale/luganda-english-parallel-corpus")
    print("  2. Click 'Accept repository'")
    print("  3. Try again with valid token")
    sys.exit(1)

# Step 3: Save as CSV Files
print("\n[STEP 3: SAVING DATASET AS CSV FILES]")
print("="*80)

output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

print(f"\nSaving to: {output_dir}/\n")

for split_name, split_data in dataset.items():
    try:
        # Get columns
        print(f"Processing {split_name} split ({len(split_data)} samples)...")
        
        # Convert to pandas DataFrame
        df = split_data.to_pandas()
        
        # Standardize column names
        if 'english' in df.columns and 'luganda' in df.columns:
            pass  # Already standard
        elif 'en' in df.columns and 'lg' in df.columns:
            df = df.rename(columns={'en': 'english', 'lg': 'luganda'})
        elif 'source' in df.columns and 'target' in df.columns:
            df = df.rename(columns={'source': 'english', 'target': 'luganda'})
        else:
            print(f"  ⚠️  Unexpected columns: {list(df.columns)}")
            print(f"  Using first two columns as english/luganda")
            cols = list(df.columns)
            df = df[[cols[0], cols[1]]]
            df.columns = ['english', 'luganda']
        
        # Save to CSV
        filename = output_dir / f"kambale_{split_name}.csv"
        df[['english', 'luganda']].to_csv(filename, index=False)
        
        print(f"  ✓ Saved: {filename}")
        print(f"    Size: {len(df)} rows, {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
        
    except Exception as e:
        print(f"  ✗ Error processing {split_name}: {e}")
        continue

# Step 4: Verify Downloads
print("\n[STEP 4: VERIFYING DOWNLOADED FILES]")
print("="*80)

csv_files = list(output_dir.glob("kambale_*.csv"))

if csv_files:
    print(f"\n✓ Successfully downloaded {len(csv_files)} files:\n")
    total_rows = 0
    for csv_file in sorted(csv_files):
        import pandas as pd
        df = pd.read_csv(csv_file)
        total_rows += len(df)
        print(f"  • {csv_file.name}: {len(df):,} rows")
    
    print(f"\n✓ Total training data: {total_rows:,} samples")
else:
    print("\n✗ No files found. Download may have failed.")
    sys.exit(1)

# Step 5: Update Preprocessing Script
print("\n[STEP 5: UPDATING PREPROCESSING CONFIGURATION]")
print("="*80)

print("\n✓ Next steps:")
print("  1. The Kambale dataset is now saved locally in data/raw/")
print("  2. Run preprocessing to combine all datasets:")
print("     python preprocess_combine_datasets.py")
print("  3. Train model with cultural balancing:")
print("     python train_colab_kambale_combined.py")

print("\n" + "="*80)
print("✓ KAMBALE DATASET DOWNLOADED SUCCESSFULLY")
print("="*80 + "\n")

print("📊 DATASET SUMMARY:")
print(f"   Location: {output_dir}/")
print(f"   Files: {len(csv_files)} CSV files")
print(f"   Total samples: {total_rows:,}")
print(f"   Format: english, luganda (standardized columns)")
print(f"   Status: Ready for training ✓")
