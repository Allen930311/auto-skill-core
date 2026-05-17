#!/usr/bin/env python3
"""
Auto-Skill Bridge Sync
Usage:
  python bridge_sync.py push          # copy experience/ + knowledge-base/ to vault
  python bridge_sync.py pull          # sync vault changes back to local repo
  python bridge_sync.py status        # show diff between local and vault
  python bridge_sync.py push --dry-run
"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent.parent
EXP_DIR  = BASE_DIR / "experience"
KB_DIR   = BASE_DIR / "knowledge-base"


# ── Config ────────────────────────────────────────────────────────────────────

def get_vault_dir() -> Path:
    config_path = BASE_DIR / "auto-skill.config.json"
    if not config_path.exists():
        config_path = BASE_DIR / "auto-skill.config.example.json"
    if not config_path.exists():
        return Path(os.path.expanduser("~/note"))

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    username = os.environ.get("USERNAME") or os.environ.get("USER") or "user"
    home = os.path.expanduser("~")
    platform = sys.platform
    if platform not in config.get("platforms", {}):
        platform = "linux"

    platform_config = config.get("platforms", {}).get(platform, {})
    mapping = {"{USERNAME}": username, "{USER_HOME}": home}

    resolved_base = {}
    for k, v in platform_config.items():
        val = v
        for var, real in mapping.items():
            val = val.replace(var, real)
        resolved_base[f"{{{k}}}"] = val

    vault_raw = config.get("specialPaths", {}).get("vault", "{USER_HOME}/note")
    for var, real in {**resolved_base, **mapping}.items():
        vault_raw = vault_raw.replace(var, real)
    return Path(vault_raw)


# ── File Operations ───────────────────────────────────────────────────────────

SYNC_DIRS = {
    "experience":     EXP_DIR,
    "knowledge-base": KB_DIR,
}


def get_vault_mirror(vault_dir: Path) -> Path:
    return vault_dir / "auto-skill-sync"


def collect_files(src_dir: Path):
    return [p for p in src_dir.rglob("*") if p.is_file()]


def sync_dir(src: Path, dst: Path, dry_run: bool) -> tuple[int, int]:
    copied, skipped = 0, 0
    for src_file in collect_files(src):
        rel = src_file.relative_to(src)
        dst_file = dst / rel
        src_mtime = src_file.stat().st_mtime

        if dst_file.exists():
            dst_mtime = dst_file.stat().st_mtime
            if src_mtime <= dst_mtime:
                skipped += 1
                continue

        if dry_run:
            print(f"  [dry-run] would copy: {rel}")
        else:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
            print(f"  → {rel}")
        copied += 1
    return copied, skipped


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_push(dry_run: bool):
    vault_dir = get_vault_dir()
    mirror = get_vault_mirror(vault_dir)
    print(f"{'[DRY RUN] ' if dry_run else ''}Pushing to vault: {mirror}")

    if not vault_dir.exists():
        print(f"✗ Vault directory not found: {vault_dir}")
        print("  Update 'specialPaths.vault' in auto-skill.config.json")
        sys.exit(1)

    total_copied = total_skipped = 0
    for name, src_dir in SYNC_DIRS.items():
        if not src_dir.exists():
            continue
        dst_dir = mirror / name
        print(f"\n  [{name}]")
        copied, skipped = sync_dir(src_dir, dst_dir, dry_run)
        total_copied += copied
        total_skipped += skipped

    print(f"\n{'[dry-run] ' if dry_run else ''}Done — {total_copied} copied, {total_skipped} up-to-date.")


def cmd_pull(dry_run: bool):
    vault_dir = get_vault_dir()
    mirror = get_vault_mirror(vault_dir)
    print(f"{'[DRY RUN] ' if dry_run else ''}Pulling from vault: {mirror}")

    if not mirror.exists():
        print(f"✗ Mirror not found: {mirror}. Run `push` first.")
        sys.exit(1)

    total_copied = total_skipped = 0
    for name, dst_dir in SYNC_DIRS.items():
        src_dir = mirror / name
        if not src_dir.exists():
            continue
        print(f"\n  [{name}]")
        copied, skipped = sync_dir(src_dir, dst_dir, dry_run)
        total_copied += copied
        total_skipped += skipped

    print(f"\n{'[dry-run] ' if dry_run else ''}Done — {total_copied} copied, {total_skipped} up-to-date.")


def cmd_status():
    vault_dir = get_vault_dir()
    mirror = get_vault_mirror(vault_dir)
    print(f"Status — local vs vault mirror ({mirror})\n")

    for name, local_dir in SYNC_DIRS.items():
        mirror_dir = mirror / name
        local_files = {p.relative_to(local_dir) for p in collect_files(local_dir)} if local_dir.exists() else set()
        vault_files = {p.relative_to(mirror_dir) for p in collect_files(mirror_dir)} if mirror_dir.exists() else set()

        only_local = local_files - vault_files
        only_vault = vault_files - local_files
        both = local_files & vault_files

        stale_local = [
            p for p in both
            if (local_dir / p).stat().st_mtime > (mirror_dir / p).stat().st_mtime
        ]

        print(f"  [{name}]")
        for p in sorted(only_local):
            print(f"    + local only  : {p}")
        for p in sorted(only_vault):
            print(f"    + vault only  : {p}")
        for p in sorted(stale_local):
            print(f"    ~ local newer : {p}")
        if not only_local and not only_vault and not stale_local:
            print(f"    ✓ in sync")


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto-Skill Bridge Sync")
    sub = parser.add_subparsers(dest="command")

    p_push = sub.add_parser("push", help="Copy local files to vault mirror")
    p_push.add_argument("--dry-run", action="store_true", help="Show what would be copied without writing")

    p_pull = sub.add_parser("pull", help="Sync vault mirror changes back to local repo")
    p_pull.add_argument("--dry-run", action="store_true", help="Show what would be copied without writing")

    sub.add_parser("status", help="Show diff between local and vault mirror")

    args = parser.parse_args()

    if args.command == "push":
        cmd_push(dry_run=args.dry_run)
    elif args.command == "pull":
        cmd_pull(dry_run=args.dry_run)
    elif args.command == "status":
        cmd_status()
    else:
        parser.print_help()
