# Auto-Skill · Task Debrief (SKILL_CLOSE)

> **Trigger**: Triggered when the user says "Task Completed" or "Mission Finished".
> **Purpose**: Atomic archiving of lessons learned. Do not skip.

---

## Execution Flow

```
A Summary → B Experience Archive → C Pitfall & Reflection Archive
→ E Sub-skill Linkage → F Keyword Evolution → F2 Failure Snapshot
→ H Summary Card → G System Sync
```

> **Only lightweight steps run every time** (A / B / C / E / H + the cheap index sync).
> Heavy operations — rewriting the trigger index, rebuilding search vectors, vault mirroring —
> are **deferred until a threshold is reached**. See *Accumulation Counter* before section F.
> This keeps a routine debrief cheap: appending one entry should cost a file write, not a full re-index.

---

## Where does knowledge go?

| Content Type | Destination | Notes |
|---|---|---|
| Complete Task Case (Success/Failure) | `experience/skill-[id].md` Pending Zone | Distilled later into legacy/ or worst-practice |
| Technical Pitfalls / API Errors | `knowledge-base/[category].md` | Searchable immediately |
| Actionable Rules | `knowledge-base/[category].md` | Must be a rule, not a thought |
| Environment Preferences | `knowledge-base/user-dna.md` | Keep technical pitfalls out of here |

> **Do NOT archive**: one-off Q&A, pure concept explanations, non-reusable conclusions.

### Project-level routing (takes precedence over the table above)

Before section B, check `experienceRouting[<skill-id>]` in `auto-skill.config.json`.
If it exists and `mode = "project-ledger"`:

1. Full cases go **only** to `caseLedger` — never to the global `experience/skill-{id}.md`.
2. Every case needs a unique `case_id: YYYY-MM-DD-<slug>`. Search for it before appending;
   if it exists, add a correction entry (`<original-case-id>-correction-N`) rather than writing twice.
3. `legacyArchive` is read-only.
4. The global file is a map, not a ledger — update it only when the entry point, paths,
   or governance rules change.

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

## C. Pitfall & Reflection Archive → `knowledge-base/[category].md` (if any)

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

### C2. Non-pitfall rules (same step — no separate pass)

After archiving pitfalls, if the session also produced **non-pitfall** actionable rules,
route them by nature — not feelings, rules:

- General technical rules → append `knowledge-base/[category].md`
- Project preferences → append `experience/skill-[id].md` refined zone
  (project-ledger routing: write to the project's own docs or governance file instead)
- Personal work habits → append `knowledge-base/user-dna.md`

> ✅ Good: "Always specify `encoding='utf-8'` in Python `open()` to prevent Win32 mojibake."
> ❌ Bad: "Remember to watch out for encoding."

> **Why this is one step and not two:** extracting "actionable rules" and archiving
> "technical pitfalls" have the same shape and the same destinations. Splitting them into
> separate passes produced duplicate entries phrased two different ways.

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

## Accumulation Counter (runs every time — gates F and G)

Count the pending entries `N` in the ledger you just wrote to:

```bash
python -c "import sys;sys.stdout.reconfigure(encoding='utf-8');print(open('experience/skill-<id>.md',encoding='utf-8').read().count('## 🔧'))"
# project-ledger routing: count the project's case-ledger.md instead
```

| Result | Effect |
|---|---|
| `N < 5` | F and G run in **lightweight mode** only. Skip index rewrites and vector rebuilds. |
| `N ≥ 5` | Run F and G **in full**, and surface a distillation reminder in the summary card. |

The entry is already on disk either way — deferring only delays *searchability*, never durability.
If the user says they need it searchable right now, run the full sync regardless of `N`.

### Graduation check: should this skill move to project-ledger?

When `N ≥ 5`, also check whether the skill has outgrown a single global experience file.
A skill should **graduate to project-ledger** when it meets **both**:

1. **It has its own project root** — real code, data, or a repo of its own; not just one `.md` file.
2. **It generates cases continuously** — there's a loop; each run produces a new record.
   A one-off task never graduates.

If both hold, add a hint to the summary card. **Suggest only — never migrate automatically**,
since this relocates the user's files.

**What project-ledger means:** the global `experience/skill-{id}.md` stops holding cases and becomes
a *map* (a `globalInterface`) — an entry point, a table of where each kind of knowledge lives inside
the project, and a source-of-truth ordering. Full cases live in the project's own append-only
`case-ledger.md`. The global file stays small and stops growing; the project owns its own history.

**Migration order** (do not reorder — step 1 is what makes the rest reversible):

1. Create a lossless archive of the current global file and verify it byte-for-byte (SHA-256).
2. Move full cases into `<project>/references/case-ledger.md`.
3. Rewrite the global file as a map: entry point, "where knowledge lives" table, source-of-truth order.
4. Register the route under `experienceRouting` in `auto-skill.config.json`.

```json
"experienceRouting": {
  "<skill-id>": {
    "mode": "project-ledger",
    "caseLedger":   "<project>/references/case-ledger.md",
    "governance":   "<project>/references/experience-governance.md",
    "legacyArchive":"<project>/references/legacy-experience-full.md",
    "globalInterface": "{auto_skill}/experience/skill-<skill-id>.md",
    "writeFullCaseToGlobal": false,
    "globalInterfaceBaselineSha256": "<hash of the rewritten global file>"
  }
}
```

Once registered, section B writes full cases **only** to `caseLedger` — never back to the global file.
The `baselineSha256` lets a validator detect the global map being silently overwritten.

Skills with no project root of their own (a generic API wrapper, a formatting helper) should **stay
global** — there is nowhere meaningful to move them, and centralizing them is the point.

---

## F. Keyword Evolution (success tasks only — skip if Failed)

**Lightweight mode (`N < 5`)** — append candidates to a queue; do **not** open the trigger index:

```markdown
<!-- TRIGGER date={YYYY-MM-DD} skill={skill-id} -->
- {candidate term 1}, {candidate term 2}
```

Write to `{auto_skill}/.trigger_queue.md`. The index is the most-read file in the system;
a read-modify-write per task is the single most wasteful thing a debrief can do.

**Full mode (`N ≥ 5`)** — process this task's terms plus everything queued:

1. Extract 2–4 terms from the task summary (the words you actually used), plus queued candidates.
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

5. Clear `.trigger_queue.md` after a successful write so candidates aren't reprocessed.

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
🧵 Backlog: <ledger> N/5 pending
⏭️ Next Steps:
   * [ ] <Todo 1>
═══════════════════════════════════════════════
```

**Backlog line — append a hint based on the Accumulation Counter:**

| Condition | Append to the `🧵` line |
|---|---|
| `N < 5` | nothing (just show `N/5`) |
| `N ≥ 5` | `→ time to distill` |
| `N ≥ 5` and both graduation criteria met | add a line: `🏗️ Consider project-ledger: <skill-id> has its own project root and keeps producing cases` |

This is the system telling you when to prune it — without it, ledgers grow until a load becomes
expensive and nobody notices why.

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

## G. System Sync (if B or C had any writes)

### G1. Lightweight — run every time (cheap, and it catches breakage early)

```bash
# Rebuild index (count+1, last_updated); also finds new files and repairs stale paths
python scripts/experience_api.py update-index
```

Under project-ledger routing, skip the global count bump — the case lives in the project ledger,
not in the global index.

### G2. Heavy — **only when `N ≥ 5`**

```bash
# Rebuild search vectors — a full rebuild, slow once the corpus is large
# qmd embed

# Sync to vault mirror
python scripts/bridge_sync.py push
```

> Skipping G2 does not risk data: entries are already written to disk. They are simply not yet
> in the vector index, and get picked up on the next threshold run.
