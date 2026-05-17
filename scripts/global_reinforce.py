#!/usr/bin/env python3
"""
Auto-Skill Global Reinforce
Injects the auto-skill startup protocol into supported IDE config files.

Usage:
  python global_reinforce.py                  # interactive confirmation per file
  python global_reinforce.py --yes            # skip confirmation (CI / trusted env)
  python global_reinforce.py --dry-run        # show what would change, write nothing
"""

import argparse
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

PROTOCOL_MARKER = "## 任務啟動協議 (強制)"
PROTOCOL_CONTENT = f"""
{PROTOCOL_MARKER}

* 當開啟新任務或觸發任何技能時，必須先讀取並執行 auto-skill 技能的 SKILL.md。
"""

TARGET_FILES = {
    "Antigravity": "~/.gemini/GEMINI.md",
    "Cursor":      "~/.cursor/rules/global.mdc",
    "Claude Code": "~/.claude/CLAUDE.md",
    "Codex":       "~/.codex/instructions.md",
}


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".bak_{ts}{path.suffix}")
    shutil.copy2(path, backup_path)
    print(f"    💾 Backed up → {backup_path.name}")


def confirm(prompt: str) -> bool:
    try:
        answer = input(f"    {prompt} [y/N] ").strip().lower()
        return answer in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def reinforce(dry_run: bool = False, yes: bool = False):
    if dry_run:
        print("🔍 [DRY RUN] Scanning for IDE config files — nothing will be written.\n")
    else:
        print("🔍 Scanning for IDE config files...\n")

    home = Path(os.path.expanduser("~"))
    updated, skipped = [], []

    for ide, rel_path in TARGET_FILES.items():
        full_path = home / rel_path.replace("~/", "")

        if not full_path.parent.exists():
            print(f"  ▸ {ide}: parent dir not found ({full_path.parent}), skipping.")
            continue

        print(f"  ▸ {ide}: {full_path}")

        content = full_path.read_text(encoding="utf-8") if full_path.exists() else ""

        if PROTOCOL_MARKER in content:
            print(f"    ✅ Protocol already present — skipping.")
            skipped.append(ide)
            continue

        separator = "\n\n---\n" if content.strip() else ""
        new_content = content.rstrip() + separator + PROTOCOL_CONTENT

        print(f"    ⚠️  Protocol missing. Will append {len(PROTOCOL_CONTENT)} chars.")

        if dry_run:
            print(f"    [dry-run] would write to: {full_path}")
            updated.append(ide)
            continue

        if not yes:
            if not confirm(f"Modify {full_path}?"):
                print(f"    Skipped by user.")
                skipped.append(ide)
                continue

        if full_path.exists():
            backup(full_path)

        try:
            full_path.write_text(new_content, encoding="utf-8")
            print(f"    ✅ Written.")
            updated.append(ide)
        except Exception as e:
            print(f"    ❌ Write failed: {e}")

    print()
    if updated:
        action = "would update" if dry_run else "updated"
        print(f"✨ {action.capitalize()}: {', '.join(updated)}")
    if skipped:
        print(f"   Skipped      : {', '.join(skipped)}")
    if not updated and not skipped:
        print("✅ All IDE environments already comply with the protocol.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inject auto-skill protocol into IDE config files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing anything")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompts (for CI / trusted environments)")
    args = parser.parse_args()
    reinforce(dry_run=args.dry_run, yes=args.yes)
