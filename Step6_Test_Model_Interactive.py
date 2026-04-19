# ============================================================================
# STEP 6: TEST MODEL WITH INTERACTIVE INPUT
# ============================================================================
# Simple, practical testing of your trained model
# You can test with custom Luganda sentences
# ============================================================================

print("=" * 70)
print("TEST MODEL - INTERACTIVE VERSION")
print("=" * 70)

import torch

# ============================================================================
# PART 1: LOAD MODEL
# ============================================================================
print("\nLoading model...\n")

try:
    # Updated to use multilingual-to-English model for better Luganda translation
    from transformers import MarianMTModel, MarianTokenizer
    
    model_name = 'Helsinki-NLP/opus-mt-mul-en'  # Multilingual to English
    print(f"Model: {model_name}")
    print(f"Translation direction: Luganda → English\n")
    
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    print("   Make sure you have internet to download the model")
    exit()

print("✅ Translation pipeline ready\n")

# Load quality fixer for improving outputs
try:
    from luganda_translation_fixer import LugandaTranslationFixer
    fixer = LugandaTranslationFixer()
    print("✅ Luganda quality fixer loaded\n")
    HAS_FIXER = True
except ImportError:
    HAS_FIXER = False
    print("⚠️  Quality fixer not available (install luganda_translation_fixer)\n")

# ============================================================================
# PART 2: HELPER FUNCTION
# ============================================================================

def translate_sentence(luganda_text):
    """Translate a single Luganda sentence to English"""
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
        
        # Apply quality fixes if available
        if HAS_FIXER:
            translation = fixer.apply_corrections(translation)
        
        return translation.strip()
    except Exception as e:
        return f"[Error: {str(e)}]"

# ============================================================================
# PART 3: INTERACTIVE TESTING
# ============================================================================
print("=" * 70)
print("INTERACTIVE TRANSLATION TEST")
print("=" * 70)

print("\nThere are 3 ways to test:\n")

print("METHOD 1: TEST WITH EXAMPLES (Running now)")
print("-" * 70)

# Quick test with examples
examples = [
    ("Oli otya", "How are you?"),
    ("Ndi Muganda", "I am Lugandan"),
    ("Webale nnyo", "Thank you very much"),
    ("Kabaka yalambula abantu", "The Kabaka visited people")
]

print("\nTesting with example sentences:\n")
for luganda, english_meaning in examples:
    translation = translate_sentence(luganda)
    print(f"INPUT (Luganda):     {luganda}")
    print(f"Meaning:             {english_meaning}")
    print(f"OUTPUT (English):    {translation}")
    print()

# ============================================================================
# METHOD 2: HARDCODED CUSTOM SENTENCES
# ============================================================================
print("\n" + "=" * 70)
print("METHOD 2: HARDCODED CUSTOM SENTENCES")
print("=" * 70)

print("\nTo test with your own sentences, edit the list below:")
print("(Uncomment and modify the lines)\n")

# EDIT THIS LIST TO TEST CUSTOM SENTENCES:
custom_test_sentences = [
    # "Ndi wa kika kya Mmamba",           # I belong to Mmamba clan
    # "Kabaka assibwamu ekitiibwa",      # The Kabaka is respected
    # "Ssegeza abakulu",                 # Respect the elders
]

if custom_test_sentences:
    print("Testing custom sentences:\n")
    for sentence in custom_test_sentences:
        translation = translate_sentence(sentence)
        print(f"INPUT (Luganda):     {sentence}")
        print(f"OUTPUT (English):    {translation}")
        print()

# ============================================================================
# METHOD 3: INTERACTIVE INPUT (TYPE WHILE RUNNING)
# ============================================================================
print("\n" + "=" * 70)
print("METHOD 3: INTERACTIVE INPUT")
print("=" * 70)

print("\nTo type sentences while the program runs, this section is now ENABLED:")
print("(ENABLE_INTERACTIVE = True)\n")

ENABLE_INTERACTIVE = True  # <-- NOW ENABLED FOR INTERACTIVE MODE

if ENABLE_INTERACTIVE:
    print("=" * 70)
    print("🎤 INTERACTIVE MODE - TYPE YOUR LUGANDA SENTENCES")
    print("=" * 70)
    print("\n✨ Type any Luganda sentence to get English translation")
    print("\n📝 Examples to try:")
    print("  • Oli otya (How are you?)")
    print("  • Ndi Muganda (I am Lugandan)")
    print("  • Webale nnyo (Thank you very much)")
    print("  • Kabaka yalambula abantu (Kabaka visited people)")
    print("  • Ndi wa kika kya Mmamba (I'm from Mmamba clan)")
    print("  • Kabaka assibwamu ekitiibwa (Kabaka is respected)")
    print("\n⏹️  Type 'quit' or 'exit' to stop")
    print("\n" + "=" * 70 + "\n")
    
    while True:
        user_input = input("🇺🇬 Enter Luganda sentence: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!\n")
            break
        
        if not user_input:
            print("⚠️  Please enter a sentence.\n")
            continue
        
        translation = translate_sentence(user_input)
        print(f"🇬🇧 Translation: {translation}\n")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("✨ INTERACTIVE TEST READY!")
print("=" * 70 + "\n")
