"""
LECTURE 5: Logistic Regression, SVM, and Pipelines
Deep implementation of:
- Sigmoid function and logistic regression
- Support Vector Machines (SVM)
- Data pipelines and preventing leakage
"""

import numpy as np
import warnings
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_classification, load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import warnings

warnings.filterwarnings('ignore')

print("=" * 80)
print("LECTURE 5: LOGISTIC REGRESSION, SVM & PIPELINES")
print("=" * 80)

# ============================================================================
# SIGMOID FUNCTION
# ============================================================================
print("\n" + "=" * 80)
print("SIGMOID FUNCTION")
print("=" * 80)

print("""
Sigmoid: σ(z) = 1 / (1 + e^(-z))

Properties:
- Output range: [0, 1] (valid probability)
- z=0 → σ(0) = 0.5 (decision boundary)
- z → ∞ → σ(z) → 1
- z → -∞ → σ(z) → 0
- Smooth S-shaped curve
""")

def sigmoid_function():
    """Demonstrate sigmoid function"""
    print("\nSigmoid values for different z:")
    
    z_values = np.array([-10, -5, -1, 0, 1, 5, 10])
    sigma_values = 1 / (1 + np.exp(-z_values))
    
    for z, sigma in zip(z_values, sigma_values):
        print(f"  σ({z:3}) = {sigma:.4f}")
    
    print("\nInterpretation:")
    print("  z < 0: Probability < 0.5 (predict class 0)")
    print("  z = 0: Probability = 0.5 (decision boundary)")
    print("  z > 0: Probability > 0.5 (predict class 1)")
    
    return z_values, sigma_values

# ============================================================================
# LOGISTIC REGRESSION
# ============================================================================
print("\n" + "=" * 80)
print("LOGISTIC REGRESSION")
print("=" * 80)

print("""
Binary classification using sigmoid output

Decision Rule:
- If σ(z) > 0.5 → Predict class 1
- If σ(z) ≤ 0.5 → Predict class 0

Loss Function (Binary Cross-Entropy):
L = -[y*log(p) + (1-y)*log(1-p)]

Where:
- y = actual label (0 or 1)
- p = predicted probability
""")

def logistic_regression_demo():
    """Logistic Regression classification"""
    print("\nLogistic Regression Example:")
    
    # Create synthetic data
    X, y = make_classification(
        n_samples=100,
        n_features=2,
        n_informative=2,
        n_redundant=0,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train logistic regression
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train, y_train)
    
    # Predictions
    y_pred = lr.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"  Accuracy: {accuracy:.3f}")
    print(f"  Coefficients: {lr.coef_[0]}")
    print(f"  Intercept: {lr.intercept_[0]:.4f}")
    
    return accuracy

# ============================================================================
# SUPPORT VECTOR MACHINES (SVM)
# ============================================================================
print("\n" + "=" * 80)
print("SUPPORT VECTOR MACHINES (SVM)")
print("=" * 80)

print("""
Goal: Find hyperplane that maximizes margin between classes

Margin: Distance from hyperplane to nearest data point

Kernels:
- Linear: For linearly separable data
- RBF (Radial Basis Function): For non-linear data
- Polynomial: For polynomial boundaries

Key Concept: Support vectors are the points closest to the boundary
""")

def svm_demo():
    """SVM classification with different kernels"""
    print("\nSVM Example:")
    
    # Create data
    data = load_breast_cancer()
    X, y = data.data[:100], data.target[:100]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train SVM with different kernels
    results = {}
    for kernel in ['linear', 'rbf', 'poly']:
        svm = SVC(kernel=kernel, C=1.0)
        svm.fit(X_train_scaled, y_train)
        
        y_pred = svm.predict(X_test_scaled)
        acc = accuracy_score(y_test, y_pred)
        
        results[kernel] = acc
        print(f"  SVM ({kernel:6}): accuracy={acc:.3f}")
    
    return results

# ============================================================================
# DATA PIPELINES: PREVENT DATA LEAKAGE
# ============================================================================
print("\n" + "=" * 80)
print("DATA PIPELINES: PREVENT DATA LEAKAGE")
print("=" * 80)

print("""
Data Leakage: Using information from test set during training

WRONG APPROACH:
1. Combine train + test data
2. Standardize combined data
3. Split into train and test
Problem: Test data statistics leaked into training phase

CORRECT APPROACH:
1. Split data first
2. Fit StandardScaler on training data only
3. Apply same scaling to test data
Benefit: Test data remains truly unseen
""")

def pipeline_demo():
    """Demonstrate correct pipeline usage"""
    print("\nPipeline Example:")
    
    # Create data
    X, y = make_classification(
        n_samples=100,
        n_features=10,
        n_informative=5,
        n_redundant=0,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # CORRECT: Use Pipeline to prevent leakage
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(max_iter=1000))
    ])
    
    # Fit only on training data
    pipe.fit(X_train, y_train)
    
    # Predict on test data
    y_pred = pipe.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"  Pipeline accuracy: {accuracy:.3f}")
    print("\n  Pipeline benefits:")
    print("  - Scaler fit on train data only")
    print("  - Same transformation applied to test data")
    print("  - No data leakage")
    
    return accuracy

# ============================================================================
# COMPARISON: LOGISTIC REGRESSION VS SVM
# ============================================================================
print("\n" + "=" * 80)
print("COMPARISON: Logistic Regression vs SVM")
print("=" * 80)

def comparison_demo():
    """Compare Logistic Regression and SVM"""
    print("\nModel Comparison:")
    
    X, y = make_classification(
        n_samples=200,
        n_features=5,
        n_informative=3,
        n_redundant=0,
        random_state=42
    )
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Logistic Regression Pipeline
    lr_pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', LogisticRegression(max_iter=1000))
    ])
    lr_pipe.fit(X_train, y_train)
    lr_acc = accuracy_score(y_test, lr_pipe.predict(X_test))
    
    # SVM Pipeline
    svm_pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', SVC(kernel='rbf', C=1.0))
    ])
    svm_pipe.fit(X_train, y_train)
    svm_acc = accuracy_score(y_test, svm_pipe.predict(X_test))
    
    print(f"  Logistic Regression: {lr_acc:.3f}")
    print(f"  SVM (RBF):          {svm_acc:.3f}")
    
    print("\n  When to use each:")
    print("  Logistic Regression: Fast, interpretable, linear boundaries")
    print("  SVM: Non-linear boundaries, robust to outliers")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("\nRunning Lecture 5 demonstrations...\n")
    
    # Sigmoid
    z_vals, sigma_vals = sigmoid_function()
    
    # Logistic Regression
    lr_acc = logistic_regression_demo()
    
    # SVM
    svm_results = svm_demo()
    
    # Pipeline
    pipe_acc = pipeline_demo()
    
    # Comparison
    comparison_demo()
    
    print("\n" + "=" * 80)
    print("Lecture 5 demonstrations complete")
    print("=" * 80)
