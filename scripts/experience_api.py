#!/usr/bin/env python3
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# 針對 Windows 環境強制輸出 UTF-8
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ── 設定與配置 (Decoupled Config) ───────────────────────────────────────────
BASE_DIR     = Path(__file__).parent.parent
EXP_DIR      = BASE_DIR / "experience"
KB_DIR       = BASE_DIR / "knowledge-base"
EXP_INDEX    = EXP_DIR / "_index.json"
KB_INDEX     = KB_DIR / "_index.json"
SNAP_PATH    = EXP_DIR / "experience_snapshot.json"
BUNDLES_PATH = EXP_DIR / "skill-bundles.json"
KW_PATH      = EXP_DIR / "skill-keywords.json"

def get_config():
    """載入本地配置，解析動態路徑。"""
    config_path = BASE_DIR / "auto-skill.config.json"
    if not config_path.exists():
        # 回退到範例配置（如果存在）或預設值
        config_path = BASE_DIR / "auto-skill.config.example.json"
    
    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 解析路徑變數
        username = os.environ.get("USERNAME") or os.environ.get("USER") or "user"
        home = os.path.expanduser("~")
        
        platform = sys.platform
        if platform not in config.get("platforms", {}):
            # 沒匹配到平台時嘗試使用 linux 作為通用 fallback
            platform = "linux"
            
        platform_config = config.get("platforms", {}).get(platform, {})
        
        # 建立解析字典
        mapping = {
            "{USERNAME}": username,
            "{USER_HOME}": home,
            "{ONEDRIVE}": str(Path(home) / "OneDrive")
        }
        
        # 第一階段：解析基礎路徑
        resolved_base = {}
        for k, v in platform_config.items():
            val = v
            for var, real in mapping.items():
                val = val.replace(var, real)
            resolved_base[f"{{{k}}}"] = val
        
        # 第二階段：解析特殊路徑
        special = {}
        for k, v in config.get("specialPaths", {}).items():
            val = v
            # 先用基礎路徑替換，再用 mapping 替換
            for var, real in resolved_base.items():
                val = val.replace(var, real)
            for var, real in mapping.items():
                val = val.replace(var, real)
            special[k] = val
            
        return {
            "base": resolved_base,
            "special": special,
            "raw": config
        }
    except Exception:
        return {}

# 初始化路徑
config_data = get_config()
VAULT_DIR = Path(config_data.get("special", {}).get("vault", os.path.expanduser("~/note")))
DAILY_DIR = VAULT_DIR / "10_Daily"

# ── 核心功能 (保持邏輯，去除個人化) ──────────────────────────────────────────

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def load_json(path):
    if not path or not Path(path).exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_experience(skill_id, content, is_knowledge=False):
    """將成功的實戰片段併入對應的技能文件。"""
    today = get_today()
    target_dir = KB_DIR if is_knowledge else EXP_DIR
    index_path = KB_INDEX if is_knowledge else EXP_INDEX

    index = load_json(index_path)
    if not index:
        return False, f"找不到索引文件: {index_path}"

    entry = next((s for s in (index["skills"] if not is_knowledge else index["categories"])
                 if s.get("skillId" if not is_knowledge else "id") == skill_id), None)

    if not entry:
        return False, f"找不到 ID: {skill_id}"

    file_path = target_dir / entry["file"]
    formatted_content = f"\n---\n\n{content.strip()}\n"

    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(formatted_content)
    except Exception as e:
        return False, f"檔案寫入失敗: {e}"

    entry["count"] = entry.get("count", 0) + 1
    entry["last_updated"] = today
    index["lastUpdated"] = today
    save_json(index_path, index)

    return True, f"成功併入 {entry['file']}，目前記錄數: {entry['count']}"

# ... (其餘功能與經驗總結相似，但已移除與個人專案相關的 Hardcoded 檢查) ...

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Auto-Skill Core API")
    subparsers = parser.add_subparsers(dest="command")

    # Add commands: preflight, librarian, add, sync-vault ...
    # (此處省略部分詳細邏輯，以確保核心代碼乾淨)
    
    args = parser.parse_args()
    if args.command == "preflight":
        # 從實作中提取的 preflight 邏輯
        print("Running preflight...")
    # ...
