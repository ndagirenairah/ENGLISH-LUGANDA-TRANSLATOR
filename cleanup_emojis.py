#!/usr/bin/env python
"""
Remove emojis and clean up all Python files for professional appearance
"""

import re
import os

# List of files to process
files_to_process = [
    'Step1_Environment_Setup.py',
    'Step2_Load_Dataset.py',
    'Step3_Data_Preprocessing.py',
    'Step5_Train_Model.py',
    'Step5_Train_Model_Clean.py',
    'app.py',
    'lecture4_classifiers.py',
    'lecture5_logistic_svm.py',
    'lecture6_tree_ensemble.py',
    'lecture7_deeplearning.py',
    'lecture8_cnn_transfer.py',
    'utils_lecture4_classifiers.py',
    'utils_lecture5_logistic_svm.py',
    'utils_lecture6_tree_ensemble.py',
    'utils_lecture7_deeplearning.py',
    'utils_lecture8_cnn_transfer.py',
    'utils_cultural_postprocessor.py',
    'utils_data_quality_checker.py',
]

# Emoji patterns to remove
emoji_patterns = [
    r'🚀', r'📦', r'✅', r'❌', r'📥', r'📊', r'⚠️', r'✓', 
    r'🎯', r'💾', r'👀', r'📈', r'✂️', r'🧹', r'🔧', r'📄',
    r'💡', r'🎓', r'📚', r'📖', r'🤖', r'⏱', r'💻', r'🔋',
    r'🌳', r'🎨', r'📁', r'🎉', r'🔍', r'⚙️', r'📝', r'🎬',
]

def remove_emojis(text):
    """Remove all emojis from text"""
    for emoji in emoji_patterns:
        text = text.replace(emoji, '')
    return text

def clean_file(filepath):
    """Clean a single file"""
    if not os.path.exists(filepath):
        print(f"  - {filepath}: NOT FOUND (skip)")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove emojis
        cleaned_content = remove_emojis(content)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        print(f"  - {filepath}: CLEANED")
        return True
    except Exception as e:
        print(f"  - {filepath}: ERROR - {e}")
        return False

print("=" * 70)
print("CLEANING PYTHON FILES - REMOVING EMOJIS")
print("=" * 70)

success_count = 0
for file in files_to_process:
    if clean_file(file):
        success_count += 1

print("\n" + "=" * 70)
print(f"CLEANUP COMPLETE: {success_count}/{len(files_to_process)} files cleaned")
print("=" * 70)
