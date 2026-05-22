# ============================================================================
# INTERACTIVE TRANSLATION TESTING FOR GOOGLE COLAB
# ============================================================================
# Run this cell in Colab to test translations interactively
# Paste this code into a Colab cell and run it

# CELL 1: SETUP (Run this first)
# ============================================================================
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import os

# Load model
MODEL_NAME = "Helsinki-NLP/opus-mt-en-mul"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("[LOADING MODEL]")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
model = model.to(device)
print(f"✓ Model loaded on {device}\n")

def translate_text(english_text):
    """Translate English to Luganda"""
    inputs = tokenizer(english_text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        generated = model.generate(**inputs, max_length=120, num_beams=5, no_repeat_ngram_size=3)
    
    translation = tokenizer.decode(generated[0], skip_special_tokens=True)
    return translation

# CELL 2: TEST WITH YOUR OWN TEXT
# ============================================================================
# Edit the text below and run this cell multiple times

english_text = "Hello, how are you?"

print(f"EN: {english_text}")
print(f"LG: {translate_text(english_text)}")

# ============================================================================
# Try these examples:
# ============================================================================
# english_text = "What is your name?"
# english_text = "Good morning"
# english_text = "Thank you very much"
# english_text = "Where is the bathroom?"
# english_text = "I love learning languages"
# english_text = "The weather is nice today"
# english_text = "Can you help me?"
# english_text = "My name is Nairah"
# english_text = "Welcome to Uganda"
# english_text = "Please speak slowly"

# CELL 3: BATCH TEST (Multiple sentences at once)
# ============================================================================
test_sentences = [
    "Hello, how are you?",
    "What is your name?",
    "Good morning",
    "Thank you very much",
    "Where is the bathroom?",
    "I love learning languages",
    "The weather is nice today",
    "Can you help me?",
]

print("[BATCH TRANSLATION TEST]")
print("=" * 70)

for en_text in test_sentences:
    lg_text = translate_text(en_text)
    print(f"\nEN: {en_text}")
    print(f"LG: {lg_text}")

print("\n" + "=" * 70)
print("✓ Batch test complete!")
