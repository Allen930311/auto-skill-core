# Auto-Skill · Task Debrief (SKILL_CLOSE)

> **Trigger**: Triggered when the user says "Task Completed" or "Mission Finished".
> **Purpose**: Atomic archiving of lessons learned. Do not skip.

---

## Execution Flow

```
A Summary → B Experience Archive → C Pitfall Archive → D Reflection
→ E Sub-skill Linkage → F Keyword Evolution → F2 Failure Snapshot
→ H Summary Card → G System Sync
```

---

## Where does knowledge go?

| Content Type | Destination | Notes |
|---|---|---|
| Complete Task Case (Success/Failure) | `experience/skill-[id].md` Pending Zone | Distilled later into legacy/ or worst-practice |
| Technical Pitfalls / API Errors | `knowledge-base/[category].md` | Searchable immediately |
| Actionable Rules | `knowledge-base/[category].md` | Must be a rule, not a thought |
| Environment Preferences | `knowledge-base/user-dna.md` | Keep technical pitfalls out of here |

> **Do NOT archive**: one-off Q&A, pure concept explanations, non-reusable conclusions.

---

## A. Task Summary

- One liner: "What was done → Result"
- Result Score (drives routing in B, F, F2):

| Score | Meaning |
|---|---|
| `First Success` | Correct on first attempt |
| `Iteration (N times)` | Required N attempts, eventually succeeded |
| `Partial Success` | Some goals met |
| `Failed` | Goal not reached |

---

## B. Experience Archive → `experience/skill-[id].md` Pending Zone

1. Find the skill file via `experience/_index.json` by `skillId`.
2. If new skill, create file with the template below and register it.
3. **Append only** — never modify or delete existing entries unless running a formal distillation.

**New skill file template:**
```markdown
---
name: {id}
type: skill-experience
tags: []
last_updated: YYYY-MM-DD
last_distilled: (not yet)
---

# {Id} Core Essence

## 📖 Core Scenarios

## 🛠️ Best Practice Commands

## 🚨 Key Pitfalls

## 📚 Case Index
<!-- Maintained by distillation process — do not edit manually -->

---

## 📝 Pending Distillation
```

**Entry template:**
```markdown
## 🔧 {Title}
**Date:** YYYY-MM-DD
**Case:** {One-sentence case name — becomes the index pointer after distillation}
**Skill:** {primary-skill-id}
**Context:** {Specific scenario description}
**Failed Attempts:** (optional; required if score is Iteration or Failed)
- ❌ {Attempt A} → Reason failed: {reason}
**Iteration Path:** (optional; required if ≥2 attempts)
{Attempt A} → {Attempt B} → ✅ {Final solution}
**Solution:** {Full commands/logic for direct reuse}
**Source Reference:** {Files/docs actually consulted — do not leave blank; use "Self-derived" if none}
**Validation:** {How to confirm the solution works — specific command or observable output}
**Anti-pattern:** {Why this wrong path fails, to prevent re-trial — "None" if not applicable}
**Key Turning Point:** {The insight that broke the deadlock}
**Result:** {First Success / Iteration (N times) / Partial Success / Failed}
**Sub-skills Used:** {skill-id} → {role} → {key params}
**keywords:** {tag1, tag2, tag3}
```

> **Result drives distillation routing:**
> - `First Success / Iteration / Partial` → distilled into `experience/legacy/legacy-{id}.md`
> - `Failed` → distilled into `experience/skill-{id}-worst-practice.md`

**Exceptions — write directly to refined zone (skip Pending):**
- A pitfall that has appeared **3+ times** → write directly to `## 🚨 Key Pitfalls`
- A validated SOP → write directly to `## 🛠️ Best Practice Commands`

---

## C. Pitfall Archive → `knowledge-base/[category].md` (if any)

Archive technical pitfalls immediately — do not wait for distillation.

| Problem Type | File |
|---|---|
| Git / Version Control | `git-vc.md` |
| Python / Automation | `python-automation.md` |
| Environment / Config | `environment.md` |
| Platform-specific | `[platform].md` (create if missing) |

**Entry template:**
```markdown
## ⚠️ {Title — describe the symptom} [Occurrence #N]
**Date:** YYYY-MM-DD
**Context:** {Reproducible specific scenario}
**Error:** {Full error message or behavior}
**Diagnosis:** {What was tried, why it didn't work}
**Solution:** {Final fix with full commands}
**Prevention:** {One-sentence rule to avoid this next time}
**keywords:** {tag1, tag2, tag3}
```

**Pitfall counter:** Add `[Occurrence #N]` to the title where N = total times this issue appeared.

---

## D. Reflection (if B or C has entries)

Extract **actionable rules** from this session — not feelings:

- General technical rules → append `knowledge-base/[category].md`
- Project preferences → append `experience/skill-[id].md` refined zone
- Personal work habits → append `knowledge-base/user-dna.md`

> ✅ Good: "Always specify `encoding='utf-8'` in Python `open()` to prevent Win32 mojibake."
> ❌ Bad: "Remember to watch out for encoding."

---

## E. Sub-skill Linkage (if sub-skills were used)

If the `Sub-skills Used` field in the entry lists any secondary skills:
1. Find the secondary skill's file via `_index.json`.
2. Append a cross-reference entry to its Pending Zone.
3. Entry title format: `## 🔧 {Sub-task Title} (from: {Main task name})`
4. Focus content on: tuning details for that sub-skill in this specific scenario.
5. If a new skill domain was touched with no existing file, create a stub and register:
   ```
   python scripts/experience_api.py update-index
   ```

---

## F. Keyword Evolution (success tasks only — skip if Failed)

1. Extract 2–4 terms from the task summary (the words you actually used).
2. Compare against the skill's `t[]` in `experience/_index.json`.
3. For uncovered terms, propose:

```
🧬 Trigger word evolution suggestion:
  {skill-id}: suggest adding "{new term}"
Add? [y / n / select]
```

4. On confirm, write with Python (never `echo >>`):
```python
with open(index_path, encoding='utf-8') as f: data = json.load(f)
# find skill → data['skills'][i]['t'].append(new_term)
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

> ⚠️ **Windows encoding rule**: always `encoding='utf-8'` for all JSON/MD read-write.
> Never use `echo >>` for any `.md` file — it produces UTF-16LE corruption.

---

## F2. Failure Snapshot (only if: Failed or Iteration ≥3 times)

Append a compact lesson directly to knowledge-base for immediate searchability.

```bash
python scripts/experience_api.py snapshot \
  --skill-id <id> \
  --lesson "<lesson in ≤80 chars>" \
  --task-type <type>
```

This writes a `## 💥 Snapshot` entry to the most relevant KB category so the failure
is findable even before formal distillation runs.

---

## H. Summary Card

**H1. Print to conversation:**
```
═══════════════════════════════════════════════
📋 Task Summary | YYYY-MM-DD HH:mm
───────────────────────────────────────────────
🎯 Mission: <Type> — <One-line summary>
✅ Result: <Score>
🔧 Key Solution: <Most important takeaway>
📌 Pitfalls: <If any; omit if none>
💡 Reflection: <What to do differently next time; omit if none>
🧠 New Knowledge: <Which KB category, or "None">
🔗 Sub-skills: <skill-id-1>, <skill-id-2>
⏭️ Next Steps:
   * [ ] <Todo 1>
═══════════════════════════════════════════════
```

**H2. Append to diary queue** (`{auto_skill}/.diary_queue.md`):
```markdown
<!-- DIARY_CARD date={YYYY-MM-DD} time={HH:mm} project={project} task_type={type} -->
**{HH:mm} [{type}] {One-line summary}**
- Result: {Score}
- Key Solution: {solution}
- Learning: {KB category or "None"}
- Next Steps:
  * [ ] {todo}
<!-- END_CARD -->
```

> Use Python `open(path, 'a', encoding='utf-8')` to write — never `echo >>`.
> The diary skill processes the queue when you say "write diary". No need to trigger it per task.

---

## G. System Sync (if B, C, or D had any writes)

```bash
# 1. Rebuild index (count+1, last_updated)
python scripts/experience_api.py update-index

# 2. Rebuild search vectors (if using qmd)
# qmd embed

# 3. Sync to vault mirror
python scripts/bridge_sync.py push
```
