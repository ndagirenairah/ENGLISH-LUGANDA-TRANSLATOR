#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ENHANCED TRAINING FOR AUTHENTIC LUGANDA TRANSLATION
======================================================

Features:
- 3-5 epoch training (configurable)
- Cultural dataset integration
- Mixed English-Luganda detection and removal
- Aggressive noise filtering
- Repeated sentence detection
- Better quality validation

Usage:
    python train_nllb_enhanced.py --epochs 5 --use-cultural True
"""

import os
import sys
import pandas as pd
import numpy as np
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    EarlyStoppingCallback
)
from datasets import Dataset, DatasetDict
from sacrebleu import corpus_bleu
import warnings

warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[TRAIN] %(message)s'
)
logger = logging.getLogger(__name__)

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class EnhancedLugandaTrainer:
    """Enhanced trainer for authentic Luganda translation."""
    
    def __init__(self, epochs: int = 3, use_cultural: bool = True):
        """
        Initialize trainer.
        
        Args:
            epochs: Number of training epochs (3-5 recommended)
            use_cultural: Include cultural dataset
        """
        self.epochs = max(3, min(5, epochs))
        self.use_cultural = use_cultural
        
        self.model_name = "facebook/nllb-200-distilled-600M"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_input_length = 256
        self.batch_size = 16 if self.device == "cuda" else 8
        
        logger.info(f"Device: {self.device}")
        logger.info(f"Training epochs: {self.epochs}")
        logger.info(f"Use cultural dataset: {self.use_cultural}")
    
    def load_and_clean_data(self) -> pd.DataFrame:
        """Load, clean, and enhance dataset."""
        logger.info("Loading dataset...")
        
        # Load existing data
        try:
            df = pd.read_csv("data/train_dataset.csv")
            logger.info(f"Loaded {len(df)} pairs from train_dataset.csv")
        except FileNotFoundError:
            logger.error("data/train_dataset.csv not found")
            raise
        
        # Add cultural dataset if enabled
        if self.use_cultural:
            logger.info("Adding cultural dataset...")
            try:
                from cultural_dataset_builder import CulturalDatasetBuilder
                cultural_df = CulturalDatasetBuilder.build_cultural_dataset()
                df = pd.concat([df, cultural_df], ignore_index=True)
                logger.info(f"Added {len(cultural_df)} cultural pairs")
                logger.info(f"Total after cultural: {len(df)} pairs")
            except Exception as e:
                logger.warning(f"Could not load cultural dataset: {e}")
        
        logger.info("Cleaning data...")
        
        # Remove rows with missing values
        df = df.dropna(subset=['english', 'luganda'])
        logger.info(f"After removing nulls: {len(df)}")
        
        # Remove exact duplicates
        df = df.drop_duplicates(subset=['english', 'luganda'])
        logger.info(f"After removing exact duplicates: {len(df)}")
        
        # Remove very short sentences
        df = df[
            (df['english'].str.len() > 3) &
            (df['luganda'].str.len() > 3)
        ]
        logger.info(f"After length filtering: {len(df)}")
        
        # Remove very long sentences
        df = df[
            (df['english'].str.len() < 200) &
            (df['luganda'].str.len() < 200)
        ]
        logger.info(f"After max length filtering: {len(df)}")
        
        # Remove mixed language pairs
        df = df[~df.apply(self._has_mixed_language, axis=1)]
        logger.info(f"After removing mixed language: {len(df)}")
        
        # Remove highly repeated sentences
        df = df[~df.apply(self._is_overly_repeated, axis=1)]
        logger.info(f"After removing repeated sentences: {len(df)}")
        
        # Remove noisy translations
        df = df[~df.apply(self._is_noisy, axis=1)]
        logger.info(f"After noise filtering: {len(df)}")
        
        return df
    
    @staticmethod
    def _has_mixed_language(row) -> bool:
        """Check if sentence has mixed English-Luganda."""
        english_text = str(row.get('english', '')).lower()
        luganda_text = str(row.get('luganda', '')).lower()
        
        # Check if English has too much Luganda-like content
        luganda_keywords = {
            'oli', 'nkwagala', 'webale', 'wasuubire', 'amazzi', 'emmere',
            'kulala', 'baganda', 'kabaka', 'kwagala', 'karibu'
        }
        
        english_luganda_count = sum(
            1 for word in english_text.split() if word in luganda_keywords
        )
        
        # Check if Luganda has too much English
        if english_luganda_count > len(english_text.split()) * 0.2:
            return True
        
        # Check if Luganda contains mostly English-like characters
        ascii_in_luganda = sum(1 for c in luganda_text if ord(c) < 128)
        if ascii_in_luganda / len(luganda_text) > 0.9:
            return True
        
        return False
    
    @staticmethod
    def _is_overly_repeated(row) -> bool:
        """Check if sentence has excessive repetition."""
        english_text = str(row.get('english', ''))
        luganda_text = str(row.get('luganda', ''))
        
        # Check for repeated words
        english_words = english_text.lower().split()
        luganda_words = luganda_text.lower().split()
        
        if len(english_words) > 0:
            english_unique = len(set(english_words)) / len(english_words)
            if english_unique < 0.4:  # Less than 40% unique words
                return True
        
        if len(luganda_words) > 0:
            luganda_unique = len(set(luganda_words)) / len(luganda_words)
            if luganda_unique < 0.4:
                return True
        
        return False
    
    @staticmethod
    def _is_noisy(row) -> bool:
        """Check if sentence contains noise."""
        english_text = str(row.get('english', ''))
        luganda_text = str(row.get('luganda', ''))
        
        # Check for URLs, emails
        if any(pattern in english_text.lower() for pattern in ['http', 'www', '@']):
            return True
        if any(pattern in luganda_text.lower() for pattern in ['http', 'www', '@']):
            return True
        
        # Check for too many numbers
        english_digits = sum(1 for c in english_text if c.isdigit())
        luganda_digits = sum(1 for c in luganda_text if c.isdigit())
        
        if english_digits / len(english_text) > 0.2:
            return True
        if luganda_digits / len(luganda_text) > 0.2:
            return True
        
        # Check for too many special characters
        special_chars = '!@#$%^&*()[]{}|;:<>?/\\'
        english_special = sum(1 for c in english_text if c in special_chars)
        luganda_special = sum(1 for c in luganda_text if c in special_chars)
        
        if english_special / len(english_text) > 0.1:
            return True
        if luganda_special / len(luganda_text) > 0.1:
            return True
        
        return False
    
    def prepare_dataset(self, df: pd.DataFrame) -> DatasetDict:
        """Prepare dataset for training."""
        logger.info("Preparing dataset...")
        
        # Split into train/val/test: 80/10/10
        train_df = df.sample(frac=0.8, random_state=42)
        remaining_df = df.drop(train_df.index)
        val_df = remaining_df.sample(frac=0.5, random_state=42)
        test_df = remaining_df.drop(val_df.index)
        
        logger.info(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
        
        # Convert to datasets
        train_dataset = Dataset.from_pandas(train_df[['english', 'luganda']])
        val_dataset = Dataset.from_pandas(val_df[['english', 'luganda']])
        test_dataset = Dataset.from_pandas(test_df[['english', 'luganda']])
        
        # Tokenize
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        def preprocess_function(examples):
            inputs = examples['english']
            targets = examples['luganda']
            
            model_inputs = tokenizer(
                inputs,
                max_length=self.max_input_length,
                truncation=True,
                padding=True,
                return_tensors=None
            )
            
            labels = tokenizer(
                targets,
                max_length=self.max_input_length,
                truncation=True,
                padding=True,
                return_tensors=None
            )
            
            model_inputs['labels'] = labels['input_ids']
            
            return model_inputs
        
        train_dataset = train_dataset.map(
            preprocess_function,
            batched=True,
            remove_columns=['english', 'luganda']
        )
        val_dataset = val_dataset.map(
            preprocess_function,
            batched=True,
            remove_columns=['english', 'luganda']
        )
        test_dataset = test_dataset.map(
            preprocess_function,
            batched=True,
            remove_columns=['english', 'luganda']
        )
        
        return DatasetDict(
            train=train_dataset,
            validation=val_dataset,
            test=test_dataset
        )
    
    def train(self):
        """Run training pipeline."""
        # Load and clean data
        df = self.load_and_clean_data()
        
        # Prepare dataset
        dataset_dict = self.prepare_dataset(df)
        
        # Load model and tokenizer
        logger.info(f"Loading model: {self.model_name}")
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
        # Training arguments
        training_args = Seq2SeqTrainingArguments(
            output_dir="models/trained_nllb_enhanced",
            num_train_epochs=self.epochs,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
            weight_decay=0.01,
            gradient_accumulation_steps=2,
            gradient_checkpointing=True,
            learning_rate=1e-4,
            warmup_steps=500,
            max_grad_norm=1.0,
            fp16=True if self.device == "cuda" else False,
            logging_steps=100,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            save_total_limit=3,
            seed=42,
        )
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            tokenizer,
            model=model,
            padding=True,
            max_length=self.max_input_length
        )
        
        # Trainer
        trainer = Seq2SeqTrainer(
            model=model,
            args=training_args,
            train_dataset=dataset_dict['train'],
            eval_dataset=dataset_dict['validation'],
            data_collator=data_collator,
            tokenizer=tokenizer,
            callbacks=[
                EarlyStoppingCallback(
                    early_stopping_patience=3,
                    early_stopping_threshold=0.0001
                )
            ]
        )
        
        # Train
        logger.info(f"Starting training for {self.epochs} epochs...")
        trainer.train()
        
        # Save
        logger.info("Saving model...")
        trainer.save_model("models/trained_nllb_enhanced/final")
        
        logger.info("Training complete!")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Enhanced Luganda Translation Training')
    parser.add_argument('--epochs', type=int, default=3, help='Number of training epochs (3-5)')
    parser.add_argument('--use-cultural', type=lambda x: x.lower() == 'true', default=True,
                       help='Include cultural dataset')
    
    args = parser.parse_args()
    
    trainer = EnhancedLugandaTrainer(
        epochs=args.epochs,
        use_cultural=args.use_cultural
    )
    trainer.train()


if __name__ == "__main__":
    main()
