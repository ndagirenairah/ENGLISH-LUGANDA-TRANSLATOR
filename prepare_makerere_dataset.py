#!/usr/bin/env python
# ============================================================================
# LOAD & PREPARE MAKERERE AI LAB LUGANDA DATASET
# High-quality 15K+ sentences from Makerere University
# ============================================================================

import pandas as pd
import os

print("=" * 80)
print("🇺🇬 LOADING MAKERERE AI LAB LUGANDA DATASET")
print("=" * 80)

# Load the Makerere dataset
dataset_path = 'makerere_luganda_dataset.csv'

if not os.path.exists(dataset_path):
    print(f"❌ Error: {dataset_path} not found!")
    exit(1)

print(f"\n📥 Loading dataset from: {dataset_path}")

# Read the CSV with different encoding attempts
df = None
encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']

for encoding in encodings_to_try:
    try:
        print(f"   Trying encoding: {encoding}...")
        df = pd.read_csv(dataset_path, encoding=encoding)
        print(f"   ✅ Successfully loaded with {encoding} encoding")
        break
    except Exception as e:
        continue

if df is None:
    print(f"❌ Error: Could not read file with any encoding!")
    exit(1)

print(f"\n📊 Initial Dataset Info:")
print(f"   • Rows: {len(df)}")
print(f"   • Columns: {df.columns.tolist()}")
print(f"   • Shape: {df.shape}")

# Show first few rows
print(f"\n📝 First 5 rows:")
print(df.head())

print(f"\n🔍 Data types:")
print(df.dtypes)

print(f"\n🧹 Cleaning dataset...")

# Identify English and Luganda columns (try common names)
english_col = None
luganda_col = None

for col in df.columns:
    col_lower = col.lower().strip()
    if any(x in col_lower for x in ['english', 'eng', 'en', 'source']):
        english_col = col
    if any(x in col_lower for x in ['luganda', 'lug', 'lg', 'target']):
        luganda_col = col

# If not found, try positional
if english_col is None or luganda_col is None:
    print(f"   Trying positional columns...")
    if len(df.columns) >= 2:
        english_col = df.columns[0]
        luganda_col = df.columns[1]

print(f"   Detected columns:")
print(f"   • English: {english_col}")
print(f"   • Luganda: {luganda_col}")

# Extract and rename
if english_col and luganda_col:
    df_clean = df[[english_col, luganda_col]].copy()
    df_clean.columns = ['english', 'luganda']
else:
    print("❌ Could not identify English/Luganda columns!")
    exit(1)

# Data cleaning
print(f"\n🧹 Applying cleaning operations:")

before = len(df_clean)

# Remove duplicates
df_clean = df_clean.drop_duplicates(subset=['english', 'luganda'])
print(f"   ✅ Removed duplicates: {before - len(df_clean)} rows")

# Remove NaN
before = len(df_clean)
df_clean = df_clean.dropna()
print(f"   ✅ Removed NaN values: {before - len(df_clean)} rows")

# Strip whitespace
df_clean['english'] = df_clean['english'].str.strip()
df_clean['luganda'] = df_clean['luganda'].str.strip()

# Remove rows where english == luganda
before = len(df_clean)
df_clean = df_clean[df_clean['english'] != df_clean['luganda']]
print(f"   ✅ Removed identical pairs: {before - len(df_clean)} rows")

# Remove empty rows
before = len(df_clean)
df_clean = df_clean[(df_clean['english'].str.len() > 0) & (df_clean['luganda'].str.len() > 0)]
print(f"   ✅ Removed empty entries: {before - len(df_clean)} rows")

print(f"\n✅ FINAL DATASET STATISTICS:")
print(f"   • Total sentences: {len(df_clean)}")
print(f"   • Unique English: {df_clean['english'].nunique()}")
print(f"   • Unique Luganda: {df_clean['luganda'].nunique()}")
print(f"   • Memory usage: {df_clean.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

# Save the cleaned dataset
output_path = 'makerere_luganda_cleaned.csv'
df_clean.to_csv(output_path, index=False)
print(f"\n✅ Saved cleaned dataset to: {output_path}")

# Also create a training-friendly version
df_clean.to_csv('luganda_training_data.csv', index=False)
print(f"✅ Saved training data to: luganda_training_data.csv")

# Show samples
print(f"\n📝 Sample Translations (First 10):")
print("-" * 80)
for idx in range(min(10, len(df_clean))):
    en = df_clean['english'].iloc[idx][:60].ljust(60)
    lu = df_clean['luganda'].iloc[idx][:60]
    print(f"{idx+1:2d}. EN: {en} | LU: {lu}")

print("\n" + "=" * 80)
print("✅ MAKERERE DATASET IS READY FOR TRAINING!")
print("=" * 80 + "\n")
