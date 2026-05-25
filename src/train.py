"""
STEP 3: Train Model - Week 9 (Transformers)
============================================
Fine-tune a pre-trained transformer model (OPUS-MT) on Luganda data.

Key concepts:
  - Transfer Learning: Start with pre-trained model
  - Sequence-to-Sequence: Input sequence (English) → Output sequence (Luganda)
  - Fine-tuning: Adapt model to our specific task
  - Regularization (Week 3): Dropout, weight decay
"""

from pathlib import Path
from datetime import datetime
import sys
import json
import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    DataCollatorForSeq2Seq,
)

try:
    from config import (
        MODEL_NAME, DEVICE, BATCH_SIZE, LEARNING_RATE, NUM_EPOCHS,
        MAX_SOURCE_LENGTH, MAX_TARGET_LENGTH, DROPOUT,
        PROCESSED_DATA_DIR, TRAIN_OUTPUT_DIR, WARMUP_STEPS,
        GRADIENT_ACCUMULATION_STEPS, WEIGHT_DECAY
    )
    from utils import print_section
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from config import (
        MODEL_NAME, DEVICE, BATCH_SIZE, LEARNING_RATE, NUM_EPOCHS,
        MAX_SOURCE_LENGTH, MAX_TARGET_LENGTH, DROPOUT,
        PROCESSED_DATA_DIR, TRAIN_OUTPUT_DIR, WARMUP_STEPS,
        GRADIENT_ACCUMULATION_STEPS, WEIGHT_DECAY
    )
    from utils import print_section


def load_training_data():
    """Load preprocessed train/val/test splits."""
    train_path = PROCESSED_DATA_DIR / "train.csv"
    val_path = PROCESSED_DATA_DIR / "val.csv"
    
    if not train_path.exists():
        raise FileNotFoundError(
            f"❌ Training data not found at {train_path}\n"
            f"   Run: python src/2_preprocess.py first"
        )
    
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)
    
    train_dataset = Dataset.from_dict({
        'source': train_df['english'].tolist(),
        'target': train_df['luganda'].tolist(),
    })
    
    val_dataset = Dataset.from_dict({
        'source': val_df['english'].tolist(),
        'target': val_df['luganda'].tolist(),
    })
    
    return train_dataset, val_dataset, len(train_df), len(val_df)


def tokenize_data(train_dataset, val_dataset, tokenizer):
    """Tokenize datasets for training."""
    print("🔤 Tokenizing data...")
    
    def preprocess_batch(batch):
        """Tokenize source and target texts."""
        inputs = tokenizer(
            batch['source'],
            max_length=MAX_SOURCE_LENGTH,
            truncation=True,
            padding="max_length"
        )
        
        outputs = tokenizer(
            batch['target'],
            max_length=MAX_TARGET_LENGTH,
            truncation=True,
            padding="max_length"
        )
        
        inputs['labels'] = outputs['input_ids']
        return inputs
    
    # Tokenize training data
    train_tokenized = train_dataset.map(
        preprocess_batch,
        batched=True,
        batch_size=100,
        remove_columns=['source', 'target']
    )
    
    # Tokenize validation data
    val_tokenized = val_dataset.map(
        preprocess_batch,
        batched=True,
        batch_size=100,
        remove_columns=['source', 'target']
    )
    
    print(f"   ✅ Tokenization complete")
    
    return train_tokenized, val_tokenized


def main():
    """Train the model."""
    print_section("STEP 3: TRAINING MODEL", width=80)
    
    # Load data
    print("\n📁 Loading training data...")
    train_dataset, val_dataset, n_train, n_val = load_training_data()
    print(f"   Train: {n_train:,} | Val: {n_val:,}")
    
    # Load model and tokenizer
    print(f"\n🤖 Loading model: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    
    # Move to device
    model = model.to(DEVICE)
    print(f"   Device: {DEVICE}")
    print(f"   Model size: {sum(p.numel() for p in model.parameters()):,} parameters")
    
    # Tokenize data
    print("\n🔤 Preprocessing datasets...")
    train_tokenized, val_tokenized = tokenize_data(
        train_dataset, val_dataset, tokenizer
    )
    
    # Training arguments
    print("\n⚙️  Configuring training...")
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(TRAIN_OUTPUT_DIR),
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        warmup_steps=WARMUP_STEPS,
        weight_decay=WEIGHT_DECAY,
        
        # Evaluation and saving
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        
        # Regularization (Week 3 concepts)
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        gradient_checkpointing=True,
        fp16=torch.cuda.is_available(),
        
        # Logging
        logging_steps=50,
        logging_dir=str(TRAIN_OUTPUT_DIR / "logs"),
        report_to="none",
        
        # Generation for evaluation
        predict_with_generate=True,
    )
    
    print(f"   Epochs: {NUM_EPOCHS}")
    print(f"   Batch size: {BATCH_SIZE}")
    print(f"   Learning rate: {LEARNING_RATE}")
    print(f"   Device: {DEVICE}")
    
    # Data collator
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)
    
    # Trainer
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_tokenized,
        eval_dataset=val_tokenized,
        data_collator=data_collator,
    )
    
    # Train
    print("\n" + "="*80)
    print(f"🚀 STARTING TRAINING")
    print(f"   Dataset: {n_train:,} training samples")
    print(f"   Estimated time: 5-15 minutes on GPU, 30-60 minutes on CPU")
    print("="*80 + "\n")
    
    start_time = datetime.now()
    
    result = trainer.train()
    
    end_time = datetime.now()
    training_time = (end_time - start_time).total_seconds() / 60
    
    print("\n✅ Training complete!")
    print(f"   Training loss: {result.training_loss:.4f}")
    print(f"   Time elapsed: {training_time:.1f} minutes")
    
    # Save model and tokenizer
    print("\n💾 Saving model and tokenizer...")
    TRAIN_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    model.save_pretrained(TRAIN_OUTPUT_DIR)
    tokenizer.save_pretrained(TRAIN_OUTPUT_DIR)
    
    print(f"   ✅ Saved to {TRAIN_OUTPUT_DIR}")
    
    # Save training info
    training_info = {
        "model": MODEL_NAME,
        "training_loss": float(result.training_loss),
        "num_epochs": NUM_EPOCHS,
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "training_samples": n_train,
        "validation_samples": n_val,
        "training_time_minutes": training_time,
        "timestamp": datetime.now().isoformat(),
    }
    
    info_file = TRAIN_OUTPUT_DIR / "training_info.json"
    with open(info_file, 'w') as f:
        json.dump(training_info, f, indent=2)
    
    print_section("TRAINING COMPLETE", width=80)
    print(f"\n✅ Model trained successfully!")
    print(f"\n   Next step: python src/4_evaluate.py")
    
    return model, tokenizer


if __name__ == "__main__":
    main()
