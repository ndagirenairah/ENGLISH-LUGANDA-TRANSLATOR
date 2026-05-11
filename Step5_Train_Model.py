"""
STEP 5: Train Neural Machine Translation Model
Integration of Lecture 3 concepts: Regularization, CV, Learning Rate Scheduling
"""

import pickle
import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
)
import evaluate

print("=" * 80)
print(" ML WORKFLOW: MODEL TRAINING & EVALUATION (PART 1)")
print("=" * 80)
print("""
ML Workflow Progress:
  ✓ 1. Define the problem
  ✓ 2. Collect data
  ✓ 3. Exploratory Data Analysis
  ✓ 4. Data cleaning & preprocessing
  ✓ 5. Feature engineering
  ✓ 6. Model selection
  ► 7. Model training           (This step - fine-tuning with Lecture 3)
  8. Model evaluation
  9. Deployment & monitoring
""")
print("\nSTEP 5: TRAINING WITH LECTURE 3 DEEP CONCEPTS")

# ============================================================================
# LECTURE 3 CONCEPTS: BIAS-VARIANCE TRADEOFF & REGULARIZATION
# ============================================================================
print("\n" + "=" * 80)
print("LECTURE 3: BIAS-VARIANCE TRADEOFF & REGULARIZATION")
print("=" * 80)
print("""
Key Concepts:

1. BIAS-VARIANCE TRADEOFF
   Bias: Error from wrong model assumptions (underfitting)
   Variance: Error from sensitivity to training data (overfitting)
   Total Error = Bias^2 + Variance + Irreducible Error
   
2. REGULARIZATION (L2 - WEIGHT DECAY)
   Loss = Cross-Entropy + lambda * sum(weights^2)
   Penalizes large weights to prevent memorization
   
3. LEARNING RATE SCHEDULING
   Warmup: Gradually increase learning rate early on
   Cosine Decay: Gradually decrease learning rate for fine-tuning
   
4. CROSS-VALIDATION
   Monitor validation loss during training
   Early stopping prevents overfitting
""")

# ============================================================================
# LOAD DATASETS AND MODEL
# ============================================================================
print("\n" + "=" * 80)
print("Loading datasets and model...")
print("=" * 80)

with open('data/train_dataset.pkl', 'rb') as f:
    train_dataset_raw = pickle.load(f)

with open('data/val_dataset.pkl', 'rb') as f:
    val_dataset_raw = pickle.load(f)

model = AutoModelForSeq2SeqLM.from_pretrained(
    'Helsinki-NLP/opus-mt-en-mul',
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(
    'Helsinki-NLP/opus-mt-en-mul',
    trust_remote_code=True
)

print(f"Model loaded successfully")
print(f"   Train samples: {len(train_dataset_raw)}")
print(f"   Validation samples: {len(val_dataset_raw)}")

# ============================================================================
# TOKENIZATION
# ============================================================================

def preprocess_function(examples):
    """Tokenize translation pairs"""
    sources = [ex['en'] for ex in examples['translation']]
    targets = [ex['lg'] for ex in examples['translation']]
    
    inputs = tokenizer(
        sources,
        max_length=512,
        truncation=True,
        padding='max_length'
    )
    
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(
            targets,
            max_length=512,
            truncation=True,
            padding='max_length'
        )
    
    inputs["labels"] = labels["input_ids"]
    return inputs

print("Tokenizing datasets...")
train_dataset = train_dataset_raw.map(
    preprocess_function,
    batched=True,
    remove_columns=train_dataset_raw.column_names
)
val_dataset = val_dataset_raw.map(
    preprocess_function,
    batched=True,
    remove_columns=val_dataset_raw.column_names
)
print("Tokenization complete")

# ============================================================================
# EVALUATION METRICS
# ============================================================================

try:
    bleu = evaluate.load("sacrebleu")
except Exception as e:
    print(f"Warning: BLEU metric not available: {e}")
    bleu = None

def compute_metrics(eval_preds):
    """Compute evaluation metrics (BLEU score)"""
    preds, labels = eval_preds
    
    # Filter -100 tokens (padding indicators)
    labels = [[l for l in label if l != -100] for label in labels]
    
    # Decode predictions and labels
    pred_str = tokenizer.batch_decode(preds, skip_special_tokens=True)
    label_str = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
    if bleu is not None:
        result = bleu.compute(predictions=pred_str, references=label_str)
        return {"bleu": result["score"]}
    else:
        return {"accuracy": sum(p == l for p, l in zip(pred_str, label_str)) / len(pred_str)}

# ============================================================================
# TRAINING ARGUMENTS: LECTURE 3 CONCEPTS
# ============================================================================
print("\n" + "=" * 80)
print("Configuring training with Lecture 3 concepts")
print("=" * 80)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device.type.upper()}")

training_args = Seq2SeqTrainingArguments(
    output_dir="checkpoints",
    
    # LECTURE 3: Learning Rate Scheduling
    # Warmup prevents bad updates early when model is untrained
    warmup_steps=500,
    # Cosine decay gradually reduces learning rate during training
    lr_scheduler_type="cosine",
    
    # LECTURE 3: Regularization (L2 Weight Decay)
    # Penalizes large weights to prevent overfitting
    weight_decay=0.01,
    
    # LECTURE 3: Bias-Variance Control
    # Evaluate frequently to detect overfitting
    eval_strategy="epoch",
    save_strategy="epoch",
    # Load best model based on validation loss
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    
    # Training parameters
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    
    # LECTURE 3: Gradient Clipping
    # Prevents exploding gradients during backpropagation
    max_grad_norm=1.0,
    
    # Additional settings
    logging_steps=50,
    logging_dir="logs",
    fp16=torch.cuda.is_available(),
    gradient_accumulation_steps=4,
    seed=42,
    predict_with_generate=True,
    generation_max_length=128,
    generation_num_beams=4,
)

print("\nLecture 3 Training Configuration:")
print(f"  Bias-Variance Control:")
print(f"    Evaluation: {training_args.eval_strategy}")
print(f"    Monitor metric: {training_args.metric_for_best_model}")
print(f"  Regularization:")
print(f"    Weight decay (L2): {training_args.weight_decay}")
print(f"    Max gradient norm: {training_args.max_grad_norm}")
print(f"  Learning Rate Schedule:")
print(f"    Base learning rate: {training_args.learning_rate}")
print(f"    Warmup steps: {training_args.warmup_steps}")
print(f"    Decay schedule: {training_args.lr_scheduler_type}")

# ============================================================================
# INITIALIZE TRAINER
# ============================================================================
print("\n" + "=" * 80)
print("Initializing trainer")
print("=" * 80)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

print("Trainer initialized successfully")

# ============================================================================
# TRAIN MODEL
# ============================================================================
print("\n" + "=" * 80)
print("Starting training")
print("=" * 80)
print("Training will take 10-30 minutes on GPU\n")

try:
    train_result = trainer.train()
    print("\nTraining completed successfully")
    print(f"Final training loss: {train_result.training_loss:.4f}")
    
except Exception as e:
    print(f"Training failed: {e}")
    exit(1)

# ============================================================================
# EVALUATE ON VALIDATION SET
# ============================================================================
print("\n" + "=" * 80)
print("Evaluating on validation set")
print("=" * 80)

eval_results = trainer.evaluate()

print(f"\nValidation Metrics:")
for metric, value in eval_results.items():
    if metric != 'epoch':
        print(f"  {metric}: {value:.4f}")

# ============================================================================
# BIAS-VARIANCE ANALYSIS
# ============================================================================
print("\n" + "=" * 80)
print("Lecture 3 Analysis: Bias-Variance Interpretation")
print("=" * 80)

train_loss = train_result.training_loss
val_loss = eval_results.get('eval_loss', 0)

print(f"\nTraining Loss: {train_loss:.4f}")
print(f"Validation Loss: {val_loss:.4f}")
print(f"Gap (Val - Train): {val_loss - train_loss:.4f}")

print("\nInterpretation:")
if val_loss - train_loss > 0.5:
    print("  High variance detected (overfitting risk)")
    print("  Model fits training data too closely")
    print("  Recommendation: Increase regularization or reduce model complexity")
elif val_loss - train_loss < -0.1:
    print("  Anomaly: Validation loss < training loss")
    print("  Check data preprocessing or learning rate schedule")
else:
    print("  Good balance between bias and variance")
    print("  Model generalizes well to unseen data")

# ============================================================================
# SAVE MODEL
# ============================================================================
print("\n" + "=" * 80)
print("Saving model")
print("=" * 80)

trainer.save_model("models/final_nmt_model")
print("Model saved to: models/final_nmt_model")

print("\nTraining pipeline complete")
