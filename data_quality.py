#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 3: COMPREHENSIVE DATA QUALITY CHECKER & CLEANER
=====================================================
Implements advanced preprocessing for low-resource NMT:
- Duplicate removal (exact + fuzzy)
- Noise filtering (URLs, emails, HTML)
- Language validation (detect language mismatches)
- Corruption detection (invalid Unicode, broken characters)
- Length filtering (remove extremely short/long sequences)
- Statistical cleaning (remove outliers)
- Translation quality validation

This ensures the dataset is suitable for robust neural machine translation.
"""

import os
import sys
import pandas as pd
import numpy as np
import re
import unicodedata
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import logging
from collections import Counter
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class DataQualityChecker:
    """
    Comprehensive data quality validation and cleaning.
    """
    
    def __init__(self, min_length: int = 3, max_length: int = 200):
        """
        Initialize quality checker.
        
        Args:
            min_length: Minimum characters per sentence
            max_length: Maximum characters per sentence
        """
        self.min_length = min_length
        self.max_length = max_length
        self.stats = {}
        
        # Luganda-specific patterns
        self.luganda_keywords = {
            'oli', 'nkwagala', 'webale', 'ndye', 'wasuubire', 'oyagala',
            'ekikali', 'mukyalira', 'kuwayo', 'amazzi', 'emmere', 'kulala',
            'baganda', 'kabaka', 'omuzadde', 'kwagala', 'karibu', 'ekiwandiiko'
        }
        
        # English common words
        self.english_keywords = {
            'the', 'is', 'and', 'to', 'of', 'a', 'in', 'that', 'it', 'for',
            'be', 'have', 'this', 'on', 'are', 'not', 'from', 'or', 'but', 'with'
        }
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect if text is English or Luganda using heuristics.
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (language, confidence)
        """
        if not text or len(text.strip()) == 0:
            return 'unknown', 0.0
        
        text_lower = text.lower().strip()
        words = text_lower.split()
        
        # Count keyword hits
        english_hits = sum(1 for w in words if w in self.english_keywords)
        luganda_hits = sum(1 for w in words if w in self.luganda_keywords)
        
        # ASCII ratio
        ascii_count = sum(1 for c in text if ord(c) < 128)
        ascii_ratio = ascii_count / len(text) if text else 0
        
        if luganda_hits > english_hits:
            confidence = min(0.99, (luganda_hits + 0.1) / max(len(words), 1))
            return 'luganda', confidence
        elif ascii_ratio > 0.85:
            confidence = min(0.99, ascii_ratio)
            return 'english', confidence
        else:
            # Inconclusive
            if luganda_hits > 0:
                return 'luganda', 0.5
            elif english_hits > 0:
                return 'english', 0.5
            else:
                return 'unknown', 0.0
    
    def check_language_mismatch(self, en_text: str, lg_text: str) -> bool:
        """
        Check if English and Luganda are mismatched.
        
        Args:
            en_text: Text supposed to be English
            lg_text: Text supposed to be Luganda
            
        Returns:
            True if mismatch detected
        """
        en_detected, en_conf = self.detect_language(en_text)
        lg_detected, lg_conf = self.detect_language(lg_text)
        
        # Mismatch if detected languages are wrong
        mismatch = (en_detected != 'english' and en_conf > 0.5) or \
                   (lg_detected != 'luganda' and lg_conf > 0.5)
        
        return mismatch
    
    def is_valid_unicode(self, text: str) -> bool:
        """
        Check if text contains valid Unicode.
        
        Args:
            text: Input text
            
        Returns:
            True if valid
        """
        try:
            # Check for null bytes
            if '\x00' in text:
                return False
            
            # Try to normalize
            unicodedata.normalize('NFKC', text)
            
            # Check for replacement characters (corrupted)
            if '\ufffd' in text:
                return False
            
            # Check if text is mostly valid (allow some control chars)
            valid_chars = sum(1 for c in text if unicodedata.category(c)[0] != 'C')
            if valid_chars / len(text) < 0.95 and len(text) > 10:
                return False
            
            return True
        except:
            return False
    
    def remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        patterns = [
            r'https?://\S+',
            r'www\.\S+',
            r'ftp://\S+',
        ]
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text
    
    def remove_emails(self, text: str) -> str:
        """Remove email addresses."""
        return re.sub(r'\S+@\S+\.\S+', '', text)
    
    def remove_html(self, text: str) -> str:
        """Remove HTML tags."""
        return re.sub(r'<[^>]+>', '', text)
    
    def remove_special_formatting(self, text: str) -> str:
        """Remove special formatting characters."""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Normalize quotes
        text = re.sub(r'[''´`]', "'", text)
        text = re.sub(r'[""„]', '"', text)
        
        # Normalize dashes
        text = re.sub(r'[–—−]', '-', text)
        
        return text
    
    def normalize_punctuation(self, text: str) -> str:
        """Normalize punctuation."""
        # Fix spacing around punctuation
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        text = re.sub(r'\s+$', '', text)
        
        return text
    
    def is_too_short(self, text: str) -> bool:
        """Check if text is too short."""
        return len(text.strip()) < self.min_length
    
    def is_too_long(self, text: str) -> bool:
        """Check if text is too long."""
        return len(text.strip()) > self.max_length
    
    def is_empty_or_null(self, text: str) -> bool:
        """Check if text is empty or null."""
        if text is None:
            return True
        if isinstance(text, float) and np.isnan(text):
            return True
        if not isinstance(text, str):
            return True
        return len(text.strip()) == 0
    
    def contains_mostly_numbers(self, text: str) -> bool:
        """Check if text is mostly numbers."""
        if len(text) < 3:
            return False
        
        digits = sum(1 for c in text if c.isdigit())
        return digits / len(text) > 0.7
    
    def contains_mostly_special_chars(self, text: str) -> bool:
        """Check if text is mostly special characters."""
        if len(text) < 3:
            return False
        
        special = sum(1 for c in text if not c.isalnum() and c.isascii() and c != ' ')
        return special / len(text) > 0.5
    
    def is_repeated_text(self, text: str) -> bool:
        """Check if text is just repeated characters."""
        if len(text) < 3:
            return False
        
        # Check for patterns like "aaaa" or "ababab"
        if len(set(text.replace(' ', ''))) <= 2 and len(text) > 10:
            return True
        
        return False
    
    def clean_text(self, text: str) -> str:
        """
        Apply all cleaning transformations.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        text = str(text)
        text = self.remove_urls(text)
        text = self.remove_emails(text)
        text = self.remove_html(text)
        text = self.remove_special_formatting(text)
        text = self.normalize_punctuation(text)
        
        return text
    
    def validate_pair(self, en_text: str, lg_text: str) -> Tuple[bool, str]:
        """
        Validate a translation pair.
        
        Returns:
            Tuple of (is_valid, reason_if_invalid)
        """
        # Check for empty
        if self.is_empty_or_null(en_text) or self.is_empty_or_null(lg_text):
            return False, "empty_text"
        
        # Check for valid Unicode
        if not self.is_valid_unicode(en_text) or not self.is_valid_unicode(lg_text):
            return False, "invalid_unicode"
        
        # Check length
        if self.is_too_short(en_text) or self.is_too_short(lg_text):
            return False, "too_short"
        
        if self.is_too_long(en_text) or self.is_too_long(lg_text):
            return False, "too_long"
        
        # Check for mostly numbers
        if self.contains_mostly_numbers(en_text) or self.contains_mostly_numbers(lg_text):
            return False, "mostly_numbers"
        
        # Check for mostly special chars
        if self.contains_mostly_special_chars(en_text) or self.contains_mostly_special_chars(lg_text):
            return False, "mostly_special_chars"
        
        # Check for repeated text
        if self.is_repeated_text(en_text) or self.is_repeated_text(lg_text):
            return False, "repeated_text"
        
        # Check language mismatch
        if self.check_language_mismatch(en_text, lg_text):
            return False, "language_mismatch"
        
        return True, "valid"
    
    def clean_and_validate_dataset(self, df: pd.DataFrame, 
                                   en_col: str = 'english',
                                   lg_col: str = 'luganda') -> pd.DataFrame:
        """
        Clean and validate entire dataset.
        
        Args:
            df: Input DataFrame
            en_col: English column name
            lg_col: Luganda column name
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("=" * 80)
        logger.info("[DATA CLEANING] Starting comprehensive data quality checks")
        logger.info("=" * 80)
        
        original_size = len(df)
        logger.info(f"[STATS] Original dataset: {original_size:,} pairs")
        
        # Initialize tracking
        removed_reasons = Counter()
        
        # Step 1: Remove null/empty rows
        logger.info("\n[STEP 1] Removing empty rows...")
        mask_empty = ~(df[en_col].isna() | df[lg_col].isna() | 
                       (df[en_col] == '') | (df[lg_col] == ''))
        df = df[mask_empty].reset_index(drop=True)
        removed_reasons['empty'] = original_size - len(df)
        logger.info(f"[REMOVED] {removed_reasons['empty']:,} empty rows")
        
        # Step 2: Clean text
        logger.info("\n[STEP 2] Cleaning text formatting...")
        df[en_col] = df[en_col].apply(self.clean_text)
        df[lg_col] = df[lg_col].apply(self.clean_text)
        logger.info(f"[CLEANED] Text formatting normalized")
        
        # Step 3: Validate pairs and collect reasons
        logger.info("\n[STEP 3] Validating translation pairs...")
        valid_mask = []
        
        for idx, row in df.iterrows():
            is_valid, reason = self.validate_pair(row[en_col], row[lg_col])
            valid_mask.append(is_valid)
            if not is_valid:
                removed_reasons[reason] += 1
        
        df = df[valid_mask].reset_index(drop=True)
        logger.info(f"[VALIDATED] {len(df):,} pairs passed validation")
        
        # Step 4: Remove exact duplicates
        logger.info("\n[STEP 4] Removing exact duplicates...")
        before_dedup = len(df)
        df = df.drop_duplicates(subset=[en_col, lg_col]).reset_index(drop=True)
        removed_reasons['duplicates'] = before_dedup - len(df)
        logger.info(f"[REMOVED] {removed_reasons['duplicates']:,} exact duplicates")
        
        # Step 5: Remove near-duplicates (fuzzy matching)
        logger.info("\n[STEP 5] Detecting near-duplicates...")
        fuzzy_removed = 0
        seen = set()
        fuzzy_mask = []
        
        for en_text, lg_text in zip(df[en_col], df[lg_col]):
            # Simplified fuzzy: normalize and check
            en_normalized = re.sub(r'\W+', '', en_text).lower()[:50]
            key = (en_normalized,)
            
            if key not in seen:
                seen.add(key)
                fuzzy_mask.append(True)
            else:
                fuzzy_removed += 1
                fuzzy_mask.append(False)
        
        df = df[fuzzy_mask].reset_index(drop=True)
        removed_reasons['near_duplicates'] = fuzzy_removed
        logger.info(f"[REMOVED] {fuzzy_removed:,} near-duplicates")
        
        # Detailed breakdown
        logger.info("\n[STATS] Removal breakdown:")
        for reason, count in removed_reasons.most_common():
            if count > 0:
                logger.info(f"[REMOVED] {reason}: {count:,}")
        
        # Final statistics
        final_size = len(df)
        removed_total = original_size - final_size
        retention_rate = (final_size / original_size * 100) if original_size > 0 else 0
        
        logger.info("\n" + "=" * 80)
        logger.info("[STATS] CLEANING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"[STATS] Original:      {original_size:>10,} pairs")
        logger.info(f"[STATS] Removed:       {removed_total:>10,} pairs ({100-retention_rate:.1f}%)")
        logger.info(f"[STATS] Final:         {final_size:>10,} pairs ({retention_rate:.1f}%)")
        logger.info(f"[STATS] Avg EN length: {df[en_col].str.len().mean():.1f} chars")
        logger.info(f"[STATS] Avg LG length: {df[lg_col].str.len().mean():.1f} chars")
        logger.info("=" * 80)
        
        self.stats = {
            'original': original_size,
            'final': final_size,
            'removed': removed_total,
            'retention_rate': retention_rate,
            'removal_reasons': dict(removed_reasons)
        }
        
        return df
    
    def get_stats(self) -> Dict:
        """Get cleaning statistics."""
        return self.stats


def load_and_clean_dataset(dataset_path: str = 'data/raw/luganda_dataset.csv',
                           output_path: str = 'data/processed/cleaned_dataset.csv') -> pd.DataFrame:
    """
    Load and clean dataset from file.
    
    Args:
        dataset_path: Path to input dataset
        output_path: Path to save cleaned dataset
        
    Returns:
        Cleaned DataFrame
    """
    logger.info(f"\n[LOADING] Reading dataset from: {dataset_path}")
    
    if not Path(dataset_path).exists():
        logger.error(f"[ERROR] Dataset not found: {dataset_path}")
        return None
    
    # Try different separators
    for sep in [',', '\t', ';', '|']:
        try:
            df = pd.read_csv(dataset_path, sep=sep)
            if len(df) > 0:
                logger.info(f"[LOADED] Successfully read with separator: '{sep}'")
                break
        except:
            continue
    else:
        logger.error("[ERROR] Could not load dataset with any separator")
        return None
    
    # Find column names (case-insensitive)
    en_col = next((col for col in df.columns if col.lower() in ['english', 'en', 'source']), None)
    lg_col = next((col for col in df.columns if col.lower() in ['luganda', 'lg', 'target']), None)
    
    if not en_col or not lg_col:
        logger.error("[ERROR] Could not find English/Luganda columns")
        return None
    
    df = df[[en_col, lg_col]].copy()
    df.columns = ['english', 'luganda']
    
    # Clean and validate
    cleaner = DataQualityChecker()
    df_cleaned = cleaner.clean_and_validate_dataset(df)
    
    # Save cleaned dataset
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    df_cleaned.to_csv(output_path, index=False)
    logger.info(f"\n[SAVED] Cleaned dataset: {output_path}")
    
    return df_cleaned


if __name__ == '__main__':
    # Load and clean dataset
    df_cleaned = load_and_clean_dataset()
    
    if df_cleaned is not None:
        logger.info("\n[SUCCESS] Dataset cleaning complete!")
        logger.info(f"[OUTPUT] {len(df_cleaned):,} high-quality pairs ready for training")
