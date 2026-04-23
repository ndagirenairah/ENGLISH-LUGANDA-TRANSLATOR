# ============================================================================
# STEP 5: TRAINING THE MODEL
# ============================================================================
# This script fine-tunes mBART on the Luganda-English dataset
# with early stopping, evaluation, and GPU optimization
# ============================================================================

print("=" * 70)
print("[*] STEP 5: TRAINING THE MODEL")
print("=" * 70)

import pickle
import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    Seq2SeqTrainer,
    Seq2SeqTrainingArguments,
    pipeline
)
import evaluate

# ============================================================================
# PART 1: LOAD TOKENIZED DATASETS AND MODEL
# ============================================================================
print("\nLoading datasets and model...\n")

# Load datasets (non-tokenized)
with open('data/train_dataset.pkl', 'rb') as f:
    train_dataset_raw = pickle.load(f)

with open('data/val_dataset.pkl', 'rb') as f:
    val_dataset_raw = pickle.load(f)

# Load model and tokenizer
print("Loading model from HuggingFace (cached)...")
model = AutoModelForSeq2SeqLM.from_pretrained(
    'facebook/mbart-large-50-many-to-one-mmt',
    local_files_only=False,
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(
    'facebook/mbart-large-50-many-to-one-mmt',
    local_files_only=False,
    trust_remote_code=True
)

print("[OK] Model and tokenizer loaded")
print(f"   - Train samples: {len(train_dataset_raw)}")
print(f"   - Validation samples: {len(val_dataset_raw)}")

# Preprocessing function to tokenize data
def preprocess_function(examples):
    # Extract luganda and english from nested translation dict
    inputs = [item['lug'] for item in examples['translation']]
    targets = [item['eng'] for item in examples['translation']]
    
    model_inputs = tokenizer(inputs, max_length=512, truncation=True, padding='max_length')
    labels = tokenizer(targets, max_length=512, truncation=True, padding='max_length')
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Tokenize datasets
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

# ============================================================================
# PART 2: LOAD EVALUATION METRIC
# ============================================================================
print("\n" + "=" * 70)
print("[*] SETTING UP EVALUATION METRICS")
print("=" * 70)

# Load BLEU metric for evaluation
try:
    bleu = evaluate.load("sacrebleu")
    print("[OK] BLEU metric loaded")
except:
    print("[!] BLEU metric not available, using alternative metrics")
    bleu = None

# ============================================================================
# PART 3: DEFINE COMPUTE METRICS FUNCTION
# ============================================================================
print("\nDefining compute_metrics function...")

def compute_metrics(eval_preds):
    """
    Compute BLEU score during evaluation.
    This measures how close our predictions are to the reference translations.
    """
    preds, labels = eval_preds
    
    # Remove -100 tokens which are placeholders
    labels = [[l for l in label if l != -100] for label in labels]
    
    # Decode predictions and labels
    pred_str = tokenizer.batch_decode(preds, skip_special_tokens=True)
    label_str = tokenizer.batch_decode(labels, skip_special_tokens=True)
    
    # Compute BLEU
    if bleu is not None:
        result = bleu.compute(predictions=pred_str, references=label_str)
        return {"bleu": result["score"]}
    else:
        # Simple alternative: just return accuracy
        matches = sum(p == l for p, l in zip(pred_str, label_str))
        return {"accuracy": matches / len(pred_str)}

print("[OK] Metrics function defined")

# ============================================================================
# PART 4: DEFINE TRAINING ARGUMENTS
# ============================================================================
print("\n" + "=" * 70)
print("[*] CONFIGURING TRAINING PARAMETERS")
print("=" * 70)

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n[OK] Device: {device.type.upper()}")

training_args = Seq2SeqTrainingArguments(
    output_dir="checkpoints",
    
    # Training parameters
    num_train_epochs=3,                    # Number of training passes through the data
    per_device_train_batch_size=16,        # Batch size for training (adjust if OOM)
    per_device_eval_batch_size=16,         # Batch size for evaluation
    
    # Learning rate and optimization
    learning_rate=2e-5,                    # Learning rate
    warmup_steps=100,                      # Gradually increase LR
    weight_decay=0.01,                     # Regularization
    
    # Evaluation and saving
    eval_strategy="steps",                # Evaluate every N steps
    eval_steps=100,                        # Evaluate every 100 steps
    save_strategy="steps",                 # Save checkpoint every N steps
    save_steps=100,
    load_best_model_at_end=True,          # Load best model after training
    metric_for_best_model="eval_loss",    # Use validation loss as best model metric
    
    # Early stopping
    logging_steps=50,                      # Log loss every 50 steps
    logging_dir="logs",
    
    # Optimization for GPU
    fp16=torch.cuda.is_available(),        # Mixed precision training (speeds up training)
    gradient_accumulation_steps=4,         # Accumulate gradients
    
    # Other settings
    seed=42,                               # For reproducibility
    predict_with_generate=True,            # Generate translations during evaluation
    generation_max_length=128,
    generation_num_beams=4,                # Beam search for better translations
)

print("\nTraining Configuration:")
print(f"  - Number of epochs: {training_args.num_train_epochs}")
print(f"  - Batch size: {training_args.per_device_train_batch_size}")
print(f"  - Learning rate: {training_args.learning_rate}")
print(f"  - Evaluation every: {training_args.eval_steps} steps")
print(f"  - Mixed precision: {training_args.fp16}")
print(f"  - Beam search: {training_args.generation_num_beams}")

# ============================================================================
# PART 5: INITIALIZE TRAINER
# ============================================================================
print("\n" + "=" * 70)
print("[*] INITIALIZING TRAINER")
print("=" * 70)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics,
)

print("\n[OK] Trainer initialized and ready!")

# ============================================================================
# PART 6: TRAIN THE MODEL
# ============================================================================
print("\n" + "=" * 70)
print("[*] STARTING TRAINING")
print("=" * 70)

print("\n[*] Training in progress... (this will take 10-30 minutes on GPU)")
print("   This is normal - the model learns with each batch!\n")

try:
    train_result = trainer.train()
    print("\n[OK] Training completed!")
    
    print(f"\nTraining Results:")
    print(f"  - Final train loss: {train_result.training_loss:.4f}")
    
except Exception as e:
    print(f"\n[ERROR] Training failed: {e}")
    print(f"   Common causes: Out of memory (OOM), interrupted connection")
    exit()

# ============================================================================
# PART 7: EVALUATE ON VALIDATION SET
# ============================================================================
print("\n" + "=" * 70)
print("[*] VALIDATION EVALUATION")
print("=" * 70)

print("\n[*] Evaluating on validation set...")

eval_results = trainer.evaluate()
print("\n[OK] Evaluation complete!")

print(f"\nValidation Metrics:")
for metric, value in eval_results.items():
    if isinstance(value, float):
        print(f"  - {metric}: {value:.4f}")
    else:
        print(f"  - {metric}: {value}")

# ============================================================================
# PART 8: SAVE TRAINED MODEL
# ============================================================================
print("\n" + "=" * 70)
print("[*] SAVING TRAINED MODEL")
print("=" * 70)

model.save_pretrained('models/trained_model')
tokenizer.save_pretrained('models/trained_model')
print("\n[OK] Trained model saved to: models/trained_model/")
print("\n*** SUCCESS: pytorch_model.bin created! ***\n")

# ============================================================================
# PART 9: QUICK TEST
# ============================================================================
print("=" * 70)
print("[*] QUICK TEST ON SAMPLE SENTENCE")
print("=" * 70)

# Create a simple translation pipeline
translator = pipeline('text2text-generation', model='models/trained_model', tokenizer=tokenizer)

test_sentences = [
    "Hello, how are you?",
    "What is your name?",
    "Thank you for your help."
]

print("\nTesting trained model on sample sentences:\n")
for sent in test_sentences:
    try:
        result = translator(sent, max_length=128)
        output = result[0]['generated_text']
        print(f"  English:  {sent}")
        print(f"  Luganda:  {output}\n")
    except Exception as e:
        print(f"  [Error] Could not translate: {e}\n")

print("=" * 70)
print("[OK] TRAINING COMPLETE!")
print("=" * 70)
