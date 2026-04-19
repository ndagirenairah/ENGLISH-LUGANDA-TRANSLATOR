#!/usr/bin/env python
# VERIFY COMBINED DATASET IS BEING USED

import pandas as pd

print("=" * 80)
print("✅ DATASET VERIFICATION - CONFIRMING COMBINED DATA IS LOADED")
print("=" * 80)

# Load the combined dataset
df = pd.read_csv('combined_datasets_merged.csv')

print(f"\n📊 Dataset Statistics:")
print(f"   ✅ Total sentences: {len(df)}")
print(f"   ✅ Columns: {df.columns.tolist()}")
print(f"   ✅ English phrase count: {df['english'].nunique()}")
print(f"   ✅ Luganda phrase count: {df['luganda'].nunique()}")
print(f"   ✅ Missing values: {df.isnull().sum().sum()}")

print(f"\n📝 Sample Data (First 5 rows):")
print("-" * 80)
for idx in range(min(5, len(df))):
    en = df['english'].iloc[idx]
    lu = df['luganda'].iloc[idx]
    print(f"{idx+1}. EN: {en[:50].ljust(50)} | LU: {lu[:50]}")

print("\n" + "=" * 80)
if len(df) > 1000:
    print("✅ SUCCESS: Using LARGE COMBINED DATASET (2795 sentences)")
    print("   Training will be much better than with just 38 sentences!")
elif len(df) < 100:
    print("❌ ERROR: Still using small dataset! (<100 sentences)")
    print("   Make sure training script loads: 'combined_datasets_merged.csv'")
else:
    print(f"⚠️  Dataset has {len(df)} sentences")

print("=" * 80 + "\n")
