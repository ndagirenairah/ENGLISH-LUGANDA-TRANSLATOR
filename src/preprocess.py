"""
STEP 2: Preprocess Data - Week 2 ML Workflow
=============================================
Combine datasets and create train/validation/test splits.

This implements the core ML workflow:
  - Train set: 80% (for training)
  - Validation set: 10% (for hyperparameter tuning)
  - Test set: 10% (for final evaluation)
"""

from pathlib import Path
from typing import Tuple
import sys
import pandas as pd
from sklearn.model_selection import train_test_split

try:
    from config import (
        PROCESSED_DATA_DIR, TEST_SET_FRACTION, VAL_SET_FRACTION, 
        RANDOM_SEED, TEXT_MIN_LENGTH, TEXT_MAX_LENGTH
    )
    from utils import print_section, clean_text
    from load_data import load_all_datasets
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import (
        PROCESSED_DATA_DIR, TEST_SET_FRACTION, VAL_SET_FRACTION, 
        RANDOM_SEED, TEXT_MIN_LENGTH, TEXT_MAX_LENGTH
    )
    from utils import print_section, clean_text
    from load_data import load_all_datasets


def preprocess_and_split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Preprocess text and split into train/val/test sets.
    
    Week 2 ML Workflow:
    - Data cleaning: normalize text
    - Train/test split: typically 80/20, then split val from train
    
    Args:
        df: Combined dataframe with 'english' and 'luganda' columns
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    print_section("STEP 2: PREPROCESSING DATA", width=80)
    
    # Clean text
    print("\n🧹 Cleaning text...")
    df['english'] = df['english'].apply(clean_text)
    df['luganda'] = df['luganda'].apply(clean_text)
    
    # Filter invalid pairs, remove noise, and deduplicate
    before = len(df)
    df = df[df.apply(lambda row: validate_pair(row['english'], row['luganda']), axis=1)]
    df = df.drop_duplicates(subset=['english', 'luganda']).reset_index(drop=True)
    removed = before - len(df)
    if removed > 0:
        print(f"   Removed {removed} invalid/duplicate entries")

    print(f"   ✅ {len(df):,} clean pairs")
    
    # Test set split (10%)
    train_val_df, test_df = train_test_split(
        df,
        test_size=TEST_SET_FRACTION,
        random_state=RANDOM_SEED
    )
    
    # Validation set split from remaining (10% of original = 11.1% of train_val)
    val_fraction = VAL_SET_FRACTION / (1 - TEST_SET_FRACTION)
    train_df, val_df = train_test_split(
        train_val_df,
        test_size=val_fraction,
        random_state=RANDOM_SEED
    )
    
    print(f"   Train: {len(train_df):,} | Val: {len(val_df):,} | Test: {len(test_df):,}")
    
    # Reset indices
    train_df = train_df.reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)
    
    return train_df, val_df, test_df


def save_splits(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
    """Save train/val/test splits to CSV files."""
    print("\n[INFO] Saving splits...")
    
    # Create directory if needed
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    train_path = PROCESSED_DATA_DIR / "train.csv"
    val_path = PROCESSED_DATA_DIR / "val.csv"
    test_path = PROCESSED_DATA_DIR / "test.csv"
    
    # Save with only english/luganda columns (drop source for cleaner training)
    train_df[['english', 'luganda']].to_csv(train_path, index=False)
    val_df[['english', 'luganda']].to_csv(val_path, index=False)
    test_df[['english', 'luganda']].to_csv(test_path, index=False)
    
    print(f"   ✅ Saved to {PROCESSED_DATA_DIR}/")
    print(f"      - train.csv ({len(train_df):,} samples)")
    print(f"      - val.csv ({len(val_df):,} samples)")
    print(f"      - test.csv ({len(test_df):,} samples)")


def main():
    """Load raw data, preprocess, and create splits."""
    # Load all raw datasets
    combined_df = load_all_datasets()
    
    # Preprocess and split
    train_df, val_df, test_df = preprocess_and_split(combined_df)
    
    # Save splits
    save_splits(train_df, val_df, test_df)
    
    print_section("PREPROCESSING COMPLETE", width=80)
    print(f"\n✅ Data ready for training!")
    print(f"\n   Next step: python src/3_train.py")
    
    return train_df, val_df, test_df


if __name__ == "__main__":
    main()
