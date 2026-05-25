"""
Utility functions for the ML Pipeline
"""

import re
from typing import Tuple
import pandas as pd
from pathlib import Path


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    - Remove URLs and emails
    - Normalize whitespace
    - Remove extra punctuation
    """
    if not isinstance(text, str):
        return ""
    
    text = str(text).strip()
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Remove emails
    text = re.sub(r"\S+@\S+", "", text)
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def validate_pair(english: str, luganda: str, min_len: int = 3, max_len: int = 256) -> bool:
    """
    Validate if a text pair is acceptable.
    - Both must not be empty
    - Both must be within length bounds
    - Both must have meaningful content
    """
    english = clean_text(english)
    luganda = clean_text(luganda)
    
    if not english or not luganda:
        return False
    
    if len(english) < min_len or len(luganda) < min_len:
        return False
    
    if len(english) > max_len or len(luganda) > max_len:
        return False
    
    return True


def load_csv_safe(path: Path, 
                   english_col: str = None, 
                   luganda_col: str = None) -> pd.DataFrame:
    """
    Load CSV and normalize columns to 'english' and 'luganda'.
    Auto-detect columns if names not provided.
    """
    if not path.exists():
        print(f"⚠️  Skipping {path}: File not found")
        return pd.DataFrame(columns=["english", "luganda"])
    
    try:
        df = pd.read_csv(path)
        
        # Auto-detect columns if not provided
        if english_col is None or luganda_col is None:
            col_map = {c.lower().strip(): c for c in df.columns}
            
            english_candidates = ["english", "eng", "en", "translation_en"]
            luganda_candidates = ["luganda", "lug", "lg", "translation_lg"]
            
            english_col = next((col_map[c] for c in english_candidates 
                              if c in col_map), None)
            luganda_col = next((col_map[c] for c in luganda_candidates 
                              if c in col_map), None)
            
            # Try reverse mapping (luganda -> english)
            if english_col is None and luganda_col is None:
                cols = list(col_map.values())
                if len(cols) >= 2:
                    # Assume first two columns are language pairs
                    english_col, luganda_col = cols[0], cols[1]
        
        if english_col is None or luganda_col is None:
            print(f"⚠️  Skipping {path}: Cannot detect language columns")
            return pd.DataFrame(columns=["english", "luganda"])
        
        # Rename and keep only these columns
        result = pd.DataFrame({
            "english": df[english_col].astype(str),
            "luganda": df[luganda_col].astype(str),
        })
        
        result["source"] = str(path.name)
        return result
        
    except Exception as e:
        print(f"⚠️  Error loading {path}: {e}")
        return pd.DataFrame(columns=["english", "luganda"])


def print_section(title: str, width: int = 80):
    """Print a formatted section header."""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)
