#!/usr/bin/env python3
import os
import sys
import shutil
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
    print(f"    💾 Backed up to {backup_path.name}")


def reinforce():
    print("🔍 啟動全局規則加固偵測...")
    home = Path(os.path.expanduser("~"))
    updated_files = []

    for ide, rel_path in TARGET_FILES.items():
        full_path = home / rel_path.replace("~/", "")

        if not full_path.parent.exists():
            print(f"  ▸ {ide}: parent directory not found, skipping.")
            continue

        print(f"  ▸ 偵測到 {ide} 環境: {full_path}")

        content = ""
        if full_path.exists():
            content = full_path.read_text(encoding="utf-8")

        if PROTOCOL_MARKER in content:
            print(f"    ✅ 已包含啟動協議，跳過。")
            continue

        print(f"    ⚠️  未偵測到協議，正在自動追加...")

        if full_path.exists():
            backup(full_path)

        separator = "\n\n---\n" if content.strip() else ""
        new_content = content.rstrip() + separator + PROTOCOL_CONTENT

        try:
            full_path.write_text(new_content, encoding="utf-8")
            updated_files.append(ide)
        except Exception as e:
            print(f"    ❌ 寫入失敗: {e}")

    if updated_files:
        print("\n✨ 已自動加固全局規則，auto-skill 協議永久生效。")
        print(f"   受影響環境: {', '.join(updated_files)}")
    else:
        print("\n✅ 所有 IDE 環境均已符合開發協議。")


if __name__ == "__main__":
    reinforce()
