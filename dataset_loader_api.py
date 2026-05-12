#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KABALE DATASET API LOADER
Loads the Kabale English-Luganda corpus using HuggingFace API directly.
Handles gated dataset access via bearer token authentication.
"""

import os
import sys
import requests
import json
import pandas as pd
from pathlib import Path
from typing import Tuple, List, Dict, Optional

class KabaleDatasetLoader:
    """
    Loads Kabale English-Luganda parallel corpus via HuggingFace API.
    """
    
    BASE_URL = "https://datasets-server.huggingface.co"
    DATASET_ID = "kambale/luganda-english-parallel-corpus"
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize loader with HuggingFace token.
        
        Args:
            token: HF token (from environment or parameter)
        """
        self.token = token or os.getenv('HF_TOKEN') or os.getenv('HUGGINGFACE_HUB_TOKEN')
        if not self.token:
            raise ValueError(
                "HuggingFace token not found. Set HF_TOKEN or HUGGINGFACE_HUB_TOKEN "
                "environment variable. Get token from: https://huggingface.co/settings/tokens"
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "EnglishLugandaTranslator/1.0"
        }
    
    def get_splits(self) -> List[str]:
        """Get available dataset splits."""
        url = f"{self.BASE_URL}/splits"
        params = {"dataset": self.DATASET_ID}
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        splits = [s['split'] for s in data.get('splits', [])]
        return splits
    
    def get_config(self) -> str:
        """Get dataset configuration name."""
        url = f"{self.BASE_URL}/configs"
        params = {"dataset": self.DATASET_ID}
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        configs = data.get('configs', [])
        if not configs:
            return 'default'
        return configs[0]['config']
    
    def get_row_count(self, split: str = 'train') -> int:
        """Get number of rows in a split."""
        url = f"{self.BASE_URL}/rows"
        params = {
            "dataset": self.DATASET_ID,
            "config": self.get_config(),
            "split": split,
            "offset": 0,
            "length": 1
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get('total', 0)
    
    def fetch_rows(self, split: str = 'train', offset: int = 0, 
                  length: int = 100) -> List[Dict]:
        """
        Fetch rows from dataset.
        
        Args:
            split: Dataset split (train/validation/test)
            offset: Starting row index
            length: Number of rows to fetch
            
        Returns:
            List of row dictionaries
        """
        url = f"{self.BASE_URL}/rows"
        params = {
            "dataset": self.DATASET_ID,
            "config": self.get_config(),
            "split": split,
            "offset": offset,
            "length": length
        }
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get('rows', [])
    
    def load_full_dataset(self, split: str = 'train', 
                         max_samples: Optional[int] = None) -> pd.DataFrame:
        """
        Load entire dataset split into DataFrame.
        
        Args:
            split: Dataset split name
            max_samples: Maximum samples to load (None = all)
            
        Returns:
            DataFrame with 'english' and 'luganda' columns
        """
        print(f"[LOADER] Fetching {split} split...")
        
        # Get total count
        total = self.get_row_count(split)
        if max_samples:
            total = min(total, max_samples)
        
        print(f"[LOADER] Total samples: {total:,}")
        
        # Fetch in batches
        all_rows = []
        batch_size = 100
        
        for offset in range(0, total, batch_size):
            length = min(batch_size, total - offset)
            
            print(f"[LOADER] Fetching rows {offset:,}-{offset + length:,}...")
            
            try:
                rows = self.fetch_rows(split, offset, length)
                all_rows.extend(rows)
            except Exception as e:
                print(f"[WARNING] Error fetching batch: {e}")
                continue
        
        # Normalize to DataFrame
        df = self._normalize_rows(all_rows)
        print(f"[LOADER] Loaded {len(df):,} valid pairs from {split}")
        
        return df
    
    def _normalize_rows(self, rows: List[Dict]) -> pd.DataFrame:
        """
        Normalize API response rows to DataFrame with english/luganda columns.
        """
        data = []
        
        for row in rows:
            try:
                # Row data is under 'row' key from API
                item = row.get('row', row)
                
                # Handle nested translation column
                if 'translation' in item and isinstance(item['translation'], dict):
                    eng = item['translation'].get('en') or item['translation'].get('eng') or ''
                    lug = item['translation'].get('lg') or item['translation'].get('lug') or ''
                # Handle flat columns
                elif 'english' in item and 'luganda' in item:
                    eng = item['english']
                    lug = item['luganda']
                else:
                    continue
                
                # Clean
                eng = str(eng).strip() if eng else ''
                lug = str(lug).strip() if lug else ''
                
                # Validate
                if len(eng) > 3 and len(lug) > 3 and eng != 'nan' and lug != 'nan':
                    data.append({'english': eng, 'luganda': lug})
            except Exception as e:
                continue
        
        return pd.DataFrame(data)


def load_all_available_datasets(token: Optional[str] = None) -> pd.DataFrame:
    """
    Load all available splits from Kabale dataset.
    Combines train, validation, and test splits if available.
    """
    loader = KabaleDatasetLoader(token)
    
    all_data = []
    
    try:
        # Get available splits
        splits = loader.get_splits()
        print(f"[LOADER] Available splits: {splits}")
        
        # Load each split
        for split in splits:
            print(f"\n[LOADER] Processing split: {split}")
            try:
                df = loader.load_full_dataset(split)
                if len(df) > 0:
                    df['source'] = split
                    all_data.append(df)
            except Exception as e:
                print(f"[WARNING] Could not load split '{split}': {e}")
                continue
        
        # Combine
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            print(f"\n[LOADER] Combined total: {len(combined):,} pairs")
            return combined
        else:
            raise ValueError("Could not load any dataset splits")
            
    except Exception as e:
        print(f"[ERROR] Failed to load dataset: {e}")
        raise


if __name__ == '__main__':
    # Example usage
    print("[TEST] Kabale Dataset Loader")
    print("=" * 80)
    
    try:
        # Load with environment token
        data = load_all_available_datasets()
        
        print(f"\nDataset Statistics:")
        print(f"  Total pairs: {len(data):,}")
        print(f"  English avg length: {data['english'].str.len().mean():.1f} chars")
        print(f"  Luganda avg length: {data['luganda'].str.len().mean():.1f} chars")
        
        print(f"\nSample pairs:")
        for idx in range(min(3, len(data))):
            print(f"  [{idx+1}] EN: {data.iloc[idx]['english'][:50]}")
            print(f"      LG: {data.iloc[idx]['luganda'][:50]}")
        
        print(f"\n[SUCCESS] Loader working correctly!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
