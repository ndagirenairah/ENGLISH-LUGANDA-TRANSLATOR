# ============================================================================
# STEP 3: DATA PREPROCESSING WITH QUALITY FILTERING
# ============================================================================
# 1. Loads Luganda-English dataset
# 2. QUALITY FILTER: Removes broken/noisy Luganda
# 3. Integrates cultural data (80-20 ratio)
# 4. Splits into train/val/test
# 5. Saves cleaned datasets
# ============================================================================

import pandas as pd
import os
from utils_data_quality_checker import LugandaDataCleaner

print("\n" + "=" * 80)
print("STEP 3: DATA PREPROCESSING WITH QUALITY FILTERING")
print("=" * 80)

# ============================================================================
# STEP 1: LOAD ORIGINAL DATASET
# ============================================================================

print("\n📂 STEP 1: Loading dataset...")

try:
    df_original = pd.read_csv("data/luganda_english_dataset_combined.csv")
    print(f"   ✅ Loaded: {len(df_original)} sentences")
except FileNotFoundError:
    print("   ❌ Error: data/luganda_english_dataset_combined.csv not found")
    print("   Using Step0 integration script first...")
    exit(1)

# ============================================================================
# STEP 2: QUALITY FILTERING
# ============================================================================

print("\n🔍 STEP 2: Quality filtering Luganda sentences...")

cleaner = LugandaDataCleaner()

# Get stats before
print(f"\n   📊 BEFORE filtering:")
print(f"      - Total sentences: {len(df_original)}")
avg_len_before = df_original["luganda"].str.split().str.len().mean()
print(f"      - Avg Luganda length: {avg_len_before:.1f} words")

# Apply quality filter
mask_clean = df_original["luganda"].apply(lambda x: cleaner.is_clean_luganda(x))
df_filtered = df_original[mask_clean].copy()

print(f"\n   ✅ AFTER filtering:")
print(f"      - Clean sentences: {len(df_filtered)}")
print(f"      - Removed: {len(df_original) - len(df_filtered)} noisy sentences")
print(f"      - Quality ratio: {len(df_filtered)/len(df_original)*100:.1f}%")

avg_len_after = df_filtered["luganda"].str.split().str.len().mean()
print(f"      - Avg Luganda length: {avg_len_after:.1f} words")

# Remove duplicates
df_filtered = df_filtered.drop_duplicates(subset=["luganda"])
print(f"\n   ✅ Duplicates removed: {len(df_filtered)} unique sentences")

# ============================================================================
# STEP 3: INTEGRATE CULTURAL DATA (80-20 ratio)
# ============================================================================

print("\n🏛️  STEP 3: Integrating cultural data...")

try:
    df_cultural = pd.read_csv("data/cultural_training_data.csv")
    print(f"   ✅ Loaded cultural data: {len(df_cultural)} sentences")
    
    # Sample cultural data (20% of final dataset)
    sample_size = max(1, int(len(df_filtered) * 0.2 / 0.8))
    df_cultural_sample = df_cultural.sample(n=min(sample_size, len(df_cultural)), random_state=42)
    
    print(f"   ✅ Sampled {len(df_cultural_sample)} cultural sentences (20% ratio)")
    
    # Combine datasets
    df_combined = pd.concat([df_filtered, df_cultural_sample], ignore_index=True)
    df_combined = df_combined.drop_duplicates(subset=["luganda"])
    
    print(f"   ✅ Combined dataset: {len(df_combined)} sentences")
    print(f"      - General: {len(df_filtered)} ({len(df_filtered)/len(df_combined)*100:.1f}%)")
    print(f"      - Cultural: {len(df_cultural_sample)} ({len(df_cultural_sample)/len(df_combined)*100:.1f}%)")

except FileNotFoundError:
    print("   ⚠️  Cultural data not found - using general data only")
    df_combined = df_filtered.copy()

# ============================================================================
# STEP 4: SPLIT INTO TRAIN/VAL/TEST
# ============================================================================

print("\n📊 STEP 4: Splitting dataset...")

# Shuffle
df_combined = df_combined.sample(frac=1.0, random_state=42).reset_index(drop=True)

# Calculate split sizes
total = len(df_combined)
train_size = int(total * 0.7)
val_size = int(total * 0.15)

print(f"   Total samples: {total}")
print(f"   - Train: {train_size} (70%)")
print(f"   - Val: {val_size} (15%)")
print(f"   - Test: {total - train_size - val_size} (15%)")

# Split
df_train = df_combined[:train_size]
df_val = df_combined[train_size:train_size + val_size]
df_test = df_combined[train_size + val_size:]

# Verify no overlap
assert len(set(df_train["luganda"]) & set(df_val["luganda"])) == 0, "Train/Val overlap!"
assert len(set(df_train["luganda"]) & set(df_test["luganda"])) == 0, "Train/Test overlap!"
assert len(set(df_val["luganda"]) & set(df_test["luganda"])) == 0, "Val/Test overlap!"

print("   ✅ No data leakage detected")

# ============================================================================
# STEP 5: SAVE PREPROCESSED DATA
# ============================================================================

print("\n💾 STEP 5: Saving preprocessed data...")

os.makedirs("data", exist_ok=True)

# Save splits
df_train.to_csv("data/train_data_clean.csv", index=False)
df_val.to_csv("data/val_data_clean.csv", index=False)
df_test.to_csv("data/test_data_clean.csv", index=False)

print(f"   ✅ data/train_data_clean.csv ({len(df_train)} samples)")
print(f"   ✅ data/val_data_clean.csv ({len(df_val)} samples)")
print(f"   ✅ data/test_data_clean.csv ({len(df_test)} samples)")

# Save combined for reference
df_combined.to_csv("data/combined_data_clean.csv", index=False)
print(f"   ✅ data/combined_data_clean.csv ({len(df_combined)} samples)")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("✨ PREPROCESSING COMPLETE")
print("=" * 80)

print("\n📈 SUMMARY:")
print(f"   Original → Filtered → Combined → Split")
print(f"   {len(df_original)} → {len(df_filtered)} → {len(df_combined)} → (70/15/15)")
print(f"\n   Quality improvement: {len(df_filtered)/len(df_original)*100:.1f}% clean data")

print("\n🎯 NEXT STEP:")
print("   python Step4_MarianMT_Setup.py")

print("\n" + "=" * 80 + "\n")
