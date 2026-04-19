#!/usr/bin/env python
import torch
from transformers import MarianMTModel, MarianTokenizer

print("=" * 70)
print("🔬 TESTING BOTH MODEL DIRECTIONS")
print("=" * 70)

# Test 1: EN → MUL (what we're using)
print("\n1️⃣  MODEL: Helsinki-NLP/opus-mt-en-mul (English → Multilingual)")
print("-" * 70)

try:
    tokenizer_en_mul = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-en-mul')
    model_en_mul = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-en-mul')
    
    test_text = "How are you today?"
    prefixed = f">>lug<< {test_text}"
    
    print(f"Input: {test_text}")
    print(f"With prefix: {prefixed}")
    
    inputs = tokenizer_en_mul(prefixed, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = model_en_mul.generate(**inputs, max_length=512)
    translation = tokenizer_en_mul.decode(outputs[0], skip_special_tokens=True)
    
    print(f"Output: {translation}")
    print("✅ Model works")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: MUL → EN (reverse direction)
print("\n2️⃣  MODEL: Helsinki-NLP/opus-mt-mul-en (Multilingual → English)")
print("-" * 70)

try:
    tokenizer_mul_en = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-mul-en')
    model_mul_en = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-mul-en')
    
    # Test what languages this supports
    print("Testing multilingual model with different language prefixes...")
    
    test_text = "girl"
    for lang_prefix in [">>lug<<", ">>ny<<", ">>swa<<"]:
        prefixed = f"{lang_prefix} {test_text}"
        inputs = tokenizer_mul_en(prefixed, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model_mul_en.generate(**inputs, max_length=512)
        translation = tokenizer_mul_en.decode(outputs[0], skip_special_tokens=True)
        print(f"  {lang_prefix} {test_text} → {translation}")
    
    print("✅ Model works")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 70)
