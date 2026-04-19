# HOW TO TEST YOUR TRANSLATION MODEL

**Quick Answer**: There are 3 ways to test your model. Pick one:

---

## 🚀 EASIEST WAY: Run Examples Immediately

```bash
python Step6_Test_Model_Interactive.py
```

**What it does:**
- ✅ Loads your trained model
- ✅ Shows 4 example translations
- ✅ You see output instantly

**Example output:**
```
INPUT (Luganda):     Oli otya
Meaning:             How are you?
OUTPUT (English):    How are you

INPUT (Luganda):     Kabaka yalambula abantu
Meaning:             The Kabaka visited people
OUTPUT (English):    The Kabaka visited the people
```

---

## 💻 METHOD 1: HARDCODED TEST SENTENCES

**Best for:** Quick testing without retyping

### Step 1: Open the file
```bash
Step6_Test_Model_Interactive.py
```

### Step 2: Find this section (around line 100):
```python
# EDIT THIS LIST TO TEST CUSTOM SENTENCES:
custom_test_sentences = [
    # "Ndi wa kika kya Mmamba",           # I belong to Mmamba clan
    # "Kabaka assibwamu ekitiibwa",      # The Kabaka is respected
    # "Ssegeza abakulu",                 # Respect the elders
]
```

### Step 3: Add your sentences (uncomment and modify):
```python
custom_test_sentences = [
    "Ndi wa kika kya Mmamba",           # I belong to Mmamba clan
    "Kabaka assibwamu ekitiibwa",       # The Kabaka is respected
    "Ssegeza abakulu",                  # Respect the elders
    "I am learning machine learning",   # Add any test sentence
]
```

### Step 4: Run
```bash
python Step6_Test_Model_Interactive.py
```

### Step 5: Check output
```
INPUT (Luganda):     Ndi wa kika kya Mmamba
OUTPUT (English):    I belong to the Mmamba clan

INPUT (Luganda):     Kabaka assibwamu ekitiibwa
OUTPUT (English):    The Kabaka is respected
```

---

## ⌨️ METHOD 2: INTERACTIVE MODE (TYPE WHILE RUNNING)

**Best for:** Live demonstrations or testing many sentences

### Step 1: Open the file
```bash
Step6_Test_Model_Interactive.py
```

### Step 2: Find this line (around line 125):
```python
ENABLE_INTERACTIVE = False  # <-- CHANGE THIS TO True
```

### Step 3: Change to True
```python
ENABLE_INTERACTIVE = True   # <-- NOW ENABLED
```

### Step 4: Run
```bash
python Step6_Test_Model_Interactive.py
```

### Step 5: You'll see:
```
================================================================================
INTERACTIVE MODE - TYPE YOUR LUGANDA SENTENCES
================================================================================

Type any Luganda sentence to get English translation
Examples:
  - Oli otya
  - Ndi Muganda
  - Kabaka yalambula abantu

Type 'quit' or 'exit' to stop

================================================================================

Enter Luganda sentence:
```

### Step 6: Type sentences
```
Enter Luganda sentence: Oli otya
Translation: How are you

Enter Luganda sentence: Kabaka yalambula abantu  
Translation: The Kabaka visited the people

Enter Luganda sentence: quit
Goodbye!
```

---

## 📊 METHOD 3: FULL DATASET TESTING

**Best for:** Thorough evaluation on test set

Use the original Step6:
```bash
python Step6_Test_Model.py
```

**What it does:**
- ✅ Tests on entire test dataset
- ✅ Shows 10 sample translations
- ✅ Saves detailed results to CSV
- ✅ Generates statistics

---

## 📝 RECOMMENDED TEST SENTENCES

Try these to see if your model works:

### Basic Tests
```
Oli otya                 → How are you?
Ndi Muganda              → I am Lugandan
Webale nnyo              → Thank you very much
Ssebo                    → Sir
```

### Cultural Tests (Best for Your Project!)
```
Ndi wa kika kya Mmamba   → I belong to Mmamba clan
Kabaka yalambula abantu  → The Kabaka visited people
Kabaka assibwamu ekitiibwa → The Kabaka is respected
Ssegeza abakulu          → Respect the elders
```

### Longer Tests
```
Nkekkaanya Oluganda       → I speak Luganda
Agalimi gaffe tumukulira  → We love our country
Kakaasa esaawa ezaano     → Wake up at five o'clock
```

---

## 🎯 WHICH METHOD SHOULD I USE?

| Use Case | Method | Time |
|----------|--------|------|
| Quick test now | Run examples directly | 30 sec |
| Test few sentences | Edit list (Method 1) | 2 min |
| Test many sentences | Interactive (Method 2) | 5 min |
| Full evaluation | Step6_Test_Model.py (Method 3) | 10 min |
| **For presentation** | **Interactive (Method 2)** | **Live** |

---

## 🔥 BEST FOR YOUR PRESENTATION

**Use Method 2 (Interactive Mode)**

Here's why:
- ✅ You can show live translations
- ✅ Type sentences in real-time
- ✅ Shows model working interactively
- ✅ Impressive for demonstration

---

## ⚠️ COMMON ISSUES & FIXES

### Issue: "Model not found" Error
```
Error loading model: [Errno 2] No such file or directory: 'models/trained_model'
```

**Fix**: Make sure you ran Step5 (training) first

---

### Issue: "Translation Error" Output
```
OUTPUT (English):    [Error: CUDA out of memory]
```

**Fix**: Your GPU ran out of memory
- Try smaller max_length: Change line to `max_length=256`
- Or use CPU: Restart with fewer sentences

---

### Issue: Blank or No Output
```
Enter Luganda sentence: 
```

**Fix**: 
- If in interactive mode, you need to PRESS ENTER after typing
- If running examples, wait 10-20 seconds for model to load

---

## 📌 SUMMARY

**Fastest way to test RIGHT NOW:**
```bash
python Step6_Test_Model_Interactive.py
```

**To test with your own sentences:**
1. Edit `custom_test_sentences` list
2. Run script

**For interactive demo:**
1. Change `ENABLE_INTERACTIVE = True`
2. Run script
3. Type sentences

---

**That's it! You're ready to go.** 🚀
