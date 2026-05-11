"""
STAGE 2: COLLECT DATA
=====================
Loads, validates, and splits English-Luganda parallel corpus from multiple sources.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import os
from datasets import load_dataset

class DataCollector:
    """
    Responsible for loading, validating, and splitting datasets.
    Supports multiple data sources: CSV files with English-Luganda pairs.
    """
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.df = None
        self.stats = {}
    
    def load_dataset(self, filepath):
        """
        Load CSV dataset with 'english' and 'luganda' columns.
        
        Args:
            filepath (str): Path to CSV file
            
        Returns:
            pd.DataFrame: Loaded dataframe
        """
        print(f"\n[DATA COLLECTION] Loading dataset: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            # Validate columns
            if 'english' not in df.columns or 'luganda' not in df.columns:
                raise ValueError("Dataset must contain 'english' and 'luganda' columns")
            
            print(f"  ✓ Loaded {len(df):,} translation pairs")
            return df
        
        except Exception as e:
            print(f"  ✗ Error loading dataset: {e}")
            return None

    def load_huggingface_dataset(self, dataset_name="kambale/luganda-english-parallel-corpus"):
        """
        Load the Hugging Face English-Luganda parallel corpus.

        Args:
            dataset_name (str): Hugging Face dataset identifier

        Returns:
            pd.DataFrame: Normalized dataframe with 'english' and 'luganda' columns
        """
        print(f"\n[DATA COLLECTION] Loading Hugging Face dataset: {dataset_name}")

        try:
            hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
            dataset = load_dataset(dataset_name, token=hf_token if hf_token else None)

            if hasattr(dataset, "keys") and "train" in dataset:
                data_frame = dataset["train"].to_pandas()
            else:
                data_frame = dataset.to_pandas()

            if "translation" in data_frame.columns:
                english_values = []
                luganda_values = []

                for item in data_frame["translation"]:
                    if isinstance(item, dict):
                        english_values.append(item.get("eng") or item.get("english") or item.get("src") or "")
                        luganda_values.append(item.get("lug") or item.get("luganda") or item.get("tgt") or "")
                    else:
                        english_values.append("")
                        luganda_values.append("")

                data_frame = pd.DataFrame({"english": english_values, "luganda": luganda_values})

            elif not {"english", "luganda"}.issubset(data_frame.columns):
                raise ValueError("Hugging Face dataset must contain english/luganda or translation columns")

            data_frame = data_frame[["english", "luganda"]].dropna().reset_index(drop=True)
            print(f"  ✓ Loaded {len(data_frame):,} translation pairs")
            return data_frame

        except Exception as error:
            print(f"  ✗ Error loading Hugging Face dataset: {error}")
            if "gated dataset" in str(error).lower():
                print("  • Set HF_TOKEN or HUGGINGFACE_HUB_TOKEN after requesting access to the dataset.")
            return None
    
    def load_multiple_datasets(self, filepaths):
        """
        Load and concatenate multiple datasets.
        
        Args:
            filepaths (list): List of CSV file paths
            
        Returns:
            pd.DataFrame: Combined dataframe
        """
        print(f"\n[DATA COLLECTION] Loading {len(filepaths)} datasets...")
        
        dfs = []
        for filepath in filepaths:
            df = self.load_dataset(filepath)
            if df is not None:
                dfs.append(df)
        
        if dfs:
            self.df = pd.concat(dfs, ignore_index=True)
            print(f"\n  ✓ Total pairs after combining: {len(self.df):,}")
            return self.df
        
        return None
    
    def validate_dataset(self):
        """
        Validate dataset quality.
        
        Checks:
        - No missing values
        - Text length sanity
        - Encoding issues
        - Duplicates
        """
        print("\n[DATA VALIDATION] Checking dataset quality...")
        
        if self.df is None:
            print("  ✗ No dataset loaded")
            return False
        
        # Check missing values
        missing = self.df.isnull().sum()
        print(f"  • Missing values: {missing.sum()}")
        if missing.sum() > 0:
            self.df.dropna(inplace=True)
            print(f"    Dropped {missing.sum()} rows with missing values")
        
        # Check duplicates
        duplicates = self.df.duplicated(subset=['english', 'luganda']).sum()
        print(f"  • Duplicate pairs: {duplicates}")
        if duplicates > 0:
            self.df.drop_duplicates(subset=['english', 'luganda'], inplace=True)
            print(f"    Dropped {duplicates} duplicate pairs")
        
        # Check text lengths
        self.df['en_length'] = self.df['english'].str.split().str.len()
        self.df['lg_length'] = self.df['luganda'].str.split().str.len()
        
        print(f"  • English sentence lengths: {self.df['en_length'].min()}-{self.df['en_length'].max()} words")
        print(f"  • Luganda sentence lengths: {self.df['lg_length'].min()}-{self.df['lg_length'].max()} words")
        
        # Remove extremely long sequences (likely errors)
        before = len(self.df)
        self.df = self.df[(self.df['en_length'] <= 100) & (self.df['lg_length'] <= 100)]
        removed = before - len(self.df)
        if removed > 0:
            print(f"    Removed {removed} sentences > 100 words")
        
        self.df.drop(['en_length', 'lg_length'], axis=1, inplace=True)
        
        print(f"\n  ✓ Validation complete. Final dataset: {len(self.df):,} pairs")
        return True
    
    def split_dataset(self, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, random_state=42):
        """
        Split dataset into train, validation, and test sets.
        
        Args:
            train_ratio (float): Proportion for training (default 0.8)
            val_ratio (float): Proportion for validation (default 0.1)
            test_ratio (float): Proportion for testing (default 0.1)
            random_state (int): Random seed for reproducibility
            
        Returns:
            dict: Contains 'train', 'val', 'test' dataframes
        """
        print(f"\n[DATA SPLITTING] Splitting dataset...")
        print(f"  • Train: {train_ratio*100:.0f}%, Validation: {val_ratio*100:.0f}%, Test: {test_ratio*100:.0f}%")
        
        np.random.seed(random_state)
        
        # Shuffle dataframe
        df_shuffled = self.df.sample(frac=1, random_state=random_state).reset_index(drop=True)
        
        # Calculate split indices
        n = len(df_shuffled)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        # Split
        train_df = df_shuffled[:train_end]
        val_df = df_shuffled[train_end:val_end]
        test_df = df_shuffled[val_end:]
        
        splits = {
            'train': train_df.reset_index(drop=True),
            'val': val_df.reset_index(drop=True),
            'test': test_df.reset_index(drop=True)
        }
        
        # Print statistics
        print(f"\n  ✓ Train set: {len(train_df):,} pairs")
        print(f"  ✓ Validation set: {len(val_df):,} pairs")
        print(f"  ✓ Test set: {len(test_df):,} pairs")
        
        self.stats = {
            'total': len(self.df),
            'train': len(train_df),
            'val': len(val_df),
            'test': len(test_df)
        }
        
        return splits
    
    def save_splits(self, splits, output_dir="data"):
        """
        Save train/val/test splits as CSV files.
        
        Args:
            splits (dict): Dictionary with 'train', 'val', 'test' dataframes
            output_dir (str): Directory to save files
        """
        print(f"\n[SAVING DATA] Writing splits to {output_dir}/...")
        
        Path(output_dir).mkdir(exist_ok=True)
        processed_dir = Path("data/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        for split_name, split_df in splits.items():
            filepath = Path(output_dir) / f"{split_name}_dataset.csv"
            split_df.to_csv(filepath, index=False)
            print(f"  ✓ {filepath}: {len(split_df):,} pairs")

            pickle_path = processed_dir / f"{split_name}_dataset.pkl"
            split_df.to_pickle(pickle_path)
            print(f"  ✓ {pickle_path}: {len(split_df):,} pairs")
    
    def save_statistics(self, output_file="reports/data_statistics.json"):
        """
        Save dataset statistics as JSON.
        
        Args:
            output_file (str): Path to output JSON file
        """
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        stats_report = {
            "total_pairs": self.stats.get('total', 0),
            "train_size": self.stats.get('train', 0),
            "val_size": self.stats.get('val', 0),
            "test_size": self.stats.get('test', 0),
            "dataset_info": {
                "source": "kambale/luganda-english-parallel-corpus (preferred) with local CSV fallback",
                "languages": "English ↔ Luganda",
                "format": "CSV/Pickle with 'english' and 'luganda' columns"
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(stats_report, f, indent=2)
        
        print(f"✓ Statistics saved to: {output_file}")


def collect_data(data_sources=None):
    """
    Main data collection pipeline.
    
    Args:
        data_sources (list): List of CSV file paths
        
    Returns:
        dict: Train/val/test splits
    """
    collector = DataCollector()
    
    # Load datasets
    hf_dataset = collector.load_huggingface_dataset()

    if hf_dataset is not None:
        collector.df = hf_dataset
    elif data_sources:
        collector.load_multiple_datasets(data_sources)
    else:
        # Try to load from default location
        csv_files = list(Path("data/raw").glob("*.csv"))
        if csv_files:
            collector.load_multiple_datasets([str(f) for f in csv_files])
        else:
            print("No CSV files found in data/raw/")
            return None
    
    # Validate
    if collector.df is None or not collector.validate_dataset():
        return None
    
    # Split
    splits = collector.split_dataset()
    
    # Save
    collector.save_splits(splits)
    collector.save_statistics()
    
    return splits


if __name__ == "__main__":
    print("=" * 80)
    print("STAGE 2: DATA COLLECTION & VALIDATION")
    print("=" * 80)
    collect_data()
    collect_data()
    
    # Example usage
    data_sources = [
        "data/raw/sunbird_salt.csv",
        "data/raw/makerere_nlp.csv",
        "data/raw/jw300_parallel.csv"
    ]
    
    splits = collect_data(data_sources)
