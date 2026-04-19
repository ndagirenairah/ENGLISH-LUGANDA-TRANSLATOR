# ============================================================================
# STEP 6: TEST MODEL ON UNSEEN DATA
# ============================================================================
# This script tests the trained model on new Luganda sentences
# and generates English translations
# ============================================================================

print("=" * 70)
print("ðŸš€ STEP 6: TESTING ON UNSEEN DATA")
print("=" * 70)

import pickle
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd

# ============================================================================
# PART 1: LOAD TRAINED MODEL
# ============================================================================
print("\\nðŸ¤– Loading trained model...\\n")

try:
    model = AutoModelForSeq2SeqLM.from_pretrained('models/trained_model')
    tokenizer = AutoTokenizer.from_pretrained('models/trained_model')
    print("âœ… Model loaded successfully!")
except Exception as e:
    print(f"âŒ Error loading model: {e}")
    print("   Make sure Step 5 (Training) was completed first")
    exit()

# Create translation pipeline
translator = pipeline(
    "translation",
    model=model,
    tokenizer=tokenizer,
    src_lang="lug",
    tgt_lang="eng"
)
print("âœ… Translation pipeline created")

# ============================================================================
# PART 2: LOAD TEST DATA
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“¥ LOADING TEST DATA")
print("=" * 70)

with open('data/tokenized_test_dataset.pkl', 'rb') as f:
    test_dataset = pickle.load(f)

# Also load original test data for reference
test_df = pd.read_csv('data/test_data.csv')

print(f"\\nâœ… Test dataset loaded: {len(test_dataset)} samples")
print(f"âœ… Test data CSV loaded: {len(test_df)} samples")

# ============================================================================
# PART 3: GENERATE TRANSLATIONS FOR TEST SET
# ============================================================================
print("\\n" + "=" * 70)
print("âœï¸ GENERATING TRANSLATIONS")
print("=" * 70)

print(f"\\nâ³ Generating translations for {len(test_df)} test samples...")

predictions = []
references = []

# Process in batches for efficiency
batch_size = 32
for i in range(0, len(test_df), batch_size):
    batch = test_df.iloc[i:i+batch_size]
    luganda_batch = batch['luganda_clean'].tolist()
    english_batch = batch['english_clean'].tolist()
    
    # Translate each sentence
    for luganda_sent in luganda_batch:
        try:
            result = translator(luganda_sent, max_length=128)
            translation = result[0]['translation_text']
            predictions.append(translation)
        except:
            predictions.append("[Translation Error]")
    
    references.extend(english_batch)
    
    if (i // batch_size + 1) % 5 == 0:
        print(f"   âœ“ Processed {min(i + batch_size, len(test_df))}/{len(test_df)} samples")

print(f"\\nâœ… All translations generated!")

# ============================================================================
# PART 4: CREATE COMPARISON DATAFRAME
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“Š COMPARISON: REFERENCE vs PREDICTED")
print("=" * 70)

results_df = pd.DataFrame({
    'luganda': test_df['luganda_clean'].values[:len(predictions)],
    'english_reference': references[:len(predictions)],
    'english_predicted': predictions
})

print(f"\\nResults DataFrame created with {len(results_df)} samples")

# ============================================================================
# PART 5: DISPLAY SAMPLE TRANSLATIONS
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ‘€ SAMPLE TRANSLATIONS (First 10)")
print("=" * 70)

for idx in range(min(10, len(results_df))):
    row = results_df.iloc[idx]
    print(f"\\n{idx+1}. Translation Pair:")
    print(f"   🇺🇬 Luganda Input:")
    print(f"      {row['luganda']}")
    print(f"   ✅ Reference English (from dataset):")
    print(f"      {row['english_reference']}")
    print(f"   🤖 Predicted English (by our model):")
    print(f"      {row['english_predicted']}")
    print(f"   {'✅ MATCH!' if row['english_predicted'].lower()[:20] == row['english_reference'].lower()[:20] else '   (Different translation)'}")

# ============================================================================
# PART 6: SAVE DETAILED RESULTS
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ’¾ SAVING RESULTS")
print("=" * 70)

output_csv = 'outputs/translation_results.csv'
results_df.to_csv(output_csv, index=False)
print(f"\\nâœ… Results saved to: {output_csv}")

# Create a nicer formatted version
with open('outputs/translation_results.txt', 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\\n")
    f.write("LUGANDA-ENGLISH TRANSLATOR - TEST RESULTS\\n")
    f.write("=" * 80 + "\\n\\n")
    
    for idx, row in results_df.iterrows():
        f.write(f"\\nTranslation #{idx+1}:\\n")
        f.write(f"-" * 80 + "\\n")
        f.write(f"Luganda Input:\\n  {row['luganda']}\\n\\n")
        f.write(f"Reference Translation (from dataset):\\n  {row['english_reference']}\\n\\n")
        f.write(f"Model Prediction:\\n  {row['english_predicted']}\\n\\n")

print(f"âœ… Formatted results saved to: outputs/translation_results.txt")

# ============================================================================
# PART 7: INTERACTIVE TRANSLATION (Single Sentences)
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ’¬ INTERACTIVE TRANSLATION")
print("=" * 70)

print("\\nYou can now test with your own sentences!")
print("\\nExample Luganda phrases to try:")
print("  - 'Ndi Muganda' (I am Lugandan)")
print("  - 'Eggulo lya buggulo' (It's a good time)")
print("  - 'Ssebo, jooga mweraba' (Sir/Ma'am, please speak slowly)")

print("\\nTo test your own sentences, modify the code below:")
print("""
# UNCOMMENT LINES BELOW TO TEST CUSTOM SENTENCES:

custom_sentences = [
    "Ndi Muganda",
    "Nkwatira owange",
    "Erya kiwandiiko"
]

print("\\n" + "="*70)
print("CUSTOM TRANSLATION TESTS")
print("="*70)

for sentence in custom_sentences:
    result = translator(sentence, max_length=128)
    translation = result[0]['translation_text']
    print(f"\\nðŸ‡ºðŸ‡¬ {sentence}")
    print(f"ðŸ‡¬ðŸ‡§ {translation}")
""")

# ============================================================================
# PART 8: SUMMARY STATISTICS
# ============================================================================
print("\\n" + "=" * 70)
print("ðŸ“Š TRANSLATION STATISTICS")
print("=" * 70)

print(f"\\nTotal test samples: {len(results_df)}")
print(f"Average Luganda sentence length: {results_df['luganda'].str.len().mean():.0f} characters")
print(f"Average predicted English length: {results_df['english_predicted'].str.len().mean():.0f} characters")
print(f"Average reference English length: {results_df['english_reference'].str.len().mean():.0f} characters")

# Count translation errors
error_count = (results_df['english_predicted'] == "[Translation Error]").sum()
print(f"\\nTranslation errors: {error_count}/{len(results_df)}")

# ============================================================================
# PART 9: SUMMARY
# ============================================================================
print("\\n" + "=" * 70)
print("âœ… STEP 6 COMPLETE!")
print("=" * 70)

print(f"\\nâœ“ Tested on {len(results_df)} unseen Luganda sentences")
print(f"âœ“ Generated English translations")
print(f"âœ“ Compared with reference translations from dataset")
print(f"\\nðŸ“„ Results saved:")
print(f"   - CSV: outputs/translation_results.csv")
print(f"   - TXT: outputs/translation_results.txt")
print(f"\\nðŸŽ¯ Next: STEP 7 - Evaluate with BLEU Score")
print(f"   Run: Step7_Evaluate_BLEU.py\\n")

