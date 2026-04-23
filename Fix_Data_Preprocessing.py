"""
Rebuild the pickle files with the FULL dataset properly split
"""

import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from datasets import Dataset

print("=" * 70)
print("FIXING DATA PREPROCESSING")
print("=" * 70)

# Load the full dataset
print("\nLoading luganda_training_data.csv (15,020 samples)...")
df = pd.read_csv('luganda_training_data.csv')
print(f"Loaded: {len(df)} rows")

# Apply same filters as Step3
print("\nApplying data filters...")

# Remove rows with None or NaN
df_filtered = df.dropna()
print(f"After removing NaN: {len(df_filtered)} rows")

# Keep only sentences between 5-500 chars
df_filtered = df_filtered[
    (df_filtered['luganda'].str.len() >= 5) & 
    (df_filtered['luganda'].str.len() <= 500)
]
print(f"After length filter (5-500 chars): {len(df_filtered)} rows")

# Remove exact duplicates
df_filtered = df_filtered.drop_duplicates(subset=['english', 'luganda'])
print(f"After removing duplicates: {len(df_filtered)} rows")

# PROPER SPLIT: 80% train, 10% val, 10% test
print("\nSplitting data (80/10/10)...")
train, temp = train_test_split(df_filtered, test_size=0.2, random_state=42)
val, test = train_test_split(temp, test_size=0.5, random_state=42)

print(f"  - Train: {len(train)} samples ({len(train)/len(df_filtered)*100:.1f}%)")
print(f"  - Val:   {len(val)} samples ({len(val)/len(df_filtered)*100:.1f}%)")
print(f"  - Test:  {len(test)} samples ({len(test)/len(df_filtered)*100:.1f}%)")

# Create HuggingFace Dataset format with nested 'translation' key
def create_translation_dataset(df_split):
    """Convert dataframe to HuggingFace Dataset with proper format"""
    dataset_dict = {
        'translation': []
    }
    
    for _, row in df_split.iterrows():
        dataset_dict['translation'].append({
            'lug': row['luganda'],
            'eng': row['english']
        })
    
    return Dataset.from_dict(dataset_dict)

print("\nCreating HuggingFace datasets...")
train_dataset = create_translation_dataset(train)
val_dataset = create_translation_dataset(val)
test_dataset = create_translation_dataset(test)

print(f"  - Train dataset: {len(train_dataset)} samples")
print(f"  - Val dataset: {len(val_dataset)} samples")
print(f"  - Test dataset: {len(test_dataset)} samples")

# Save CLEAN pickle files
print("\nSaving pickle files...")
with open('data/train_dataset.pkl', 'wb') as f:
    pickle.dump(train_dataset, f)
print("[OK] data/train_dataset.pkl")

with open('data/val_dataset.pkl', 'wb') as f:
    pickle.dump(val_dataset, f)
print("[OK] data/val_dataset.pkl")

with open('data/test_dataset.pkl', 'wb') as f:
    pickle.dump(test_dataset, f)
print("[OK] data/test_dataset.pkl")

# Verify
print("\nVerifying pickle files...")
with open('data/train_dataset.pkl', 'rb') as f:
    check_train = pickle.load(f)
print(f"  - train_dataset.pkl verified: {len(check_train)} samples")

print("\n" + "=" * 70)
print("DATA PREPROCESSING FIXED!")
print("=" * 70)
print(f"\nNOW READY TO TRAIN with {len(train_dataset)} training samples!")
