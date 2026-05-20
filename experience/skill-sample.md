---
name: sample
type: skill-experience
tags: [git, python, sample, template]
last_updated: 2026-05-20
last_distilled: (not yet)
count: 2
hit_count: 0
---

# Sample Skill — Core Essence

> This file is a **template reference**. Replace "sample" with your skill domain.
> Each entry in the Pending Zone must be directly reusable by a future AI agent.

## 📖 Core Scenarios

1. **Git branch cleanup**: Remove merged local branches after a feature ships.
2. **Python environment refresh**: Rebuild venv cleanly when dependencies conflict.

---

## 🛠️ Best Practice Commands

### Git Branch Cleanup
```bash
# Delete all local branches already merged into main
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d
```

### Python Environment Rebuild (Windows)
```bash
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install --no-cache-dir -r requirements.txt
```

---

## 🚨 Key Pitfalls

| Problem | Root Cause | Fix |
|---------|-----------|-----|
| `echo >> file.md` corrupts content on Windows | Outputs UTF-16LE BOM | Use `python open(f, "a", encoding="utf-8")` |
| `pip install` uses stale cache | Old wheels cached | Add `--no-cache-dir` flag |

---

## 📚 Case Index
<!-- Maintained by distillation process — do not edit manually -->

---

## 📝 Pending Distillation

## 🔧 Git Branch Cleanup After Feature Merge [SAMPLE — FULLY FILLED ENTRY]
**Date:** 2026-04-22
**Case:** Clean up 8 stale local branches after a sprint merged to main
**Skill:** sample
**Context:** After merging 3 PRs, local repo had 8 branches — `git branch` output was cluttered and slowed tab-completion. Needed a safe one-liner that would not touch unmerged branches.
**Failed Attempts:**
- ❌ `git branch -d $(git branch)` → Includes `*` (current branch) in the list; errors out and deletes nothing.
**Iteration Path:** Manual deletion → scripted via `--merged` filter → ✅ one-liner below
**Solution:**
```bash
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d
```
Run from `main`. Safe: only deletes branches already merged into the current branch.
**Source Reference:** `git-scm.com/docs/git-branch` — `--merged` flag documentation
**Validation:** After running, `git branch --merged` returns only the current branch (`* main`).
**Anti-pattern:** ❌ Do not use `git branch -D` (force-delete) — bypasses merge check, can delete unmerged work.
**Key Turning Point:** `grep -v "\*"` is required to exclude the current branch from the xargs pipe.
**Result:** First Success
**Sub-skills Used:** (none)
**keywords:** git, cleanup, branch-management, merged

## 🔧 Python Venv Rebuild After Dependency Conflict [SAMPLE — ITERATION ENTRY]
**Date:** 2026-04-22
**Case:** Conflicting numpy/pandas versions caused ImportError after bumping requirements.txt
**Skill:** sample
**Context:** CI pipeline upgrade bumped pandas to 2.x. Local venv still had pandas 1.x cached, causing `ImportError: cannot import name DataFrame`. Clean rebuild was faster than resolving pin conflicts.
**Failed Attempts:**
- ❌ `pip install -r requirements.txt` without clearing cache → installs stale wheel, error persists
- ❌ `pip install --no-cache-dir -r requirements.txt` without deleting venv → old incompatible packages remain
**Iteration Path:** plain pip install (failed) → `--no-cache-dir` (failed) → ✅ delete venv + `--no-cache-dir`
**Solution:**
```bash
# Windows
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate
pip install --no-cache-dir -r requirements.txt
```
**Source Reference:** Self-derived
**Validation:** `python -c "import pandas; print(pandas.__version__)"` returns `2.x` without error.
**Anti-pattern:** ❌ `pip install --upgrade` alone does not fix conflicts when the venv contains incompatible cached wheels.
**Key Turning Point:** Root cause was the stale `.venv` directory, not pip's download cache — deleting the whole env was necessary.
**Result:** Iteration (2 times)
**Sub-skills Used:** (none)
**keywords:** python, pip, venv, dependency-conflict, rebuild
