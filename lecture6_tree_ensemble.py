"""
LECTURE 6: Tree-based Models and Ensemble Methods
Deep implementation of:
- Decision Trees: Gini impurity, information gain
- Random Forest: Bagging, variance reduction
- XGBoost: Boosting, sequential refinement
"""

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import warnings

warnings.filterwarnings('ignore')

print("=" * 80)
print("LECTURE 6: TREE-BASED MODELS AND ENSEMBLE METHODS")
print("=" * 80)

# ============================================================================
# DECISION TREES
# ============================================================================
print("\n" + "=" * 80)
print("DECISION TREES")
print("=" * 80)

print("""
Algorithm:
1. Start with all data at root node
2. For each feature, calculate Gini impurity if we split on it
3. Choose split that maximizes information gain
4. Recursively split left and right children
5. Stop when: max depth reached, min samples reached, or pure node

Gini Impurity:
G = 1 - sum(p_i^2)
Where p_i is proportion of class i

Information Gain:
IG = G_parent - (N_left/N * G_left + N_right/N * G_right)
""")

def decision_tree_demo():
    """Decision Tree classification"""
    print("\nDecision Tree Example:")
    
    # Load data
    data = load_breast_cancer()
    X, y = data.data[:100], data.target[:100]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train decision tree
    dt = DecisionTreeClassifier(max_depth=5, random_state=42)
    dt.fit(X_train, y_train)
    
    y_pred = dt.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"  Accuracy: {accuracy:.3f}")
    print(f"  Tree depth: {dt.get_depth()}")
    print(f"  Number of leaves: {dt.get_n_leaves()}")
    
    # Feature importance
    feature_importance = dt.feature_importances_
    top_features = np.argsort(feature_importance)[-5:][::-1]
    
    print(f"\n  Top 5 important features:")
    for rank, idx in enumerate(top_features, 1):
        print(f"    {rank}. Feature {idx}: {feature_importance[idx]:.4f}")
    
    return accuracy

# ============================================================================
# RANDOM FOREST
# ============================================================================
print("\n" + "=" * 80)
print("RANDOM FOREST (BAGGING)")
print("=" * 80)

print("""
Algorithm:
1. For each tree i (from 1 to N):
   a. Bootstrap sample from training data (sample with replacement)
   b. Build decision tree on bootstrap sample
   c. Make tree deep (overfit on purpose)
2. For prediction:
   a. Get prediction from each tree
   b. Majority vote (classification) or average (regression)

Why it works:
- Each tree is overfit on its bootstrap sample
- Averaging many overfit models reduces variance
- Variance reduction: ~sqrt(1/N)
- With N trees, variance decreases by factor of sqrt(N)

Bagging vs Boosting:
- Bagging: Parallel, independent trees, reduces variance
- Boosting: Sequential trees, each corrects previous errors, reduces bias
""")

def random_forest_demo():
    """Random Forest classification"""
    print("\nRandom Forest Example:")
    
    # Load data
    data = load_breast_cancer()
    X, y = data.data, data.target
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Compare different numbers of trees
    accuracies = {}
    for n_trees in [1, 5, 10, 50, 100]:
        rf = RandomForestClassifier(n_estimators=n_trees, random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        
        y_pred = rf.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        accuracies[n_trees] = acc
        print(f"  Trees={n_trees:3}: accuracy={acc:.3f}")
    
    # Feature importance
    rf_final = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_final.fit(X_train, y_train)
    
    feature_importance = rf_final.feature_importances_
    top_features = np.argsort(feature_importance)[-5:][::-1]
    
    print(f"\n  Top 5 important features:")
    for rank, idx in enumerate(top_features, 1):
        print(f"    {rank}. Feature {idx}: {feature_importance[idx]:.4f}")
    
    return accuracies

# ============================================================================
# BAGGING VS BOOSTING
# ============================================================================
print("\n" + "=" * 80)
print("BAGGING VS BOOSTING")
print("=" * 80)

print("""
Bagging (Bootstrap Aggregating):
- Create multiple bootstrap samples
- Train separate model on each sample
- Combine predictions (voting/averaging)
- Models are independent, train in parallel
- Reduces variance through averaging

Boosting:
- Create sequential ensemble
- Each model trained to correct errors of previous models
- Assign higher weights to misclassified samples
- Models are interdependent, train sequentially
- Reduces bias through iterative refinement

Comparison:
Bagging:   Parallel, variance reduction, robust to outliers
Boosting:  Sequential, bias reduction, sensitive to outliers
""")

def bagging_vs_boosting_demo():
    """Compare bagging and boosting approaches"""
    print("\nBagging vs Boosting Comparison:")
    
    from sklearn.ensemble import AdaBoostClassifier
    
    data = load_breast_cancer()
    X, y = data.data[:150], data.target[:150]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Bagging: Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)
    rf_acc = accuracy_score(y_test, rf.predict(X_test))
    
    # Boosting: AdaBoost
    ab = AdaBoostClassifier(n_estimators=100, random_state=42)
    ab.fit(X_train, y_train)
    ab_acc = accuracy_score(y_test, ab.predict(X_test))
    
    # Single Tree baseline
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X_train, y_train)
    dt_acc = accuracy_score(y_test, dt.predict(X_test))
    
    print(f"  Single Decision Tree: {dt_acc:.3f}")
    print(f"  Random Forest (Bagging): {rf_acc:.3f}")
    print(f"  AdaBoost (Boosting): {ab_acc:.3f}")
    
    print(f"\n  Improvements:")
    print(f"    Bagging: +{(rf_acc - dt_acc):.3f}")
    print(f"    Boosting: +{(ab_acc - dt_acc):.3f}")

# ============================================================================
# ENSEMBLE IMPORTANCE
# ============================================================================
print("\n" + "=" * 80)
print("WHY ENSEMBLES WORK")
print("=" * 80)

print("""
Bias-Variance Decomposition:
Error = Bias^2 + Variance + Irreducible Error

Single Complex Model:
- Low bias (flexible)
- High variance (sensitive to training data)

Ensemble of Simple Models:
- Same bias as single model
- Lower variance through averaging
- Result: Reduced total error

Mathematical Foundation:
If models have variance V and correlation ρ:
Ensemble variance = V/N * (1 + (N-1)*ρ)

Where:
- V = individual model variance
- N = number of models
- ρ = correlation between models (0 = independent)

Best case (ρ=0): Variance reduces by 1/N with N models
""")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("\nRunning Lecture 6 demonstrations...\n")
    
    # Decision Tree
    dt_acc = decision_tree_demo()
    
    # Random Forest
    rf_accs = random_forest_demo()
    
    # Bagging vs Boosting
    bagging_vs_boosting_demo()
    
    print("\n" + "=" * 80)
    print("Lecture 6 demonstrations complete")
    print("=" * 80)
