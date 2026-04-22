# Auto-Skill · Task Debrief (SKILL_CLOSE)

> **Trigger**: Triggered when the user says "Task Completed" or "Mission Finished".
> **Purpose**: Atomic archiving of lessons learned. Do not skip.

---

## Execution Flow

```
A Summary → B Experience Archive → C Pitfall Archive → D Reflection
→ E Sub-skill Linkage → F Keyword Evolution → G System Sync → H Summary Card
```

---

## Where does knowledge go?

| Content Type | Destination | Notes |
|---|---|---|
| Complete Task Case (Success/Failure) | `experience/skill-[id].md` (Pending Area) | Will be distilled later |
| Technical Pitfalls / API Errors | `knowledge-base/[category].md` | Searchable immediately |
| Actionable Rules | `knowledge-base/[category].md` | Must be a rule, not a thought |
| Environment Preferences | `knowledge-base/user-dna.md` | Keep technical pitfalls out of here |

---

## A. Task Summary

- One liner: "What was done → Result"
- Result Score: `First Success` / `Iteration (N times)` / `Partial Success` / `Failed`

---

## B. Experience Archive → `experience/skill-[id].md`

1. Find the skill file in `experience/_index.json`.
2. Append the entry to the `## 📝 Pending Distillation` section.
3. **Template**:
```markdown
## 🔧 {Title}
**Date:** YYYY-MM-DD
**Case:** {One-sentence name}
**Context:** {Detailed scenario}
**Solution:** {Full command/logic for reuse}
**Result:** {Score}
**keywords:** {tags}
```

---

## C. Pitfall Archive → `knowledge-base/[category].md`

Archive technical pitfalls immediately to ensure they are searchable next time.

| Category | File |
|---|---|
| Git / Version Control | `git-vc.md` |
| Python / Automation | `python-automation.md` |
| Environment / Config | `environment.md` |
| (Platform Specific) | `[platform].md` |

---

## D. Reflection (Distill actionable rules)

- Convert "lessons" into "rules".
- Good: "Always specify `encoding='utf-8'` in Python `open()` to avoid Win32 mojibake."
- Bad: "Remember encoding issues."

---

## G. System Sync

```powershell
# 1. Update index
python scripts/experience_api.py update-index

# 2. Rebuild search vectors (if using QMD)
qmd embed

# 3. Optional: Sync to Vault
python scripts/bridge_sync.py push
```

---

## H. Summary Card

Print a high-density summary card to the conversation.

```
═══════════════════════════════════════════════
📋 Task Summary | YYYY-MM-DD HH:mm
───────────────────────────────────────────────
🎯 Mission: <Type> — <Summary>
✅ Result: <Score>
🔧 Key Solution: <Main takeaway>
📌 Pitfalls: <If any>
⏭️ Next Steps:
   * [ ] <Todo>
═══════════════════════════════════════════════
```
