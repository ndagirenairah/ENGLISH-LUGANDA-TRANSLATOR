#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
STEP 2 & 5: PRODUCTION-GRADE NLLB-200 TRAINING PIPELINE
========================================================
Implements professional neural machine translation training with:
- NLLB-200 distilled 600M (trained on 200+ languages including Luganda)
- Proper training best practices (early stopping, dropout, weight decay)
- Mixed precision training (FP16) for memory efficiency
- Gradient accumulation for better convergence
- Learning rate scheduling with warmup
- Validation BLEU monitoring
- Checkpoint management
- Comprehensive logging

This pipeline is optimized for low-resource Luganda translation.
"""

import os
import sys
import json
import pandas as pd
import numpy as np
import torch
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import logging
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# HuggingFace imports
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
    EarlyStoppingCallback,
    EvalPrediction
)
from datasets import Dataset, DatasetDict
from sacrebleu import corpus_bleu

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


class NLLB200Trainer:
    """
    Professional trainer for NLLB-200 translation models.
    """
    
    # NLLB-200 language codes
    LANGUAGE_CODES = {
        'english': 'eng_Latn',
        'luganda': 'lug_Latn',
    }
    
    def __init__(self, 
                 model_name: str = 'facebook/nllb-200-distilled-600M',
                 output_dir: str = 'models/nllb_trained'):
        """
        Initialize trainer.
        
        Args:
            model_name: HuggingFace model identifier
            output_dir: Directory to save checkpoints
        """
        logger.info("=" * 80)
        logger.info("[TRAINER] Initializing NLLB-200 Trainer")
        logger.info("=" * 80)
        
        self.model_name = model_name
        self.output_dir = output_dir
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        logger.info(f"\n[CONFIG] Model: {model_name}")
        logger.info(f"[CONFIG] Device: {self.device.upper()}")
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Load model and tokenizer
        logger.info("\n[LOADING] Tokenizer and Model...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        logger.info(f"[LOADED] Model parameters: {self.model.num_parameters():,}")
        logger.info(f"[LOADED] Tokenizer vocab: {len(self.tokenizer):,}")
        
        self.model.to(self.device)
    
    def preprocess_function(self, examples: Dict, max_length: int = 256):
        """
        Tokenize inputs and targets for NLLB-200.
        
        Args:
            examples: Dict with 'english' and 'luganda' keys
            max_length: Maximum sequence length
            
        Returns:
            Dict with tokenized inputs and labels
        """
        # NLLB-200 requires language tokens
        en_lang_token = self.LANGUAGE_CODES['english']
        lg_lang_token = self.LANGUAGE_CODES['luganda']
        
        # Set language token for target
        self.tokenizer.tgt_lang = lg_lang_token
        
        # Tokenize inputs (English -> Luganda)
        model_inputs = self.tokenizer(
            examples['english'],
            max_length=max_length,
            truncation=True,
            padding='max_length',
            return_tensors=None
        )
        
        # Tokenize targets (Luganda)
        labels = self.tokenizer(
            examples['luganda'],
            max_length=max_length,
            truncation=True,
            padding='max_length',
            return_tensors=None
        )
        
        model_inputs['labels'] = labels['input_ids']
        
        return model_inputs
    
    def prepare_datasets(self,
                        train_df: pd.DataFrame,
                        val_df: pd.DataFrame,
                        test_df: Optional[pd.DataFrame] = None,
                        max_length: int = 256) -> Tuple[Dataset, Dataset, Optional[Dataset]]:
        """
        Convert DataFrames to HuggingFace Datasets.
        
        Args:
            train_df: Training DataFrame
            val_df: Validation DataFrame
            test_df: Test DataFrame (optional)
            max_length: Maximum sequence length
            
        Returns:
            Tuple of (train_dataset, val_dataset, test_dataset)
        """
        logger.info("\n[DATASETS] Preparing datasets...")
        logger.info(f"[DATASETS] Train: {len(train_df):,} samples")
        logger.info(f"[DATASETS] Val:   {len(val_df):,} samples")
        if test_df is not None:
            logger.info(f"[DATASETS] Test:  {len(test_df):,} samples")
        
        # Create HF datasets
        train_dataset = Dataset.from_pandas(train_df[['english', 'luganda']])
        val_dataset = Dataset.from_pandas(val_df[['english', 'luganda']])
        test_dataset = Dataset.from_pandas(test_df[['english', 'luganda']]) if test_df is not None else None
        
        # Tokenize
        logger.info("\n[TOKENIZE] Tokenizing datasets (this may take a while)...")
        
        preprocess_lambda = lambda x: self.preprocess_function(x, max_length)
        
        train_dataset = train_dataset.map(
            preprocess_lambda,
            batched=True,
            remove_columns=['english', 'luganda'],
            desc="Tokenizing train"
        )
        
        val_dataset = val_dataset.map(
            preprocess_lambda,
            batched=True,
            remove_columns=['english', 'luganda'],
            desc="Tokenizing validation"
        )
        
        if test_dataset is not None:
            test_dataset = test_dataset.map(
                preprocess_lambda,
                batched=True,
                remove_columns=['english', 'luganda'],
                desc="Tokenizing test"
            )
        
        logger.info("[TOKENIZE] Tokenization complete")
        
        return train_dataset, val_dataset, test_dataset
    
    def compute_metrics(self, eval_pred: EvalPrediction) -> Dict[str, float]:
        """
        Compute BLEU score for validation.
        
        Args:
            eval_pred: Predictions and labels
            
        Returns:
            Dict with BLEU score
        """
        predictions, labels = eval_pred
        
        # Decode predictions and labels
        if isinstance(predictions, tuple):
            predictions = predictions[0]
        
        # Replace -100 (padding) with pad token id
        predictions = np.where(
            predictions != -100,
            predictions,
            self.tokenizer.pad_token_id
        )
        labels = np.where(
            labels != -100,
            labels,
            self.tokenizer.pad_token_id
        )
        
        # Decode
        decoded_preds = self.tokenizer.batch_decode(
            predictions,
            skip_special_tokens=True
        )
        decoded_labels = self.tokenizer.batch_decode(
            labels,
            skip_special_tokens=True
        )
        
        # Compute BLEU
        bleu = corpus_bleu(decoded_preds, [[ref] for ref in decoded_labels])
        
        return {
            'bleu': bleu.score,
            'gen_len': np.mean([len(x.split()) for x in decoded_preds]),
        }
    
    def train(self,
              train_df: pd.DataFrame,
              val_df: pd.DataFrame,
              test_df: Optional[pd.DataFrame] = None,
              num_epochs: int = 10,
              batch_size: int = 16,
              learning_rate: float = 1e-4,
              warmup_steps: int = 500,
              max_grad_norm: float = 1.0,
              weight_decay: float = 0.01,
              early_stopping_patience: int = 3) -> Dict:
        """
        Train the model.
        
        Args:
            train_df: Training DataFrame
            val_df: Validation DataFrame
            test_df: Test DataFrame (optional)
            num_epochs: Number of training epochs
            batch_size: Batch size
            learning_rate: Learning rate
            warmup_steps: Warmup steps
            max_grad_norm: Maximum gradient norm (clipping)
            weight_decay: Weight decay for regularization
            early_stopping_patience: Early stopping patience
            
        Returns:
            Training results dict
        """
        logger.info("=" * 80)
        logger.info("[TRAIN] Starting model training")
        logger.info("=" * 80)
        
        # Prepare datasets
        train_dataset, val_dataset, test_dataset = self.prepare_datasets(
            train_df, val_df, test_df
        )
        
        # Training arguments with all best practices
        training_args = Seq2SeqTrainingArguments(
            output_dir=self.output_dir,
            
            # Training parameters
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            gradient_accumulation_steps=2,
            learning_rate=learning_rate,
            warmup_steps=warmup_steps,
            max_grad_norm=max_grad_norm,
            weight_decay=weight_decay,
            
            # Optimization
            optim='adamw_torch',
            lr_scheduler_type='linear',
            label_smoothing_factor=0.1,
            
            # Evaluation
            evaluation_strategy='epoch',
            save_strategy='epoch',
            load_best_model_at_end=True,
            metric_for_best_model='bleu',
            greater_is_better=True,
            
            # Logging
            logging_steps=100,
            logging_strategy='steps',
            log_level='info',
            
            # Optimization flags
            fp16=torch.cuda.is_available(),  # Mixed precision if GPU available
            fp16_opt_level='O2',
            
            # Generation
            predict_with_generate=True,
            generation_max_length=256,
            
            # Misc
            seed=42,
            dataloader_num_workers=0,
            remove_unused_columns=False,
            report_to=['tensorboard']
        )
        
        logger.info("\n[CONFIG] Training Arguments:")
        logger.info(f"  Epochs:        {num_epochs}")
        logger.info(f"  Batch size:    {batch_size}")
        logger.info(f"  Learning rate: {learning_rate}")
        logger.info(f"  Warmup steps:  {warmup_steps}")
        logger.info(f"  Max grad norm: {max_grad_norm}")
        logger.info(f"  Weight decay:  {weight_decay}")
        logger.info(f"  FP16 enabled:  {training_args.fp16}")
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            self.tokenizer,
            model=self.model,
            padding=True,
            max_length=256
        )
        
        # Early stopping callback
        early_stopping = EarlyStoppingCallback(
            early_stopping_patience=early_stopping_patience,
            early_stopping_threshold=0.0
        )
        
        # Trainer
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            data_collator=data_collator,
            tokenizer=self.tokenizer,
            compute_metrics=self.compute_metrics,
            callbacks=[early_stopping]
        )
        
        # Train
        logger.info("\n[TRAIN] Starting training...")
        train_result = trainer.train()
        
        logger.info("\n[TRAIN] Training complete!")
        logger.info(f"[TRAIN] Final loss: {train_result.training_loss:.4f}")
        
        # Evaluate on test set if provided
        if test_dataset is not None:
            logger.info("\n[EVAL] Evaluating on test set...")
            eval_results = trainer.evaluate(test_dataset)
            
            logger.info("\n[EVAL] Test Results:")
            for key, value in eval_results.items():
                logger.info(f"[EVAL] {key}: {value:.4f}")
        
        # Save model
        logger.info(f"\n[SAVE] Saving model to: {self.output_dir}")
        trainer.save_model(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        
        logger.info("[SUCCESS] Model saved successfully!")
        
        return {
            'training_loss': train_result.training_loss,
            'output_dir': self.output_dir,
            'model_params': self.model.num_parameters()
        }


def load_and_split_data(input_path: str = 'data/processed/cleaned_dataset.csv',
                       train_ratio: float = 0.8,
                       val_ratio: float = 0.1) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load and split dataset.
    
    Args:
        input_path: Path to cleaned dataset
        train_ratio: Proportion for training
        val_ratio: Proportion for validation
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    logger.info(f"\n[LOAD] Loading dataset from: {input_path}")
    
    if not Path(input_path).exists():
        logger.error(f"[ERROR] Dataset not found: {input_path}")
        raise FileNotFoundError(f"Dataset not found: {input_path}")
    
    df = pd.read_csv(input_path)
    logger.info(f"[LOAD] Loaded {len(df):,} samples")
    
    # Shuffle
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    # Split
    test_ratio = 1.0 - train_ratio - val_ratio
    
    train_size = int(len(df) * train_ratio)
    val_size = int(len(df) * val_ratio)
    
    train_df = df[:train_size]
    val_df = df[train_size:train_size + val_size]
    test_df = df[train_size + val_size:]
    
    logger.info(f"\n[SPLIT] Train: {len(train_df):,} ({train_ratio*100:.0f}%)")
    logger.info(f"[SPLIT] Val:   {len(val_df):,} ({val_ratio*100:.0f}%)")
    logger.info(f"[SPLIT] Test:  {len(test_df):,} ({test_ratio*100:.0f}%)")
    
    return train_df, val_df, test_df


def main():
    """Main training pipeline."""
    logger.info("=" * 80)
    logger.info("[PIPELINE] NLLB-200 ENGLISH-LUGANDA TRAINING PIPELINE")
    logger.info("=" * 80)
    
    # Load data
    try:
        train_df, val_df, test_df = load_and_split_data()
    except FileNotFoundError:
        logger.error("\n[ERROR] Please run data_quality.py first to prepare datasets")
        sys.exit(1)
    
    # Initialize trainer
    trainer = NLLB200Trainer(
        model_name='facebook/nllb-200-distilled-600M',
        output_dir='models/nllb_trained'
    )
    
    # Train
    results = trainer.train(
        train_df=train_df,
        val_df=val_df,
        test_df=test_df,
        num_epochs=10,
        batch_size=16,
        learning_rate=1e-4,
        warmup_steps=500,
        max_grad_norm=1.0,
        weight_decay=0.01,
        early_stopping_patience=3
    )
    
    logger.info("\n" + "=" * 80)
    logger.info("[SUCCESS] TRAINING PIPELINE COMPLETE")
    logger.info("=" * 80)
    logger.info(f"[OUTPUT] Model: {results['output_dir']}")
    logger.info(f"[OUTPUT] Parameters: {results['model_params']:,}")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
