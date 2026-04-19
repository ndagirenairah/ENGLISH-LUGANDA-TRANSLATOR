# ============================================================================
# QUICK TEST WITH PRE-TRAINED MODEL
# ============================================================================
# Test translations immediately without training
# ============================================================================

print("=" * 70)
print("QUICK TEST - PRE-TRAINED LUGANDA MODEL")
print("=" * 70)

from transformers import MarianMTModel, MarianTokenizer
import torch

# Load PRE-TRAINED model (no training needed!)
print("\nLoading pre-trained Helsinki-NLP model...")
print("(This is trained on existing Luganda data)\n")

try:
    model_name = "Helsinki-NLP/opus-mt-en-lg"  # English → Luganda
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    print("✅ Model loaded successfully!\n")
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# ============================================================================
# TRANSLATION FUNCTION
# ============================================================================

def translate(english_text):
    """Translate English to Luganda"""
    try:
        tokens = tokenizer(english_text, return_tensors="pt", padding=True)
        translated = model.generate(**tokens, max_length=512)
        luganda_text = tokenizer.decode(translated[0], skip_special_tokens=True)
        return luganda_text
    except Exception as e:
        return f"[Error: {e}]"

# ============================================================================
# TEST EXAMPLES
# ============================================================================

print("=" * 70)
print("TEST EXAMPLES (Pre-trained Model)")
print("=" * 70)

test_sentences = [
    "How are you?",
    "I am Lugandan",
    "Thank you very much",
    "I love my country",
    "The king is respected",
    "We are learning machine learning"
]

print("\nTranslating English to Luganda:\n")

for english in test_sentences:
    luganda = translate(english)
    print(f"EN: {english}")
    print(f"LG: {luganda}\n")

# ============================================================================
# INTERACTIVE MODE
# ============================================================================

print("=" * 70)
print("INTERACTIVE MODE - Type Your Own Sentences")
print("=" * 70)

print("\n💡 Now you can type English sentences to translate to Luganda")
print("⏹️  Type 'quit' to exit\n")

while True:
    user_input = input("Enter English sentence: ").strip()
    
    if user_input.lower() in ['quit', 'exit', 'q']:
        print("\n✅ Done! Now run Step5 to train your own model.\n")
        break
    
    if not user_input:
        print("Please enter a sentence.\n")
        continue
    
    luganda = translate(user_input)
    print(f"→ {luganda}\n")

print("=" * 70)
print("NEXT STEPS")
print("=" * 70)
print("""
To train your own model:

1. Run Step3: python Step3_Data_Preprocessing.py
2. Run Step5: python Step5_Train_Model.py (30-45 min)
3. Then test: python Step6_Test_Model_Interactive.py

This will use YOUR trained model with cultural data!
""")
print("=" * 70)
