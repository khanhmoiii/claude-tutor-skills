"""Unit tests for skills/retrieve/scripts/leitner.py.  Run: python -m unittest discover tests"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "retrieve" / "scripts" / "leitner.py"
FIXTURE = ROOT / "tests" / "fixture" / ".learning"


class LeitnerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = pathlib.Path(tempfile.mkdtemp())
        shutil.copytree(FIXTURE, self.tmp / ".learning")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_cli(self, *args):
        out = subprocess.run([sys.executable, str(SCRIPT), *args, "--dir", str(self.tmp / ".learning")],
                             capture_output=True, text=True, encoding="utf-8")
        return out.returncode, out.stdout + out.stderr

    def meta(self, file, entry_id):
        lines = (self.tmp / ".learning" / file).read_text(encoding="utf-8").splitlines()
        return lines[lines.index(next(l for l in lines if l.startswith(f"### {entry_id}"))) + 1]

    def test_due_lists_only_due_entries_lowest_box_first(self):
        code, out = self.run_cli("due", "--today", "2026-10-22")
        self.assertEqual(code, 0)
        rows = [l.split("\t")[0] for l in out.splitlines() if not l.startswith("#")]
        self.assertEqual(rows, ["M-20261015-01", "C-20261015-01"])
        self.assertIn("2 mục đến hạn / 3 mục", out)

    def test_grade_good_promotes_and_crosses_month(self):
        self.run_cli("grade", "C-20261015-01", "nho", "--today", "2026-10-28")
        self.assertEqual(self.meta("concepts.md", "C-20261015-01"),
                         "- Hộp: 3 | Ôn lần tới: 2026-11-04 | Ôn lần cuối: 2026-10-28")

    def test_grade_forgot_resets_to_box_1(self):
        self.run_cli("grade", "C-20261020-01", "quen", "--today", "2026-10-22")
        self.assertIn("Hộp: 1 | Ôn lần tới: 2026-10-23", self.meta("concepts.md", "C-20261020-01"))

    def test_grade_fuzzy_keeps_box(self):
        self.run_cli("grade", "C-20261015-01", "mo", "--today", "2026-12-30")
        self.assertIn("Hộp: 2 | Ôn lần tới: 2027-01-02", self.meta("concepts.md", "C-20261015-01"))

    def test_unknown_id_fails(self):
        code, out = self.run_cli("grade", "C-20000101-01", "nho")
        self.assertNotEqual(code, 0)
        self.assertIn("Không tìm thấy", out)

    def test_next_id_increments_within_day(self):
        self.assertEqual(self.run_cli("next-id", "C", "--today", "2026-10-15")[1].strip(), "C-20261015-02")
        self.assertEqual(self.run_cli("next-id", "M", "--today", "2026-10-22")[1].strip(), "M-20261022-01")


if __name__ == "__main__":
    unittest.main()
