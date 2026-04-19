# ============================================================================
# CULTURAL DATA INTEGRATION
# ============================================================================
# This script integrates cultural vocabulary and training data
# into your existing Luganda-English translation pipeline
# ============================================================================

print("=" * 70)
print("🎭 CULTURAL DATA INTEGRATION")
print("=" * 70)

import pandas as pd
import json
import os

# ============================================================================
# PART 1: LOAD CULTURAL RESOURCES
# ============================================================================
print("\n📚 Loading cultural resources...\n")

# Load cultural dictionary
with open('data/cultural_dictionary.json', 'r', encoding='utf-8') as f:
    cultural_dict = json.load(f)

print("✅ Cultural dictionary loaded")
print(f"   - Clans: {len(cultural_dict['clans'])}")
print(f"   - Cultural terms: {len(cultural_dict['cultural_terms'])}")
print(f"   - Kingdom references: {len(cultural_dict['kingdom'])}")

# Load cultural training data
cultural_df = pd.read_csv('data/cultural_training_data.csv', encoding='utf-8')
print(f"\n✅ Cultural training data loaded: {len(cultural_df)} sentences")
print(f"   - Contexts: {cultural_df['cultural_context'].unique().tolist()}")

# ============================================================================
# PART 2: COMBINE WITH EXISTING DATASET
# ============================================================================
print("\n" + "=" * 70)
print("🔗 COMBINING DATASETS")
print("=" * 70)

# Load original dataset
original_df = pd.read_csv('data/luganda_english_dataset_combined.csv', encoding='utf-8')
print(f"\n📥 Original dataset: {len(original_df)} samples")

# Prepare cultural data for merging
cultural_train_df = cultural_df[['english', 'luganda', 'cultural_context']].copy()
cultural_train_df['source'] = 'Cultural_Dataset'

# Select only needed columns to match original format
cultural_train_df = cultural_train_df[['luganda', 'english', 'source']]

# Combine datasets (80% original, 20% cultural as recommended)
print("\n🎯 Creating mixed dataset:")
print("   - Original samples: 80% (general translation ability)")
print("   - Cultural samples: 20% (cultural authenticity)")

# Take a sample from cultural data to maintain 80-20 ratio
cultural_sample_size = int(len(original_df) * 0.25)  # 20% of original size
cultural_sample = cultural_train_df.sample(n=min(cultural_sample_size, len(cultural_train_df)), random_state=42)

# Combine
combined_df = pd.concat([original_df, cultural_sample], ignore_index=True)

print(f"\n✅ Combined dataset created:")
print(f"   - Total samples: {len(combined_df)}")
print(f"   - Original: {len(original_df)} ({len(original_df)/len(combined_df)*100:.1f}%)")
print(f"   - Cultural: {len(cultural_sample)} ({len(cultural_sample)/len(combined_df)*100:.1f}%)")

# Save combined dataset
combined_df.to_csv('data/luganda_english_dataset_with_culture.csv', index=False, encoding='utf-8')
print(f"\n   📁 Saved: data/luganda_english_dataset_with_culture.csv")

# Verify
print(f"\n📊 Sample from combined dataset:")
print(combined_df.sample(3))

# ============================================================================
# PART 3: CREATE CULTURAL TEST SET
# ============================================================================
print("\n" + "=" * 70)
print("🧪 CREATING CULTURAL TEST SET")
print("=" * 70)

cultural_test_df = cultural_df[['english', 'luganda', 'cultural_context']].copy()

# Save for separate evaluation
cultural_test_df.to_csv('data/cultural_test_set.csv', index=False, encoding='utf-8')
print(f"\n✅ Cultural test set created: {len(cultural_test_df)} samples")
print(f"   📁 Saved: data/cultural_test_set.csv")

print(f"\n📊 Sample from cultural test set:")
print(cultural_test_df.sample(3))

# ============================================================================
# PART 4: SAVE CULTURAL CONTEXT MAPPING
# ============================================================================
print("\n" + "=" * 70)
print("📋 CREATING CONTEXT TAGS")
print("=" * 70)

# Create a mapping of sentences to contexts for analysis
context_mapping = cultural_test_df[['english', 'cultural_context']].drop_duplicates().groupby('cultural_context')['english'].count()
print("\n✅ Cultural context distribution:")
for context, count in context_mapping.items():
    print(f"   - {context}: {count} examples")

# ============================================================================
# PART 5: STATISTICS
# ============================================================================
print("\n" + "=" * 70)
print("📈 INTEGRATION SUMMARY")
print("=" * 70)

print(f"\n✅ Datasets prepared for training:")
print(f"   1. Combined dataset: data/luganda_english_dataset_with_culture.csv")
print(f"   2. Cultural test set: data/cultural_test_set.csv")
print(f"   3. Cultural dictionary: data/cultural_dictionary.json")

print(f"\n💡 Next steps:")
print(f"   1. Use 'luganda_english_dataset_with_culture.csv' in Step3 preprocessing")
print(f"   2. Fine-tune model with 80-20 ratio on this mixed data")
print(f"   3. Evaluate separately on 'cultural_test_set.csv'")
print(f"   4. Apply post-processing rules for cultural terms")

print("\n" + "=" * 70)
print("✨ Integration complete!")
print("=" * 70 + "\n")
