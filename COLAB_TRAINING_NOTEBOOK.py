"""
ENGLISH-LUGANDA TRANSLATOR - TRAINING IN GOOGLE COLAB
Complete training notebook for model improvement and fine-tuning

This notebook allows you to:
1. Load your data from GitHub
2. Train the model with GPU acceleration
3. Monitor performance in real-time
4. Evaluate on test set
5. Visualize results
6. Save improved model
7. Download results
"""

# ============================================================
# CELL 1: SETUP - Install Dependencies
# ============================================================
# Run this first!

!pip install -q torch transformers datasets pandas numpy scikit-learn sacrebleu evaluate tqdm matplotlib seaborn

print("✓ Dependencies installed successfully!")

# ============================================================
# CELL 2: Clone and Setup
# ============================================================

import os
import sys
from pathlib import Path

!git clone https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git /content/translator
os.chdir('/content/translator')
sys.path.insert(0, '/content/translator')

print("✓ Repository cloned")
print(f"✓ Working directory: {os.getcwd()}")

# ============================================================
# CELL 3: Verify GPU and Load Libraries
# ============================================================

import torch
import transformers
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json

print("[SYSTEM INFO]")
print("=" * 60)
print(f"PyTorch version: {torch.__version__}")
print(f"Transformers version: {transformers.__version__}")
print(f"GPU Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")
    print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f}GB")
else:
    print("CPU mode (slower, but still works)")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

# ============================================================
# CELL 4: Load Training Data
# ============================================================

print("\n[LOADING DATA]")
print("=" * 60)

# Load datasets
train_df = pd.read_csv('data/processed/train.csv')
val_df = pd.read_csv('data/processed/val.csv')
test_df = pd.read_csv('data/processed/test.csv')

print(f"Training samples: {len(train_df)}")
print(f"Validation samples: {len(val_df)}")
print(f"Test samples: {len(test_df)}")

print("\nFirst 3 training samples:")
print(train_df.head(3))

# ============================================================
# CELL 5: Load Base Model
# ============================================================

print("\n[LOADING BASE MODEL]")
print("=" * 60)

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "Helsinki-NLP/opus-mt-en-mul"  # English to multiple languages

print(f"Loading model: {MODEL_NAME}")
print("(This will download ~600MB on first run)")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
model.to(device)

print(f"✓ Model loaded on {device}")
print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

# ============================================================
# CELL 6: Test Base Model (Before Training)
# ============================================================

print("\n[TEST BASE MODEL - BEFORE TRAINING]")
print("=" * 60)

def translate_batch(texts, model, tokenizer, device, max_length=120):
    """Translate a batch of texts"""
    inputs = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        generated = model.generate(
            **inputs,
            max_length=max_length,
            num_beams=5,
            no_repeat_ngram_size=3,
            repetition_penalty=1.2,
        )
    
    translations = tokenizer.batch_decode(generated, skip_special_tokens=True)
    return translations

# Test a few examples
test_samples = train_df['english'].head(5).tolist()
print("Testing base model on training samples:\n")

base_translations = translate_batch(test_samples, model, tokenizer, device)
for en, translation in zip(test_samples, base_translations):
    print(f"EN: {en}")
    print(f"LG: {translation}\n")

# ============================================================
# CELL 7: Setup Training Parameters
# ============================================================

print("\n[TRAINING SETUP]")
print("=" * 60)

from transformers import Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq

# Training parameters
EPOCHS = 3
BATCH_SIZE = 8
LEARNING_RATE = 2e-5
WARMUP_STEPS = 500

training_args = Seq2SeqTrainingArguments(
    output_dir="./results",
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    learning_rate=LEARNING_RATE,
    warmup_steps=WARMUP_STEPS,
    weight_decay=0.01,
    save_strategy="epoch",
    evaluation_strategy="epoch",
    logging_steps=100,
    save_total_limit=3,
    predict_with_generate=True,
    report_to="none",  # No wandb logging
    seed=42,
)

print(f"Epochs: {EPOCHS}")
print(f"Batch size: {BATCH_SIZE}")
print(f"Learning rate: {LEARNING_RATE}")
print(f"Warmup steps: {WARMUP_STEPS}")
print(f"Device: {device}")

# ============================================================
# CELL 8: Prepare Data for Training
# ============================================================

print("\n[PREPARING DATA]")
print("=" * 60)

from datasets import Dataset

# Create HuggingFace datasets
def create_dataset(df):
    """Convert dataframe to HuggingFace dataset"""
    dataset = Dataset.from_dict({
        'source': df.get('english', df.get('en', [])).fillna('').tolist(),
        'target': df.get('luganda', df.get('lg', [])).fillna('').tolist(),
    })
    return dataset

train_dataset = create_dataset(train_df)
val_dataset = create_dataset(val_df)
test_dataset = create_dataset(test_df)

print(f"Train dataset: {len(train_dataset)} samples")
print(f"Val dataset: {len(val_dataset)} samples")
print(f"Test dataset: {len(test_dataset)} samples")

# Preprocessing function
def preprocess_function(examples):
    """Tokenize and prepare data for training"""
    inputs = tokenizer(
        examples['source'],
        text_target=examples['target'],
        max_length=128,
        truncation=True,
        padding="max_length"
    )
    return inputs

# Apply preprocessing
print("Tokenizing data...")
train_dataset = train_dataset.map(preprocess_function, batched=True, batch_size=100)
val_dataset = val_dataset.map(preprocess_function, batched=True, batch_size=100)
test_dataset = test_dataset.map(preprocess_function, batched=True, batch_size=100)

print("✓ Data prepared for training")

# ============================================================
# CELL 9: Start Training
# ============================================================

print("\n[STARTING TRAINING]")
print("=" * 60)
print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    data_collator=data_collator,
    tokenizer=tokenizer,
)

# Train the model
training_result = trainer.train()

print(f"✓ Training completed!")
print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total training loss: {training_result.training_loss:.4f}")

# ============================================================
# CELL 10: Evaluate on Test Set
# ============================================================

print("\n[EVALUATING ON TEST SET]")
print("=" * 60)

from sacrebleu import corpus_bleu

# Get predictions on test set
predictions = trainer.predict(test_dataset)
decoded_preds = tokenizer.batch_decode(predictions.predictions, skip_special_tokens=True)

# Get references (ground truth)
decoded_labels = tokenizer.batch_decode(predictions.label_ids, skip_special_tokens=True)

# Calculate BLEU score
bleu = corpus_bleu(decoded_preds, [decoded_labels])

print(f"Test Set BLEU Score: {bleu.score:.4f}")
print(f"Individual BLEU: {bleu.precisions}")

# Show sample predictions
print("\n[SAMPLE PREDICTIONS ON TEST SET]")
print("=" * 60)

for i in range(min(5, len(decoded_preds))):
    print(f"\nSample {i+1}:")
    print(f"Predicted: {decoded_preds[i]}")
    print(f"Reference: {decoded_labels[i]}")

# ============================================================
# CELL 11: Compare Before vs After Training
# ============================================================

print("\n[COMPARING BASE MODEL VS FINE-TUNED]")
print("=" * 60)

print("\nTesting on same samples (AFTER training):\n")

after_translations = translate_batch(test_samples, model, tokenizer, device)
for en, before, after in zip(test_samples, base_translations, after_translations):
    print(f"EN: {en}")
    print(f"Base Model:      {before}")
    print(f"Fine-tuned:      {after}\n")

# ============================================================
# CELL 12: Calculate Performance Metrics
# ============================================================

print("\n[PERFORMANCE METRICS]")
print("=" * 60)

import time

# Measure inference speed
inference_times = []
for _ in range(10):
    start = time.time()
    _ = translate_batch([test_samples[0]], model, tokenizer, device)
    inference_times.append(time.time() - start)

avg_inference_time = np.mean(inference_times)
std_inference_time = np.std(inference_times)

metrics = {
    "training_samples": len(train_dataset),
    "validation_samples": len(val_dataset),
    "test_samples": len(test_dataset),
    "epochs": EPOCHS,
    "batch_size": BATCH_SIZE,
    "learning_rate": LEARNING_RATE,
    "bleu_score": float(bleu.score),
    "avg_inference_time_ms": avg_inference_time * 1000,
    "std_inference_time_ms": std_inference_time * 1000,
    "device": str(device),
    "model_name": MODEL_NAME,
    "timestamp": datetime.now().isoformat(),
}

print(json.dumps(metrics, indent=2))

# Save metrics
with open('/content/translator/training_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)

print("\n✓ Metrics saved to training_metrics.json")

# ============================================================
# CELL 13: Visualize Training Results
# ============================================================

print("\n[VISUALIZING RESULTS]")
print("=" * 60)

# Plot training history
if hasattr(trainer.state, 'log_history'):
    history = trainer.state.log_history
    
    losses = [h.get('loss', None) for h in history if 'loss' in h]
    val_losses = [h.get('eval_loss', None) for h in history if 'eval_loss' in h]
    
    plt.figure(figsize=(12, 5))
    
    if losses:
        plt.subplot(1, 2, 1)
        plt.plot(losses)
        plt.title('Training Loss')
        plt.xlabel('Step')
        plt.ylabel('Loss')
        plt.grid(True)
    
    if val_losses:
        plt.subplot(1, 2, 2)
        plt.plot(val_losses)
        plt.title('Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.grid(True)
    
    plt.tight_layout()
    plt.savefig('/content/translator/training_plots.png', dpi=100, bbox_inches='tight')
    plt.show()
    
    print("✓ Training plots saved to training_plots.png")

# ============================================================
# CELL 14: Save Fine-tuned Model
# ============================================================

print("\n[SAVING FINE-TUNED MODEL]")
print("=" * 60)

model_save_path = '/content/translator/models/fine_tuned_model'
os.makedirs(model_save_path, exist_ok=True)

model.save_pretrained(model_save_path)
tokenizer.save_pretrained(model_save_path)

print(f"✓ Model saved to {model_save_path}")
print(f"Model size: {sum(p.numel() for p in model.parameters()):,} parameters")

# ============================================================
# CELL 15: Create Comprehensive Report
# ============================================================

print("\n[CREATING TRAINING REPORT]")
print("=" * 60)

report = f"""
# ENGLISH-LUGANDA TRANSLATOR - TRAINING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Training Configuration
- Model: {MODEL_NAME}
- Epochs: {EPOCHS}
- Batch Size: {BATCH_SIZE}
- Learning Rate: {LEARNING_RATE}
- Warmup Steps: {WARMUP_STEPS}
- Device: {device}
- Max Sequence Length: 128

## Dataset Statistics
- Training samples: {len(train_dataset)}
- Validation samples: {len(val_dataset)}
- Test samples: {len(test_dataset)}
- Total: {len(train_dataset) + len(val_dataset) + len(test_dataset)}

## Training Results
- Final Training Loss: {training_result.training_loss:.4f}
- BLEU Score on Test Set: {bleu.score:.4f}
- Average Inference Time: {avg_inference_time*1000:.2f}ms
- Inference Speed: {1000/avg_inference_time:.0f} translations/sec

## Sample Translations (After Training)
"""

for i, (en, pred, ref) in enumerate(zip(test_samples[:3], after_translations[:3], decoded_labels[:3])):
    report += f"""
### Sample {i+1}
- English: {en}
- Predicted: {pred}
- Reference: {ref}
"""

report += """
## Model Location
- Path: /content/translator/models/fine_tuned_model/
- Contains: model weights, tokenizer, config files

## Next Steps for Improvement
1. **Increase Training Data**: Add more parallel sentences
2. **Longer Training**: Increase epochs to 5-10
3. **Data Augmentation**: Create synthetic training data
4. **Larger Model**: Try bigger base model (e.g., mBART, mT5)
5. **Hyperparameter Tuning**: Adjust learning rate, batch size
6. **Domain-Specific Data**: Add cultural/specialized terms
7. **Back-translation**: Generate additional training data

## Performance Observations
- BLEU Score indicates translation quality (higher is better)
- Inference speed shows real-world performance
- Consider accuracy vs speed trade-off for deployment

## Files Generated
- training_metrics.json: Numerical metrics
- training_plots.png: Loss curves visualization
- fine_tuned_model/: Trained model weights
- training_report.md: This report
"""

with open('/content/translator/training_report.md', 'w') as f:
    f.write(report)

print(report)

# ============================================================
# CELL 16: Download Results
# ============================================================

print("\n[DOWNLOADING RESULTS]")
print("=" * 60)

from google.colab import files

# Create a zip file with all results
import zipfile

with zipfile.ZipFile('/content/translator/training_results.zip', 'w') as zipf:
    zipf.write('/content/translator/training_metrics.json', 'training_metrics.json')
    zipf.write('/content/translator/training_plots.png', 'training_plots.png')
    zipf.write('/content/translator/training_report.md', 'training_report.md')

# Download
files.download('/content/translator/training_results.zip')

print("✓ training_results.zip downloaded to your computer")
print("\nContains:")
print("  - training_metrics.json (numeric results)")
print("  - training_plots.png (loss curves)")
print("  - training_report.md (full report)")

# ============================================================
# CELL 17: IMPROVEMENT STRATEGIES
# ============================================================

print("\n[STRATEGIES TO IMPROVE MODEL PERFORMANCE]")
print("=" * 60)

strategies = """
## 1. DATA IMPROVEMENTS
   → Add more training data (currently: {len(train_dataset)} samples)
   → Target: 10,000+ parallel sentences
   → Sources: More cultural dataset, open datasets

## 2. TRAINING IMPROVEMENTS
   → Increase epochs: 3 → 10
   → Adjust learning rate: 2e-5 → 5e-5
   → Increase batch size (if GPU memory allows)
   → Add gradient accumulation steps

## 3. MODEL IMPROVEMENTS
   → Use larger base model
   → Try different model architectures
   → Multi-task learning (EN→LG + LG→EN simultaneously)

## 4. DATA AUGMENTATION
   → Back-translation: LG→EN→LG to generate new data
   → Paraphrasing: Create variations of same meaning
   → Synthetic data generation

## 5. PREPROCESSING IMPROVEMENTS
   → Better text normalization
   → Remove duplicate/similar sentences
   → Filter low-quality translations
   → Add domain-specific preprocessing

## 6. EVALUATION IMPROVEMENTS
   → Compute BLEU, ROUGE, METEOR scores
   → Manual evaluation by native speakers
   → Test on specific domains (medical, legal, etc.)

## 7. INFERENCE OPTIMIZATION
   → Model quantization for faster inference
   → Knowledge distillation to smaller models
   → Batch processing for throughput
"""

print(strategies)

# ============================================================
# CELL 18: FEEDBACK AND NEXT STEPS
# ============================================================

print("\n[NEXT STEPS]")
print("=" * 60)

next_steps = f"""
✓ Model trained successfully!

WHAT TO DO NOW:

1. **Review Results**
   - Open training_results.zip on your computer
   - Check training_metrics.json for BLEU score
   - View training_plots.png to see loss curves

2. **Evaluate Quality**
   - Test model on your own sentences
   - Compare BLEU score (target: > 25)
   - Check if translations make sense

3. **Decide on Improvement**
   - If BLEU < 20: Need more data or longer training
   - If BLEU 20-30: Good! Consider adding data
   - If BLEU > 30: Excellent! Ready for deployment

4. **Plan Next Training**
   - Use strategies from CELL 17
   - Collect more training data
   - Re-run training with improvements

5. **Deploy**
   - Push fine-tuned model to GitHub
   - Use in production Flask app
   - Share with team

QUESTIONS?
- Check training_report.md for detailed analysis
- Review MODEL_IMPROVEMENT_GUIDE.md in repo
- Test on your specific use cases
"""

print(next_steps)

# ============================================================
# CELL 19: FINAL SUMMARY
# ============================================================

print("\n" + "="*60)
print("TRAINING COMPLETE! 🎉")
print("="*60)

summary = f"""
Training Summary:
- ✓ Model fine-tuned successfully
- ✓ Trained on {len(train_dataset)} samples
- ✓ BLEU Score: {bleu.score:.4f}
- ✓ Inference Speed: {1000/avg_inference_time:.0f} translations/sec
- ✓ Results downloaded to your computer
- ✓ Model ready for use and deployment

Your model is improving! 📈

Next: Review results, plan improvements, train again!
"""

print(summary)
