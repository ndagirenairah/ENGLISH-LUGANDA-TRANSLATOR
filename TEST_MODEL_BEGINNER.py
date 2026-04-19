#!/usr/bin/env python3
# ============================================================================
# 🧪 BEGINNER'S MODEL TESTING GUIDE
# ============================================================================
# This script shows how the trained model translates Luganda to English
# Easy to understand + examples you can modify
# ============================================================================

print("=" * 70)
print("🧪 TESTING YOUR LUGANDA-ENGLISH TRANSLATOR MODEL")
print("=" * 70)
print()

# ============================================================================
# STEP 1: IMPORT LIBRARIES
# ============================================================================
print("📦 Step 1: Loading libraries...")
print("   (This is like loading the tools we need)")
print()

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    import pandas as pd
    print("   ✅ Libraries loaded successfully!")
except Exception as e:
    print(f"   ❌ Error loading libraries: {e}")
    exit()

print()

# ============================================================================
# STEP 2: LOAD THE TRAINED MODEL
# ============================================================================
print("=" * 70)
print("🤖 Step 2: Loading the trained model...")
print("   (This downloads our model from disk/internet)")
print()

try:
    # We'll use a simple pre-trained model for testing
    # In real scenario, this would be your trained model
    model_name = "facebook/mbart-large-50-many-to-one-mmt"
    print(f"   📥 Loading: {model_name}")
    
    # Load tokenizer (converts text to numbers)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("   ✅ Tokenizer loaded (converts text to numbers)")
    
    # Load model (does the translation)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    print("   ✅ Model loaded (ready to translate)")
    
    # Create translator pipeline
    translator = pipeline('translation_mul_to_en', model=model, tokenizer=tokenizer)
    print("   ✅ Translation pipeline ready!")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("   💡 Tip: Make sure you have internet to download the model")
    exit()

print()

# ============================================================================
# STEP 3: TEST WITH SIMPLE EXAMPLES
# ============================================================================
print("=" * 70)
print("📝 Step 3: Testing with Luganda sentences")
print("=" * 70)
print()

# Sample Luganda sentences for testing
test_sentences = [
    "Oli otya",                    # How are you?
    "Webale nnyo",                # Thank you very much
    "Ndi Muganda",                # I am Lugandan
    "Ssebo",                      # Sir
    "Nnyabo",                     # Ma'am
]

print("Here are our test sentences:\n")

# Create results list
results = []

for i, luganda_text in enumerate(test_sentences, 1):
    print(f"{i}. 🇺🇬 Luganda: {luganda_text}")
    
    try:
        # Translate
        translation = translator(luganda_text, max_length=512)
        english_text = translation[0]['translation_text']
        
        print(f"   🇬🇧 English: {english_text}")
        print(f"   ✅ Translation successful!")
        
        results.append({
            'Luganda': luganda_text,
            'English': english_text,
            'Status': '✅ Success'
        })
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append({
            'Luganda': luganda_text,
            'English': 'ERROR',
            'Status': f'❌ {str(e)[:30]}...'
        })
    
    print()

print()

# ============================================================================
# STEP 4: SAVE RESULTS TO CSV
# ============================================================================
print("=" * 70)
print("💾 Step 4: Saving results")
print("=" * 70)
print()

try:
    df = pd.DataFrame(results)
    df.to_csv('test_results.csv', index=False)
    print("✅ Results saved to: test_results.csv")
    print()
    print("📊 Summary:")
    print(df.to_string(index=False))
except Exception as e:
    print(f"❌ Error saving: {e}")

print()

# ============================================================================
# STEP 5: UNDERSTANDING THE RESULTS
# ============================================================================
print("=" * 70)
print("🎯 Step 5: Understanding the results")
print("=" * 70)
print()

print("📚 What's happening:")
print()
print("1. INPUT")
print("   - We provide a Luganda sentence")
print("   - Tokenizer converts it to numbers")
print()
print("2. MODEL PROCESSING")
print("   - Encoder (first half): Understands Luganda")
print("   - Attention: Focuses on important words")
print("   - Decoder (second half): Generates English")
print()
print("3. OUTPUT")
print("   - Model produces English text")
print("   - We display the translation")
print()

print("=" * 70)
print("🎉 TEST COMPLETE!")
print("=" * 70)
print()
print("💡 Next steps:")
print("   1. Open test_results.csv to see all translations")
print("   2. Try modifying the test_sentences list above")
print("   3. Add your own Luganda sentences to test")
print("   4. Look at quality of translations")
print()
print("📊 Metrics to check:")
print("   - Does it understand Luganda?")
print("   - Is the English grammatically correct?")
print("   - Does it preserve cultural markers? (ssebo, nnyabo)")
print("   - How fast are the translations? (should be <1 sec each)")
print()
