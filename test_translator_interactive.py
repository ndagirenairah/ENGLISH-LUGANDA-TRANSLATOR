#!/usr/bin/env python3
# ============================================================================
# INTERACTIVE ENGLISH-LUGANDA TRANSLATOR
# ============================================================================
# Run this script to test translations interactively
# python test_translator_interactive.py
# ============================================================================

import torch
import os
import sys
import time
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def main():
    print("\n" + "=" * 80)
    print("   ENGLISH-LUGANDA TRANSLATOR - INTERACTIVE TEST")
    print("=" * 80)
    
    # Check GPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"\n Device: {device}")
    if device.type == "cuda":
        print(f" GPU: {torch.cuda.get_device_name(0)}")
    
    # Load model
    print("\n[Loading Model...]")
    print("This may take 1-2 minutes on first run...")
    
    try:
        model_name = "Helsinki-NLP/opus-mt-en-mul"
        print(f"Loading: {model_name}")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model = model.to(device)
        print(f" Model loaded successfully!")
    except Exception as e:
        print(f" Error loading model: {e}")
        print("Make sure you have transformers installed: pip install transformers torch")
        return
    
    # Translation function
    def translate(text):
        """Translate English to Luganda"""
        try:
            # Tokenize
            inputs = tokenizer(
                text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate
            start_time = time.time()
            with torch.no_grad():
                generated = model.generate(
                    **inputs,
                    max_length=120,
                    num_beams=5,
                    no_repeat_ngram_size=3
                )
            elapsed = time.time() - start_time
            
            # Decode
            translation = tokenizer.decode(generated[0], skip_special_tokens=True)
            return translation, elapsed
        except Exception as e:
            return f"Error: {e}", 0
    
    # Interactive loop
    print("\n" + "=" * 80)
    print("  INTERACTIVE MODE - Type English text to translate to Luganda")
    print("=" * 80)
    print("\nExamples you can try:")
    print("   Hello, how are you?")
    print("   What is your name?")
    print("   Good morning!")
    print("   Thank you very much")
    print("   Where is the bathroom?")
    print("   I love learning languages")
    print("   The weather is beautiful today")
    print("\nCommands:")
    print("   Type English to translate")
    print("   Type 'help' for options")
    print("   Type 'quit' to exit\n")
    
    history = []
    
    while True:
        try:
            # Get user input
            english = input(" English: ").strip()
            
            # Handle commands
            if english.lower() in ['quit', 'exit', 'q']:
                print("\n Thank you for testing! Goodbye!")
                break
            
            if english.lower() == 'help':
                print("""

       TRANSLATION TESTER COMMANDS        


quit/exit/q     - Exit the program
help            - Show this help
history         - Show all translations
clear           - Clear history
stats           - Show model info

Tips:
   Shorter sentences work better
   Simple grammar is easier to translate
   First translation is slower (model loading)
   Subsequent translations are much faster

                """)
                continue
            
            if english.lower() == 'history':
                if not history:
                    print(" No translations yet\n")
                else:
                    print("\n" + "=" * 80)
                    print("   TRANSLATION HISTORY")
                    print("=" * 80)
                    for i, (en, lg, elapsed) in enumerate(history, 1):
                        print(f"\n{i}. EN: {en}")
                        print(f"   LG: {lg}")
                        print(f"     {elapsed:.2f}s")
                    print("\n" + "=" * 80 + "\n")
                continue
            
            if english.lower() == 'clear':
                history.clear()
                print(" History cleared\n")
                continue
            
            if english.lower() == 'stats':
                total_params = sum(p.numel() for p in model.parameters())
                print(f"\n Model Statistics:")
                print(f"   Model: {model_name}")
                print(f"   Parameters: {total_params:,}")
                print(f"   Device: {device}")
                print(f"   Total translations: {len(history)}")
                if history:
                    avg_time = sum(t[2] for t in history) / len(history)
                    total_time = sum(t[2] for t in history)
                    print(f"   Average time/translation: {avg_time:.2f}s")
                    print(f"   Total time: {total_time:.2f}s")
                print()
                continue
            
            if not english:
                continue
            
            # Translate
            print(" Translating...", end=" ", flush=True)
            luganda, elapsed = translate(english)
            print("\r" + " " * 30 + "\r", end="")  # Clear the "Translating..." message
            
            # Display result
            print(f" Luganda:  {luganda}")
            print(f"  Time:      {elapsed:.2f}s")
            
            # Add to history
            history.append((english, luganda, elapsed))
            
            # Show translation number
            print(f"   (Translation #{len(history)})\n")
        
        except KeyboardInterrupt:
            print("\n\n Interrupted. Goodbye!")
            break
        except Exception as e:
            print(f" Error: {e}\n")
    
    # Final summary
    if history:
        print("\n" + "=" * 80)
        print(f"  SUMMARY: {len(history)} translations completed")
        print("=" * 80)
        print("\nYour Translations:")
        for en, lg, elapsed in history:
            print(f"\n  EN: {en}")
            print(f"  LG: {lg} ({elapsed:.2f}s)")
        print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
