"""
STAGE 4: DATA CLEANING & PREPROCESSING
======================================
Cleans, normalizes, and tokenizes text data.
Handles text normalization, punctuation removal, and lowercasing.
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class TextPreprocessor:
    """
    Handles text cleaning, normalization, and preprocessing.
    """
    
    def __init__(self, language='english'):
        self.language = language
        self.stop_words = set(stopwords.words(language)) if language in stopwords.fileids() else set()
    
    def lowercase(self, text):
        """Convert to lowercase."""
        return text.lower()
    
    def remove_urls(self, text):
        """Remove URLs."""
        url_pattern = r'https?://\S+|www\.\S+'
        return re.sub(url_pattern, '', text)
    
    def remove_emails(self, text):
        """Remove email addresses."""
        email_pattern = r'\S+@\S+'
        return re.sub(email_pattern, '', text)
    
    def remove_special_chars(self, text, keep_punctuation=True):
        """Remove special characters, optionally keeping punctuation."""
        if keep_punctuation:
            # Keep letters, numbers, punctuation, and spaces
            text = re.sub(r'[^\w\s\.\,\!\?\-\']', '', text)
        else:
            # Remove all non-alphanumeric except spaces
            text = re.sub(r'[^\w\s]', '', text)
        return text
    
    def normalize_whitespace(self, text):
        """Normalize whitespace (remove extra spaces)."""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single
        return text
    
    def remove_accents(self, text):
        """Remove accents from text."""
        import unicodedata
        return ''.join(c for c in unicodedata.normalize('NFD', text)
                      if unicodedata.category(c) != 'Mn')
    
    def tokenize(self, text):
        """Tokenize text into words."""
        return word_tokenize(text)
    
    def remove_stopwords(self, tokens):
        """Remove stopwords from tokens."""
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def clean_text(self, text, remove_stopwords=False, keep_punctuation=True):
        """
        Complete text cleaning pipeline.
        
        Args:
            text (str): Input text
            remove_stopwords (bool): Whether to remove stopwords
            keep_punctuation (bool): Whether to keep punctuation
            
        Returns:
            str: Cleaned text
        """
        # Step 1: Lowercase
        text = self.lowercase(text)
        
        # Step 2: Remove URLs and emails
        text = self.remove_urls(text)
        text = self.remove_emails(text)
        
        # Step 3: Remove special characters
        text = self.remove_special_chars(text, keep_punctuation=keep_punctuation)
        
        # Step 4: Remove accents
        text = self.remove_accents(text)
        
        # Step 5: Normalize whitespace
        text = self.normalize_whitespace(text)
        
        # Step 6: Remove stopwords (optional)
        if remove_stopwords:
            tokens = self.tokenize(text)
            tokens = self.remove_stopwords(tokens)
            text = ' '.join(tokens)
        
        return text


class DataPreprocessor:
    """
    Preprocesses entire dataset.
    """
    
    def __init__(self, df):
        self.df = df.copy()
        self.en_preprocessor = TextPreprocessor(language='english')
        self.lg_preprocessor = TextPreprocessor(language='english')  # Luganda stopwords not in NLTK
    
    def preprocess_dataset(self, remove_stopwords=False):
        """
        Preprocess entire dataset.
        
        Args:
            remove_stopwords (bool): Whether to remove English stopwords
            
        Returns:
            pd.DataFrame: Preprocessed dataframe
        """
        print("\n[PREPROCESSING] Cleaning and normalizing text...")
        
        original_count = len(self.df)
        
        # Clean English text
        print("  • Cleaning English text...")
        self.df['english'] = self.df['english'].apply(
            lambda x: self.en_preprocessor.clean_text(x, remove_stopwords=remove_stopwords)
        )
        
        # Clean Luganda text
        print("  • Cleaning Luganda text...")
        self.df['luganda'] = self.df['luganda'].apply(
            lambda x: self.lg_preprocessor.clean_text(x, remove_stopwords=False, keep_punctuation=True)
        )
        
        # Remove empty strings
        self.df = self.df[(self.df['english'].str.strip() != '') & (self.df['luganda'].str.strip() != '')]
        removed = original_count - len(self.df)
        
        if removed > 0:
            print(f"  • Removed {removed} empty translations")
        
        print(f"  ✓ Preprocessing complete: {len(self.df):,} valid pairs")
        
        return self.df
    
    def save_preprocessed(self, output_path="data/preprocessed_dataset.csv"):
        """Save preprocessed dataset."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(output_path, index=False)
        print(f"  ✓ Saved preprocessed data to: {output_path}")
        return output_path


def preprocess_data(input_path, output_path="data/preprocessed_dataset.csv", remove_stopwords=False):
    """
    Main preprocessing pipeline.
    
    Args:
        input_path (str): Path to input CSV
        output_path (str): Path to save preprocessed CSV
        remove_stopwords (bool): Whether to remove stopwords
        
    Returns:
        pd.DataFrame: Preprocessed dataframe
    """
    print("=" * 80)
    print("STAGE 4: DATA CLEANING & PREPROCESSING")
    print("=" * 80)
    
    # Load data
    print(f"\n[LOADING] Reading from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"  ✓ Loaded {len(df):,} pairs")
    
    # Preprocess
    preprocessor = DataPreprocessor(df)
    df_clean = preprocessor.preprocess_dataset(remove_stopwords=remove_stopwords)
    
    # Save
    preprocessor.save_preprocessed(output_path)
    
    print("\n" + "=" * 80)
    print("PREPROCESSING COMPLETE")
    print("=" * 80)
    
    return df_clean


if __name__ == "__main__":
    # Example usage
    try:
        df = preprocess_data("data/train_dataset.csv")
        print(f"\nSample preprocessed pairs:")
        for idx in range(min(3, len(df))):
            print(f"  EN: {df['english'].iloc[idx]}")
            print(f"  LG: {df['luganda'].iloc[idx]}")
            print()
    except FileNotFoundError:
        print("Dataset not found. Run data_collection.py first.")
