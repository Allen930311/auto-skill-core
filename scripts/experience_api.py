#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))
from bm25_engine import BM25Engine

BASE_DIR  = Path(__file__).parent.parent
EXP_DIR   = BASE_DIR / "experience"
KB_DIR    = BASE_DIR / "knowledge-base"
EXP_INDEX = EXP_DIR / "_index.json"
KB_INDEX  = KB_DIR / "_index.json"


# ── Config ────────────────────────────────────────────────────────────────────

def get_config():
    config_path = BASE_DIR / "auto-skill.config.json"
    if not config_path.exists():
        config_path = BASE_DIR / "auto-skill.config.example.json"
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        username = os.environ.get("USERNAME") or os.environ.get("USER") or "user"
        home = os.path.expanduser("~")
        platform = sys.platform
        if platform not in config.get("platforms", {}):
            platform = "linux"
        platform_config = config.get("platforms", {}).get(platform, {})
        mapping = {
            "{USERNAME}": username,
            "{USER_HOME}": home,
            "{ONEDRIVE}": str(Path(home) / "OneDrive"),
        }
        resolved_base = {}
        for k, v in platform_config.items():
            val = v
            for var, real in mapping.items():
                val = val.replace(var, real)
            resolved_base[f"{{{k}}}"] = val
        special = {}
        for k, v in config.get("specialPaths", {}).items():
            val = v
            for var, real in resolved_base.items():
                val = val.replace(var, real)
            for var, real in mapping.items():
                val = val.replace(var, real)
            special[k] = val
        return {"base": resolved_base, "special": special, "raw": config}
    except Exception:
        return {}


config_data = get_config()
VAULT_DIR = Path(config_data.get("special", {}).get("vault", os.path.expanduser("~/note")))
DIARY_QUEUE = Path(config_data.get("special", {}).get("diary_queue",
    str(BASE_DIR / ".diary_queue.md")))


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def load_json(path):
    p = Path(path)
    if not p.exists():
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── BM25 Search ───────────────────────────────────────────────────────────────

def _build_corpus(include_kb=False):
    docs = []
    index = load_json(EXP_INDEX)
    if index:
        for skill in index.get("skills", []):
            fp = EXP_DIR / skill["file"]
            if not fp.exists():
                continue
            text = fp.read_text(encoding="utf-8", errors="ignore")
            triggers = " ".join(skill.get("t", skill.get("keywords", [])))
            docs.append({
                "id": skill["skillId"],
                "file": skill["file"],
                "name": skill.get("name", skill["skillId"]),
                "type": "experience",
                "text": triggers + " " + text,
            })
    if include_kb:
        kb_index = load_json(KB_INDEX)
        if kb_index:
            for cat in kb_index.get("categories", []):
                fp = KB_DIR / cat["file"]
                if not fp.exists():
                    continue
                text = fp.read_text(encoding="utf-8", errors="ignore")
                docs.append({
                    "id": cat["id"],
                    "file": cat["file"],
                    "name": cat.get("name", cat["id"]),
                    "type": "knowledge-base",
                    "text": text,
                })
    return docs


def cmd_search(keywords, top_n=5, include_kb=False):
    query = " ".join(keywords)
    docs = _build_corpus(include_kb=include_kb)
    if not docs:
        print("No documents indexed. Run `update-index` first.")
        return
    engine = BM25Engine()
    engine.add_documents(docs)
    results = engine.search(query, top_n=top_n)
    if not results:
        print(f"No results for: {query}")
        return
    print(f"Top {len(results)} results for '{query}':")
    for r in results:
        tag = f" [{r['type']}]" if include_kb else ""
        print(f"  [{r['score']:.2f}] {r['name']}{tag} → {r['file']}")


# ── Vault Query ───────────────────────────────────────────────────────────────

def cmd_vault_query(keywords, top_n=5):
    """BM25 search across all markdown files in the vault directory."""
    query = " ".join(keywords)

    if not VAULT_DIR.exists():
        print(f"Vault not found: {VAULT_DIR}")
        print("Update 'specialPaths.vault' in auto-skill.config.json")
        return

    docs = []
    for md_file in VAULT_DIR.rglob("*.md"):
        try:
            text = md_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        docs.append({
            "id": str(md_file.relative_to(VAULT_DIR)),
            "file": str(md_file),
            "name": md_file.stem,
            "type": "vault",
            "text": text,
        })

    if not docs:
        print(f"No markdown files found in vault: {VAULT_DIR}")
        return

    engine = BM25Engine()
    engine.add_documents(docs)
    results = engine.search(query, top_n=top_n)

    if not results:
        print(f"No vault results for: {query}")
        return

    print(f"Top {len(results)} vault results for '{query}':")
    for r in results:
        print(f"  [{r['score']:.2f}] {r['name']}")
        print(f"           {r['file']}")


# ── Index Management ──────────────────────────────────────────────────────────

def cmd_update_index():
    index = load_json(EXP_INDEX) or {"lastUpdated": get_today(), "skills": []}
    existing_ids = {s["skillId"] for s in index["skills"]}
    added = 0
    for md_file in sorted(EXP_DIR.glob("skill-*.md")):
        skill_id = md_file.stem.replace("skill-", "", 1)
        if skill_id not in existing_ids:
            index["skills"].append({
                "skillId": skill_id,
                "name": skill_id.replace("-", " ").title(),
                "file": md_file.name,
                "count": 0,
                "last_updated": get_today(),
                "t": [],
                "keywords": [],
            })
            added += 1
    index["lastUpdated"] = get_today()
    save_json(EXP_INDEX, index)
    print(f"Index updated: {len(index['skills'])} skills total, {added} newly added.")


# ── Append Entry ──────────────────────────────────────────────────────────────

def cmd_add(skill_id, content, is_kb=False):
    today = get_today()
    target_dir = KB_DIR if is_kb else EXP_DIR
    index_path = KB_INDEX if is_kb else EXP_INDEX
    key = "categories" if is_kb else "skills"
    id_field = "id" if is_kb else "skillId"

    index = load_json(index_path)
    if not index:
        print(f"Index not found: {index_path}")
        return

    entry = next((s for s in index[key] if s.get(id_field) == skill_id), None)
    if not entry:
        available = [s[id_field] for s in index[key]]
        print(f"ID not found: {skill_id}. Available: {available}")
        return

    file_path = target_dir / entry["file"]
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(f"\n---\n\n{content.strip()}\n")

    entry["count"] = entry.get("count", 0) + 1
    entry["last_updated"] = today
    index["lastUpdated"] = today
    save_json(index_path, index)
    print(f"Appended to {entry['file']} (total entries: {entry['count']})")


# ── Snapshot (Failure / Multi-attempt lesson) ─────────────────────────────────

def cmd_snapshot(skill_id, lesson, task_type="general"):
    """
    Append a compact failure/lesson snapshot directly to knowledge-base.
    Used by SKILL_CLOSE Step F2 for failed tasks or tasks with ≥3 attempts.
    """
    today = get_today()
    kb_index = load_json(KB_INDEX)

    # Try to find an existing KB category for this skill; fall back to general
    target_cat = None
    if kb_index:
        target_cat = next(
            (c for c in kb_index.get("categories", []) if skill_id in c.get("id", "")),
            None
        )
        if not target_cat:
            # Use first available category as fallback
            cats = kb_index.get("categories", [])
            target_cat = cats[0] if cats else None

    if not target_cat:
        print("No KB categories found. Run preflight or create knowledge-base/_index.json.")
        return

    file_path = KB_DIR / target_cat["file"]
    if not file_path.exists():
        file_path.write_text(f"# {target_cat.get('name', target_cat['id'])}\n", encoding="utf-8")

    snapshot_entry = (
        f"\n---\n\n"
        f"## 💥 Snapshot: {lesson[:80]} ({today}) [{task_type}]\n"
        f"**Skill:** {skill_id}\n"
        f"**Lesson:** {lesson}\n"
        f"**Task Type:** {task_type}\n"
    )

    with open(file_path, "a", encoding="utf-8") as f:
        f.write(snapshot_entry)

    target_cat["count"] = target_cat.get("count", 0) + 1
    target_cat["last_updated"] = today
    if kb_index:
        kb_index["lastUpdated"] = today
        save_json(KB_INDEX, kb_index)

    print(f"Snapshot written to {target_cat['file']}: {lesson[:60]}...")


# ── Preflight ────────────────────────────────────────────────────────────────

def cmd_preflight():
    issues = []
    if not EXP_INDEX.exists():
        issues.append(f"Missing: {EXP_INDEX}")
    if not KB_INDEX.exists():
        issues.append(f"Missing: {KB_INDEX}")
    if not (BASE_DIR / "auto-skill.config.json").exists():
        issues.append("Missing: auto-skill.config.json  (copy from auto-skill.config.example.json)")
    if not VAULT_DIR.exists():
        issues.append(f"Vault not found: {VAULT_DIR}  (update specialPaths.vault in config)")
    if issues:
        print("Preflight FAILED:")
        for i in issues:
            print(f"  ✗ {i}")
        sys.exit(1)
    print("Preflight OK — all required files present.")
    print(f"  Vault : {VAULT_DIR}")
    print(f"  Queue : {DIARY_QUEUE}")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Skill Core API")
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search", help="BM25 search across experience files")
    p_search.add_argument("keywords", nargs="+")
    p_search.add_argument("-n", type=int, default=5)
    p_search.add_argument("--kb", action="store_true", help="Also search knowledge-base")

    p_vault = sub.add_parser("vault-query", help="BM25 search across all vault markdown files")
    p_vault.add_argument("keywords", nargs="+")
    p_vault.add_argument("-n", type=int, default=5)

    sub.add_parser("update-index", help="Rebuild experience/_index.json from skill files")

    p_add = sub.add_parser("add", help="Append an entry to a skill or KB file")
    p_add.add_argument("skill_id")
    p_add.add_argument("content")
    p_add.add_argument("--kb", action="store_true")

    p_snap = sub.add_parser("snapshot", help="Append a compact failure/lesson snapshot to KB (Step F2)")
    p_snap.add_argument("--skill-id", required=True)
    p_snap.add_argument("--lesson", required=True, help="Lesson in ≤80 chars")
    p_snap.add_argument("--task-type", default="general")

    sub.add_parser("preflight", help="Verify environment is ready")

    args = parser.parse_args()

    if args.command == "search":
        cmd_search(args.keywords, top_n=args.n, include_kb=args.kb)
    elif args.command == "vault-query":
        cmd_vault_query(args.keywords, top_n=args.n)
    elif args.command == "update-index":
        cmd_update_index()
    elif args.command == "add":
        cmd_add(args.skill_id, args.content, is_kb=args.kb)
    elif args.command == "snapshot":
        cmd_snapshot(args.skill_id, args.lesson, task_type=args.task_type)
    elif args.command == "preflight":
        cmd_preflight()
    else:
        parser.print_help()
