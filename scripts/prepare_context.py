#!/usr/bin/env python3
"""
Auto-Skill Context Preparer
Usage: python prepare_context.py [directory_path]

Generates AGENT_CONTEXT.md — a high-density snapshot that gives an AI agent
instant situational awareness when starting a session.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR  = Path(__file__).parent.parent
EXP_DIR   = BASE_DIR / "experience"
KB_DIR    = BASE_DIR / "knowledge-base"
EXP_INDEX = EXP_DIR / "_index.json"


# ── Tree ─────────────────────────────────────────────────────────────────────

SKIP = {".", "node_modules", "__pycache__", "dist", "build", "venv", ".git", ".venv"}

def get_tree(path, prefix="", max_depth=3, depth=0):
    if depth >= max_depth:
        return []
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return []
    filtered = [e for e in entries if e not in SKIP and not e.startswith(".")]
    lines = []
    for i, entry in enumerate(filtered):
        is_last = i == len(filtered) - 1
        connector = "└── " if is_last else "├── "
        full = os.path.join(path, entry)
        lines.append(f"{prefix}{connector}{entry}")
        if os.path.isdir(full):
            ext = "    " if is_last else "│   "
            lines.extend(get_tree(full, prefix + ext, max_depth, depth + 1))
    return lines


# ── Skill Summary ────────────────────────────────────────────────────────────

def get_skill_summary():
    if not EXP_INDEX.exists():
        return []
    with open(EXP_INDEX, "r", encoding="utf-8") as f:
        index = json.load(f)
    rows = []
    for skill in index.get("skills", []):
        triggers = ", ".join(skill.get("t", skill.get("keywords", [])))
        rows.append(
            f"- **{skill['skillId']}** ({skill.get('count', 0)} entries)"
            + (f" — triggers: `{triggers}`" if triggers else "")
        )
    return rows


# ── Diary TODOs ──────────────────────────────────────────────────────────────

def get_diary_todos(root: Path):
    """Find the most recent diary file under root/diary/ and extract pending TODOs."""
    diary_dir = root / "diary"
    if not diary_dir.exists():
        return None, []

    latest_file, latest_date = None, ""
    for md in diary_dir.rglob("*.md"):
        name = md.stem
        if len(name) >= 10 and name[:4].isdigit():
            date_str = name[:10]
            if date_str > latest_date:
                latest_date, latest_file = date_str, md

    if not latest_file:
        return None, []

    try:
        text = latest_file.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return latest_date, []

    todos = []
    in_section = False
    for line in text.split("\n"):
        stripped = line.strip()
        if any(kw in stripped.lower() for kw in ["next step", "下一步", "待辦", "todo"]):
            in_section = True
            continue
        if in_section:
            if stripped.startswith(("- [", "* [")):
                todos.append(stripped)
            elif stripped.startswith("#"):
                break
    return latest_date, todos


# ── KB Summary ───────────────────────────────────────────────────────────────

def get_kb_summary():
    kb_index = KB_DIR / "_index.json"
    if not kb_index.exists():
        return []
    with open(kb_index, "r", encoding="utf-8") as f:
        index = json.load(f)
    return [
        f"- **{cat['id']}**: {cat.get('name', cat['id'])} ({cat.get('count', 0)} entries)"
        for cat in index.get("categories", [])
    ]


# ── Main ──────────────────────────────────────────────────────────────────────

def prepare_context(root_path: str):
    root = Path(root_path).resolve()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    output_path = root / "AGENT_CONTEXT.md"

    tree_lines = get_tree(str(root))
    skill_lines = get_skill_summary()
    kb_lines = get_kb_summary()
    diary_date, todos = get_diary_todos(root)

    sections = [
        f"# Agent Context Snapshot",
        f"_Generated: {now}_",
        "",
        "---",
        "",
        "## Project Structure",
        "```",
        *tree_lines,
        "```",
        "",
    ]

    if skill_lines:
        sections += [
            "## Loaded Skills",
            *skill_lines,
            "",
        ]

    if kb_lines:
        sections += [
            "## Knowledge Base Categories",
            *kb_lines,
            "",
        ]

    if todos:
        sections += [
            f"## Pending TODOs (from diary {diary_date})",
            *todos,
            "",
        ]
    elif diary_date:
        sections += [
            f"## Pending TODOs (from diary {diary_date})",
            "_No pending items found._",
            "",
        ]

    sections += [
        "---",
        "_This file is auto-generated. Do not edit manually._",
    ]

    content = "\n".join(sections)
    output_path.write_text(content, encoding="utf-8")
    print(f"✅ Context written to: {output_path}")
    print(f"   Skills indexed : {len(skill_lines)}")
    print(f"   KB categories  : {len(kb_lines)}")
    print(f"   Pending TODOs  : {len(todos)}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    prepare_context(target)
