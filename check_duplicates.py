#!/usr/bin/env python
"""
Identify and list duplicate functions between lecture and utils files
"""

import re
import os

def extract_function_names(filepath):
    """Extract all function definitions from a Python file"""
    if not os.path.exists(filepath):
        return set()
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all function definitions
        functions = re.findall(r'^def\s+(\w+)\s*\(', content, re.MULTILINE)
        return set(functions)
    except:
        return set()

# Pairs to check
pairs = [
    ('lecture5_logistic_svm.py', 'utils_lecture5_logistic_svm.py'),
    ('lecture6_tree_ensemble.py', 'utils_lecture6_tree_ensemble.py'),
    ('lecture7_deeplearning.py', 'utils_lecture7_deeplearning.py'),
    ('lecture8_cnn_transfer.py', 'utils_lecture8_cnn_transfer.py'),
]

print("=" * 70)
print("DUPLICATE FUNCTION ANALYSIS")
print("=" * 70)

for lecture_file, utils_file in pairs:
    lecture_funcs = extract_function_names(lecture_file)
    utils_funcs = extract_function_names(utils_file)
    
    duplicates = lecture_funcs & utils_funcs
    
    if duplicates:
        print(f"\n{lecture_file} ↔ {utils_file}")
        print(f"  Duplicate functions: {', '.join(sorted(duplicates))}")
    else:
        print(f"\n{lecture_file} ↔ {utils_file}")
        print(f"  No duplicates found")

print("\n" + "=" * 70)
print("NOTE: Duplicates should be removed from utils files")
print("      as they should only contain helper/utility functions")
print("=" * 70)
