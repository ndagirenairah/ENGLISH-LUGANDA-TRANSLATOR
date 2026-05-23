#!/usr/bin/env python3
"""Test model generalization on unseen cultural data."""

import json
from pathlib import Path
from translate_english_luganda import TransformerTranslator

print("\n" + "="*80)
print("TESTING CULTURAL GENERALIZATION ON UNSEEN DATA")
print("="*80)

translator = TransformerTranslator(
    en_lg_model_path="models/trained_model_final",
    lg_en_model_path="models/trained_model_kabale"
)

UNSEEN_CULTURAL_TESTS = [
    ("I greet you with respect", "Respectful greeting"),
    ("How do you greet elders in your culture?", "Respectful inquiry"),
    ("Please sit respectfully", "Culturally aware request"),
    ("Thank you for welcoming me to your home", "Gratitude with cultural context"),
    ("I respect your traditions and values", "Cultural respect"),
    ("What are your cultural customs?", "Cultural inquiry"),
    ("Our ancestors taught us wisdom", "Ancestral/cultural reference"),
    ("The clan gatherings are important", "Cultural gathering reference"),
    ("Respect for elders is fundamental", "Cultural value statement"),
    ("I want to learn about Buganda culture", "Interest in local culture"),
]

print("\n[EVALUATING CULTURAL GENERALIZATION]")
print("="*80)

results = []

for english_text, description in UNSEEN_CULTURAL_TESTS:
    try:
        result = translator.translate(
            text=english_text,
            source_lang="english",
            target_lang="luganda",
            num_beams=5,
            max_new_tokens=120
        )
        
        translation = result.get("translation", "")
        
        print(f"\n[{description}]")
        print(f"  EN: {english_text}")
        print(f"  LG: {translation}")
        
        results.append({
            "english": english_text,
            "luganda": translation,
            "description": description,
            "status": "success"
        })
        
    except Exception as e:
        print(f"\n[{description}]")
        print(f"  EN: {english_text}")
        print(f"  ERROR: {e}")
        
        results.append({
            "english": english_text,
            "luganda": "",
            "description": description,
            "status": "error",
            "error": str(e)
        })

print("\n" + "="*80)
print("CULTURAL GENERALIZATION TEST SUMMARY")
print("="*80)

successful = sum(1 for r in results if r["status"] == "success")
failed = sum(1 for r in results if r["status"] == "error")

print(f"\nTotal tests: {len(results)}")
print(f"  Successful: {successful} ({successful/len(results)*100:.1f}%)")
print(f"  Failed: {failed} ({failed/len(results)*100:.1f}%)")

print("\n[GENERALIZATION METRICS]")
print("="*80)

has_cultural_words = []
for result in results:
    if result["status"] == "success":
        lg_text = result["luganda"].lower()
        cultural_indicators = ["webale", "nnyo", "oli otya", "buganda", "kabaka", "ekika", "abantu"]
        has_cultural = sum(1 for word in cultural_indicators if word in lg_text)
        if has_cultural > 0:
            has_cultural_words.append(result)

cultural_alignment_score = (len(has_cultural_words) / successful * 100) if successful > 0 else 0
print(f"Translations with cultural content: {len(has_cultural_words)}/{successful} ({cultural_alignment_score:.1f}%)")

print("\n[SAVING RESULTS]")
output_file = "outputs/cultural_generalization_test.json"
Path("outputs").mkdir(exist_ok=True)
with open(output_file, "w") as f:
    json.dump({
        "test_date": str(Path("__file__").stat().st_mtime),
        "total_tests": len(results),
        "successful": successful,
        "failed": failed,
        "cultural_alignment_score": cultural_alignment_score,
        "results": results
    }, f, indent=2)
print(f"Results saved to: {output_file}")

print("\n[RECOMMENDATIONS]")
print("="*80)
if cultural_alignment_score < 50:
    print("⚠️  Low cultural alignment detected")
    print("   ACTION: Increase cultural_training dataset weight further")
    print("   ACTION: Add more cultural phrases to injection set")
    print("   ACTION: Train longer with reduced learning rate")
else:
    print("✓ Good cultural alignment achieved")
    print("  Model is learning culturally appropriate translations")

print("\nDone!")
