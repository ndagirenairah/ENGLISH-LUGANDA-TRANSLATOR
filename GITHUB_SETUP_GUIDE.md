# 🚀 GitHub Setup & Push Guide

**Complete step-by-step instructions to push your Luganda-English Translator to GitHub**

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ Git installed on your computer
  - Windows: Download from https://git-scm.com/download/win
  - Mac: `brew install git`
  - Linux: `sudo apt install git`

- ✅ GitHub account (free): https://github.com/signup

- ✅ Repository created: https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR

- ✅ All project files ready locally

---

## 🔧 Step 1: Verify Your Git Installation

Open **PowerShell** (Windows), **Terminal** (Mac/Linux), and run:

```bash
git --version
git config --global user.name "Your Name"
git config --global user.email "your.email@gmail.com"
```

**Example:**
```bash
git config --global user.name "Nairah Ndigire"
git config --global user.email "ndagirenairah@gmail.com"
```

---

## 🗂️ Step 2: Navigate to Your Project Directory

Change to your project folder:

```bash
cd "d:\ENGLISH-LUGANDA TRANSLATOR"
```

Verify you're in the right place:

```bash
ls
```

You should see:
- `Step1_Environment_Setup.py`
- `Step2_Load_Dataset.py`
- (and other files)

---

## 📝 Step 3: Initialize Git Repository Locally

Run this command **once** in your project folder:

```bash
git init
```

Output:
```
Initialized empty Git repository in d:\ENGLISH-LUGANDA TRANSLATOR\.git/
```

---

## ✅ Step 4: Add All Files to Git Staging Area

Add everything:

```bash
git add .
```

Or verify what's being added:

```bash
git status
```

You should see (in green):
```
new file:   Step1_Environment_Setup.py
new file:   Step2_Load_Dataset.py
new file:   Step3_Data_Preprocessing.py
... (all files)
```

---

## 💬 Step 5: Create First Commit

Make your initial commit:

```bash
git commit -m "Initial commit: Complete Luganda-English translator pipeline with multi-source datasets and rigorous evaluation"
```

Output:
```
[main (root-commit) abc123d] Initial commit...
 12 files changed, 5000 insertions(+)
 create mode 100644 Step1_Environment_Setup.py
 create mode 100644 Step2_Load_Dataset.py
 ... (more files)
```

---

## 🔌 Step 6: Add Remote Repository

Connect your local repo to GitHub:

```bash
git remote add origin https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git
```

Verify the connection:

```bash
git remote -v
```

Output:
```
origin  https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git (fetch)
origin  https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git (push)
```

---

## 🚀 Step 7: Push to GitHub

Push your code to GitHub:

```bash
git branch -M main
git push -u origin main
```

**First time?** You'll be asked to authenticate:
- Click through the browser login
- Or use your GitHub personal access token

**Output (success):**
```
Enumerating objects: 12, done.
Counting objects: 100% (12/12), done.
Delta compression using up to 8 threads.
Compressing objects: 100% (10/10), done.
Writing objects: 100% (12/12), 250.15 KiB | 5.00 MiB/s, done.
Total 12 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git
 * [new branch]      main -> main
Branch 'main' is set to track remote branch 'main' from 'origin'.
```

✅ **Success!** Your code is now on GitHub!

---

## 🎉 Verify on GitHub

1. Go to: https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR
2. You should see all your files listed
3. The README should display with formatting

---

## 📚 What's Inside Your Repository

### Files You Should Have

| File | Purpose |
|------|---------|
| `README.md` | Project overview & quick start |
| `FORMAL_PROPOSAL.md` | Academic motivation & background |
| `PRESENTATION_NOTES.txt` | Talking points for your lecturer |
| `Step1-8_*.py` | Complete 8-step pipeline |
| `Step5_Train_Model_Advanced.py` | Two-stage training (bonus) |
| `Step7_Evaluate_Advanced.py` | Multi-metric evaluation |
| `COMPARISON_SingleVsMultiSource.py` | Dataset comparison analysis |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Files to exclude from Git |

---

## 🔄 Making Updates & Additional Commits

After you train your model or make improvements:

```bash
# Make your changes...

# Add modified files
git add .

# Create descriptive commit
git commit -m "Add trained model checkpoints and evaluation results"

# Push to GitHub
git push
```

**Good commit messages:**
```
✅ git commit -m "Add two-stage training strategy"
✅ git commit -m "Update evaluation with METEOR and TER metrics"
❌ git commit -m "fix stuff"
❌ git commit -m "update"
```

---

## 🏷️ Creating Release Tags

After training is successful, create a tagged release:

```bash
git tag -a v1.0 -m "Version 1.0: Trained model with 48 BLEU score"
git push --tags
```

---

## 🚨 Troubleshooting

### Problem: Authentication Failed

**Solution 1: Use Personal Access Token**
```bash
git remote set-url origin https://YOUR_PAT@github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git
```

**Solution 2: Use SSH (Advanced)**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@gmail.com"

# Add to GitHub settings → SSH Keys

# Change remote to SSH
git remote set-url origin git@github.com:ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR.git
```

### Problem: File Too Large

If a model file > 100MB:
```bash
# Option 1: Use Git LFS (Large File Storage)
git lfs install
git lfs track "*.pt"

# Option 2: Add to .gitignore and upload separately
echo "models/trained_model/*.pt" >> .gitignore
```

### Problem: Wrong Commit

```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Fix last commit message
git commit --amend -m "New message"
git push --force-with-lease
```

---

## 🎓 For Your Lecturer: Show GitHub Stats

Once on GitHub, you can show your lecturer:

1. **Repository**: https://github.com/ndagirenairah/ENGLISH-LUGANDA-TRANSLATOR
2. **Code statistics**: 1200+ lines of Python
3. **Commit history**: Shows your development process
4. **README**: Professional documentation
5. **File structure**: Well-organized project

---

## 📊 What Appears on Your GitHub Profile

After pushing, GitHub shows:
- ✅ Repository on your profile
- ✅ Contribution graph (green squares = commits)
- ✅ Your code publicly viewable
- ✅ Cloneable repository for others

---

## 💡 Pro Tips

### 1. **Add a Project Description**
On GitHub repo page:
- Click "Settings"
- Add description: "Neural Machine Translation for Luganda-English with multi-source datasets"
- Add topics: `machine-learning`, `nlp`, `translation`, `luganda`

### 2. **Add Social Preview**
- Create a nice image (400x210px)
- Upload as "Social preview" in Settings

### 3. **Create Release Notes**
```bash
git tag -a v1.0 -m "Initial release - 48 BLEU score achieved"
git push --tags
```

Then on GitHub → Releases, add detailed notes.

### 4. **Pin Important Files**
In your repo, tell people to:
- Start with `README.md`
- Review `FORMAL_PROPOSAL.md` for background
- See `PRESENTATION_NOTES.txt` for summary

---

## ✨ Next Steps After Pushing

1. ✅ **Create GitHub Actions** (continuous testing)
   - File: `.github/workflows/test.yml`
   - Automatically runs tests on push

2. ✅ **Add issues & milestones**
   - Let community know what you're working on

3. ✅ **Create GitHub Pages** (optional)
   - Host interactive demo
   - Show live results

4. ✅ **Share your repo**
   - Tweet: "Just published my Luganda-English translator! Check it out: [link]"
   - LinkedIn: Professional post about low-resource NLP
   - University forum: Share with classmates

---

## 📋 Checklist Before Submitting to Your Lecturer

Before presenting or submitting your project, verify:

- ✅ Repository is public
- ✅ README.md displays correctly
- ✅ All 8 Step files included
- ✅ requirements.txt has all dependencies
- ✅ .gitignore excludes large files
- ✅ FORMAL_PROPOSAL.md in repo
- ✅ PRESENTATION_NOTES.txt for reference
- ✅ At least 5+ commits (shows progress)
- ✅ No API keys or passwords exposed
- ✅ Code has no syntax errors

---

## 🎯 Expected GitHub Layout

Your repo should look like:

```
ENGLISH-LUGANDA-TRANSLATOR/
├── README.md                          ← People see this first
├── FORMAL_PROPOSAL.md                 ← Academic background
├── PRESENTATION_NOTES.txt
├── Step1_Environment_Setup.py
├── Step2_Load_Dataset.py
├── Step3_Data_Preprocessing.py
├── Step4_MarianMT_Setup.py
├── Step5_Train_Model.py
├── Step5_Train_Model_Advanced.py
├── Step6_Test_Model.py
├── Step7_Evaluate_BLEU.py
├── Step7_Evaluate_Advanced.py
├── Step8_Build_WebApp.py
├── COMPARISON_SingleVsMultiSource.py
├── requirements.txt
├── .gitignore
└── GITHUB_SETUP_GUIDE.md (this file)
```

---

## 🎉 Congratulations!

You've successfully:
- ✅ Organized your project
- ✅ Pushed to GitHub
- ✅ Have public code repository
- ✅ Are ready to present

**Now**: Run your pipeline, train your model, and get those BLEU scores! 🚀

---

## 📞 Need Help?

If `git` commands fail:

1. **Check Git installation**
   ```bash
   git --version
   ```

2. **Verify GitHub authentication**
   ```bash
   git ls-remote origin
   ```

3. **Read error messages carefully** - they often tell you exactly what's wrong

4. **Ask GitHub support**: https://support.github.com

---

**Remember**: Your GitHub repo shows your employer/university that you can:
- Write clean code
- Document your work
- Use professional tools
- Collaborate professionally

Make your repo shine! ⭐

---

**Last Updated**: April 17, 2026
**For**: Makerere University & ndagirenairah
