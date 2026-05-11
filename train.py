"""
STAGE 6A: MODEL TRAINING
========================
Fine-tunes MarianMT model for English-Luganda translation.
Implements proper ML techniques: regularization, learning rate scheduling, early stopping.
"""

import torch
import pandas as pd
import numpy as np
from pathlib import Path
from transformers import (
    AutoTokenizer,
    MarianMTModel,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    DataCollatorForSeq2Seq
)
from datasets import Dataset, DatasetDict
import json
from datetime import datetime


def normalize_translation_frame(data):
    """Return a DataFrame with english and luganda columns."""
    if isinstance(data, pd.DataFrame):
        if {'english', 'luganda'}.issubset(data.columns):
            return data[['english', 'luganda']].copy()
        if 'translation' in data.columns:
            english_values = []
            luganda_values = []
            for item in data['translation']:
                if isinstance(item, dict):
                    english_values.append(item.get('eng') or item.get('english') or item.get('src') or '')
                    luganda_values.append(item.get('lug') or item.get('luganda') or item.get('tgt') or '')
                else:
                    english_values.append('')
                    luganda_values.append('')
            return pd.DataFrame({'english': english_values, 'luganda': luganda_values})

    if hasattr(data, 'to_pandas'):
        return normalize_translation_frame(data.to_pandas())

    if hasattr(data, 'column_names') and 'translation' in getattr(data, 'column_names', []):
        rows = []
        for item in data['translation']:
            if isinstance(item, dict):
                rows.append({
                    'english': item.get('eng') or item.get('english') or item.get('src') or '',
                    'luganda': item.get('lug') or item.get('luganda') or item.get('tgt') or ''
                })
        return pd.DataFrame(rows)

    raise ValueError("Unsupported dataset format. Expected english/luganda columns or translation entries.")


class TranslationModelTrainer:
    """
    Trainer for MarianMT translation model.
    """
    
    def __init__(self, model_name='Helsinki-NLP/opus-mt-en-mul', 
                 output_dir='models/trained_model_cpu'):
        """
        Initialize trainer.
        
        Args:
            model_name (str): HuggingFace model name
            output_dir (str): Directory to save checkpoints
        """
        print(f"\n[MODEL TRAINING] Initializing trainer")
        print(f"  • Model: {model_name}")
        print(f"  • Output: {output_dir}")
        
        self.model_name = model_name
        self.output_dir = output_dir
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
        
        print(f"  ✓ Model loaded (parameters: {self.model.num_parameters():,})")
    
    def prepare_dataset_for_training(self, train_df, val_df, test_df=None, max_length=128):
        """
        Convert DataFrames to HuggingFace Datasets for training.
        
        Args:
            train_df (pd.DataFrame): Training data
            val_df (pd.DataFrame): Validation data
            test_df (pd.DataFrame): Test data (optional)
            max_length (int): Maximum sequence length
            
        Returns:
            DatasetDict: Train, validation, test datasets
        """
        print(f"\n[DATASET PREPARATION]")
        print(f"  • Train samples: {len(train_df):,}")
        print(f"  • Validation samples: {len(val_df):,}")
        if test_df is not None:
            print(f"  • Test samples: {len(test_df):,}")
        
        def preprocess_function(examples):
            """Tokenize inputs and targets."""
            inputs = [ex for ex in examples['english']]
            targets = [ex for ex in examples['luganda']]
            
            model_inputs = self.tokenizer(
                inputs,
                max_length=max_length,
                truncation=True,
                padding='max_length'
            )
            
            labels = self.tokenizer(
                targets,
                max_length=max_length,
                truncation=True,
                padding='max_length'
            )
            
            model_inputs['labels'] = labels['input_ids']
            return model_inputs
        
        # Create HF Datasets
        train_df = normalize_translation_frame(train_df)
        val_df = normalize_translation_frame(val_df)
        train_dataset = Dataset.from_pandas(train_df[['english', 'luganda']])
        val_dataset = Dataset.from_pandas(val_df[['english', 'luganda']])
        
        # Tokenize
        print("  • Tokenizing train dataset...")
        train_dataset = train_dataset.map(preprocess_function, batched=True)
        
        print("  • Tokenizing validation dataset...")
        val_dataset = val_dataset.map(preprocess_function, batched=True)
        
        dataset_dict = DatasetDict({
            'train': train_dataset,
            'validation': val_dataset
        })
        
        if test_df is not None:
            test_df = normalize_translation_frame(test_df)
            test_dataset = Dataset.from_pandas(test_df[['english', 'luganda']])
            print("  • Tokenizing test dataset...")
            test_dataset = test_dataset.map(preprocess_function, batched=True)
            dataset_dict['test'] = test_dataset
        
        print("  ✓ Dataset preparation complete")
        
        return dataset_dict
    
    def train(self, train_df, val_df, test_df=None,
              epochs=3, batch_size=2, learning_rate=1e-4,
              weight_decay=0.01, warmup_steps=500,
              max_grad_norm=1.0, save_strategy='epoch', max_length=128):
        """
        Train the model.
        
        Args:
            train_df (pd.DataFrame): Training data
            val_df (pd.DataFrame): Validation data
            test_df (pd.DataFrame): Test data (optional)
            epochs (int): Number of training epochs
            batch_size (int): Batch size
            learning_rate (float): Learning rate
            weight_decay (float): L2 regularization
            warmup_steps (int): Warmup steps
            max_grad_norm (float): Gradient clipping
            save_strategy (str): Save strategy ('epoch' or 'steps')
        """
        print("\n" + "=" * 80)
        print("STAGE 6A: MODEL TRAINING")
        print("=" * 80)
        
        # Prepare datasets
        datasets = self.prepare_dataset_for_training(train_df, val_df, test_df, max_length=max_length)
        
        # Training arguments with Lecture 3 concepts
        training_args = Seq2SeqTrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            weight_decay=weight_decay,
            warmup_steps=warmup_steps,
            max_grad_norm=max_grad_norm,
            lr_scheduler_type='cosine',
            logging_steps=100,
            eval_strategy='epoch',
            save_strategy=save_strategy,
            load_best_model_at_end=True,
            metric_for_best_model='loss',
            greater_is_better=False,
            seed=42,
            fp16=torch.cuda.is_available()  # Mixed precision if GPU available
        )
        
        print(f"\n[TRAINING CONFIGURATION]")
        print(f"  • Epochs: {epochs}")
        print(f"  • Batch size: {batch_size}")
        print(f"  • Learning rate: {learning_rate}")
        print(f"  • Weight decay (L2): {weight_decay}")
        print(f"  • Warmup steps: {warmup_steps}")
        print(f"  • Max grad norm: {max_grad_norm}")
        print(f"  • LR scheduler: cosine")
        print(f"  • Device: {'GPU (FP16)' if torch.cuda.is_available() else 'CPU'}")
        
        # Data collator
        data_collator = DataCollatorForSeq2Seq(
            self.tokenizer,
            model=self.model,
            label_pad_token_id=-100
        )
        
        # Trainer
        trainer = Seq2SeqTrainer(
            model=self.model,
            args=training_args,
            train_dataset=datasets['train'],
            eval_dataset=datasets['validation'],
            processing_class=self.tokenizer,
            data_collator=data_collator
        )
        
        # Train
        print("\n[TRAINING STARTED]")
        train_result = trainer.train()
        
        print("\n[TRAINING RESULTS]")
        print(f"  • Final loss: {train_result.training_loss:.4f}")
        
        # Save model
        print(f"\n[SAVING MODEL] to {self.output_dir}")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), Path(self.output_dir) / 'pytorch_model.bin')
        self.model.config.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)
        
        # Save training history
        history = {
            'timestamp': datetime.now().isoformat(),
            'model': self.model_name,
            'epochs': epochs,
            'batch_size': batch_size,
            'learning_rate': learning_rate,
            'weight_decay': weight_decay,
            'warmup_steps': warmup_steps,
            'final_loss': float(train_result.training_loss),
            'training_samples': len(train_df),
            'validation_samples': len(val_df),
            'test_samples': len(test_df) if test_df is not None else 0
        }
        
        history_path = Path(self.output_dir) / 'training_history.json'
        with open(history_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        print(f"  ✓ Training history saved")
        
        # Evaluate on test set if provided
        if test_df is not None:
            print(f"\n[EVALUATION ON TEST SET]")
            test_results = trainer.evaluate(datasets['test'])
            print(f"  • Test loss: {test_results['eval_loss']:.4f}")
        
        print("\n" + "=" * 80)
        print("TRAINING COMPLETE")
        print("=" * 80)
        
        return trainer, train_result


def train_model(train_path='data/processed/train_dataset.pkl',
                val_path='data/processed/val_dataset.pkl',
                test_path='data/processed/test_dataset.pkl',
                output_dir='models/trained_model_cpu',
                epochs=3, batch_size=2, learning_rate=1e-4):
    """
    Main training pipeline.
    
    Args:
        train_path (str): Path to training data
        val_path (str): Path to validation data
        test_path (str): Path to test data
        output_dir (str): Output directory
        epochs (int): Number of epochs
        batch_size (int): Batch size
        learning_rate (float): Learning rate
    """
    # Load data
    print(f"\n[LOADING DATA]")
    print(f"  • Train: {train_path}")
    train_df = pd.read_pickle(train_path)
    train_df = normalize_translation_frame(train_df)
    
    print(f"  • Validation: {val_path}")
    val_df = pd.read_pickle(val_path)
    val_df = normalize_translation_frame(val_df)
    
    print(f"  • Test: {test_path}")
    test_df = pd.read_pickle(test_path)
    test_df = normalize_translation_frame(test_df)
    
    print(f"  ✓ Data loaded")
    
    # Initialize trainer
    trainer_obj = TranslationModelTrainer(output_dir=output_dir)
    
    # Train
    trainer, result = trainer_obj.train(
        train_df, val_df, test_df,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=learning_rate
    )
    
    return trainer


if __name__ == "__main__":
    try:
        train_model()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run data_collection.py and preprocessing.py first.")
