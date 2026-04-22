#!/usr/bin/env python3
"""
AI Agent Context Preparer v2 (Core Engine)
Usage: python prepare_context.py [directory_path]
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# 強制 Windows 終端機使用 UTF-8 輸出
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_tree(path, prefix="", max_depth=3, current_depth=0):
    if current_depth >= max_depth:
        return []
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        return []
    tree_lines = []
    skip_prefixes = (".", "node_modules", "__pycache__", "dist", "build", "venv", ".git")
    filtered = [e for e in entries if not e.startswith(skip_prefixes)]
    for i, entry in enumerate(filtered):
        is_last = i == len(filtered) - 1
        connector = "└── " if is_last else "├── "
        full_path = os.path.join(path, entry)
        tree_lines.append(f"{prefix}{connector}{entry}")
        if os.path.isdir(full_path):
            extension = "    " if is_last else "│   "
            tree_lines.extend(get_tree(full_path, prefix + extension, max_depth, current_depth + 1))
    return tree_lines

def extract_latest_diary_todos(root):
    """偵測日記區域並提取 TODO。路徑應由環境或配置定義。"""
    # 這裡的邏輯可以配合 auto-skill-core 的配置進行擴充
    diary_dirs = [root / "diary"]
    
    # 如果有全域路徑設定，可以從這裡加入
    # 預防性檢查：避免 hardcode 使用者的特定路徑
    
    latest_file = None
    latest_date = ""

    for diary_dir in diary_dirs:
        if not diary_dir.exists():
            continue
        for md_file in diary_dir.rglob("*.md"):
            name = md_file.stem
            if len(name) >= 10 and name[:4].isdigit():
                date_str = name[:10]
                if date_str > latest_date:
                    latest_date = date_str
                    latest_file = md_file

    if not latest_file:
        return None, []

    try:
        text = latest_file.read_text(encoding="utf-8", errors="ignore")
        lines = text.split("\n")
        todos = []
        in_next_section = False
        for line in lines:
            stripped = line.strip()
            if any(kw in stripped.lower() for kw in ["next step", "下一步", "待辦", "todo"]):
                in_next_section = True
                continue
            if in_next_section:
                if stripped.startswith("- [") or stripped.startswith("* ["):
                    todos.append(stripped)
                elif stripped.startswith("#"):
                    break
        return latest_date, todos
    except:
        return None, []

def prepare_context(root_path):
    root = Path(root_path).resolve()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    context_file = root / "AGENT_CONTEXT.md"

    print(f"📋 Generating Context: {context_file}")
    # ... (餘下邏輯與原版本相似，但確保編碼安全) ...
    # 這裡產生的檔案內容與原版 prepare_context 一致
    # ...
    
if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    # 由於此指令與原版相似，暫時僅作簡化測試
    print("Prepare Context initialized.")
