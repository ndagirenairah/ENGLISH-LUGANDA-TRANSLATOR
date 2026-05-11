"""
STAGE 5: FEATURE ENGINEERING
============================
Handles tokenization, embedding creation, and sequence preparation for transformers.
Converts text to model-ready tensors with attention masks and token type IDs.
"""

import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer
from torch.utils.data import Dataset
from pathlib import Path
import json


class TranslationDataset(Dataset):
    """
    PyTorch Dataset for translation task.
    """
    
    def __init__(self, english_texts, luganda_texts, tokenizer, max_length=512):
        self.english_texts = english_texts
        self.luganda_texts = luganda_texts
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.english_texts)
    
    def __getitem__(self, idx):
        en_text = self.english_texts[idx]
        lg_text = self.luganda_texts[idx]
        
        # Tokenize source (English)
        source = self.tokenizer(
            en_text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        
        # Tokenize target (Luganda)
        target = self.tokenizer(
            lg_text,
            max_length=self.max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        
        return {
            'input_ids': source['input_ids'].squeeze(0),
            'attention_mask': source['attention_mask'].squeeze(0),
            'labels': target['input_ids'].squeeze(0)
        }


class FeatureEngineer:
    """
    Handles feature engineering for translation model.
    """
    
    def __init__(self, model_name='Helsinki-NLP/opus-mt-en-mul'):
        """
        Initialize tokenizer.
        
        Args:
            model_name (str): HuggingFace model name for tokenizer
        """
        print(f"\n[FEATURE ENGINEERING] Loading tokenizer: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model_name = model_name
        print(f"  ✓ Tokenizer loaded (vocab size: {len(self.tokenizer)})")
    
    def tokenize_text(self, text, max_length=512):
        """
        Tokenize single text.
        
        Args:
            text (str): Input text
            max_length (int): Maximum sequence length
            
        Returns:
            dict: Tokenized output with input_ids, attention_mask
        """
        encoded = self.tokenizer(
            text,
            max_length=max_length,
            truncation=True,
            padding='max_length',
            return_tensors='pt'
        )
        
        return encoded
    
    def create_dataset(self, english_texts, luganda_texts, max_length=512):
        """
        Create PyTorch Dataset from texts.
        
        Args:
            english_texts (list): List of English sentences
            luganda_texts (list): List of Luganda sentences
            max_length (int): Maximum sequence length
            
        Returns:
            TranslationDataset: PyTorch Dataset object
        """
        dataset = TranslationDataset(
            english_texts,
            luganda_texts,
            self.tokenizer,
            max_length=max_length
        )
        return dataset
    
    def tokenize_dataset(self, df, max_length=512, batch_size=32):
        """
        Tokenize entire dataset.
        
        Args:
            df (pd.DataFrame): Dataset with 'english' and 'luganda' columns
            max_length (int): Maximum sequence length
            batch_size (int): Batch size for processing
            
        Returns:
            dict: Tokenized data with input_ids, attention_mask, labels
        """
        print(f"\n[TOKENIZATION] Processing {len(df):,} pairs...")
        print(f"  • Max length: {max_length}")
        print(f"  • Batch size: {batch_size}")
        
        all_input_ids = []
        all_attention_masks = []
        all_labels = []
        
        english_texts = df['english'].tolist()
        luganda_texts = df['luganda'].tolist()
        
        # Process in batches
        for i in range(0, len(df), batch_size):
            if i % (batch_size * 10) == 0:
                print(f"  • Progress: {i:,}/{len(df):,}")
            
            batch_en = english_texts[i:i+batch_size]
            batch_lg = luganda_texts[i:i+batch_size]
            
            # Tokenize source
            source = self.tokenizer(
                batch_en,
                max_length=max_length,
                truncation=True,
                padding='max_length',
                return_tensors='pt'
            )
            
            # Tokenize target
            target = self.tokenizer(
                batch_lg,
                max_length=max_length,
                truncation=True,
                padding='max_length',
                return_tensors='pt'
            )
            
            all_input_ids.extend(source['input_ids'].numpy())
            all_attention_masks.extend(source['attention_mask'].numpy())
            all_labels.extend(target['input_ids'].numpy())
        
        tokenized_data = {
            'input_ids': np.array(all_input_ids),
            'attention_mask': np.array(all_attention_masks),
            'labels': np.array(all_labels)
        }
        
        print(f"  ✓ Tokenization complete")
        print(f"    - input_ids shape: {tokenized_data['input_ids'].shape}")
        print(f"    - attention_mask shape: {tokenized_data['attention_mask'].shape}")
        print(f"    - labels shape: {tokenized_data['labels'].shape}")
        
        return tokenized_data
    
    def save_tokenized_features(self, tokenized_data, output_dir='data/tokenized'):
        """
        Save tokenized features as numpy files.
        
        Args:
            tokenized_data (dict): Tokenized data
            output_dir (str): Output directory
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"\n[SAVING] Writing tokenized features to {output_dir}/...")
        
        for key, value in tokenized_data.items():
            filepath = Path(output_dir) / f"{key}.npy"
            np.save(filepath, value)
            print(f"  ✓ {filepath}")
        
        # Save metadata
        metadata = {
            'model_name': self.model_name,
            'vocab_size': len(self.tokenizer),
            'input_ids_shape': tokenized_data['input_ids'].shape,
            'attention_mask_shape': tokenized_data['attention_mask'].shape,
            'labels_shape': tokenized_data['labels'].shape
        }
        
        metadata_path = Path(output_dir) / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  ✓ metadata.json")


def engineer_features(input_path, output_dir='data/tokenized', 
                     model_name='Helsinki-NLP/opus-mt-en-mul',
                     max_length=512):
    """
    Main feature engineering pipeline.
    
    Args:
        input_path (str): Path to preprocessed CSV
        output_dir (str): Output directory for tokenized features
        model_name (str): Model name for tokenizer
        max_length (int): Maximum sequence length
        
    Returns:
        dict: Tokenized data
    """
    print("=" * 80)
    print("STAGE 5: FEATURE ENGINEERING & TOKENIZATION")
    print("=" * 80)
    
    # Load data
    print(f"\n[LOADING] Reading from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"  ✓ Loaded {len(df):,} pairs")
    
    # Initialize feature engineer
    engineer = FeatureEngineer(model_name=model_name)
    
    # Tokenize
    tokenized_data = engineer.tokenize_dataset(df, max_length=max_length)
    
    # Save
    engineer.save_tokenized_features(tokenized_data, output_dir)
    
    print("\n" + "=" * 80)
    print("FEATURE ENGINEERING COMPLETE")
    print("=" * 80)
    
    return tokenized_data


if __name__ == "__main__":
    # Example usage
    try:
        tokenized_data = engineer_features("data/preprocessed_dataset.csv")
    except FileNotFoundError:
        print("Dataset not found. Run preprocessing.py first.")
