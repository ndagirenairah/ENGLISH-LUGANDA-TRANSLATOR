================================================================================
# STEP 4: MODEL SELECTION & MARIANMT SETUP
================================================================================
# This script loads the Helsinki-NLP MarianMT pretrained model for
# Luganda-English translation fine-tuning
================================================================================

print("=" * 70)
print("STEP 4: MODEL SELECTION & MARIANMT SETUP")
print("=" * 70)

import pickle
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ============================================================================
# PART 1: LOAD PREPROCESSED DATASETS
# ============================================================================
print("\nLoading preprocessed datasets...\n")

with open('data/train_dataset.pkl', 'rb') as f:
    train_dataset = pickle.load(f)

with open('data/val_dataset.pkl', 'rb') as f:
    val_dataset = pickle.load(f)

with open('data/test_dataset.pkl', 'rb') as f:
    test_dataset = pickle.load(f)

print(f"Datasets loaded:")
print(f"   - Train: {len(train_dataset)} samples")
print(f"   - Validation: {len(val_dataset)} samples")
print(f"   - Test: {len(test_dataset)} samples")

# ============================================================================
# PART 2: UNDERSTAND MARIANMT
# ============================================================================
print("\n" + "=" * 70)
print("WHAT IS MARIANMT?")
print("=" * 70)

explanation = """
MarianMT is a pre-trained neural machine translation model developed by
Helsinki-NLP. It is trained on millions of parallel sentences using the
Transformer architecture.

KEY POINTS:
  - Already trained on many language pairs
  - Can be fine-tuned with custom data
  - Very accurate for translation tasks
  - Works with GPU acceleration
  - State-of-the-art performance

MODEL STRUCTURE:
  - Encoder: Converts Luganda to numerical representation
  - Decoder: Generates English word by word
  - Attention: Focuses on relevant Luganda words while generating English
"""

print(explanation)

# ============================================================================
# PART 3: SELECT MARIANMT MODEL FOR LUGANDA-ENGLISH
# ============================================================================
print("\n" + "=" * 70)
print("SELECTING MODEL")
print("=" * 70)

# Model identifier for Luganda-English translation
model_name = "Helsinki-NLP/Tatoeba-MT-mul+eng-eng"  # Multilingual to English
# Alternative: "Helsinki-NLP/Tatoeba-MT-enb-eng" for pidgin to English

print(f"\nModel Selected: {model_name}")
print(f"\nThis model can translate to English from multiple languages.")

# ============================================================================
# PART 4: LOAD TOKENIZER
# ============================================================================
print("\n" + "=" * 70)
print("LOADING TOKENIZER")
print("=" * 70)

print(f"\nLoading tokenizer... (this may take a moment)")

try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print(f"Tokenizer loaded successfully!")

    print(f"\nTokenizer Info:")
    print(f"  - Vocabulary size: {len(tokenizer):,} tokens")
    print(f"  - Model max length: {tokenizer.model_max_length} tokens")

except Exception as e:
    print(f"Error loading tokenizer: {e}")
    print(f"   Make sure you have internet connection")
    exit()

# ============================================================================
# PART 5: LOAD MODEL
# ============================================================================
print("\n" + "=" * 70)
print("LOADING PRETRAINED MODEL")
print("=" * 70)

print(f"\nLoading model... (this may take 1-2 minutes)")

try:
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    print(f"Model loaded successfully!")

    # Move to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    print(f"Model moved to: {device.upper()}")

except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# ============================================================================
# PART 6: MODEL INFORMATION
# ============================================================================
print("\n" + "=" * 70)
print("MODEL ARCHITECTURE")
print("=" * 70)

print(f"\nModel Config:")
print(f"  - Encoder layers: {model.config.encoder_layers}")
print(f"  - Decoder layers: {model.config.decoder_layers}")
print(f"  - Hidden size: {model.config.d_model}")
print(f"  - Number of attention heads: {model.config.encoder_attention_heads}")
print(f"  - Total parameters: {sum(p.numel() for p in model.parameters()):,}")

# ============================================================================
# PART 7: TEST TOKENIZATION
# ============================================================================
print("\n" + "=" * 70)
print("TESTING TOKENIZATION")
print("=" * 70)

print("\nSample tokenization:\n")

# Test with sample Luganda sentence
test_sentence = "Ndi Muganda nkekkaanya oluganda n'Olungereza"
print(f"Original: {test_sentence}")

tokens = tokenizer(test_sentence, return_tensors="pt", padding=True)
print(f"\nTokenized input_ids: {tokens['input_ids']}")
print(f"Number of tokens: {tokens['input_ids'].shape[1]}")

# Decode back
decoded = tokenizer.decode(tokens['input_ids'][0], skip_special_tokens=True)
print(f"\nDecoded back: {decoded}")

# ============================================================================
# PART 8: PREPARE DATA FOR TOKENIZATION
# ============================================================================
print("\n" + "=" * 70)
print("DATA TOKENIZATION FUNCTION")
print("=" * 70)

def preprocess_function(examples):
    """
    Tokenize all datasets.
    Handles both source (Luganda) and target (English) languages.
    """

    # Get source and target languages
    source_lang = "lug"
    target_lang = "eng"

    # Add language tags (required by MarianMT)
    inputs = [f">>{target_lang}<< " + example[source_lang] for example in examples['translation']]
    targets = [example[target_lang] for example in examples['translation']]

    # Tokenize inputs
    model_inputs = tokenizer(inputs, max_length=128, truncation=True, padding="max_length")

    # Tokenize targets
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=128, truncation=True, padding="max_length")

    model_inputs["labels"] = labels["input_ids"]

    return model_inputs

print(f"\nPreprocess function defined")
print(f"\nThis function:")
print(f"  1. Adds language tags (>>en<< for English)")
print(f"  2. Tokenizes Luganda input (max 128 tokens)")
print(f"  3. Tokenizes English output (max 128 tokens)")
print(f"  4. Prepares labels for training")

# ============================================================================
# PART 9: TOKENIZE DATASETS
# ============================================================================
print("\n" + "=" * 70)
print("TOKENIZING DATASETS")
print("=" * 70)

print("\nTokenizing train dataset...")
tokenized_train = train_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=train_dataset.column_names
)
print(f"Train dataset tokenized: {len(tokenized_train)} samples")

print("\nTokenizing validation dataset...")
tokenized_val = val_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=val_dataset.column_names
)
print(f"Validation dataset tokenized: {len(tokenized_val)} samples")

print("\nTokenizing test dataset...")
tokenized_test = test_dataset.map(
    preprocess_function,
    batched=True,
    remove_columns=test_dataset.column_names
)
print(f"Test dataset tokenized: {len(tokenized_test)} samples")

# ============================================================================
# PART 10: SAVE TOKENIZED DATASETS AND MODEL
# ============================================================================
print("\n" + "=" * 70)
print("SAVING TOKENIZED DATA & MODEL")
print("=" * 70)

# Save tokenized datasets
with open('data/tokenized_train_dataset.pkl', 'wb') as f:
    pickle.dump(tokenized_train, f)
print(f"Saved: data/tokenized_train_dataset.pkl")

with open('data/tokenized_val_dataset.pkl', 'wb') as f:
    pickle.dump(tokenized_val, f)
print(f"Saved: data/tokenized_val_dataset.pkl")

with open('data/tokenized_test_dataset.pkl', 'wb') as f:
    pickle.dump(tokenized_test, f)
print(f"Saved: data/tokenized_test_dataset.pkl")

# Save tokenizer and model
tokenizer.save_pretrained('models/tokenizer')
model.save_pretrained('models/marianmt_model')
print(f"Saved: models/tokenizer/")
print(f"Saved: models/marianmt_model/")

# ============================================================================
# PART 11: SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("STEP 4 COMPLETE!")
print("=" * 70)

print(f"\nModel loaded: {model_name}")
print(f"Tokenizer loaded and configured")
print(f"All datasets tokenized")
print(f"Ready for fine-tuning!")
print(f"\nTokenized Dataset Sizes:")
print(f"   - Train: {len(tokenized_train)} samples")
print(f"   - Validation: {len(tokenized_val)} samples")
print(f"   - Test: {len(tokenized_test)} samples")
print(f"\nNext: STEP 5 - Train the Model")
print(f"   Run: Step5_Train_Model.py\n")
