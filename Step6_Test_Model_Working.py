#!/usr/bin/env python
# ============================================================================
# STEP 6: TEST MODEL - WORKING VERSION
# ============================================================================
# Tests the translation model with example sentences
# ============================================================================

print("=" * 80)
print("🇬🇧🇺🇬 ENGLISH-LUGANDA TRANSLATION TESTER 🇬🇧🇺🇬")
print("=" * 80)

import torch
from transformers import MarianMTModel, MarianTokenizer

print("\n⏳ Loading model and tokenizer...")

try:
    # Load the base model (Helsinki-NLP OPUS-MT - Multilingual to English)
    # This model translates FROM multiple languages (including Luganda) TO English
    model_name = 'Helsinki-NLP/opus-mt-mul-en'
    
    print(f"Using model: {model_name}")
    print(f"Model type: Multilingual → English Translation")
    print(f"Device: {'GPU (CUDA)' if torch.cuda.is_available() else 'CPU'}\n")
    
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    
    # Move to GPU if available
    if torch.cuda.is_available():
        model = model.to('cuda')
    
    print("✅ Model loaded successfully!\n")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    exit(1)

# ============================================================================
# Translation Function
# ============================================================================

def translate_luganda_to_english(luganda_text):
    """Translate Luganda text to English"""
    try:
        # Tokenize input
        inputs = tokenizer(luganda_text, return_tensors="pt", padding=True)
        
        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.to('cuda') for k, v in inputs.items()}
        
        # Generate translation
        with torch.no_grad():
            outputs = model.generate(**inputs, max_length=512)
        
        # Decode translation
        translation = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return translation.strip()
    
    except Exception as e:
        return f"[Error: {str(e)}]"

# ============================================================================
# Test Examples
# ============================================================================

print("=" * 80)
print("📝 TESTING WITH EXAMPLE SENTENCES")
print("=" * 80 + "\n")

examples = [
    ("Oli otya", "How are you?"),
    ("Ndi Muganda", "I am Lugandan"),
    ("Webale nnyo", "Thank you very much"),
    ("Kabaka yalambula abantu", "The Kabaka visited people"),
    ("Ndi wa kika kya Mmamba", "I belong to Mmamba clan"),
    ("Kabaka assibwamu ekitiibwa", "The Kabaka is respected"),
    ("Ssegeza abakulu", "Respect the elders"),
]

for i, (luganda, english_meaning) in enumerate(examples, 1):
    print(f"Example {i}:")
    print(f"  🇺🇬 Luganda:      {luganda}")
    print(f"  Meaning:         {english_meaning}")
    
    translation = translate_luganda_to_english(luganda)
    print(f"  🇬🇧 Translation:   {translation}\n")

# ============================================================================
# Interactive Mode
# ============================================================================

print("=" * 80)
print("🎤 INTERACTIVE MODE")
print("=" * 80)
print("\n💡 You can now test with your own Luganda sentences!")
print("⏹️  Type 'quit' or 'exit' to stop\n")

while True:
    user_input = input("🇺🇬 Enter Luganda text: ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("\n👋 Testing complete! Thank you!\n")
        break
    
    if not user_input:
        print("⚠️  Please enter some text.\n")
        continue
    
    translation = translate_luganda_to_english(user_input)
    print(f"🇬🇧 Translation: {translation}\n")

print("=" * 80)
