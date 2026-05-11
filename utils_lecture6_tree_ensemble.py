# ============================================================================
# LECTURE 6: TREE-BASED MODELS & ENSEMBLE METHODS
# ============================================================================
# Deep implementation of:
# 1. Decision Trees - Gini Impurity, Information Gain
# 2. Random Forest (Bagging) - Ensemble method
# 3. XGBoost (Boosting) - Sequential tree building
# ============================================================================

print("=" * 80)
print(" LECTURE 6: TREE-BASED MODELS & ENSEMBLE METHODS")
print("=" * 80)

import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PART 1: DECISION TREES
# ============================================================================
print("\n" + "=" * 80)
print(" LECTURE 6: DECISION TREES")
print("=" * 80)

print("""
Decision Tree Algorithm:
────────────────────────
Recursive binary splitting based on feature values

1. ROOT NODE: Start with all data
2. SPLIT: Choose feature and threshold that best separates classes
3. LEAF NODE: Terminal node with class prediction
4. REPEAT: For each child node until stopping criteria

Splitting Criteria:
───────────────────

GINI IMPURITY:
  Gini = 1 - Σ(p_i)²
  
  Where p_i = proportion of class i
  
  Properties:
    • Gini = 0: Pure node (all same class)
    • Gini = 0.5: Completely mixed (binary classification)
    • Lower Gini = Better split
  
  Example:
    Node with 8 class-0, 2 class-1:
    Gini = 1 - (0.8² + 0.2²) = 1 - 0.68 = 0.32

INFORMATION GAIN:
  IG = Gini_parent - (weighted avg of children Gini)
  
  Measures: How much impurity decreases with split
  
  Algorithm:
    1. Try all features and thresholds
    2. Calculate Information Gain for each
    3. Choose split with highest IG

Tree Growing:
──────────────
• Grows until:
  - All samples in node are same class (pure)
  - Max depth reached
  - Min samples per leaf reached
  - No improvement possible

Advantages:
  • Interpretable (can visualize decision path)
  • No feature scaling needed
  • Handles non-linear relationships
  
Disadvantages:
  • High variance (small data changes → big tree changes)
  • Prone to overfitting
  • Can create biased trees if classes imbalanced
""")

# ============================================================================
# PART 2: RANDOM FOREST (BAGGING)
# ============================================================================
print("\n" + "=" * 80)
print("🌲 LECTURE 6: RANDOM FOREST (BAGGING)")
print("=" * 80)

print("""
Random Forest - Ensemble Method:
────────────────────────────────
Combines multiple decision trees to reduce variance

Bagging (Bootstrap Aggregating):
  1. Sample WITH replacement from training data
  2. Train tree on each bootstrap sample
  3. Combine predictions via:
     • Voting (classification)
     • Averaging (regression)

Why It Works:
  • Each tree sees different random subset
  • Trees uncorrelated with each other
  • Variance of ensemble ≈ Var(tree)/n_trees
  • Reduces overfitting of single tree

Key Hyperparameters:
  • n_estimators: Number of trees (more = better, slower)
  • max_depth: Max depth per tree
  • min_samples_split: Min samples to split node
  • max_features: Features considered per split
    - "sqrt": √n_features (good default)
    - "log2": log₂(n_features)
    - None: All features

Advantages over Single Tree:
  • Much more stable
  • Better generalization
  • Parallelizable (trees independent)
  • Good feature importance estimation
  
Disadvantages:
  • More complex (many trees)
  • Slower prediction (evaluate all trees)
  • Less interpretable than single tree
""")

# ============================================================================
# PART 3: XGBOOST (BOOSTING)
# ============================================================================
print("\n" + "=" * 80)
print("⚡ LECTURE 6: XGBOOST (BOOSTING)")
print("=" * 80)

print("""
Gradient Boosting (XGBoost):
────────────────────────────
Build trees sequentially, each correcting previous errors

Algorithm:
  1. Initialize: Predict mean value (F₀ = mean)
  2. For each iteration m = 1 to M:
     a. Calculate residuals: r_m = y - F_{m-1}(x)
     b. Fit tree to predict residuals
     c. Update: F_m = F_{m-1} + λ * tree_m
     d. λ (learning_rate): Controls step size

Why Sequential Building Works:
  • Each tree focuses on remaining errors
  • Previous predictions + new tree = better prediction
  • Accumulation of small improvements

XGBoost Specific:
  • Regularized: Penalizes tree complexity
  • Optimized: Fast computation
  • Handles missing values
  • Feature importance based on gain

Pseudocode:
  predictions = 0
  for i in range(n_estimators):
      residuals = y - predictions
      tree_i = fit_tree(X, residuals)
      predictions += learning_rate * tree_i.predict(X)

Hyperparameters:
  • n_estimators: Number of trees (more = better, slower)
  • learning_rate: Step size (0.01-0.1, lower = slower but better)
  • max_depth: Tree depth (1-10)
  • subsample: Fraction of samples per iteration (0-1)
""")

def xgboost_demo():
    """Gradient Boosting for classification"""
    
    print("\n Gradient Boosting Demo:")
    
    # Create data
    X, y = make_classification(n_samples=200, n_features=4, n_informative=3,
                               n_redundant=1, random_state=42)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Gradient Boosting
    gb = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1,
                                    max_depth=3, random_state=42)
    gb.fit(X_train, y_train)
    
    y_pred = gb.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nGradient Boosting Configuration:")
    print(f"  • Number of iterations: 100")
    print(f"  • Learning rate: 0.1")
    print(f"  • Max depth per tree: 3")
    print(f"  • Strategy: Sequential error correction")
    print(f"  • Accuracy: {accuracy:.2%}")
    
    print(f"\nFeature Importances:")
    for i, importance in enumerate(gb.feature_importances_):
        print(f"  • Feature {i}: {importance:.3f}")

# ============================================================================
# PART 4: BAGGING vs BOOSTING
# ============================================================================
print("\n" + "=" * 80)
print("🏆 LECTURE 6: BAGGING vs BOOSTING")
print("=" * 80)

print("""
Comparison:
───────────

BAGGING (Random Forest):
  • Parallel: Train trees independently
  • Bootstrap: Random samples with replacement
  • Combine: Average predictions
  • Reduces: Variance (mainly)
  • Error = Bias + Variance/n_trees
  
  Use case: High variance, low bias problems

BOOSTING (XGBoost):
  • Sequential: Each tree corrects previous
  • Weighted: Each sample has weight
  • Focus: Hard examples (high residuals)
  • Reduces: Both bias and variance
  • Error = Low bias + Low variance
  
  Use case: Low variance, high bias problems

Empirical Performance:
  • XGBoost usually > Random Forest > Single Tree
  • XGBoost slower to train (sequential)
  • Random Forest parallelizable (faster training)
  • Both much better than single tree

When to Use:
  • Random Forest: Fast training, simple, good baseline
  • XGBoost: Maximum accuracy, Kaggle competitions, industry
  • Single Tree: Interpretability is critical
""")

# ============================================================================
# PART 5: LECTURE 6 IN NMT CONTEXT
# ============================================================================
print("\n" + "=" * 80)
print("🧠 LECTURE 6 CONCEPTS IN NEURAL MACHINE TRANSLATION")
print("=" * 80)

print("""
How Lecture 6 Relates to NMT:
──────────────────────────────

1. ENSEMBLE IDEA (Multiple Trees):
   • Transformer has 24 layers (like ensemble)
   • Each layer processes information differently
   • Output = combination of all 24 layer outputs
   • Similar effect: Reduced variance, better generalization

2. SEQUENTIAL BUILDING (Boosting Concept):
   • Decoder generates tokens one at a time (like boosting)
   • Each token generated considers previous tokens
   • Corrects errors as it goes (autoregressive generation)
   • Similar effect: Sequential refinement

3. GRADIENT-BASED LEARNING:
   • Decision trees use Gini impurity (discrete splits)
   • Transformers use gradient descent (continuous updates)
   • But both optimizing for better predictions

4. FEATURE IMPORTANCE:
   • Trees compute feature importance (which features matter)
   • Attention weights in transformer (which tokens matter)
   • Both showing what model considers important

5. REGULARIZATION:
   • Tree depth limiting (prevents overfitting)
   • XGBoost learning rate (small steps prevent overfitting)
   • Transformer: dropout, layer norm (prevent overfitting)
   
   All use same principle: Constrain model complexity
""")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("LECTURE 6: TREE-BASED MODELS & ENSEMBLE METHODS")
    print("=" * 80)
    
    # Decision Tree
    decision_tree_demo()
    
    # Random Forest
    random_forest_demo()
    
    # XGBoost
    xgboost_demo()
    
    print("\n" + "=" * 80)
    print(" LECTURE 6: ALL CONCEPTS IMPLEMENTED")
    print("=" * 80)
    print("""
Summary:
   Decision Trees: Non-linear classifier, interpretable
   Random Forest: Ensemble via bagging (parallel trees)
   XGBoost: Ensemble via boosting (sequential trees)
   Bagging vs Boosting: Different variance/bias tradeoffs
  
Performance Hierarchy:
  Single Tree < Random Forest ≤ XGBoost
  
Comparison to NMT:
  • Multiple layers ≈ Ensemble of models
  • Autoregressive generation ≈ Boosting sequential refinement
  • Attention ≈ Feature importance (what's important?)
""")
