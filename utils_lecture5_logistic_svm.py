# ============================================================================
# LECTURE 5: LOGISTIC REGRESSION, SVM, AND PIPELINES
# ============================================================================
# Deep implementation of:
# 1. Logistic Regression - Sigmoid function, probability outputs
# 2. Support Vector Machines (SVM) - Maximum margin hyperplane
# 3. Pipelines - Prevent data leakage
# ============================================================================

print("=" * 80)
print(" LECTURE 5: LOGISTIC REGRESSION, SVM & PIPELINES")
print("=" * 80)

import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, SVR
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification, make_blobs
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

# ============================================================================
# PART 1: LOGISTIC REGRESSION & SIGMOID FUNCTION
# ============================================================================
print("\n" + "=" * 80)
print(" LECTURE 5: LOGISTIC REGRESSION & SIGMOID FUNCTION")
print("=" * 80)

print("""
Logistic Regression:
────────────────────
Binary classification using sigmoid function

Sigmoid Function:
  σ(z) = 1 / (1 + e^(-z))
  
Properties:
  • Output range: [0, 1] (valid probability)
  • z=0 → σ(0)=0.5 (decision boundary)
  • z→∞ → σ(z)→1
  • z→-∞ → σ(z)→0
  • Monotonically increasing (S-shaped)

Decision Rule:
  • If σ(z) > 0.5 → Predict class 1
  • If σ(z) ≤ 0.5 → Predict class 0

Loss Function (Binary Cross-Entropy):
  L = -[y*log(p) + (1-y)*log(1-p)]
  
  Where:
    y = actual label (0 or 1)
    p = predicted probability from sigmoid
  
  Optimization:
    Minimize L using gradient descent
    dL/dw ∝ (p - y) * x
""")

Key observations:
  • σ(-10) ≈ 0 (very confident: class 0)
  • σ(0) = 0.5 (uncertain: decision boundary)
  • σ(10) ≈ 1 (very confident: class 1)
  • S-shaped curve enables smooth probability transitions
""")

# ============================================================================
# PART 2: SUPPORT VECTOR MACHINES (SVM)
# ============================================================================
print("\n" + "=" * 80)
print("⚡ LECTURE 5: SUPPORT VECTOR MACHINES (SVM)")
print("=" * 80)

print("""
Support Vector Machines:
────────────────────────
Find the hyperplane that maximizes margin between classes

Key Concepts:
  
  1. MARGIN: Distance from hyperplane to nearest data point
     • Larger margin = better generalization
     • Support vectors: Points exactly on margin
     
  2. DECISION BOUNDARY: Hyperplane that separates classes
     w^T x + b = 0
     
     Decision rule:
       If w^T x + b > 0 → Predict class 1
       If w^T x + b ≤ 0 → Predict class 0
  
  3. OPTIMIZATION: Maximize margin = minimize 1/2 * ||w||²
     Subject to: y_i(w^T x_i + b) ≥ 1 for all i
  
  4. KERNEL TRICK: Map data to higher dimension implicitly
     • Linear kernel: x_i^T x_j
     • RBF kernel: exp(-γ||x_i - x_j||²)
     • Polynomial kernel: (x_i^T x_j + c)^d
     
     Allows non-linear decision boundaries in original space

For Text Classification (NMT):
  • Not directly used in seq2seq
  • But useful for: classification helper tasks
  • Example: Is this translation acceptable? (SVM classifier)
""")

# ============================================================================
# PART 3: PIPELINES - PREVENT DATA LEAKAGE
# ============================================================================
print("\n" + "=" * 80)
print("🔗 LECTURE 5: PIPELINES & DATA LEAKAGE PREVENTION")
print("=" * 80)

print("""
What is Data Leakage?
────────────────────
Information from outside the training set leaks into the model

Example (WRONG):
  1. Scale ALL data (train + test)
  2. Split into train/test
  3. Train model
  
Problem:
  • Test scaling parameters come from test data
  • Model learns from future information
  • Unrealistic performance on real data
  
Example (CORRECT):
  1. Split into train/test
  2. Scale ONLY training data
  3. Apply same scaling to test data
  4. Train model

Pipelines Prevent Leakage:
──────────────────────────
Pipeline ensures preprocessing is fitted ONLY on training data

Pipeline Steps:
  1. StandardScaler: Fit on train, transform on test
  2. Model: Train on scaled data
  3. Prediction: Applies scaling automatically

Syntax:
  pipe = Pipeline([
      ('scaler', StandardScaler()),
      ('model', LogisticRegression())
  ])
  pipe.fit(X_train, y_train)
  y_pred = pipe.predict(X_test)  # Scaling applied automatically!
""")

""")

# ============================================================================
# PART 4: LECTURE 5 IN NMT CONTEXT
# ============================================================================
print("\n" + "=" * 80)
print("🧠 LECTURE 5 CONCEPTS IN NEURAL MACHINE TRANSLATION")
print("=" * 80)

print("""
How Lecture 5 Relates to NMT:
─────────────────────────────

1. SIGMOID/SOFTMAX (Logistic Regression):
   • Attention mechanism uses softmax (multi-class sigmoid)
   • Attention = probability distribution over encoder states
   • Output layer: softmax over 50K vocabulary
   
   Code in transformer:
     attn_weights = softmax(query @ key^T / √d)  # Sigmoid-like!
     output_probs = softmax(hidden @ vocab_matrix)
   
2. MARGIN MAXIMIZATION (SVM Concept):
   • Similar idea in max-margin training
   • Loss functions that encourage separation
   • Some modern approaches use margin-based losses

3. PIPELINE (Data Handling):
   • Model → Tokenizer → Encoder
   • Pipeline pattern prevents leakage
   • Each component fits on appropriate data
   
   In our NMT:
     pipeline = [
         Tokenizer → (fit on train data)
         Model → (train on tokenized data)
     ]

4. FEATURE SCALING (Normalization):
   • Layer Normalization in transformers
   • Attention: outputs normalized
   • Embeddings: sometimes scaled by √d_model
   
   In code:
     LayerNorm(x) similar to StandardScaler on each sample
""")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("LECTURE 5: LOGISTIC REGRESSION, SVM & PIPELINES")
    print("=" * 80)
    
    # Sigmoid
    sigmoid_function()
    
    # Logistic regression
    logistic_regression_demo()
    
    # SVM
    svm_demo()
    
    # Pipelines
    pipeline_demo()
    
    print("\n" + "=" * 80)
    print(" LECTURE 5: ALL CONCEPTS IMPLEMENTED")
    print("=" * 80)
    print("""
Summary:
   Sigmoid: Converts scores to probabilities [0,1]
   Logistic Regression: Probabilistic linear classifier
   SVM: Maximizes margin for robust classification
   Pipelines: Prevents data leakage in ML workflows
  
Connection to NMT:
  • Attention uses sigmoid/softmax logic
  • Output layer uses softmax (multi-class logistic)
  • Preprocessing pipeline prevents leakage
  • Normalization similar to feature scaling
""")
