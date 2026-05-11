"""
LECTURE 4: Classification Algorithms
Deep implementation of:
- K-Nearest Neighbors (KNN) with distance metrics
- Naive Bayes probabilistic classification
- Log Trick for numerical stability
"""

import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score
import warnings

warnings.filterwarnings('ignore')

print("=" * 80)
print("LECTURE 4: CLASSIFICATION ALGORITHMS")
print("=" * 80)

# ============================================================================
# K-NEAREST NEIGHBORS (KNN)
# ============================================================================
print("\n" + "=" * 80)
print("K-NEAREST NEIGHBORS (KNN)")
print("=" * 80)

print("""
Algorithm:
1. Calculate distance from query point to all training points
2. Find k nearest neighbors (k closest points)
3. Predict by majority vote among k neighbors

Distance Metrics:
- Euclidean: sqrt(sum((x_i - y_i)^2)) - straight line distance
- Manhattan: sum(|x_i - y_i|) - grid distance
- Minkowski: (sum(|x_i - y_i|^p))^(1/p) - generalized
""")

def knn_distance_demo():
    """Demonstrate distance metrics"""
    print("\nDistance Metrics Example:")
    
    point_a = np.array([0, 0])
    point_b = np.array([3, 4])
    
    euclidean = np.sqrt(np.sum((point_a - point_b)**2))
    manhattan = np.sum(np.abs(point_a - point_b))
    
    print(f"  Point A: {point_a}")
    print(f"  Point B: {point_b}")
    print(f"  Euclidean distance: {euclidean:.2f}")
    print(f"  Manhattan distance: {manhattan:.2f}")
    
    return euclidean, manhattan

# ============================================================================
# NAIVE BAYES CLASSIFIER
# ============================================================================
print("\n" + "=" * 80)
print("NAIVE BAYES CLASSIFIER")
print("=" * 80)

print("""
Algorithm:
P(Class|Features) = P(Class) * P(Features|Class) / P(Features)

Assumption: All features are conditionally independent given the class
(This is "naive" but works well in practice)

Applications:
- Text classification (spam detection)
- Language detection
- Sentiment analysis
""")

def naive_bayes_demo():
    """Naive Bayes classification"""
    print("\nNaive Bayes Example:")
    
    # Load data
    data = load_breast_cancer()
    X, y = data.data, data.target
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Train Naive Bayes
    nb = GaussianNB()
    nb.fit(X_train, y_train)
    
    y_pred = nb.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    
    print(f"  Accuracy: {accuracy:.3f}")
    print(f"  Precision: {precision:.3f}")
    print(f"  Recall: {recall:.3f}")
    
    return accuracy, precision, recall

# ============================================================================
# LOG TRICK
# ============================================================================
print("\n" + "=" * 80)
print("LOG TRICK: PREVENT NUMERICAL UNDERFLOW")
print("=" * 80)

print("""
Problem: Computing products of small probabilities causes underflow
Example: 0.8 * 0.9 * 0.7 * 0.6 * ... gets exponentially smaller

Solution: Use logarithm property
log(a * b * c) = log(a) + log(b) + log(c)

This prevents underflow and improves numerical stability
""")

def log_trick_demo():
    """Demonstrate log trick"""
    print("\nLog Trick Example:")
    
    probabilities = np.array([0.8, 0.9, 0.7, 0.6, 0.5])
    
    # Direct multiplication (underflow risk)
    direct_product = np.prod(probabilities)
    
    # Log trick (stable computation)
    log_product = np.sum(np.log(probabilities))
    log_result = np.exp(log_product)
    
    print(f"  Probabilities: {probabilities}")
    print(f"  Direct multiplication: {direct_product:.10f}")
    print(f"  Log trick result: {log_result:.10f}")
    print(f"  Match: {np.isclose(direct_product, log_result)}")
    
    return direct_product, log_result

# ============================================================================
# KNN CLASSIFIER DEMO
# ============================================================================
print("\n" + "=" * 80)
print("KNN Classifier Full Example")
print("=" * 80)

def knn_full_demo():
    """Complete KNN classification example"""
    print("\nTraining KNN classifier on breast cancer dataset:")
    
    # Load data
    data = load_breast_cancer()
    X, y = data.data, data.target
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    # Scale features (important for distance-based algorithms)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Train KNN with different k values
    results = {}
    for k in [3, 5, 7, 10]:
        knn = KNeighborsClassifier(n_neighbors=k)
        knn.fit(X_train, y_train)
        
        y_pred = knn.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        results[k] = acc
        print(f"  k={k}: accuracy={acc:.3f}")
    
    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("\nRunning Lecture 4 demonstrations...\n")
    
    # KNN distance metrics
    euclidean, manhattan = knn_distance_demo()
    
    # Naive Bayes
    nb_acc, nb_prec, nb_rec = naive_bayes_demo()
    
    # Log trick
    direct, log_result = log_trick_demo()
    
    # Full KNN demo
    knn_results = knn_full_demo()
    
    print("\n" + "=" * 80)
    print("Lecture 4 demonstrations complete")
    print("=" * 80)
