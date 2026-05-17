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

## E. Sub-skill Linkage

Identify if this task touched skills beyond the primary one:
1. List all skill IDs that were loaded or referenced during this session.
2. For each secondary skill, append a cross-reference note in `experience/_index.json` under a `"related"` array.
3. If a new skill domain was used that has no existing skill file, create a stub `experience/skill-[new-id].md` and register it via:
   ```
   python scripts/experience_api.py update-index
   ```

---

## F. Keyword Evolution

Review and update the `t[]` trigger word list in `experience/_index.json` for the primary skill:
1. Add any new terms used in this session that weren't in `t[]` before.
2. Remove terms that proved to be noise (matched but were irrelevant).
3. Target: 5–10 high-signal trigger words per skill.

```json
{ "skillId": "example", "t": ["new-term", "existing-term", ...] }
```

Save with:
```
python scripts/experience_api.py update-index
```

---

## G. System Sync

```powershell
# 1. Update index
python scripts/experience_api.py update-index

# 2. Optional: Sync to Vault
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
🔗 Sub-skills touched: <skill-id-1>, <skill-id-2>
⏭️ Next Steps:
   * [ ] <Todo>
═══════════════════════════════════════════════
```
