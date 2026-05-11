# ============================================================================
# LECTURE 7: DEEP LEARNING - BACKPROPAGATION & OPTIMIZATION
# ============================================================================
# Deep implementation of:
# 1. Neural Network Architecture (Input/Hidden/Output layers)
# 2. Backpropagation via Chain Rule
# 3. Gradient Descent & Optimization
# 4. Activation Functions (ReLU, Sigmoid, Tanh)
# ============================================================================

print("=" * 80)
print(" LECTURE 7: DEEP LEARNING - BACKPROPAGATION & OPTIMIZATION")
print("=" * 80)

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

# ============================================================================
# PART 1: NEURAL NETWORK ARCHITECTURE
# ============================================================================
print("\n" + "=" * 80)
print("🧠 LECTURE 7: NEURAL NETWORK ARCHITECTURE")
print("=" * 80)

print("""
Fully Connected Neural Network:
───────────────────────────────

Structure:
  Input Layer (784) → Hidden Layer 1 (128) → Hidden Layer 2 (64) → Output Layer (10)

Terminology:
  • Neurons: Individual units that compute
  • Layers: Groupings of neurons
  • Weights: Parameters to learn (w)
  • Biases: Offset parameters (b)
  • Activation: Non-linear transformation

Forward Pass (Inference):
  1. x (input)
  2. z1 = w1^T * x + b1 (pre-activation)
  3. a1 = ReLU(z1) (activation)
  4. z2 = w2^T * a1 + b2
  5. a2 = ReLU(z2)
  6. z_out = w_out^T * a2 + b_out
  7. y_pred = softmax(z_out) (probabilities)

Backward Pass (Training):
  1. Compute loss L
  2. dL/dw_out (gradient at output layer)
  3. dL/dw2 (propagate through hidden layer)
  4. dL/dw1 (propagate through first hidden layer)
  5. Update weights: w_new = w - lr * dL/dw

Parameter Count:
  Layer 1: 784*128 + 128 = 100,480 parameters
  Layer 2: 128*64 + 64 = 8,256 parameters
  Layer 3: 64*10 + 10 = 650 parameters
  Total: 109,386 parameters

Deep Networks:
  • Many layers allow hierarchical features
  • Lower layers: Simple features (edges)
  • Middle layers: Complex patterns (shapes)
  • Upper layers: Semantic concepts (objects)
""")

# ============================================================================
# PART 2: ACTIVATION FUNCTIONS
# ============================================================================
print("\n" + "=" * 80)
print("⚡ LECTURE 7: ACTIVATION FUNCTIONS")
print("=" * 80)

print("""
Why Activation Functions?
──────────────────────────
Without activation:
  y = w3(w2(w1*x + b1) + b2) + b3
    = w3*w2*w1*x + ...
    = W*x + b  (still linear!)
  
Stacking layers without activation = single linear transformation
Can't learn complex non-linear functions

Activation Functions:
──────────────────

1. ReLU (Rectified Linear Unit):
   ReLU(z) = max(0, z)
   
   Properties:
     • z ≥ 0: Returns z
     • z < 0: Returns 0
     • Simple, fast computation
     • Sparse activations (many zeros)
   
   Advantages:
     • Fast training
     • Avoids vanishing gradient (for z > 0)
     • Default choice for hidden layers
   
   Disadvantages:
     • Dead ReLU: Some neurons always 0
     • Dying ReLU problem

2. Sigmoid:
   σ(z) = 1 / (1 + e^(-z))
   
   Properties:
     • Output range: [0, 1]
     • S-shaped curve
     • Smooth gradients
   
   Use case:
     • Binary classification output
     • Old networks (rarely used now)
     • Very prone to vanishing gradient

3. Tanh (Hyperbolic Tangent):
   tanh(z) = (e^z - e^(-z)) / (e^z + e^(-z))
   
   Properties:
     • Output range: [-1, 1]
     • Centered at 0 (better than sigmoid)
     • Smooth gradients
   
   Use case:
     • RNN/LSTM networks
     • Slightly better than sigmoid

4. Softmax:
   σ(z_i) = e^z_i / Σ_j e^z_j
   
   Properties:
     • Output range: [0, 1]
     • Sums to 1 (valid probability)
     • Multi-class classification
   
   Use case:
     • Output layer for classification
""")

Observations:
  • ReLU: Simple (0 or z), fast
  • Sigmoid: Smooth [0,1], prone to vanishing gradients
  • Tanh: Smooth [-1,1], centered (better than sigmoid)
  
For Machine Translation (Transformer):
  • Encoder/Decoder layers: ReLU in feed-forward
  • Attention outputs: Linear (no activation)
  • Final layer: Softmax over vocabulary
""")

# ============================================================================
# PART 3: BACKPROPAGATION & CHAIN RULE
# ============================================================================
print("\n" + "=" * 80)
print("⛓️  LECTURE 7: BACKPROPAGATION & CHAIN RULE")
print("=" * 80)

print("""
Backpropagation Algorithm:
──────────────────────────
Compute gradients via chain rule (dynamic programming)

Chain Rule of Calculus:
  If y = f(u) and u = g(x), then
  dy/dx = dy/du * du/dx

Example: y = ReLU(w*x + b)
  Let u = w*x + b
  Then y = ReLU(u)
  
  dy/dw = dy/du * du/dw
        = ReLU'(u) * x
        = (u > 0) ? x : 0
  
  dy/db = dy/du * du/db
        = ReLU'(u) * 1
        = (u > 0) ? 1 : 0

Forward Pass Example:
─────────────────────
Input: x = 0.5
Weight: w = 2.0, b = 0.1

Forward:
  u1 = 2.0 * 0.5 + 0.1 = 1.1
  a1 = ReLU(1.1) = 1.1  (since 1.1 > 0)
  
Loss (simplified): L = (a1 - target)²
Assume target = 0, so L = 1.1² = 1.21

Backward Pass:
─────────────
1. dL/da1 = 2 * (a1 - target) = 2 * 1.1 = 2.2
2. da1/du1 = ReLU'(u1) = 1 (since u1 > 0)
3. du1/dw = x = 0.5
4. du1/db = 1

Final Gradients:
  dL/dw = dL/da1 * da1/du1 * du1/dw
        = 2.2 * 1 * 0.5 = 1.1
  
  dL/db = dL/da1 * da1/du1 * du1/db
        = 2.2 * 1 * 1 = 2.2

Weight Update (lr = 0.01):
  w_new = w - lr * dL/dw = 2.0 - 0.01 * 1.1 = 1.989
  b_new = b - lr * dL/db = 0.1 - 0.01 * 2.2 = 0.078

Computational Efficiency:
  • Backprop: O(n_params) operations
  • Forward + Backward = ~2x forward cost
  • Alternative (finite differences): O(n_params²) operations
  • Backprop is essential for deep networks
""")

def backprop_example():
    """Simple backpropagation example"""
    
    print("\n🔄 Backpropagation Example:")
    
    # Using PyTorch for automatic differentiation
    x = torch.tensor([0.5], requires_grad=False)
    w = torch.tensor([2.0], requires_grad=True)
    b = torch.tensor([0.1], requires_grad=True)
    target = torch.tensor([0.0])
    
    print(f"\nInitial values:")
    print(f"  x={x.item():.2f}, w={w.item():.2f}, b={b.item():.2f}, target={target.item():.2f}")
    
    # Forward pass
    u = w * x + b
    a = torch.relu(u)
    loss = (a - target) ** 2
    
    print(f"\nForward pass:")
    print(f"  u = w*x + b = {u.item():.2f}")
    print(f"  a = ReLU(u) = {a.item():.2f}")
    print(f"  L = (a - target)² = {loss.item():.2f}")
    
    # Backward pass
    loss.backward()
    
    print(f"\nBackward pass (gradients):")
    print(f"  dL/dw = {w.grad.item():.2f}")
    print(f"  dL/db = {b.grad.item():.2f}")
    
    # Update
    lr = 0.01
    with torch.no_grad():
        w_new = w - lr * w.grad
        b_new = b - lr * b.grad
    
    print(f"\nAfter update (lr={lr}):")
    print(f"  w_new = {w_new.item():.3f}")
    print(f"  b_new = {b_new.item():.3f}")

# ============================================================================
# PART 4: GRADIENT DESCENT & OPTIMIZATION
# ============================================================================
print("\n" + "=" * 80)
print("📉 LECTURE 7: GRADIENT DESCENT & OPTIMIZATION")
print("=" * 80)

print("""
Gradient Descent:
─────────────────
Update rule: θ_new = θ - lr * ∇L

Where:
  θ = parameters (weights, biases)
  lr = learning rate (step size)
  ∇L = gradient of loss

Effect of Learning Rate:
  • lr too small: Slow training, may not converge
  • lr too large: Oscillations, divergence
  • lr optimal: Fast convergence

Variants:

1. SGD (Stochastic Gradient Descent):
   Update on single sample or mini-batch
   θ_new = θ - lr * ∇L_batch
   
   Pros: Fast, noisy gradients help escape local minima
   Cons: Noisy, unpredictable convergence

2. Adam (Adaptive Moment Estimation):
   Adaptive learning rates per parameter
   
   Keeps running average of gradients (momentum)
   Keeps running average of gradient squares (variance)
   
   Update: θ_new = θ - α * m_hat / (√v_hat + ε)
   
   Properties:
     • Adaptive: Different LR per parameter
     • Momentum: Accelerates in consistent directions
     • Variance normalization: Stabilizes training
   
   Default for most deep learning

3. AdamW (Adam with Weight Decay):
   Adam + L2 regularization
   Slightly better than standard Adam

Learning Rate Scheduling:
──────────────────────
Adjust learning rate during training

• Warmup: Gradually increase LR from 0
  Why: Prevents bad updates early (loss unstable)

• Decay: Gradually decrease LR
  Why: Fine-tuning requires smaller steps

• Cosine annealing: cos-shaped decay
  Why: Good empirical performance

• ReduceLROnPlateau: Decrease if validation plateaus
  Why: Adapt to training dynamics
""")

# ============================================================================
# PART 5: LECTURE 7 IN NMT CONTEXT
# ============================================================================
print("\n" + "=" * 80)
print("🧠 LECTURE 7 CONCEPTS IN NEURAL MACHINE TRANSLATION")
print("=" * 80)

print("""
How Lecture 7 Relates to NMT:
──────────────────────────────

1. ARCHITECTURE (Multiple Layers):
   Transformer NMT:
     • 12 encoder layers
     • 12 decoder layers
     • Each with attention + feed-forward
     • 600M total parameters
   
   Feature Hierarchy:
     • Layer 1-4: Morphology, syntax
     • Layer 5-8: Semantic patterns
     • Layer 9-12: Translation logic

2. ACTIVATION FUNCTIONS:
   In transformer:
     • Attention: Linear (no activation)
     • Feed-forward: ReLU in hidden
     • Output: Softmax over vocabulary
   
   Softmax for probability distribution:
     P(word) = exp(score) / Σ exp(all_scores)

3. BACKPROPAGATION:
   Computing gradients through:
     • 24 layers
     • Attention mechanisms
     • Embedding layers
     • Output softmax
   
   Chain rule applied 600M times per update!

4. OPTIMIZATION:
   Training uses:
     • Adam optimizer (adaptive learning rates)
     • Warmup (first 4000 steps)
     • Learning rate scheduling
     • Gradient clipping (max_grad_norm)
   
   Loss function: Cross-entropy
     L = -log(P(correct_word))

5. REGULARIZATION:
   Prevents overfitting:
     • Dropout (random neuron zeroing)
     • Layer normalization (stabilizes)
     • Weight decay (L2 penalty)
""")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("LECTURE 7: DEEP LEARNING - BACKPROPAGATION & OPTIMIZATION")
    print("=" * 80)
    
    # Activations
    activation_functions_demo()
    
    # Backprop
    backprop_example()
    
    # Optimization
    optimization_demo()
    
    print("\n" + "=" * 80)
    print(" LECTURE 7: ALL CONCEPTS IMPLEMENTED")
    print("=" * 80)
    print("""
Summary:
   Neural Network: Hierarchical feature learning
   Activations: ReLU, Sigmoid, Tanh, Softmax
   Backpropagation: Efficient gradient computation via chain rule
   Gradient Descent: Iterative optimization
   Adam Optimizer: Adaptive, works well in practice
  
In Your NMT Project:
  • 24 layers extract hierarchical translation features
  • ReLU activations enable non-linear learning
  • Backprop computes gradients through all 600M parameters
  • Adam optimizer trains efficiently
  • Softmax outputs valid probability distribution over words
""")
