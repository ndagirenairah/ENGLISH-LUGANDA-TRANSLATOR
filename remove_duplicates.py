#!/usr/bin/env python
"""
Remove duplicate functions from utils files
"""

import re
import os

def remove_function_from_file(filepath, function_names):
    """
    Remove specified functions from a Python file
    Removes the entire function definition (def to next def or end of file)
    """
    if not os.path.exists(filepath):
        print(f"  - {filepath}: NOT FOUND")
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find line numbers of functions to remove
        lines_to_remove = set()
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line starts a function we want to remove
            for func_name in function_names:
                pattern = rf'^def\s+{func_name}\s*\('
                if re.match(pattern, line):
                    # Mark this function for removal
                    # Find the end of the function (next def at same or lower indent, or EOF)
                    indent_level = len(line) - len(line.lstrip())
                    j = i + 1
                    
                    while j < len(lines):
                        next_line = lines[j]
                        if next_line.strip() == '':  # Skip empty lines
                            lines_to_remove.add(j)
                            j += 1
                            continue
                        
                        # Check if next_line is a new definition at same indent or less
                        if next_line.lstrip() and not next_line[0].isspace():
                            # This is a top-level statement
                            break
                        elif re.match(rf'^def\s+\w+\s*\(', next_line):
                            # This is another function definition
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= indent_level:
                                break
                        
                        lines_to_remove.add(j)
                        j += 1
                    
                    # Also remove the function definition line
                    for k in range(i, j):
                        if k < len(lines):
                            lines_to_remove.add(k)
                    
                    i = j
                    continue
            
            i += 1
        
        # Remove lines (in reverse to maintain indices)
        new_lines = [lines[i] for i in range(len(lines)) if i not in lines_to_remove]
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        removed_count = len(lines_to_remove)
        print(f"  - {filepath}: CLEANED (removed {removed_count} lines)")
        return True
    except Exception as e:
        print(f"  - {filepath}: ERROR - {e}")
        return False

# Duplicates to remove from each utils file
duplicates_to_remove = {
    'utils_lecture5_logistic_svm.py': ['sigmoid_function', 'logistic_regression_demo', 'svm_demo', 'pipeline_demo'],
    'utils_lecture6_tree_ensemble.py': ['decision_tree_demo', 'random_forest_demo'],
    'utils_lecture7_deeplearning.py': ['activation_functions_demo', 'optimization_demo'],
    'utils_lecture8_cnn_transfer.py': ['convolution_demo', 'pooling_demo', 'transfer_learning_comparison'],
}

print("=" * 70)
print("REMOVING DUPLICATE FUNCTIONS FROM UTILS FILES")
print("=" * 70)

success_count = 0
for utils_file, functions in duplicates_to_remove.items():
    if remove_function_from_file(utils_file, functions):
        success_count += 1

print("\n" + "=" * 70)
print(f"CLEANUP COMPLETE: {success_count}/{len(duplicates_to_remove)} files cleaned")
print("=" * 70)
