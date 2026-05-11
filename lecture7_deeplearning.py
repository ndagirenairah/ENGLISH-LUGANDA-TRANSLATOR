"""
LECTURE 7: Deep Learning Fundamentals
Deep implementation of:
- Neural network architecture
- Activation functions: ReLU, Sigmoid, Tanh, Softmax
- Backpropagation and chain rule
- Optimization: Gradient descent, Adam, Learning rate scheduling
"""

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')

print("=" * 80)
print("LECTURE 7: DEEP LEARNING FUNDAMENTALS")
print("=" * 80)

# ============================================================================
# ACTIVATION FUNCTIONS
# ============================================================================
print("\n" + "=" * 80)
print("ACTIVATION FUNCTIONS")
print("=" * 80)

print("""
Activation functions introduce non-linearity into neural networks

ReLU (Rectified Linear Unit):
  f(z) = max(0, z)
  - Fast to compute
  - Sparse activation
  - Avoids vanishing gradient
  - Used in hidden layers

Sigmoid:
  σ(z) = 1 / (1 + e^(-z))
  - Output: [0, 1]
  - Can suffer from vanishing gradient
  - Used in binary classification output

Tanh (Hyperbolic Tangent):
  tanh(z) = (e^z - e^(-z)) / (e^z + e^(-z))
  - Output: [-1, 1]
  - Stronger gradient than sigmoid
  - Zero-centered output

Softmax (Multi-class):
  softmax(z_i) = e^(z_i) / sum(e^(z_j))
  - Outputs probabilities for K classes
  - Normalizes to sum=1
  - Used in multi-class output layers
""")

def activation_functions_demo():
    """Demonstrate various activation functions"""
    print("\nActivation Functions Example:")
    
    z = np.linspace(-5, 5, 100)
    
    # ReLU
    relu = np.maximum(0, z)
    
    # Sigmoid
    sigmoid = 1 / (1 + np.exp(-z))
    
    # Tanh
    tanh = np.tanh(z)
    
    print("\n  Value ranges:")
    print(f"    ReLU: [{relu.min():.2f}, {relu.max():.2f}]")
    print(f"    Sigmoid: [{sigmoid.min():.2f}, {sigmoid.max():.2f}]")
    print(f"    Tanh: [{tanh.min():.2f}, {tanh.max():.2f}]")
    
    print("\n  Example values at z=2:")
    z_test = 2.0
    print(f"    ReLU(2) = {max(0, z_test):.4f}")
    print(f"    Sigmoid(2) = {1/(1+np.exp(-z_test)):.4f}")
    print(f"    Tanh(2) = {np.tanh(z_test):.4f}")
    
    return relu, sigmoid, tanh

# ============================================================================
# NEURAL NETWORK ARCHITECTURE
# ============================================================================
print("\n" + "=" * 80)
print("NEURAL NETWORK ARCHITECTURE")
print("=" * 80)

print("""
Simple Neural Network:
INPUT → HIDDEN LAYER 1 → HIDDEN LAYER 2 → OUTPUT

Forward Pass (Prediction):
z1 = W1 * x + b1
a1 = ReLU(z1)
z2 = W2 * a1 + b2
a2 = ReLU(z2)
z3 = W3 * a2 + b3
output = Sigmoid(z3)  for binary classification

Where:
- W = weight matrices
- b = bias vectors
- a = activated outputs (passed to next layer)
- z = pre-activation values

Parameters:
- Input layer: 30 features (breast cancer dataset)
- Hidden 1: 32 neurons with ReLU
- Hidden 2: 16 neurons with ReLU
- Output: 1 neuron with Sigmoid (binary classification)
""")

def neural_network_architecture():
    """Describe neural network architecture"""
    print("\nNeural Network Architecture:")
    
    architecture = {
        'input': 30,
        'hidden1': 32,
        'hidden2': 16,
        'output': 1
    }
    
    print(f"  Input layer: {architecture['input']} neurons")
    print(f"  Hidden 1: {architecture['hidden1']} neurons (ReLU)")
    print(f"  Hidden 2: {architecture['hidden2']} neurons (ReLU)")
    print(f"  Output: {architecture['output']} neuron (Sigmoid)")
    
    # Count parameters
    params = {}
    params['W1'] = architecture['input'] * architecture['hidden1']
    params['b1'] = architecture['hidden1']
    params['W2'] = architecture['hidden1'] * architecture['hidden2']
    params['b2'] = architecture['hidden2']
    params['W3'] = architecture['hidden2'] * architecture['output']
    params['b3'] = architecture['output']
    
    total_params = sum(params.values())
    
    print(f"\n  Total parameters: {total_params}")
    for param, count in params.items():
        print(f"    {param}: {count}")
    
    return architecture, total_params

# ============================================================================
# BACKPROPAGATION
# ============================================================================
print("\n" + "=" * 80)
print("BACKPROPAGATION")
print("=" * 80)

print("""
Forward Pass: Compute predictions
Backward Pass: Compute gradients using chain rule

Chain Rule for Backpropagation:
dL/dW3 = dL/dout * dout/dz3 * dz3/dW3

General Form:
dL/dW_i = dL/da * da/dz * dz/dW  (chain of derivatives)

Example (Binary Classification):
- Loss: L = -[y*log(p) + (1-y)*log(1-p)]
- Gradient flow: Loss → Output → Hidden2 → Hidden1 → Weights

Gradient Descent Update:
W_new = W_old - learning_rate * dL/dW
""")

def backpropagation_example():
    """Illustrate backpropagation concept"""
    print("\nBackpropagation Example:")
    
    # Simple example
    # Forward pass
    x = np.array([[2, 3]])
    W1 = np.array([[0.5, 0.3], [0.2, 0.4]])
    
    z1 = np.dot(x, W1)  # Linear combination
    a1 = np.maximum(0, z1)  # ReLU activation
    
    print(f"  Input: {x}")
    print(f"  Weight matrix W1:\n{W1}")
    print(f"  z1 = x * W1: {z1}")
    print(f"  a1 = ReLU(z1): {a1}")
    
    # Backward pass (simplified)
    dL_da1 = np.array([0.1, 0.2])  # Gradient from loss
    
    # Chain rule: dL/dW1 = dL/da1 * da1/dz1 * dz1/dW1
    da1_dz1 = (z1 > 0).astype(float)  # ReLU gradient
    dL_dz1 = dL_da1 * da1_dz1
    dL_dW1 = np.dot(x.T, dL_dz1)
    
    print(f"\n  Backward pass:")
    print(f"  dL/dW1:\n{dL_dW1}")
    print(f"  (Gradient tells us how to update weights)")

# ============================================================================
# OPTIMIZATION: GRADIENT DESCENT & ADAM
# ============================================================================
print("\n" + "=" * 80)
print("OPTIMIZATION ALGORITHMS")
print("=" * 80)

print("""
Gradient Descent (Vanilla):
W = W - lr * dL/dW
- Simple but can be slow
- All parameters use same learning rate
- May oscillate around minimum

Adam (Adaptive Moment Estimation):
- Adaptive learning rate for each parameter
- Momentum: Uses exponential moving average of gradients
- RMSprop: Uses exponential moving average of squared gradients
- Better convergence, handles sparse gradients well

Learning Rate Scheduling:
1. Warmup: Gradually increase LR from 0
   - Prevents bad early updates
   - Typically 5-10% of total steps
   
2. Decay: Gradually decrease LR
   - Cosine decay: Smooth decrease following cosine curve
   - Linear decay: Constant decrease
   - Step decay: Decrease by factor every N steps

Combined Schedule:
Step 0-500 (Warmup): LR goes from 0 to 2e-5
Step 500-5000 (Training): LR decays from 2e-5 to ~0 following cosine
""")

def optimization_demo():
    """Demonstrate optimization concepts"""
    print("\nOptimization Example:")
    
    # Simulated training curves
    steps = np.arange(0, 1000)
    
    # Learning rate schedule
    warmup_steps = 100
    total_steps = 1000
    
    lr_schedule = np.zeros_like(steps, dtype=float)
    
    # Warmup phase
    warmup_mask = steps < warmup_steps
    lr_schedule[warmup_mask] = (steps[warmup_mask] / warmup_steps) * 2e-5
    
    # Cosine decay phase
    decay_mask = steps >= warmup_steps
    progress = (steps[decay_mask] - warmup_steps) / (total_steps - warmup_steps)
    lr_schedule[decay_mask] = 2e-5 * (1 + np.cos(np.pi * progress)) / 2
    
    print(f"  Warmup steps: {warmup_steps}")
    print(f"  Total steps: {total_steps}")
    print(f"  Initial LR: {lr_schedule[0]:.2e}")
    print(f"  Peak LR (end of warmup): {lr_schedule[warmup_steps-1]:.2e}")
    print(f"  Final LR: {lr_schedule[-1]:.2e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("\nRunning Lecture 7 demonstrations...\n")
    
    # Activation functions
    relu, sigmoid, tanh = activation_functions_demo()
    
    # Network architecture
    arch, total_params = neural_network_architecture()
    
    # Backpropagation
    backpropagation_example()
    
    # Optimization
    optimization_demo()
    
    print("\n" + "=" * 80)
    print("Lecture 7 demonstrations complete")
    print("=" * 80)
