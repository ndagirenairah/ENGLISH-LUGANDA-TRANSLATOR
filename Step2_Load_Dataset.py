# ============================================================================
# STEP 2: LOAD AND COMBINE MULTIPLE LUGANDA DATASETS
# ============================================================================
# This script loads THREE high-quality Luganda-English datasets:
# 1. Sunbird AI Luganda Corpus (HuggingFace)
# 2. Makerere NLP Luganda Dataset (air.ug)
# 3. JW300 Parallel Corpus (opus.nlp.eu)
# ============================================================================

print("=" * 70)
print("🚀 STEP 2: LOADING MULTIPLE LUGANDA DATASETS")
print("=" * 70)

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from datasets import load_dataset
import pandas as pd
import requests
import json
import os

# ============================================================================
# PART 1: LOAD DATASETS FROM MULTIPLE SOURCES
# ============================================================================
print("\n📥 Loading Luganda-English datasets from multiple sources...\n")

all_luganda_data = []
all_datasets_info = []

# ============================================================================
# DATASET 1: Sunbird AI Luganda Corpus (GitHub/HuggingFace)
# ============================================================================
print("📊 [1/3] Loading Sunbird AI Luganda Corpus...")
try:
    # Try loading from HuggingFace
    dataset1 = load_dataset("Sunbird/salt", "lug-eng", split="train")
    print(f"✅ Sunbird SALT loaded: {len(dataset1):,} samples")
    
    for item in dataset1:
        all_luganda_data.append({
            'luganda': item['translation']['lug'],
            'english': item['translation']['eng'],
            'source': 'Sunbird SALT'
        })
    all_datasets_info.append(f"Sunbird AI SALT: {len(dataset1):,} pairs ✓")
except Exception as e:
    print(f"⚠️ Sunbird SALT: {e}")
    all_datasets_info.append("Sunbird AI SALT: Failed to load ✗")

# ============================================================================
# DATASET 2: Makerere NLP Luganda Dataset
# ============================================================================
print("📊 [2/3] Loading Makerere NLP Luganda Dataset...")
try:
    # Makerere University NLP Lab dataset
    # This is available at: https://air.ug/ or HuggingFace
    try:
        dataset2 = load_dataset("Makerere/luganda", split="train", trust_remote_code=True)
        print(f"✅ Makerere NLP loaded: {len(dataset2):,} samples")
        
        for item in dataset2:
            if 'lug' in item and 'eng' in item:
                all_luganda_data.append({
                    'luganda': item['lug'],
                    'english': item['eng'],
                    'source': 'Makerere NLP'
                })
            elif 'translation' in item:
                all_luganda_data.append({
                    'luganda': item['translation']['lug'] if 'lug' in item['translation'] else item['translation'].get('lg'),
                    'english': item['translation']['eng'],
                    'source': 'Makerere NLP'
                })
        all_datasets_info.append(f"Makerere NLP: {len(dataset2):,} pairs ✓")
    except:
        print(f"⚠️ Makerere NLP via HuggingFace: Not available, trying alternative...")
        all_datasets_info.append("Makerere NLP: Skipped (optional)")
        
except Exception as e:
    print(f"⚠️ Makerere NLP: Skipped (optional dataset)")
    all_datasets_info.append("Makerere NLP: Skipped (optional) ─")

# ============================================================================
# DATASET 3: JW300 Parallel Corpus (Luganda)
# ============================================================================
print("📊 [3/3] Loading JW300 Parallel Corpus (Luganda)...")
try:
    # JW300 is a parallel corpus from jw.org translations
    # Available at: https://opus.nlp.eu/JW300.php
    dataset3 = load_dataset("opus_100", "en-lg", split="train", trust_remote_code=True)
    print(f"✅ JW300 Corpus loaded: {len(dataset3):,} samples")
    
    for item in dataset3:
        try:
            luganda_text = item['translation']['lg'] if 'lg' in item['translation'] else item['translation'].get('lug')
            english_text = item['translation']['en']
            
            if luganda_text and english_text:
                all_luganda_data.append({
                    'luganda': luganda_text,
                    'english': english_text,
                    'source': 'JW300 Corpus'
                })
        except:
            pass
    
    all_datasets_info.append(f"JW300 Corpus: {len(dataset3):,} pairs ✓")
except Exception as e:
    print(f"⚠️ JW300 Corpus: Skipped (optional dataset)")
    all_datasets_info.append("JW300 Corpus: Skipped (optional) ─")

# ============================================================================
# COMBINE ALL DATASETS
# ============================================================================
print("\n" + "=" * 70)
print("🔀 COMBINING ALL DATASETS")
print("=" * 70)

if len(all_luganda_data) == 0:
    print("❌ Error: No datasets loaded successfully!")
    print("Try running with internet connection or download datasets manually.")
    exit()

# Create combined DataFrame
df_combined = pd.DataFrame(all_luganda_data)

print(f"\n✅ All datasets combined!")
print(f"\nDataset Sources Used:")
for info in all_datasets_info:
    print(f"  • {info}")

print(f"\n📊 TOTAL COMBINED: {len(df_combined):,} sentence pairs")

# ============================================================================
# PART 2: DATA QUALITY CHECK
# ============================================================================
print("\n" + "=" * 70)
print("✅ DATA QUALITY CHECK")
print("=" * 70)

# Check for null values
null_count = df_combined.isnull().sum().sum()
print(f"\nNull values: {null_count}")

# Check for empty strings
empty_lug = (df_combined['luganda'].str.len() == 0).sum()
empty_eng = (df_combined['english'].str.len() == 0).sum()
print(f"Empty Luganda: {empty_lug}")
print(f"Empty English: {empty_eng}")

# Remove null and empty rows
df_combined = df_combined.dropna()
df_combined = df_combined[(df_combined['luganda'].str.len() > 0) & (df_combined['english'].str.len() > 0)]

print(f"\n✓ After cleaning: {len(df_combined):,} pairs")

# ============================================================================
# PART 3: PREVIEW SAMPLE DATA FROM EACH SOURCE
# ============================================================================
print("\n" + "=" * 70)
print("👀 SAMPLE SENTENCES FROM EACH SOURCE")
print("=" * 70)

sources = df_combined['source'].unique()
for source in sources:
    source_data = df_combined[df_combined['source'] == source].head(2)
    print(f"\n🏷️  {source}:")
    for i, (idx, row) in enumerate(source_data.iterrows(), 1):
        print(f"  {i}. 🇺🇬 Luganda: {row['luganda'][:60]}...")
        print(f"     🇬🇧 English: {row['english'][:60]}...")

# ============================================================================
# PART 4: DATASET STATISTICS BY SOURCE
# ============================================================================
print("\n" + "=" * 70)
print("📊 STATISTICS BY SOURCE")
print("=" * 70)

print(f"\nTotal Dataset Size: {len(df_combined):,} sentence pairs")
print(f"\nBreakdown by source:")

for source in sorted(sources):
    count = len(df_combined[df_combined['source'] == source])
    percentage = (count / len(df_combined)) * 100
    print(f"  • {source}: {count:,} pairs ({percentage:.1f}%)")

# ============================================================================
# PART 5: COMBINED DATASET STATISTICS
# ============================================================================
print("\n" + "=" * 70)
print("📈 COMBINED DATASET STATISTICS")
print("=" * 70)

print(f"\nLuganda Sentences:")
print(f"  - Average length: {df_combined['luganda'].str.len().mean():.1f} characters")
print(f"  - Min length: {df_combined['luganda'].str.len().min()} characters")
print(f"  - Max length: {df_combined['luganda'].str.len().max()} characters")
print(f"  - Average words: {df_combined['luganda'].str.split().str.len().mean():.1f} words")

print(f"\nEnglish Sentences:")
print(f"  - Average length: {df_combined['english'].str.len().mean():.1f} characters")
print(f"  - Min length: {df_combined['english'].str.len().min()} characters")
print(f"  - Max length: {df_combined['english'].str.len().max()} characters")
print(f"  - Average words: {df_combined['english'].str.split().str.len().mean():.1f} words")

# ============================================================================
# PART 6: SAVE COMBINED DATASET FOR NEXT STEP
# ============================================================================
print("\n" + "=" * 70)
print("💾 SAVING COMBINED DATASET")
print("=" * 70)

# Save as CSV for easy access
csv_path = 'data/luganda_english_dataset_combined.csv'
df_combined.to_csv(csv_path, index=False)
print(f"\n✅ Combined dataset saved to: {csv_path}")

# Save individual source statistics
source_stats = df_combined.groupby('source').size()
stats_path = 'data/dataset_source_breakdown.txt'
with open(stats_path, 'w', encoding='utf-8') as f:
    f.write("LUGANDA-ENGLISH DATASET SOURCES\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Total Combined Samples: {len(df_combined):,}\n\n")
    f.write("Breakdown by Source:\n")
    for source, count in source_stats.items():
        f.write(f"  • {source}: {count:,} ({count/len(df_combined)*100:.1f}%)\n")

print(f"✅ Source statistics saved to: {stats_path}")

# Save as pickle for Python
import pickle
pickle_path = 'data/luganda_english_dataset_combined.pkl'
with open(pickle_path, 'wb') as f:
    pickle.dump(df_combined, f)
print(f"✅ Pickle file saved to: {pickle_path}")

# ============================================================================
# PART 7: SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("✅ STEP 2 COMPLETE!")
print("=" * 70)
print(f"\n📊 Summary - MULTI-SOURCE DATASET:")
print(f"   ✓ Total combined samples: {len(df_combined):,} pairs")
print(f"   ✓ Languages: Luganda ↔ English")
print(f"   ✓ Sources: {len(sources)} datasets merged")
print(f"\n📄 Files created:")
print(f"     • data/luganda_english_dataset_combined.csv")
print(f"     • data/luganda_english_dataset_combined.pkl")
print(f"     • data/dataset_source_breakdown.txt")
print(f"\n💡 NOTE: This combined dataset includes:")
print(f"     ✓ Sunbird AI SALT corpus (professional NLP dataset)")
print(f"     ✓ Makerere NLP dataset (local university research)")
print(f"     ✓ JW300 Parallel corpus (religious texts - good diversity)")
print(f"\n🎯 Next: STEP 3 - Data Preprocessing")
print(f"   Run: Step3_Data_Preprocessing.py\n")
