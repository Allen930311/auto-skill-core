#!/usr/bin/env python3
"""Regression tests for cmd_snapshot() routing.

The defect these lock down: cmd_snapshot() used to fall back to the first KB
category whenever no category matched the skill-id. knowledge-base/_index.json
ships with exactly one category (user-dna), so on a default install *every*
unclassifiable technical snapshot landed in User DNA -- startup context that is
loaded every session.

Run:  python -m unittest discover -s tests   (no third-party dependencies)
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import experience_api  # noqa: E402


def write_kb(root, categories):
    """Build a throwaway knowledge-base/ and point experience_api at it."""
    kb_dir = root / "knowledge-base"
    kb_dir.mkdir(parents=True, exist_ok=True)
    for cat in categories:
        (kb_dir / cat["file"]).write_text(f"# {cat['id']}\n", encoding="utf-8")
    index = {"lastUpdated": "2026-01-01", "categories": categories}
    (kb_dir / "_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    experience_api.KB_DIR = kb_dir
    experience_api.KB_INDEX = kb_dir / "_index.json"
    return kb_dir


def cat(cat_id, count=0):
    return {"id": cat_id, "name": cat_id, "file": f"{cat_id}.md", "count": count}


class SnapshotRoutingTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._orig = (experience_api.KB_DIR, experience_api.KB_INDEX)

    def tearDown(self):
        experience_api.KB_DIR, experience_api.KB_INDEX = self._orig
        self._tmp.cleanup()

    def test_shipped_default_index_does_not_absorb_unmatched_snapshot(self):
        """The actual regression: a single-category (user-dna) index, as shipped."""
        kb = write_kb(self.root, [cat("user-dna")])
        before = (kb / "user-dna.md").read_text(encoding="utf-8")

        wrote = experience_api.cmd_snapshot("git-version-control", "detached HEAD after rebase")

        self.assertFalse(wrote)
        self.assertEqual((kb / "user-dna.md").read_text(encoding="utf-8"), before)
        self.assertNotIn("Snapshot", (kb / "user-dna.md").read_text(encoding="utf-8"))

    def test_unmatched_skill_id_writes_nothing_anywhere(self):
        kb = write_kb(self.root, [cat("user-dna"), cat("environment"), cat("dev-tools")])
        before = {p.name: p.read_text(encoding="utf-8") for p in kb.glob("*.md")}

        wrote = experience_api.cmd_snapshot("some-unknown-platform", "API returned 418")

        self.assertFalse(wrote)
        for path, text in before.items():
            self.assertEqual((kb / path).read_text(encoding="utf-8"), text)
        # index untouched too
        index = json.loads((kb / "_index.json").read_text(encoding="utf-8"))
        self.assertTrue(all(c["count"] == 0 for c in index["categories"]))

    def test_matching_category_still_appends(self):
        kb = write_kb(self.root, [cat("user-dna"), cat("git-version-control")])

        wrote = experience_api.cmd_snapshot("git-version-control", "detached HEAD after rebase")

        self.assertTrue(wrote)
        body = (kb / "git-version-control.md").read_text(encoding="utf-8")
        self.assertIn("detached HEAD after rebase", body)
        self.assertIn("Snapshot", body)

        index = json.loads((kb / "_index.json").read_text(encoding="utf-8"))
        target = next(c for c in index["categories"] if c["id"] == "git-version-control")
        self.assertEqual(target["count"], 1)
        # user-dna stayed clean
        self.assertNotIn("Snapshot", (kb / "user-dna.md").read_text(encoding="utf-8"))

    def test_user_dna_is_unreachable_even_when_the_skill_id_matches_it(self):
        """Protection is explicit, not incidental: an exact id match is still refused."""
        kb = write_kb(self.root, [cat("user-dna")])

        wrote = experience_api.cmd_snapshot("user-dna", "prefers UTF-8 everywhere")

        self.assertFalse(wrote)
        self.assertNotIn("Snapshot", (kb / "user-dna.md").read_text(encoding="utf-8"))

    def test_empty_index_refuses_instead_of_crashing(self):
        write_kb(self.root, [])
        self.assertFalse(experience_api.cmd_snapshot("anything", "lesson"))


if __name__ == "__main__":
    unittest.main()
