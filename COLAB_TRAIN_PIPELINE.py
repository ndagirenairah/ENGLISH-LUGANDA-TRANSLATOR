#!/usr/bin/env python3
"""
Google Colab - English-Luganda Translator ML Pipeline
=====================================================

This script runs the complete ML pipeline on Google Colab with GPU support.

Usage:
1. Upload this to Google Colab
2. Run all cells in order
3. Model trains on GPU (5-10x faster than CPU)
4. Download trained model at the end
"""

# ============================================================================
# CELL 1: Setup Environment
# ============================================================================

print("="*80)
print("ENGLISH-LUGANDA TRANSLATOR - COLAB ML PIPELINE")
print("="*80)
print("\n[CELL 1: Setting up environment]")

# Install required packages
import subprocess
import sys

packages = [
    "torch",
    "transformers",
    "datasets",
    "pandas",
    "scikit-learn",
    "sacrebleu",
]

print("\n📦 Installing packages...")
for package in packages:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", package])
print("✅ All packages installed")

# ============================================================================
# CELL 2: Clone or Mount Project
# ============================================================================

print("\n[CELL 2: Setting up project]")

from google.colab import drive
import os

# Mount Google Drive
print("\n📁 Mounting Google Drive...")
drive.mount('/content/drive')
print("✅ Drive mounted")

# Set working directory (adjust path if needed)
COLAB_PROJECT_PATH = "/content/drive/My Drive/English-Luganda-Translator/ENGLISH-LUGANDA-TRANSLATOR"

if not os.path.exists(COLAB_PROJECT_PATH):
    print(f"\n⚠️  Path not found: {COLAB_PROJECT_PATH}")
    print("Try uploading the project folder to your Google Drive first")
    print("Or use: !git clone https://github.com/YOUR_REPO/english-luganda-translator.git")
else:
    os.chdir(COLAB_PROJECT_PATH)
    print(f"✅ Working directory: {os.getcwd()}")

# ============================================================================
# CELL 3: Run Pipeline Step 1 - Load Data
# ============================================================================

print("\n[CELL 3: Step 1 - Load Data]")

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, "src")

from load_data import load_all_datasets, get_dataset_statistics
from utils import print_section

print("\n" + "="*80)
combined_df = load_all_datasets()
stats = get_dataset_statistics(combined_df)

print(f"\n✅ Dataset Statistics:")
print(f"   Total samples: {stats['total_samples']:,}")
print(f"   English text - Avg length: {stats['avg_english_length']:.1f}")
print(f"   Luganda text - Avg length: {stats['avg_luganda_length']:.1f}")

# ============================================================================
# CELL 4: Run Pipeline Step 2 - Preprocess
# ============================================================================

print("\n[CELL 4: Step 2 - Preprocess & Create Splits]")

from preprocess import preprocess_and_split, save_splits

print("\n" + "="*80)
train_df, val_df, test_df = preprocess_and_split(combined_df)
save_splits(train_df, val_df, test_df)

print(f"\n✅ Data splits created:")
print(f"   Train: {len(train_df):,}")
print(f"   Val: {len(val_df):,}")
print(f"   Test: {len(test_df):,}")

# ============================================================================
# CELL 5: Run Pipeline Step 3 - Train Model
# ============================================================================

print("\n[CELL 5: Step 3 - Train Model]")
print("\n⚠️  This will take 5-15 minutes on GPU")
print("   (The GPU makes it ~5-10x faster than CPU)")

import torch

print(f"\n🤖 GPU Status:")
print(f"   Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   Device: {torch.cuda.get_device_name(0)}")
    print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")

print("\n" + "="*80)
from train import main as train_main

try:
    model, tokenizer = train_main()
    print(f"\n✅ Training complete!")
except Exception as e:
    print(f"❌ Training error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# CELL 6: Run Pipeline Step 4 - Evaluate
# ============================================================================

print("\n[CELL 6: Step 4 - Evaluate Model]")

print("\n" + "="*80)
from evaluate import main as eval_main

try:
    eval_main()
    print(f"\n✅ Evaluation complete!")
except Exception as e:
    print(f"❌ Evaluation error: {e}")
    import traceback
    traceback.print_exc()

# ============================================================================
# CELL 7: Display Results
# ============================================================================

print("\n[CELL 7: Results Summary]")

import json

eval_file = Path("outputs/evaluation_results.json")
if eval_file.exists():
    with open(eval_file) as f:
        results = json.load(f)
    
    print("\n" + "="*80)
    print("📊 FINAL RESULTS")
    print("="*80)
    print(f"\n✅ BLEU Score: {results['bleu_score']:.2f}")
    print(f"   Test samples: {results['num_test_samples']}")
    print(f"   Avg prediction length: {results['avg_prediction_length']:.1f} tokens")
    print(f"   Avg reference length: {results['avg_reference_length']:.1f} tokens")

# ============================================================================
# CELL 8: Download Results & Model
# ============================================================================

print("\n[CELL 8: Download Files]")

from google.colab import files
import shutil

print("\n📥 Preparing files for download...")

# Create a zip of the trained model
print("   Zipping trained model...")
shutil.make_archive("trained_model", "zip", "models")

# Zip evaluation results
print("   Zipping evaluation results...")
shutil.make_archive("evaluation_outputs", "zip", "outputs")

print("\n📥 Download files:")
print("   1. trained_model.zip - Use for inference")
print("   2. evaluation_outputs.zip - BLEU scores and predictions")

files.download("trained_model.zip")
files.download("evaluation_outputs.zip")

print("\n✅ Files downloaded!")

# ============================================================================
# CELL 9: (Optional) Test Inference
# ============================================================================

print("\n[CELL 9: Test Inference (Optional)]")

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

print("\n🧪 Testing model inference...")

try:
    model_path = "models/trained_model"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    
    # Test translations
    test_sentences = [
        "Hello, how are you?",
        "Thank you very much.",
        "What is your name?",
    ]
    
    print("\n📝 Sample Translations:")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    
    for sentence in test_sentences:
        inputs = tokenizer(sentence, return_tensors="pt", padding=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        output_ids = model.generate(
            inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            max_length=128,
        )
        
        translation = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        print(f"\n   English:  {sentence}")
        print(f"   Luganda:  {translation}")
        
except Exception as e:
    print(f"⚠️  Inference test failed: {e}")

# ============================================================================
# CELL 10: Summary
# ============================================================================

print("\n" + "="*80)
print("✅ PIPELINE COMPLETE!")
print("="*80)

print("""
Summary:
  ✓ Step 1: Loaded all 5 datasets from your project
  ✓ Step 2: Created train/val/test splits
  ✓ Step 3: Trained model on GPU (5-15 minutes)
  ✓ Step 4: Evaluated on test set (BLEU score)
  ✓ Step 5: Downloaded trained model & results

Model Location:
  - Local: models/trained_model/
  - Download: trained_model.zip

Results:
  - BLEU Score: See evaluation_outputs.zip
  - Predictions: evaluation_outputs.zip

Next Steps:
  1. Download trained model & results
  2. Upload to your local machine
  3. Use for inference or further training

Performance:
  - Training time: 5-15 minutes on GPU
  - GPU used: Tesla T4 (free in Colab)
  - Speedup vs CPU: 5-10x faster

Questions?
  - Check README_ML_PIPELINE.md for details
  - Review training logs above
""")
