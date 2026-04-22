---
name: distill-kb
version: 1.0.0-core
description: "Knowledge Distiller: Consolidates task entries into long-term skill files. Decoupled for open-source."
---

# Distill-KB (Core)

## Overview
Distillation is the process of moving "raw task logs" from the **Pending Zone** of a skill file into structured **Permanent Knowledge** (Success/Failure cases).

---

## Workflow

### Step 1: Scan Targets
- Load the experience index from `{vault}/experience/_index.json`.
- Identify skill files with content in the `## 📝 Pending Zone`.

### Step 2: Categorization
Route entries based on their result:
- **Success/Partial Success**: Route to `legacy-{id}.md`.
- **Failure**: Route to `skill-{id}-worst-practice.md`.

### Step 3: Refinement
- Extract core commands, SOPs, and "Pitfalls to Avoid".
- Update the main `skill-{id}.md` with refined best practices.

### Step 4: Indexing
- Update the **Case Index** in the main skill file with pointers to the full legacy records.

---

## Technical Implementation (Python snippet reference)
The system uses the `Config` loader to resolve paths:
```python
from scripts.experience_api import Config
config = Config.load()
experience_base = config.get_path("vault") / "experience"
```

---

## Quality Checklist
- [ ] Refined logic reduces line count of the original entry by >50%.
- [ ] No hardcoded private paths in distilled content.
- [ ] All keywords and metadata updated in `_index.json`.
