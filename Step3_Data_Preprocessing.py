# ============================================================================
# STEP 3: DATA PREPROCESSING FOR MACHINE TRANSLATION
# ============================================================================
# This script cleans, tokenizes, and prepares data for Seq2Seq model training
# ============================================================================

print("=" * 70)
print("🚀 STEP 3: DATA PREPROCESSING")
print("=" * 70)

import pandas as pd
import numpy as np
import re
import pickle
from datasets import Dataset

# ============================================================================
# PART 1: LOAD THE DATASET
# ============================================================================
print("\n📥 Loading dataset...\n")

# Load from combined dataset
df = pd.read_csv('data/luganda_english_dataset_combined.csv')
print(f"✅ Combined dataset loaded: {len(df)} samples")
print(f"\nDataset sources breakdown:")
if 'source' in df.columns:
    for source, count in df['source'].value_counts().items():
        print(f"  • {source}: {count:,}")

print(f"\nFirst 3 samples:")
print(df.head(3))

# ============================================================================
# PART 2: TEXT CLEANING FUNCTIONS
# ============================================================================
print("\n" + "=" * 70)
print("🧹 CLEANING TEXT")
print("=" * 70)

def clean_text(text):
    """
    Clean text by:
    1. Converting to lowercase
    2. Removing extra whitespace
    3. Removing special characters (but keep punctuation)
    4. Removing URLs
    5. Removing email addresses
    """
    
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text

print("\nApplying text cleaning...")

# Clean both languages
df['luganda_clean'] = df['luganda'].apply(clean_text)
df['english_clean'] = df['english'].apply(clean_text)

# Remove empty rows
df = df[(df['luganda_clean'].str.len() > 0) & (df['english_clean'].str.len() > 0)]

print(f"✅ Text cleaned!")
print(f"   - Remaining samples after cleaning: {len(df)}")

# ============================================================================
# PART 3: REMOVE DUPLICATES & SHORT SENTENCES
# ============================================================================
print("\n" + "=" * 70)
print("🔧 FILTERING DATA")
print("=" * 70)

print(f"\nBefore filtering: {len(df)} samples")

# Remove duplicate pairs
df_filtered = df.drop_duplicates(subset=['luganda_clean', 'english_clean'])
print(f"After removing duplicates: {len(df_filtered)} samples")

# Remove very short sentences (less than 3 characters)
df_filtered = df_filtered[
    (df_filtered['luganda_clean'].str.len() >= 3) & 
    (df_filtered['english_clean'].str.len() >= 3)
]
print(f"After removing short sentences: {len(df_filtered)} samples")

# Remove very long sentences (more than 500 characters) to avoid memory issues
df_filtered = df_filtered[
    (df_filtered['luganda_clean'].str.len() <= 500) & 
    (df_filtered['english_clean'].str.len() <= 500)
]
print(f"After removing long sentences: {len(df_filtered)} samples")

# ============================================================================
# PART 4: CHARACTER & WORD STATISTICS
# ============================================================================
print("\n" + "=" * 70)
print("📊 STATISTICS AFTER PREPROCESSING")
print("=" * 70)

print("\nLuganda:")
print(f"  - Avg characters per sentence: {df_filtered['luganda_clean'].str.len().mean():.1f}")
print(f"  - Avg words per sentence: {df_filtered['luganda_clean'].str.split().str.len().mean():.1f}")

print("\nEnglish:")
print(f"  - Avg characters per sentence: {df_filtered['english_clean'].str.len().mean():.1f}")
print(f"  - Avg words per sentence: {df_filtered['english_clean'].str.split().str.len().mean():.1f}")

# ============================================================================
# PART 5: CREATE TRAIN / VALIDATION / TEST SPLIT
# ============================================================================
print("\n" + "=" * 70)
print("✂️  CREATING TRAIN / VALIDATION / TEST SPLIT")
print("=" * 70)

from sklearn.model_selection import train_test_split

# 80% train, 10% validation, 10% test
train, temp = train_test_split(df_filtered, test_size=0.2, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)

print(f"\nTotal samples: {len(df_filtered)}")
print(f"  - Training set: {len(train)} ({len(train)/len(df_filtered)*100:.1f}%)")
print(f"  - Validation set: {len(val)} ({len(val)/len(df_filtered)*100:.1f}%)")
print(f"  - Test set: {len(test)} ({len(test)/len(df_filtered)*100:.1f}%)")

# ============================================================================
# PART 6: PREPARE FOR HUGGINGFACE DATASETS
# ============================================================================
print("\n" + "=" * 70)
print("📦 CREATING HUGGINGFACE DATASETS")
print("=" * 70)

# Create dataset with proper format for fine-tuning
def create_translation_dataset(df_split):
    """Convert dataframe to HuggingFace Dataset format"""
    dataset_dict = {
        'translation': []
    }
    
    for _, row in df_split.iterrows():
        dataset_dict['translation'].append({
            'lug': row['luganda_clean'],
            'eng': row['english_clean']
        })
    
    return Dataset.from_dict(dataset_dict)

train_dataset = create_translation_dataset(train)
val_dataset = create_translation_dataset(val)
test_dataset = create_translation_dataset(test)

print(f"✅ Datasets created:")
print(f"   - Train dataset: {len(train_dataset)} samples")
print(f"   - Validation dataset: {len(val_dataset)} samples")
print(f"   - Test dataset: {len(test_dataset)} samples")

# ============================================================================
# PART 7: SAVE PREPROCESSED DATA
# ============================================================================
print("\n" + "=" * 70)
print("💾 SAVING PREPROCESSED DATA")
print("=" * 70)

# Save datasets
with open('data/train_dataset.pkl', 'wb') as f:
    pickle.dump(train_dataset, f)
print(f"✅ Saved: data/train_dataset.pkl")

with open('data/val_dataset.pkl', 'wb') as f:
    pickle.dump(val_dataset, f)
print(f"✅ Saved: data/val_dataset.pkl")

with open('data/test_dataset.pkl', 'wb') as f:
    pickle.dump(test_dataset, f)
print(f"✅ Saved: data/test_dataset.pkl")

# Also save as CSV for reference
train.to_csv('data/train_data.csv', index=False)
val.to_csv('data/val_data.csv', index=False)
test.to_csv('data/test_data.csv', index=False)
print(f"✅ Saved: data/train_data.csv, val_data.csv, test_data.csv")

# ============================================================================
# PART 8: SAMPLE FROM PREPROCESSED DATA
# ============================================================================
print("\n" + "=" * 70)
print("👀 SAMPLE FROM PREPROCESSED DATA")
print("=" * 70)

print("\nRandom samples from training data:\n")
for i in range(3):
    sample = train_dataset[i]
    print(f"{i+1}. Translation:")
    print(f"   🇺🇬 Luganda: {sample['translation']['lug']}")
    print(f"   🇬🇧 English: {sample['translation']['eng']}")
    print()

# ============================================================================
# PART 9: SUMMARY
# ============================================================================
print("=" * 70)
print("✅ STEP 3 COMPLETE!")
print("=" * 70)
print(f"\n📊 Summary:")
print(f"   - Total samples after preprocessing: {len(df_filtered):,}")
print(f"   - Train samples: {len(train):,}")
print(f"   - Validation samples: {len(val):,}")
print(f"   - Test samples: {len(test):,}")
print(f"\n💾 Files saved in data/ directory")
print(f"\n🎯 Next: STEP 4 - Model Selection & MarianMT Setup")
print(f"   Run: Step4_MarianMT_Setup.py\n")
