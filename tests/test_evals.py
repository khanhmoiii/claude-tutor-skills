"""Unit tests for the code checks in evals/run_evals.py (no API calls).  Run: python -m unittest discover tests"""
import datetime as dt
import pathlib
import shutil
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "evals"))
import run_evals as E  # noqa: E402

LEITNER = [sys.executable, str(ROOT / "skills" / "retrieve" / "scripts" / "leitner.py")]


class RenderTest(unittest.TestCase):
    def test_relative_dates(self):
        t = E.TODAY
        self.assertEqual(E.render("{{d}}"), t.isoformat())
        self.assertEqual(E.render("{{d+7}}"), (t + dt.timedelta(7)).isoformat())
        self.assertEqual(E.render("C-{{dc-1}}-01"), f"C-{(t - dt.timedelta(1)):%Y%m%d}-01")


class CodeCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.case = next(c for c in E.load_cases(["reflect-update"]))
        cls.dir = E.WORK / "unittest"
        E.prepare(cls.case, cls.dir, ROOT / "skills")
        cls.before = E.digest(cls.dir)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def check(self, c, replies=("",)):
        return E.code_check(c, list(replies), self.dir, self.before)[0]

    def test_fixture_rendered_and_valid(self):
        self.assertTrue(self.check({"type": "ids_valid"}))
        self.assertTrue(self.check({"type": "count_entries", "file": ".learning/concepts.md", "count": 2}))
        due = subprocess.run(LEITNER + ["due", "--dir", str(self.dir / ".learning")],
                             capture_output=True, text=True, encoding="utf-8").stdout
        self.assertIn("2 mục đến hạn / 3 mục", due)

    def test_entry_detects_schedule(self):
        mid = E.render("M-{{dc-7}}-01")
        self.assertTrue(self.check({"type": "entry", "file": ".learning/mistakes.md", "entry_id": mid,
                                    "box": 1, "next": E.render("{{d-6}}")}))
        self.assertFalse(self.check({"type": "entry", "file": ".learning/mistakes.md", "entry_id": mid,
                                     "box": 2, "next": E.render("{{d-6}}")}))

    def test_files_unchanged(self):
        self.assertTrue(self.check({"type": "files_unchanged"}))

    def test_labels(self):
        good = "[NGHIÊM TRỌNG] a\n❓ x\n[NHỎ] b\n❓ y"
        self.assertTrue(self.check({"type": "labels", "max": 5, "each_question": True, "sorted": True}, [good]))
        self.assertFalse(self.check({"type": "labels", "sorted": True}, ["[NHỎ] b\n[NGHIÊM TRỌNG] a"]))
        self.assertFalse(self.check({"type": "labels", "each_question": True}, ["[NHỎ] b"]))
        self.assertFalse(self.check({"type": "labels", "max": 1}, [good]))

    def test_text_checks(self):
        self.assertTrue(self.check({"type": "first_line", "pattern": r"→\s*Chế độ"}, ["\n> → Chế độ Gia sư\nx"]))
        self.assertTrue(self.check({"type": "max_count", "pattern": r"\?", "max": 2}, ["a? b?"]))
        self.assertFalse(self.check({"type": "max_count", "pattern": r"\?", "max": 2}, ["a? b? c?"]))
        self.assertFalse(self.check({"type": "no_code_block"}, ["```py\nx\n```"]))
        self.assertTrue(self.check({"type": "regex", "turn": 1, "pattern": "cấp 0"}, ["Gợi ý cấp 0/6", "cấp 1/6"]))


if __name__ == "__main__":
    unittest.main()
