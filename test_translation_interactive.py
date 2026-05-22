#!/usr/bin/env python3
"""
Interactive Translation Tester
Test English to Luganda translations in real-time
"""

import requests
import sys

API_URL = "http://127.0.0.1:5000/translate"

def test_translation(english_text):
    """Test a single translation"""
    try:
        response = requests.post(API_URL, json={"text": english_text})
        if response.status_code == 200:
            result = response.json()
            translation = result.get('translation', 'ERROR')
            confidence = result.get('confidence', 'N/A')
            return translation, confidence, None
        else:
            return None, None, f"Error {response.status_code}: {response.text}"
    except requests.exceptions.ConnectionError:
        return None, None, "❌ Cannot connect to Flask server. Is it running on port 5000?"
    except Exception as e:
        return None, None, f"Error: {str(e)}"

def main():
    """Main interactive loop"""
    print("\n" + "="*70)
    print("🌍 ENGLISH-LUGANDA TRANSLATOR - INTERACTIVE TEST")
    print("="*70)
    print("\nType English sentences to translate to Luganda")
    print("Type 'quit' or 'exit' to stop")
    print("Type 'help' for options")
    print("="*70 + "\n")
    
    test_count = 0
    
    while True:
        try:
            english_input = input("EN> ").strip()
            
            if not english_input:
                continue
                
            if english_input.lower() in ['quit', 'exit', 'q']:
                print(f"\n✓ Tested {test_count} translations. Goodbye! 👋")
                break
                
            if english_input.lower() == 'help':
                print("""
╔════════════════════════════════════════╗
║          TRANSLATION TESTER HELP        ║
╚════════════════════════════════════════╝

Commands:
  quit/exit/q     - Exit the program
  help            - Show this help message
  test SAMPLES    - Run 5 test samples
  
Examples to try:
  - "Hello, how are you?"
  - "What is your name?"
  - "Good morning"
  - "Thank you very much"
  - "Where is the bathroom?"
  - "I love learning languages"
  - "The weather is nice today"
  - "Can you help me?"
  
Tips:
  - Shorter sentences = faster & usually better
  - Simple grammar often works better
  - Wait a moment for GPU to respond
  
""")
                continue
                
            if english_input.lower() == 'test samples':
                test_samples = [
                    "Hello, how are you?",
                    "What is your name?",
                    "Good morning",
                    "Thank you very much",
                    "Where is the bathroom?"
                ]
                print("\n" + "="*70)
                print("Running 5 test samples...")
                print("="*70 + "\n")
                
                for sample in test_samples:
                    translation, confidence, error = test_translation(sample)
                    test_count += 1
                    
                    if error:
                        print(f"❌ {error}")
                    else:
                        print(f"EN: {sample}")
                        print(f"LG: {translation}")
                        if confidence != 'N/A':
                            print(f"⭐ {confidence}")
                        print()
                continue
            
            # Regular translation
            print("\n⏳ Translating...", end='', flush=True)
            translation, confidence, error = test_translation(english_input)
            test_count += 1
            
            print("\r" + " "*50 + "\r", end='')  # Clear loading message
            
            if error:
                print(f"❌ {error}\n")
            else:
                print(f"\nEN: {english_input}")
                print(f"LG: {translation}")
                if confidence and confidence != 'N/A':
                    print(f"⭐ Confidence: {confidence}")
                print()
                
        except KeyboardInterrupt:
            print(f"\n\n✓ Tested {test_count} translations. Goodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()

if __name__ == "__main__":
    # Check if Flask server is running
    try:
        response = requests.get("http://127.0.0.1:5000/")
        if response.status_code == 200:
            main()
        else:
            print("❌ Flask server not responding properly")
            print("Make sure the Flask app is running: python app.py")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server on http://127.0.0.1:5000/")
        print("\nTo start the server, run in a terminal:")
        print("  cd d:\\ENGLISH-LUGANDA\\ TRANSLATOR")
        print("  python app.py")
    except KeyboardInterrupt:
        print("\nGoodbye! 👋")
