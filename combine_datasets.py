#!/usr/bin/env python
# ============================================================================
# COMBINE MULTIPLE LUGANDA-ENGLISH DATASETS
# ============================================================================
# Combines Makerere Zenodo + Hugging Face datasets for better training
# ============================================================================

import pandas as pd
import os

print("=" * 80)
print("🔄 COMBINING LUGANDA-ENGLISH DATASETS")
print("=" * 80)

# ============================================================================
# STEP 1: ATTEMPT TO LOAD DATASET FROM HuggingFace
# ============================================================================

print("\n📥 Loading HuggingFace dataset...")

try:
    from datasets import load_dataset
    
    # Try to load the Luganda dataset from HuggingFace
    datasets_to_try = [
        "allandclive/Luganda_Sci-Math-Bio_Translations",
        "christopherthompson/luganda_english_parallel_corpus",
        "google/flores",
    ]
    
    df_hf = None
    
    for dataset_name in datasets_to_try:
        try:
            print(f"  Trying: {dataset_name}...")
            hf_data = load_dataset(dataset_name)
            
            # Try to get training split
            if 'train' in hf_data:
                df_hf = pd.DataFrame(hf_data['train'])
            else:
                # Get first available split
                first_split = list(hf_data.keys())[0]
                df_hf = pd.DataFrame(hf_data[first_split])
            
            print(f"  ✅ Successfully loaded {dataset_name}")
            print(f"  Columns: {df_hf.columns.tolist()}")
            break
        except Exception as e:
            print(f"  ❌ Could not load {dataset_name}: {str(e)[:50]}")
            continue
    
    if df_hf is not None and len(df_hf) > 0:
        print(f"\n✅ HuggingFace dataset loaded: {len(df_hf)} sentences")
        print(f"   Columns: {df_hf.columns.tolist()}")
    else:
        print("\n⚠️  Could not load HuggingFace datasets - continuing with available data")
        df_hf = None

except ImportError:
    print("⚠️  'datasets' library not installed. Install with: pip install datasets")
    df_hf = None

# ============================================================================
# STEP 2: CHECK FOR LOCAL DATASET FILES
# ============================================================================

print("\n📂 Checking for local dataset files...")

local_files = []
for filename in os.listdir('.'):
    if 'luganda' in filename.lower() or 'dataset' in filename.lower():
        if filename.endswith('.csv'):
            local_files.append(filename)
            print(f"  ✅ Found: {filename}")

# ============================================================================
# STEP 3: LOAD EXISTING PROJECT DATASETS
# ============================================================================

print("\n📊 Loading existing project datasets...")

existing_datasets = []

# Check for existing project datasets
project_data_files = [
    'data/luganda_english_dataset_combined.csv',
    'data/luganda_english_dataset_cleaned.csv',
    'data/luganda_english_dataset_with_culture.csv',
    'data/luganda_english_dataset_quality_filtered.csv',
    'data/combined_data_clean.csv',
]

for file_path in project_data_files:
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            print(f"✅ Loaded {file_path}: {len(df)} rows")
            print(f"   Columns: {df.columns.tolist()}")
            existing_datasets.append((file_path, df))
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")

# ============================================================================
# STEP 4: PREPARE DATASETS
# ============================================================================

print("\n🔧 Preparing datasets for combination...")

all_dfs = []

# Process HuggingFace dataset
if df_hf is not None and len(df_hf) > 0:
    try:
        cols = df_hf.columns.tolist()
        
        # Find English and Luganda columns
        english_col = None
        luganda_col = None
        
        for col in cols:
            if any(x in col.lower() for x in ['english', 'eng', 'en']):
                english_col = col
            if any(x in col.lower() for x in ['luganda', 'lug', 'lg']):
                luganda_col = col
        
        if english_col and luganda_col:
            df_hf_clean = df_hf[[english_col, luganda_col]].copy()
            df_hf_clean.columns = ['english', 'luganda']
            all_dfs.append(('HuggingFace Dataset', df_hf_clean))
            print(f"✅ HuggingFace prepared: {len(df_hf_clean)} rows")
    except Exception as e:
        print(f"❌ Error preparing HuggingFace data: {e}")

# Process existing project datasets
for source_name, df in existing_datasets:
    try:
        cols = df.columns.tolist()
        
        # Find English and Luganda columns
        english_col = None
        luganda_col = None
        
        for col in cols:
            if any(x in col.lower() for x in ['english', 'eng', 'en']):
                english_col = col
            if any(x in col.lower() for x in ['luganda', 'lug', 'lg']):
                luganda_col = col
        
        if english_col and luganda_col:
            df_clean = df[[english_col, luganda_col]].copy()
            df_clean.columns = ['english', 'luganda']
            all_dfs.append((source_name, df_clean))
            print(f"✅ {source_name} prepared: {len(df_clean)} rows")
        else:
            print(f"⚠️  Could not find English/Luganda columns in {source_name}")
    except Exception as e:
        print(f"❌ Error preparing {source_name}: {e}")

# ============================================================================
# STEP 5: COMBINE ALL DATASETS
# ============================================================================

if len(all_dfs) == 0:
    print("\n❌ ERROR: No datasets found to combine!")
    print("\nPlease:")
    print("1. Download from: zenodo.org/records/4764039")
    print("2. Save as: dataset1.csv")
    print("3. Run this script again")
    exit(1)

print(f"\n📚 Combining {len(all_dfs)} dataset(s)...")

combined = pd.concat([df for _, df in all_dfs], ignore_index=True)

print(f"Raw combined: {len(combined)} rows")

# ============================================================================
# STEP 6: CLEAN DATA
# ============================================================================

print("\n🧹 Cleaning combined dataset...")

# Remove duplicates
before_dedup = len(combined)
combined = combined.drop_duplicates(subset=['english', 'luganda'])
after_dedup = len(combined)
print(f"   Removed duplicates: {before_dedup - after_dedup} rows")

# Remove NaN
before_nan = len(combined)
combined = combined.dropna()
after_nan = len(combined)
print(f"   Removed NaN values: {before_nan - after_nan} rows")

# Strip whitespace
combined['english'] = combined['english'].str.strip()
combined['luganda'] = combined['luganda'].str.strip()

# Remove rows where english == luganda (broken translations)
before_same = len(combined)
combined = combined[combined['english'] != combined['luganda']]
after_same = len(combined)
print(f"   Removed identical pairs: {before_same - after_same} rows")

# Remove rows where either column is empty
before_empty = len(combined)
combined = combined[(combined['english'].str.len() > 0) & (combined['luganda'].str.len() > 0)]
after_empty = len(combined)
print(f"   Removed empty entries: {before_empty - after_empty} rows")

# ============================================================================
# STEP 7: SAVE COMBINED DATASET
# ============================================================================

print(f"\n✅ FINAL COMBINED DATASET: {len(combined)} sentences")

combined.to_csv('data/combined_datasets_merged.csv', index=False)
print("✅ Saved to: data/combined_datasets_merged.csv")

# Also save to training location
combined.to_csv('combined_datasets_merged.csv', index=False)
print("✅ Saved to: combined_datasets_merged.csv")

# ============================================================================
# STEP 8: SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)

print(f"\n📈 Dataset Sources Combined:")
for source_name, df in all_dfs:
    print(f"   • {source_name}: {len(df)} sentences")

print(f"\n📝 Final Statistics:")
print(f"   • Total sentences: {len(combined)}")
print(f"   • Unique English phrases: {combined['english'].nunique()}")
print(f"   • Unique Luganda phrases: {combined['luganda'].nunique()}")

print(f"\n📄 Sample Rows:")
print(combined.head(10).to_string(index=False))

print(f"\n✅ Ready to use for training!")
print(f"\nNext step: Update your training script to use:")
print(f"   df = pd.read_csv('combined_datasets_merged.csv')")

print("\n" + "=" * 80)
