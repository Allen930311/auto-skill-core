---
name: auto-skill-core
version: 4.1.0
description: "Cross-agent memory engine. Express Route -> Task -> Query KB on error -> Archive on close."
---

# Auto-Skill v4.1 — Core Engine

## Startup (Once per conversation)

1. Read `auto-skill.config.json` → Resolve all system paths.
2. Read `knowledge-base/user-dna.md` → Load environment, communication preferences, known risks.
3. *(Optional)* Run `python scripts/global_reinforce.py` → Ensure global shielding is active.

---

## Express Route (Priority Execution)

> If the message matches any trigger → load the corresponding experience file and start immediately.

| Trigger Keywords (any match) | Action |
|---|---|
| write diary / today log / daily review / diary | Run `skills/diary` workflow |
| git / push / commit / PR / sync repo | Run github-sync protocol |
| distill / distill kb / organize experience / crystallize | Run `skills/distill-kb` workflow |
| debug / error / bug / check log / why is it | Start immediately — no pre-analysis |
| quant / alpha / brain / factor research | Read `experience/skill-worldquant.md` |
| trading strategy / strategy research / backtest | Read `experience/skill-trading.md` |
| bounty / open source bounty / security bug | Read `experience/skill-bounty.md` |
| scraping / browser automation / playwright | Read `experience/skill-browser-automation.md` |
| scripting / automation / pipeline / batch job | Read `experience/skill-scripting-automation.md` |
| new skill / add skill / write experience / skill creator | Read `experience/skill-skill-mgmt.md` |
| update skill / update repo / look at this repo | Read `experience/skill-skill-mgmt.md` → apply SGAP protocol |
| chemistry / paper / synthesis / literature | Read `experience/skill-chemistry-research.md` |
| video analysis / youtube analysis / channel audit | Read `experience/skill-video-analysis.md` |
| **task done** / finished / completed / mission complete | Read `SKILL_CLOSE.md` → execute A→B→C→D→E→F→F2→H→G |

---

## No Express Route Match → Parallel Load

> Two tracks run simultaneously; results are merged.

### Track A — Experience Index Scan
Extract 3–5 keywords from the message. Match against each skill's `t[]` triggers in `experience/_index.json`:
- Hit → resolve file path → add to load queue
- Multiple hits (>3) → list options for user to choose

### Track B — KB Search
```bash
python scripts/experience_api.py search "<keywords>" -n 3
```
- Hit → add to load queue; also scan `Sub-skills Used` fields → add linked skills
- No hit → proceed without pre-loading; archive as new skill at task close

### Merge & Load
Deduplicate Track A + Track B results → Read all files → Start task.

> **Session cache**: Files already read in this conversation are not re-read (skip on hit).
> **Topic drift**: If 2+ consecutive messages introduce keywords not in any loaded file → re-run parallel load (session cache prevents re-reading old files).

---

## On-Demand Troubleshooting (Do not pre-load)

When encountering an error, **search the KB first**:

```bash
python scripts/experience_api.py search "<error snippet>" --kb -n 3
```

Has result → Read the file, apply the recorded solution.
No result → Diagnose manually; record to `knowledge-base/` after solving.

| Problem Type | File |
|---|---|
| Git / Version Control | `knowledge-base/git-vc.md` |
| Python / Automation | `knowledge-base/python-automation.md` |
| Environment / Config | `knowledge-base/environment.md` |
| Windows / Encoding | `knowledge-base/windows-encoding.md` |
| Platform-specific | `knowledge-base/[platform].md` (create if missing) |

---

## GitHub Research Protocol (SGAP)

> Strict acquisition protocol. Do NOT clone without user authorization.

1. **View**: `gh repo view <owner/repo>` — get README summary.
2. **Report**: Present core features, usefulness, and expected security risks.
3. **Request**: Ask user — "Clone, extract essence only, or cancel?"
4. **Scan**: After user approval, run `security-review` for basic SAST.
5. **Execute**: Based on user choice — download or extract to `global_skills/`.

> **Option B — Knowledge Distillation (no clone)**:
> Use `gh api repos/{owner}/{repo}/contents/{path}` + Python base64 decode to fetch raw content.
> Extract SOPs and patterns into the local experience file. No files written until step 3+ complete.

```python
# Fetch any file without cloning
import subprocess, base64, json

def fetch_github_file(owner, repo, path):
    r = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/contents/{path}"],
        capture_output=True, text=True, encoding="utf-8"
    )
    return base64.b64decode(json.loads(r.stdout)["content"]).decode("utf-8")
```

---

## Windows Safe Writing Rules (Mandatory)

> Violation corrupts files with UTF-16LE BOM, breaking all downstream search and indexing.

**Banned**: `echo >>` / `printf >>` for any `.md` or `.json` file.
**Required**: Python UTF-8 writers or editor Write tools.

```python
# Correct append pattern
with open("file.md", "a", encoding="utf-8") as f:
    f.write(content)

# Correct JSON write pattern
with open("_index.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## Core Operating Principles

### 1. Skill Management
- **Path priority**: All custom skills live in `{vault}/global_skills/{id}/`. Avoid scattering across multiple locations.
- **Registry-first**: Prefer BM25 semantic search and Registry auto-trigger over manual Express Route table edits.
- **Distill vs Clone**: For large external repos, prefer knowledge distillation — extract only the actionable patterns, not the whole codebase.

### 2. Task Execution
- **Fast-Track mode**: When a workflow involves chained multi-file updates, build a Python script first, then expose as a skill.
- **Validation loop**: Any `write` operation must have a corresponding `read` path to verify correctness. Reject write-only operations.
- **Long tasks**: Delay SKILL_CLOSE until the user signals completion. Do not fragment long sessions with premature archiving.

### 3. Knowledge Archiving (SKILL_CLOSE)
- **Always execute**: On task close, SKILL_CLOSE is non-negotiable. Every session must produce an experience entry or a KB entry.
- **Record failures**: Include "Failed Attempts" and "Iteration Path" fields in entries. Failures are first-class citizens in this system.

---

## Storage Paths

| Type | Path |
|---|---|
| Best Practices (HOW TO) | `experience/skill-[id].md` |
| Historical Cases (archive) | `experience/legacy/legacy-[id].md` |
| Failure / Pitfall Map | `experience/skill-[id]-worst-practice.md` |
| Error Database (searchable) | `knowledge-base/[category].md` |
| Task-close archiving | Handled by `SKILL_CLOSE.md` |
| Old backups | `SKILL_v*.md` (do not load) |
