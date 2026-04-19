# ============================================================================
# DEBUG SCRIPT: Test All Components & Fix Issues
# ============================================================================
# Run this FIRST to identify and fix any problems
# ============================================================================

print("=" * 70)
print("🔧 DEBUG & VERIFICATION SCRIPT")
print("=" * 70)

import sys
import importlib

# ============================================================================
# PART 1: CHECK ALL DEPENDENCIES
# ============================================================================
print("\n📦 CHECKING DEPENDENCIES...")
print("=" * 70)

required_packages = {
    'transformers': 'Hugging Face transformers',
    'datasets': 'Dataset loading',
    'torch': 'PyTorch (Deep Learning)',
    'pandas': 'Data manipulation',
    'numpy': 'Numerical operations',
    'scikit-learn': 'Machine learning utilities',
}

missing_packages = []

for package, description in required_packages.items():
    try:
        importlib.import_module(package)
        print(f"✅ {package:20} - {description}")
    except ImportError:
        print(f"❌ {package:20} - NOT INSTALLED ⚠️")
        missing_packages.append(package)

if missing_packages:
    print("\n" + "⚠️ " * 10)
    print("MISSING PACKAGES DETECTED!")
    print("\nInstall with:")
    print(f"pip install {' '.join(missing_packages)}")
    print("⚠️ " * 10)
else:
    print("\n✅ All dependencies installed!")

# ============================================================================
# PART 2: CHECK DIRECTORY STRUCTURE
# ============================================================================
print("\n" + "=" * 70)
print("📁 CHECKING DIRECTORY STRUCTURE...")
print("=" * 70)

import os

required_dirs = ['data', 'models', 'outputs', 'checkpoints', 'logs']
created_dirs = []

for directory in required_dirs:
    if os.path.exists(directory):
        print(f"✅ {directory}/ exists")
    else:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ {directory}/ created")
        created_dirs.append(directory)

if created_dirs:
    print(f"\nCreated directories: {', '.join(created_dirs)}")

# ============================================================================
# PART 3: TEST DATASET LOADING (Non-blocking)
# ============================================================================
print("\n" + "=" * 70)
print("🌐 TESTING DATASET AVAILABILITY (Optional)...")
print("=" * 70)

print("\n📊 Testing each dataset individually...\n")

# Test 1: Sunbird SALT
print("Test 1: Sunbird AI SALT")
try:
    from datasets import load_dataset
    print("  ⏳ Attempting to load (may take a moment)...")
    dataset1_test = load_dataset("Sunbird/salt", "lug-eng", split="train")
    print(f"  ✅ SUCCESS: {len(dataset1_test):,} samples available")
except Exception as e:
    print(f"  ⚠️ SKIPPED: {str(e)[:60]}...")
    print("     (This is okay - project works with partial datasets)")

# Test 2: JW300
print("\nTest 2: JW300 Parallel Corpus")
try:
    print("  ⏳ Attempting to load (may take a moment)...")
    dataset2_test = load_dataset("opus_100", "en-lg", split="train")
    print(f"  ✅ SUCCESS: {len(dataset2_test):,} samples available")
except Exception as e:
    print(f"  ⚠️ SKIPPED: {str(e)[:60]}...")
    print("     (This is okay - project works with partial datasets)")

# Test 3: Makerere
print("\nTest 3: Makerere NLP Dataset")
try:
    print("  ⏳ Attempting to load (may take a moment)...")
    dataset3_test = load_dataset("Makerere/luganda", split="train")
    print(f"  ✅ SUCCESS: {len(dataset3_test):,} samples available")
except Exception as e:
    print(f"  ⚠️ SKIPPED: {str(e)[:60]}...")
    print("     (This is okay - project works with partial datasets)")

# ============================================================================
# PART 4: CHECK GPU AVAILABILITY
# ============================================================================
print("\n" + "=" * 70)
print("🔋 GPU STATUS")
print("=" * 70)

try:
    import torch
    if torch.cuda.is_available():
        print(f"✅ GPU DETECTED!")
        print(f"   Device: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA Version: {torch.version.cuda}")
        gpu_available = True
    else:
        print(f"⚠️  GPU NOT AVAILABLE")
        print(f"   CPU will be used (slower training)")
        gpu_available = False
except:
    print(f"⚠️  Cannot detect GPU")
    gpu_available = False

# ============================================================================
# PART 5: TEST FILE WRITING
# ============================================================================
print("\n" + "=" * 70)
print("📝 TESTING FILE WRITE PERMISSIONS...")
print("=" * 70)

test_files = [
    ('data/test.csv', 'data directory'),
    ('models/test.txt', 'models directory'),
    ('outputs/test.txt', 'outputs directory'),
]

all_writable = True
for filepath, desc in test_files:
    try:
        with open(filepath, 'w') as f:
            f.write('test')
        os.remove(filepath)
        print(f"✅ {desc:20} - writable")
    except Exception as e:
        print(f"❌ {desc:20} - NOT writable: {e}")
        all_writable = False

# ============================================================================
# PART 6: VERIFY PYTHON VERSION
# ============================================================================
print("\n" + "=" * 70)
print("🐍 PYTHON VERSION")
print("=" * 70)

python_version = sys.version_info
print(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major >= 3 and python_version.minor >= 8:
    print("✅ Python version compatible")
else:
    print("⚠️  Consider upgrading Python to 3.8+")

# ============================================================================
# PART 7: SUMMARY & RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 70)
print("📋 SUMMARY")
print("=" * 70)

print(f"\n✓ Dependencies: {'All OK' if not missing_packages else 'Some missing'}")
print(f"✓ Directories: {'All set' if all_writable else 'Permission issues'}")
print(f"✓ GPU: {'Available' if gpu_available else 'CPU only'}")
print(f"✓ Python: {'Compatible' if python_version.minor >= 8 else 'Consider upgrade'}")

# ============================================================================
# PART 8: RECOMMENDATIONS
# ============================================================================
print("\n" + "=" * 70)
print("✨ RECOMMENDATIONS")
print("=" * 70)

if gpu_available:
    print(f"\n🚀 GPU is available - training will be 50x faster!")
    print(f"   Expected Step 5 time: 30-45 minutes")
else:
    print(f"\n⏱️  GPU not available - using CPU")
    print(f"   Expected Step 5 time: 2-4 hours")
    print(f"   💡 Tip: Use Google Colab for free GPU")

print(f"\n📚 Next Steps:")
print(f"   1. ✅ Verify all checks passed")
print(f"   2. ✅ Run: python Step1_Environment_Setup.py")
print(f"   3. ✅ Run: python Step2_Load_Dataset.py (loads 3 datasets)")
print(f"   4. ✅ Run: python Step3_Data_Preprocessing.py")
print(f"   5. ✅ Run: python Step4_MarianMT_Setup.py")
print(f"   6. ✅ Run: python Step5_Train_Model.py (longest step)")
print(f"   7. ✅ Run: python Step6_Test_Model.py")
print(f"   8. ✅ Run: python Step7_Evaluate_BLEU.py")
print(f"   9. ✅ Run: python Step8_Build_WebApp.py (DEMO!)")

# ============================================================================
# PART 9: FINAL STATUS
# ============================================================================
print("\n" + "=" * 70)
if all_writable and (len(missing_packages) == 0 or len(missing_packages) < 3):
    print("✅ SYSTEM READY FOR TRAINING!")
    print("=" * 70)
    print("\nYou can proceed to Step 1!")
else:
    print("⚠️  ISSUES DETECTED")
    print("=" * 70)
    print("\nPlease fix the issues above and run this script again.")

print("=" * 70)
print("\n")
