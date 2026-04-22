---
name: diary
description: "Unified Diary System (Core Edition). Aggregates task cards into daily logs. Decoupled from private paths."
---

# 📔 Unified Diary System (Core)

**Trigger Keywords**: `write diary`, `daily review`, `log progress`

---

## Architecture
- **Queue Location**: `{auto_skill}/.diary_queue.md` (Temporary storage for task cards)
- **Global Diary Location**: `{vault}/10_Daily/YYYY-MM-DD.md`

---

## Execution Workflow

### Step 0: Material Aggregation
- Read the queue file `{auto_skill}/.diary_queue.md`.
- Group cards by `project`.
- Inherit unfinished todos from `YESTERDAY.md`.

### Step 1: Read & Conflict Check
- Check for sync conflicts in the `{vault}/10_Daily` directory.
- Use the standard naming convention: `YYYY-MM-DD.md`.

### Step 2: AI Fusion
- Combine all progress from today's cards.
- Deduplicate "Lessons Learned" and "Action Items".
- Generate a single "Daily Highlight".

### Step 3: Dual-Write (Optional)
- **Global Diary**: Always written to `{vault}/10_Daily/`.
- **Local Project Diary**: (Disabled by default) Only written if requested explicitly.

### Step 4: Cleanup
- Remove today's cards from the queue.
- Clear session buffers.

---

## Safe Writing Rules
- Use UTF-8 encoding.
- Never overwrite existing content; always read-modify-write or append.
