# Git Workflow Guide for Beginners

**Purpose:** This guide helps you commit and push changed files to GitHub for the `graph1` repository.

---

## **Prerequisites**

- Git installed on your system
- Repository cloned locally: `c:\Projects\Graph1`
- Remote repository: `https://github.com/defarloa1-alt/graph1`

---

## **Basic Git Workflow (5 Steps)**

### **1. Check What Changed**

Before committing, see what files have been modified:

```powershell
git status
```

**Output interpretation:**
- `M` = Modified file (tracked by Git, now changed)
- `??` = Untracked file (new file not yet in Git)
- `D` = Deleted file

**Example:**
```
M  CSV/project_p_values_canonical.csv
M  Relationships/relationship_types_seed.cypher
?? Neo4j/new_file.md
```

---

### **2. Stage Files for Commit**

Tell Git which files you want to include in the next commit.

**Stage all changes:**
```powershell
git add -A
```

**Stage specific files:**
```powershell
git add "CSV/project_p_values_canonical.csv"
git add "Relationships/relationship_types_seed.cypher"
```

**Stage all files in a folder:**
```powershell
git add "Neo4j/"
```

**Tip:** Use quotes around paths with spaces.

---

### **3. Verify Staged Changes**

Check what will be committed:

```powershell
git status
```

Files shown with `M` or `A` (added) under "Changes to be committed" are ready to go.

---

### **4. Commit Changes Locally**

Save a snapshot of your staged changes with a descriptive message:

```powershell
git commit -m "Your commit message here"
```

**Good commit messages:**
- `"Add Neo4j schema constraints"`
- `"Update relationship types registry"`
- `"Fix temporal facet documentation"`

**Bad commit messages:**
- `"updates"` (too vague)
- `"stuff"` (not descriptive)

---

### **5. Push to GitHub**

Send your local commits to the remote repository:

```powershell
git push
```

**If this is your first push on a new branch:**
```powershell
git push -u origin master
```

---

## **Using VS Code (Recommended)**

VS Code has built-in Git features that simplify the workflow.

### **After Making a Commit**

VS Code will show a **"Sync Changes"** button in the Source Control panel.

**"Sync Changes" is better than manual `git push` because:**
- ✅ Pulls remote changes first (prevents conflicts)
- ✅ Then pushes your commits
- ✅ Equivalent to: `git pull` + `git push`

**Use "Sync Changes" for daily workflow** — it's the safest option.

### **VS Code Git Workflow**

1. Open Source Control panel (Ctrl+Shift+G)
2. Review changed files
3. Stage files (click `+` next to files, or `+` next to "Changes" to stage all)
4. Enter commit message in text box
5. Click **"Commit"** button
6. Click **"Sync Changes"** button

### **When to Use Manual Commands**

Use manual `git push` only when:
- You're certain no one else has pushed changes
- You're scripting/automating Git operations
- VS Code isn't available

---

## **Common Scenarios**

### **Scenario 1: You edited multiple files and want to push everything**

```powershell
# 1. Check what changed
git status

# 2. Stage all changes
git add -A

# 3. Commit with a message
git commit -m "Update documentation and CSV files"

# 4. Push to GitHub
git push
```

---

### **Scenario 2: You edited one file and want to push only that file**

```powershell
# 1. Check what changed
git status

# 2. Stage only the specific file
git add "md/Architecture/CIDOC-CRM_Alignment_Summary.md"

# 3. Commit with a message
git commit -m "Update CIDOC-CRM alignment summary"

# 4. Push to GitHub
git push
```

---

### **Scenario 3: You added a new folder with files**

```powershell
# 1. Check what changed
git status

# 2. Stage the entire folder
git add "Neo4j/"

# 3. Commit with a message
git commit -m "Add Neo4j schema and implementation roadmap"

# 4. Push to GitHub
git push
```

---

### **Scenario 4: You deleted a file and want to commit the deletion**

```powershell
# 1. Check what changed
git status

# 2. Stage the deletion
git add "Birthday.txt"

# 3. Commit with a message
git commit -m "Remove Birthday.txt"

# 4. Push to GitHub
git push
```

---

## **Handling Unstaged Changes**

If Git says "You have unstaged changes" when trying to push:

**Option 1: Commit them**
```powershell
git add -A
git commit -m "Commit unstaged changes"
git push
```

**Option 2: Stash them (save for later)**
```powershell
git stash
git push
# Restore later with: git stash pop
```

**Option 3: Discard them (WARNING: this deletes changes)**
```powershell
git checkout -- .
git push
```

---

## **Checking Your Push Worked**

After pushing, verify on GitHub:

1. Open: `https://github.com/defarloa1-alt/graph1`
2. Click "Commits" to see your latest commit message
3. Browse files to verify changes appear

---

## **Troubleshooting**

### **Problem: "Push rejected"**

**Cause:** Someone else pushed changes before you.

**Solution:** Pull first, then push:
```powershell
git pull
git push
```

---

### **Problem: "Large files detected"**

**Cause:** File exceeds GitHub's 100 MB limit.

**Solution:** Add to `.gitignore`:
```powershell
# Open .gitignore and add the file path, e.g.:
Python/fast/key/FASTTopical_parsed.csv
```

Then remove from Git:
```powershell
git rm --cached "Python/fast/key/FASTTopical_parsed.csv"
git commit -m "Ignore large data file"
git push
```

---

### **Problem: "Secret detected" (GitHub push protection)**

**Cause:** Git found a password, token, or key in your files.

**Solution:** Remove the secret from history:
```powershell
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch path/to/secret-file.txt" --prune-empty --tag-name-filter cat -- --all
git push --force
```

**Prevention:** Store secrets in:
- `config.py` (already in `.gitignore`)
- `.env` files (already in `.gitignore`)

---

## **Daily Workflow Cheat Sheet**

```powershell
# See what changed
git status

# Stage everything
git add -A

# Commit with message
git commit -m "Brief description of changes"

# Push to GitHub
git push
```

---

## **Additional Resources**

- **Git Status:** Shows current state of working tree
- **Git Log:** View commit history (`git log --oneline`)
- **Git Diff:** See exact changes before staging (`git diff`)
- **Undo Last Commit:** Keep changes but undo commit (`git reset --soft HEAD~1`)

---

## **Notes for This Repository**

- **Large files** are ignored via `.gitignore` (e.g., FAST/LCSH data dumps)
- **Secrets** should never be committed (use `config.py` or `.env`)
- **Line endings:** Windows CRLF warnings are normal and safe to ignore
- **Remote:** `origin` = `https://github.com/defarloa1-alt/graph1`

---

**Last Updated:** February 13, 2026
