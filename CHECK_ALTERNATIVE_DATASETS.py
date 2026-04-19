#!/usr/bin/env python3
"""
Check available Luganda datasets and alternatives
"""

from datasets import load_dataset
from huggingface_hub import login

# Authenticate with stored token
try:
    login()
except:
    print("ℹ️ Using stored authentication")

print("=" * 80)
print("🔍 CHECKING ALTERNATIVE LUGANDA DATASETS")
print("=" * 80)

# Try JW300 dataset
print("\n📦 TEST 1: Trying JW300 (Open source, 41,000+ pairs)")
print("-" * 80)
try:
    jw300 = load_dataset("jw300", language_pair="en-lg")
    print(f"✅ SUCCESS! JW300 loaded")
    print(f"   Train samples: {len(jw300['train'])}")
    print(f"   Validation samples: {len(jw300.get('validation', []))}")
    print(f"   Total: {len(jw300['train'])} + {len(jw300.get('validation', []))} samples")
    if len(jw300['train']) > 0:
        print(f"\n   📝 Sample:")
        print(f"      English: {jw300['train'][0]['en'][:60]}...")
        print(f"      Luganda: {jw300['train'][0]['lg'][:60]}...")
except Exception as e:
    print(f"❌ JW300 not available: {str(e)[:100]}")

# Try OPUS-100
print("\n\n📦 TEST 2: Trying OPUS MT datasets")
print("-" * 80)
try:
    opus = load_dataset("opus_books", language_pair="en-lg")
    print(f"✅ OPUS Books available")
    print(f"   Samples: {len(opus['train'])}")
except Exception as e:
    print(f"ℹ️  OPUS not available: {str(e)[:60]}")

# Try Tatoeba
print("\n\n📦 TEST 3: Trying Tatoeba")
print("-" * 80)
try:
    tatoeba = load_dataset("tatoeba", language_pair="eng-lug")
    print(f"✅ Tatoeba available")
    print(f"   Samples: {len(tatoeba['train'])}")
except Exception as e:
    print(f"ℹ️  Tatoeba not available: {str(e)[:60]}")

print("\n" + "=" * 80)
print("📋 SUMMARY: OPTIONS FOR YOUR TRAINING")
print("=" * 80)

print("""
OPTION 1: Use JW300 (Recommended - if available)
  ✅ 41,000+ verified samples
  ✅ No authentication needed
  ✅ High quality religious texts
  Usage: Load with "jw300" dataset ID

OPTION 2: Use supplementary + custom data
  ✅ No waiting time
  ✅ 79 samples for testing
  ✓ Sunbird AI (5 samples)
  ✓ Makerere NLP (5 samples)  
  ✓ Cultural data (69 samples)
  Usage: Run Step2_Load_MultiSource_Dataset.py

OPTION 3: Wait for Kambale dataset approval
  ✅ 25,000+ official samples
  ⏳ Must wait for access approval (24 hours)
  ✓ Highest quality official corpus
  
RECOMMENDED PLAN:
  1. Request access to Kambale (1 minute)
  2. Start training with JW300 or supplementary now (30 min)
  3. When Kambale approved: Retrain with best dataset (45 min)
""")

print("=" * 80)
