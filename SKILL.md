---
name: auto-skill-core
version: 4.0.0
description: "Core engine for Auto-Skill framework. Express Route → Task → Distillation."
---

# Auto-Skill v4.0 Core Engine

## Startup (Once per conversation)
1. Read `auto-skill.config.json` → Resolve system paths.
2. Run `python scripts/global_reinforce.py` → Ensure global shielding is active.
3. Read `knowledge-base/user-dna.md` → Load environmental preferences and pitfalls.

---

## Express Route (Priority Execution)

| Trigger Keywords | Action / File to Load |
|---|---|
| write diary / today log / diary | Run `diary` skill workflow |
| git sync / push / sync repo | Run `github-sync` protocol |
| distill / distill kb / organize experience | Run `distill-kb` skill |
| **task completed** / finished | Read `SKILL_CLOSE.md` |

---

## If No Express Route Match

### Parallel Search & Load
- **A | Skill Registry Scan**: Search `_index.json` using mission keywords.
- **B | Experience Search**: `python scripts/experience_api.py search <keywords>`

### Merge & Load
Combine results from A and B → Dedup → Read all matching files → Start task.

---

## Troubleshooting (On Demand)
When facing errors, search the knowledge base:
```powershell
python scripts/experience_api.py search <error_snippet> --kb
```

---

## Storage Layer

| Type | Directory Path |
|---|---|
| Best Practices (HOW TO) | `experience/skill-[id].md` |
| Historical Cases (Legacy) | `experience/legacy/legacy-[id].md` |
| Pitfall Database (Error Docs) | `knowledge-base/[category].md` |
| Task Completion Arhive | Handled by `SKILL_CLOSE.md` |

---

## Safe Writing Rules (Windows Compliance)
Never use `echo >>` for `.md` files to avoid encoding corruption.
Strictly use Python's UTF-8 writers or the editor's Write tools.
