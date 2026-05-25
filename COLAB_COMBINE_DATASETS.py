#!/usr/bin/env python3
"""
Script to combine all Kambale + local datasets for Colab training
This script is designed to run in Google Colab
"""

import pandas as pd
import os
from pathlib import Path

def combine_datasets_for_colab():
    """
    Combine all available datasets with proper cleaning and deduplication
    """
    
    # Dataset sources - adjust paths based on where you upload to Colab
    datasets_info = {
        'kambale_train.csv': 'Kambale Training Set',
        'cultural_training.csv': 'Cultural Dataset',
        'jw300_parallel.csv': 'JW300 Parallel',
        'makerere_nlp.csv': 'Makerere NLP',
        'sunbird_salt.csv': 'Sunbird SALT'
    }
    
    print("=" * 70)
    print("COMBINING DATASETS FOR COLAB TRAINING")
    print("=" * 70)
    
    combined_dfs = []
    total_samples = 0
    
    for filename, description in datasets_info.items():
        file_path = f'/content/{filename}'
        
        try:
            print(f"\n📂 Loading {description} ({filename})...")
            df = pd.read_csv(file_path)
            
            # Check for required columns
            if 'english' not in df.columns or 'luganda' not in df.columns:
                print(f"   ⚠️  Skipping: Missing 'english' or 'luganda' columns")
                continue
            
            # Get initial count
            initial_count = len(df)
            
            # Basic cleaning
            df = df[['english', 'luganda']].copy()
            df = df.dropna()
            df['english'] = df['english'].astype(str).str.strip()
            df['luganda'] = df['luganda'].astype(str).str.strip()
            df = df[(df['english'] != '') & (df['luganda'] != '')]
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['english', 'luganda'], keep='first')
            
            final_count = len(df)
            removed = initial_count - final_count
            
            print(f"   ✓ Loaded: {final_count} samples (removed {removed} duplicates)")
            combined_dfs.append(df)
            total_samples += final_count
            
        except FileNotFoundError:
            print(f"   ⚠️  File not found: {file_path}")
        except Exception as e:
            print(f"   ⚠️  Error loading file: {e}")
    
    if not combined_dfs:
        print("\n❌ ERROR: No datasets loaded!")
        return None
    
    # Combine all dataframes
    print(f"\n{'='*70}")
    print(f"🔀 Combining {len(combined_dfs)} datasets...")
    combined_df = pd.concat(combined_dfs, ignore_index=True)
    
    print(f"   Total samples before dedup: {len(combined_df)}")
    
    # Final deduplication across all datasets
    combined_df = combined_df.drop_duplicates(subset=['english', 'luganda'], keep='first')
    print(f"   Total samples after dedup: {len(combined_df)}")
    
    # Shuffle
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    print(f"\n{'='*70}")
    print(f"✅ FINAL COMBINED DATASET")
    print(f"{'='*70}")
    print(f"Total samples: {len(combined_df)}")
    print(f"\nFirst 5 samples:")
    print(combined_df.head())
    
    # Save to CSV
    output_path = '/content/combined_kambale_dataset.csv'
    combined_df.to_csv(output_path, index=False)
    print(f"\n💾 Saved to: {output_path}")
    
    return combined_df

if __name__ == "__main__":
    df = combine_datasets_for_colab()
    if df is not None:
        print(f"\n🎉 Ready for training with {len(df)} samples!")
