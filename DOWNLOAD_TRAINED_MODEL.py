"""
Download Trained Model from Google Colab
=========================================

Run this code cell in Google Colab AFTER training completes.
It will download your trained model as a ZIP file to your local machine.
"""

print("\n[DOWNLOADING TRAINED MODEL FROM COLAB]\n")

import shutil
from pathlib import Path
from google.colab import files
import os

# Get current directory
current_dir = Path(os.getcwd())
print(f"Current directory: {current_dir}")

# Check for model in different possible locations
possible_paths = [
    Path("models/trained_model"),
    Path("ENGLISH-LUGANDA-TRANSLATOR/models/trained_model"),
    current_dir / "models" / "trained_model"
]

model_path = None
for path in possible_paths:
    if path.exists():
        model_path = path
        print(f"✅ Found model at: {model_path}")
        break

if not model_path:
    print("❌ Model not found!")
    print(f"   Checked: {possible_paths}")
    print("\n⚠️  Make sure you completed STEP 5 (Training) first!")
else:
    output_zip = "trained_model"
    print(f"\n📦 Zipping model...")
    shutil.make_archive(output_zip, "zip", model_path.parent, model_path.name)
    
    print(f"✅ Created: {output_zip}.zip")
    print("\n⬇️ DOWNLOADING TO YOUR LOCAL MACHINE...")
    print("   (Check your Downloads folder)\n")
    
    files.download(f"{output_zip}.zip")
    
    print("✅ Download complete!")
