"""
LECTURE 8: CNNs and Transfer Learning
Deep implementation of:
- Convolutional layers and kernels
- Pooling layers
- Transfer learning and fine-tuning
"""

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')

print("=" * 80)
print("LECTURE 8: CONVOLUTIONAL NEURAL NETWORKS AND TRANSFER LEARNING")
print("=" * 80)

# ============================================================================
# CONVOLUTIONAL LAYERS
# ============================================================================
print("\n" + "=" * 80)
print("CONVOLUTIONAL LAYERS AND KERNELS")
print("=" * 80)

print("""
Convolution Operation:
Slide a small kernel (filter) over the input
At each position, compute element-wise product and sum

Kernel (3x3 example):
[a b c]
[d e f]
[g h i]

Properties:
- Parameter sharing: Same kernel used across all positions
- Spatial locality: Kernel captures local patterns
- Translation invariance: Detects same features at different positions

Common Kernel Types:
1. Edge Detection (horizontal):
   [-1 -2 -1]
   [ 0  0  0]
   [ 1  2  1]

2. Edge Detection (vertical):
   [-1  0  1]
   [-2  0  2]
   [-1  0  1]

3. Blur (averaging):
   [1/9 1/9 1/9]
   [1/9 1/9 1/9]
   [1/9 1/9 1/9]

Deep Networks:
- Early layers: Low-level features (edges, textures)
- Middle layers: Mid-level features (shapes, patterns)
- Late layers: High-level features (objects, concepts)
""")

def convolution_demo():
    """Demonstrate convolution operation"""
    print("\nConvolution Example:")
    
    # Simple 5x5 input
    input_data = np.array([
        [1, 2, 3, 2, 1],
        [2, 4, 6, 4, 2],
        [3, 6, 9, 6, 3],
        [2, 4, 6, 4, 2],
        [1, 2, 3, 2, 1]
    ], dtype=float)
    
    # Edge detection kernel
    kernel = np.array([
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1]
    ], dtype=float)
    
    print(f"  Input (5x5):\n{input_data.astype(int)}")
    print(f"\n  Kernel (3x3 edge detection):\n{kernel.astype(int)}")
    
    # Apply convolution at center
    window = input_data[1:4, 1:4]
    result = np.sum(window * kernel)
    
    print(f"\n  Center window:\n{window.astype(int)}")
    print(f"  Output at center: {result:.0f}")
    print(f"  (Detected vertical edge)")
    
    # Compute output size
    input_size = 5
    kernel_size = 3
    padding = 0
    stride = 1
    
    output_size = (input_size - kernel_size + 2*padding) // stride + 1
    print(f"\n  Output size: {output_size}x{output_size}")

# ============================================================================
# POOLING LAYERS
# ============================================================================
print("\n" + "=" * 80)
print("POOLING LAYERS")
print("=" * 80)

print("""
Pooling reduces spatial dimensions while retaining important information

Max Pooling:
- Divide input into non-overlapping windows
- Output maximum value in each window
- Preserves strongest features

Average Pooling:
- Divide input into non-overlapping windows
- Output average value in each window
- Smoother feature representation

Example (2x2 Max Pooling):
Input (4x4):           Output (2x2):
[1  2  3  4]           [5  8]
[5  6  7  8]      →    [13 14]
[9  10 11 12]
[13 14 15 16]

Benefits:
- Reduces parameters and computation
- Increases receptive field
- Provides translation invariance
- Helps prevent overfitting
""")

def pooling_demo():
    """Demonstrate pooling operation"""
    print("\nPooling Example:")
    
    # 4x4 feature map
    feature_map = np.array([
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ], dtype=float)
    
    print(f"  Input feature map (4x4):\n{feature_map.astype(int)}")
    
    # 2x2 Max Pooling
    output = np.zeros((2, 2))
    
    for i in range(2):
        for j in range(2):
            window = feature_map[i*2:(i+1)*2, j*2:(j+1)*2]
            output[i, j] = np.max(window)
    
    print(f"\n  2x2 Max Pooling output:\n{output.astype(int)}")
    
    # Average pooling
    output_avg = np.zeros((2, 2))
    
    for i in range(2):
        for j in range(2):
            window = feature_map[i*2:(i+1)*2, j*2:(j+1)*2]
            output_avg[i, j] = np.mean(window)
    
    print(f"\n  2x2 Average Pooling output:\n{output_avg.astype(int)}")

# ============================================================================
# TRANSFER LEARNING
# ============================================================================
print("\n" + "=" * 80)
print("TRANSFER LEARNING")
print("=" * 80)

print("""
Key Idea:
Use pre-trained model as starting point instead of training from scratch

Pre-trained Models:
- ImageNet models: Trained on 1M+ images, 1000 categories
- NLP models: Trained on billions of text tokens
- Our project: Helsinki-NLP/opus-mt-en-mul (600M params, 100M sentences)

Layer Freezing Strategy:

Option 1: Use as Feature Extractor (Freeze all layers)
- Keep pre-trained weights fixed
- Train only final classification layer
- Fast, requires less data
- Good for small datasets

Option 2: Fine-tuning (Unfreeze some layers)
- Unfreeze final N layers
- Train with lower learning rate
- Requires more data
- Better performance on target task

Option 3: Fine-tune everything (Lower LR)
- Unfreeze all layers
- Use very low learning rate (e.g., 1e-5 vs 1e-3)
- Prevents destroying learned features
- Best performance, requires most data

Why Transfer Learning Works:
1. Early layers learn universal features (edges, textures)
2. Later layers learn task-specific patterns
3. Starting from learned features is better than random initialization
4. Reduces training time and data requirements

Typical Speedup:
- Training time: 10-100x faster
- Data required: 10-100x less
- Performance: Often matches full training

Your NMT System:
Base model (Helsinki-NLP): 600M params, trained on 100M+ sentences
Fine-tune on: 300K English-Luganda pairs
Result: Excellent translation quality with limited compute
""")

def transfer_learning_comparison():
    """Compare training approaches"""
    print("\nTransfer Learning Comparison:")
    
    print("\n  Training from Scratch:")
    print("    Data required: 1M+ parallel sentences")
    print("    Training time: 100-200 GPU hours")
    print("    Compute cost: High")
    print("    Starting point: Random weights")
    
    print("\n  Fine-tuning Pre-trained Model:")
    print("    Data required: 300K parallel sentences (10x less)")
    print("    Training time: 2-4 GPU hours (50x faster)")
    print("    Compute cost: Moderate")
    print("    Starting point: Already understands language")
    
    print("\n  Feature Extraction Only:")
    print("    Data required: 100K parallel sentences")
    print("    Training time: 30 minutes (200x faster)")
    print("    Compute cost: Minimal")
    print("    Performance: Good but suboptimal")
    
    print("\n  Your Project (Fine-tuning):")
    print("    Data: 300K English-Luganda pairs")
    print("    Time: 2-4 hours")
    print("    Model: Helsinki-NLP/opus-mt-en-mul")
    print("    Expected BLEU: 60-90 (excellent)")

# ============================================================================
# CNN ARCHITECTURE
# ============================================================================
print("\n" + "=" * 80)
print("FULL CNN ARCHITECTURE EXAMPLE")
print("=" * 80)

print("""
Typical Image Classification CNN:

INPUT (224x224x3)
    ↓
CONV (32 filters, 3x3)  → (222x222x32)
RELU
POOL (2x2)              → (111x111x32)
    ↓
CONV (64 filters, 3x3)  → (109x109x64)
RELU
POOL (2x2)              → (54x54x64)
    ↓
CONV (128 filters, 3x3) → (52x52x128)
RELU
POOL (2x2)              → (26x26x128)
    ↓
FLATTEN                 → (86528,)
    ↓
DENSE (256)
RELU
DROPOUT (0.5)
    ↓
DENSE (10)              → Output classes
SOFTMAX
    ↓
OUTPUT

Parameter Count:
Conv1: 32 * (3*3*3 + 1) = 896
Conv2: 64 * (3*3*32 + 1) = 18,496
Conv3: 128 * (3*3*64 + 1) = 73,856
Dense1: 256 * 86528 + 256 = 22,150,400
Dense2: 10 * 256 + 10 = 2,570
Total: ~22.2M parameters
""")

def cnn_architecture():
    """Describe CNN architecture"""
    print("\nCNN Architecture Layers:")
    
    layers = [
        ("Input", (224, 224, 3)),
        ("Conv 32x3x3", (222, 222, 32)),
        ("ReLU", (222, 222, 32)),
        ("MaxPool 2x2", (111, 111, 32)),
        ("Conv 64x3x3", (109, 109, 64)),
        ("ReLU", (109, 109, 64)),
        ("MaxPool 2x2", (54, 54, 64)),
        ("Conv 128x3x3", (52, 52, 128)),
        ("ReLU", (52, 52, 128)),
        ("MaxPool 2x2", (26, 26, 128)),
        ("Flatten", (86528,)),
        ("Dense 256", (256,)),
        ("ReLU", (256,)),
        ("Dense 10", (10,)),
        ("Softmax", (10,)),
    ]
    
    for layer_name, shape in layers:
        print(f"  {layer_name:20} → {shape}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================
if __name__ == "__main__":
    print("\nRunning Lecture 8 demonstrations...\n")
    
    # Convolution
    convolution_demo()
    
    # Pooling
    pooling_demo()
    
    # Transfer Learning
    transfer_learning_comparison()
    
    # CNN Architecture
    cnn_architecture()
    
    print("\n" + "=" * 80)
    print("Lecture 8 demonstrations complete")
    print("=" * 80)
