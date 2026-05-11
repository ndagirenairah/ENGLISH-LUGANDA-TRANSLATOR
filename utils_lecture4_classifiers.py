# ============================================================================
# LECTURE 4: CLASSIFICATION ALGORITHMS
# ============================================================================
# Deep implementation of:
# 1. K-Nearest Neighbors (KNN) - Distance metrics
# 2. Naive Bayes - Probabilistic classification
# 3. Log Trick - Prevents arithmetic underflow
# ============================================================================

print("=" * 80)
print(" LECTURE 4: CLASSIFICATION ALGORITHMS")
print("=" * 80)

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import math

# ============================================================================
# PART 1: K-NEAREST NEIGHBORS (KNN)
# ============================================================================
print("\n" + "=" * 80)
print(" LECTURE 4: K-NEAREST NEIGHBORS (KNN)")
print("=" * 80)

print("""
KNN Algorithm:
──────────────
1. Choose k (e.g., k=5)
2. For new point, calculate distance to all training points
3. Find k nearest neighbors
4. Majority vote among k neighbors
5. Predict majority class

Distance Metrics:
─────────────────
• Euclidean: √(Σ(x_i - y_i)²) - straight line distance
• Manhattan: Σ|x_i - y_i| - grid distance (city blocks)
• Minkowski: (Σ|x_i - y_i|^p)^(1/p) - general case

Applications in NMT:
  Not directly used (too slow for 50K vocabulary)
  But used in retrieval-based MT (find similar translations)
""")

def knn_distance_demo():
    """Demonstrate KNN distance metrics"""
    
    print("\n KNN Distance Metrics Demo:")
    
    # Sample translations with features
    # Features: [english_length, luganda_length, punctuation_count]
    translations = {
        'Hello how are you': np.array([4, 4, 0]),
        'Good morning sir': np.array([3, 3, 0]),
        'Thank you very much': np.array([4, 4, 0]),
        'What is your name': np.array([4, 4, 0]),
        'I am very happy': np.array([4, 4, 0]),
    }
    
    # Query translation
    query = np.array([3, 3, 0])  # "How are you"
    
    print(f"\nQuery: How are you → features {query}")
    print("\nNeighbor distances:")
    
    distances = []
    for sentence, features in translations.items():
        # Euclidean distance
        euclidean = np.sqrt(np.sum((query - features)**2))
        
        # Manhattan distance
        manhattan = np.sum(np.abs(query - features))
        
        distances.append((sentence, euclidean, manhattan))
        print(f"  • {sentence}")
        print(f"    - Euclidean: {euclidean:.3f}")
        print(f"    - Manhattan: {manhattan:.1f}")
    
    # Sort by Euclidean distance
    distances.sort(key=lambda x: x[1])
    
    print(f"\n k=3 Nearest Neighbors (Euclidean):")
    for i, (sentence, euclidean, manhattan) in enumerate(distances[:3], 1):
        print(f"  {i}. {sentence} (distance={euclidean:.3f})")

# ============================================================================
# PART 2: NAIVE BAYES CLASSIFIER
# ============================================================================
print("\n" + "=" * 80)
print(" LECTURE 4: NAIVE BAYES CLASSIFIER")
print("=" * 80)

print("""
Naive Bayes:
────────────
Based on Bayes' Theorem:
  P(Class | Features) = P(Features | Class) * P(Class) / P(Features)

"Naive" Assumption:
  All features are conditionally independent given the class
  
  P(word_1, word_2, ..., word_n | Is_Luganda) 
  = P(word_1 | Luganda) * P(word_2 | Luganda) * ...

This is rarely true but often works surprisingly well!

Variants:
  • Multinomial NB: For discrete counts (text classification)
  • Gaussian NB: Assumes Gaussian distribution
  • Bernoulli NB: For binary features
""")

def naive_bayes_language_detection():
    """Naive Bayes for language detection"""
    
    print("\n🌍 Naive Bayes Language Detection:")
    
    # Training data (simplified)
    luganda_texts = [
        'oli otya',
        'ndi muganda',
        'webale',
        'ssebo',
        'gyambadde',
    ]
    
    english_texts = [
        'hello how are you',
        'i am fine thank you',
        'good morning sir',
        'what is your name',
        'nice to meet you',
    ]
    
    # Vectorize texts (convert to word counts)
    vectorizer = CountVectorizer()
    
    # Create training data
    all_texts = luganda_texts + english_texts
    labels = [0] * len(luganda_texts) + [1] * len(english_texts)  # 0=Luganda, 1=English
    
    X = vectorizer.fit_transform(all_texts).toarray()
    y = np.array(labels)
    
    print(f"\nTraining data:")
    print(f"  • Luganda samples: {len(luganda_texts)}")
    print(f"  • English samples: {len(english_texts)}")
    print(f"  • Vocabulary size: {len(vectorizer.get_feature_names_out())}")
    
    # Train Naive Bayes
    nb = MultinomialNB()
    nb.fit(X, y)
    
    print(f"\n Naive Bayes trained")
    
    # Test on new text
    test_texts = [
        'oli otya?',
        'hello how are you',
        'webale sana',
        'thank you very much',
    ]
    
    X_test = vectorizer.transform(test_texts).toarray()
    predictions = nb.predict(X_test)
    probabilities = nb.predict_proba(X_test)
    
    print(f"\nPredictions on new texts:")
    for text, pred, prob in zip(test_texts, predictions, probabilities):
        lang = 'Luganda' if pred == 0 else 'English'
        confidence = prob[pred] * 100
        print(f"  • '{text}'")
        print(f"    → {lang} ({confidence:.1f}% confidence)")

# ============================================================================
# PART 3: THE LOG TRICK (PREVENTING UNDERFLOW)
# ============================================================================
print("\n" + "=" * 80)
print("📉 LECTURE 4: THE LOG TRICK")
print("=" * 80)

print("""
Problem: Multiplying Many Small Probabilities
──────────────────────────────────────────────

Word probabilities in Naive Bayes (each < 1):
  P(word_1 | class) * P(word_2 | class) * ... * P(word_1000 | class)
  = 0.8 * 0.9 * 0.7 * ... * 0.5
  = 0.000000...0001 (extremely tiny!)

Computer Limit:
  • Numbers < 10^-300 become exactly ZERO (underflow)
  • Result: 0 probability causes errors
  
Solution: Use Logarithms
────────────────────────
log(a * b) = log(a) + log(b)

Transform:
  Product: 0.8 * 0.9 * 0.7 * ... → 0 (underflow!)
  Log sum: log(0.8) + log(0.9) + log(0.7) + ... → -1.523 (safe!)
  
  To recover: exp(-1.523) = 0.218

Bayes Rule with Logs:
  log(P(C|X)) ∝ log(P(X|C)) + log(P(C))
              = Σ log(P(x_i|C)) + log(P(C))

Benefits:
   No underflow (logarithms are always finite)
   Numerically stable for any number of features
   Addition faster than multiplication
""")

def log_trick_demo():
    """Demonstrate the log trick"""
    
    print("\n🔢 Log Trick Demo:")
    
    # Probability values
    probs = np.array([0.8, 0.9, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1])
    
    print(f"\nProbabilities: {probs}")
    
    # Direct multiplication (underflow risk)
    print(f"\n1️⃣  DIRECT MULTIPLICATION (Risky):")
    product = 1.0
    for p in probs:
        product *= p
    print(f"   Product = {product}")
    if product == 0:
        print(f"     UNDERFLOW! Result became exactly zero")
    else:
        print(f"   Scientific notation: {product:.2e}")
    
    # Using log trick
    print(f"\n2️⃣  USING LOG TRICK (Safe):")
    log_probs = np.log(probs)
    log_sum = np.sum(log_probs)
    print(f"   Log probabilities: {np.round(log_probs, 3)}")
    print(f"   Sum of logs: {log_sum:.4f}")
    
    result = np.exp(log_sum)
    print(f"   exp(log_sum) = {result}")
    
    if product != 0:
        print(f"    Same result: {product:.2e} ≈ {result:.2e}")
    else:
        print(f"    Recovered from underflow: {result:.2e}")

# ============================================================================
# PART 4: CLASSIFIER COMPARISON
# ============================================================================
print("\n" + "=" * 80)
print("🏆 LECTURE 4: CLASSIFIER COMPARISON")
print("=" * 80)

def classifier_comparison():
    """Compare KNN vs Naive Bayes"""
    
    print("\n Algorithm Characteristics:")
    
    comparison = pd.DataFrame({
        'Algorithm': ['KNN', 'Naive Bayes'],
        'Training Time': ['Fast', 'Fast'],
        'Prediction Time': ['Slow (k+1 scores)', 'Fast'],
        'Distance Metric': ['Euclidean/Manhattan', 'Probabilistic'],
        'Feature Scaling': ['Required', 'Not needed'],
        'Assumptions': ['None (lazy)', 'Feature independence'],
        'Works Well': ['Low-dim, balanced', 'High-dim, text'],
        'Curse of Dim.': ['Yes', 'No'],
    })
    
    print(comparison.to_string(index=False))
    
    print("""
For Machine Translation:
──────────────────────
KNN: Not typically used in NMT because
  • 50K vocabulary = 50K-dimensional space (curse of dimensionality)
  • Slow prediction time
  • But useful for: retrieval-based MT (find similar translations)

Naive Bayes: Not used in NMT but useful for
  • Pre-processing: Language detection
  • Quality estimation: Is translation good?
  • Baseline classifier for comparison

Modern NMT: Uses deep learning (Lectures 7-8)
  • Transformers (attention mechanisms)
  • Seq2Seq encoder-decoder
  • 24 layers, 600M parameters
  • All concepts (KNN, NB) subsumed in neural network
""")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("LECTURE 4: CLASSIFICATION ALGORITHMS - DEEP IMPLEMENTATION")
    print("=" * 80)
    
    # KNN
    knn_distance_demo()
    
    # Naive Bayes
    naive_bayes_language_detection()
    
    # Log Trick
    log_trick_demo()
    
    # Comparison
    classifier_comparison()
    
    print("\n" + "=" * 80)
    print(" LECTURE 4: ALL CONCEPTS IMPLEMENTED")
    print("=" * 80)
    print("""
Key Takeaways:
   KNN: Simple, intuitive, but suffers from curse of dimensionality
   Naive Bayes: Fast, probabilistic, works well for text
   Log Trick: Essential for numerical stability
   Deep Learning: Combines benefits of both via neural networks
    
For your translation project:
  • These concepts explained via neural MT architecture
  • Hidden layers = adaptive distance metrics (learned by KNN-like logic)
  • Attention = probability distribution (like Naive Bayes)
  • Softmax outputs = probabilities (uses log-sum-exp for stability)
""")
