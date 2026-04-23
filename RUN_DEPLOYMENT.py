#!/usr/bin/env python3
"""
🎯 MASTER AUTOMATION SCRIPT
Monitors training and automatically deploys when ready
"""

import os
import time
import subprocess
import sys

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║               🚀 ENGLISH-LUGANDA TRANSLATOR - LIVE DEPLOYMENT 🚀             ║
║                                                                              ║
║                    AUTOMATIC OPTIMIZATION & DEPLOYMENT                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

print("\n📋 DEPLOYMENT CHECKLIST:\n")

# Step 1: Check training status
print("✓ STEP 1: Monitor Training Completion")
print("   Status: ⏳ Running TRAIN_FAST_NOW.py")
print("   Expected: Complete in 2-5 minutes\n")

# Step 2: Auto-deploy
print("✓ STEP 2: Auto-Deploy (Once training completes)")
print("   Status: ⏳ Waiting for model file...\n")

# Step 3: Live validation
print("✓ STEP 3: Validate & Go Live")
print("   Status: ⏳ Ready\n")

print("─" * 80)
print("\n📊 SYSTEM INFORMATION:\n")

import platform
import torch
print(f"   OS: {platform.system()} {platform.release()}")
print(f"   Python: {sys.version.split()[0]}")
print(f"   PyTorch: {torch.__version__}")
print(f"   GPU Available: {'Yes ✅' if torch.cuda.is_available() else 'No (using CPU)'}")
print(f"   Working Directory: {os.getcwd()}\n")

print("─" * 80)

# Monitor for trained model
print("\n🔄 MONITORING TRAINING PROGRESS...\n")

pytorch_bin = "models/trained_model/pytorch_model.bin"
max_wait = 600  # 10 minute timeout
start_time = time.time()
check_interval = 10  # Check every 10 seconds

while time.time() - start_time < max_wait:
    if os.path.exists(pytorch_bin):
        file_size = os.path.getsize(pytorch_bin) / 1e6
        
        print(f"\n✅ MODEL TRAINED!")
        print(f"   File: {pytorch_bin}")
        print(f"   Size: {file_size:.0f} MB")
        print(f"   Time: {(time.time() - start_time):.0f} seconds\n")
        
        # Auto-run deployment
        print("─" * 80)
        print("\n🚀 AUTO-DEPLOYMENT IN PROGRESS...\n")
        
        try:
            result = subprocess.run(
                [sys.executable, "AUTO_DEPLOY.py"],
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                print("\n" + "=" * 80)
                print("✅ DEPLOYMENT SUCCESSFUL!")
                print("=" * 80)
                print("""
🎉 YOUR TRANSLATOR IS READY!

TO START THE WEB APP:
    python app.py

Then visit: http://localhost:5000

Features:
  ✓ Real-time Luganda→English translation
  ✓ Cultural phrase dictionary
  ✓ Translation history
  ✓ Mobile-responsive interface

Happy translating! 🌟
""")
                sys.exit(0)
        except Exception as e:
            print(f"⚠️  Deployment script error: {e}")
            print("   Manually run: python AUTO_DEPLOY.py")
        
        break
    
    elapsed = time.time() - start_time
    remaining = max_wait - elapsed
    bar_len = 40
    progress = elapsed / max_wait
    filled = int(bar_len * progress)
    bar = "█" * filled + "░" * (bar_len - filled)
    
    print(f"\r   [{bar}] {elapsed:3.0f}s / {max_wait//60}m  (Remaining: {remaining/60:.1f}m)", end="", flush=True)
    time.sleep(check_interval)

print("\n\n⚠️  Training timeout - check terminal for errors")
print("   Manually run: python TRAIN_FAST_NOW.py")
