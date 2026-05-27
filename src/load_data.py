"""
STEP 1: Load Data - Week 2 ML Workflow
=====================================
Load all 5 English-Luganda datasets from data/raw/ and combine them.

Datasets:
  1. kambale_train.csv         - High-quality Kambale corpus
  2. cultural_training.csv     - Buganda cultural terms
  3. jw300_parallel.csv        - Religious/literary texts
  4. makerere_nlp.csv          - Academic Luganda
  5. sunbird_salt.csv          - Low-resource language data
"""

from pathlib import Path
from typing import Dict, List
import pandas as pd
import sys

try:
    from config import RAW_DATASETS, TEXT_MIN_LENGTH, TEXT_MAX_LENGTH
    from utils import load_csv_safe, print_section, validate_pair
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import RAW_DATASETS, TEXT_MIN_LENGTH, TEXT_MAX_LENGTH
    from utils import load_csv_safe, print_section, validate_pair


def load_all_datasets(balance_per_source: int = None) -> pd.DataFrame:
    """
    Load all datasets from data/raw/ and combine them.
    
    Args:
        balance_per_source: If set to a number, sample that many pairs from each source.
                           If None or 0, use ALL data (recommended for large datasets).
    
    Returns:
        pd.DataFrame with columns: ['english', 'luganda', 'source']
    """
    print_section("STEP 1: LOADING DATASETS", width=80)
    
    if balance_per_source:
        print(f"\n[INFO] BALANCED SAMPLING MODE: {balance_per_source} samples per source")
    else:
        print(f"\n[INFO] LOADING ALL AVAILABLE DATA (no sampling)")
    
    frames: List[pd.DataFrame] = []
    total_loaded = 0
    
    for name, path in RAW_DATASETS.items():
        print(f"\n📂 Loading {name}...")
        df = load_csv_safe(path)
        
        if df.empty:
            print(f"   ⚠️  Empty or invalid")
            continue
        
        # Keep all data - just ensure both columns have non-empty text after cleaning
        # Just ensure both columns have non-empty text after cleaning
        df = df[
            (df['english'].str.len() > 0) & 
            (df['luganda'].str.len() > 0)
        ].reset_index(drop=True)
        
        if df.empty:
            print(f"   ⚠️  No valid pairs after filtering")
            continue
        
        # Apply balanced sampling if specified
        if balance_per_source and len(df) > balance_per_source:
            df = df.sample(n=balance_per_source, random_state=42).reset_index(drop=True)
            print(f"   ✅ Sampled {len(df):,} pairs (balanced) | Source: {df['source'].iloc[0]}")
        else:
            print(f"   ✅ Loaded {len(df):,} pairs | Source: {df['source'].iloc[0]}")
        
        frames.append(df)
        total_loaded += len(df)
    
    if not frames:
        raise ValueError("❌ No datasets loaded! Check data/raw/ directory.")
    
    # Combine all datasets
    combined = pd.concat(frames, ignore_index=True)
    
    print_section("DATASET SUMMARY", width=80)
    print(f"\n[INFO] Total samples loaded: {len(combined):,}")
    print(f"\n📈 Breakdown by source:")
    for source, count in combined['source'].value_counts().items():
        pct = (count / len(combined)) * 100
        print(f"   {source:30} {count:6,} ({pct:5.1f}%)")
    
    return combined


def get_dataset_statistics(df: pd.DataFrame) -> Dict:
    """Calculate statistics about the dataset."""
    stats = {
        "total_samples": len(df),
        "avg_english_length": df['english'].str.len().mean(),
        "avg_luganda_length": df['luganda'].str.len().mean(),
        "max_english_length": df['english'].str.len().max(),
        "max_luganda_length": df['luganda'].str.len().max(),
        "unique_sources": df['source'].nunique(),
    }
    return stats


def main():
    """Load and display dataset information."""
    # Load all datasets
    combined_df = load_all_datasets()
    
    # Get statistics
    stats = get_dataset_statistics(combined_df)
    
    print_section("DATASET STATISTICS", width=80)
    print(f"\n📏 Text Length Statistics:")
    print(f"   English - Avg: {stats['avg_english_length']:.1f}, Max: {stats['max_english_length']}")
    print(f"   Luganda - Avg: {stats['avg_luganda_length']:.1f}, Max: {stats['max_luganda_length']}")
    
    print(f"\n✅ Step 1 Complete!")
    print(f"   Total dataset size: {len(combined_df):,} pairs")
    print(f"   Ready for preprocessing...")
    
    return combined_df


if __name__ == "__main__":
    main()
