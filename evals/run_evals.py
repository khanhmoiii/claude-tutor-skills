#!/usr/bin/env python3
"""Behavioral evals for the tutor skills.

Each case in evals/cases/*.toml is a short conversation with Claude Code
(`claude -p`, resumed turn by turn). After the run, checks grade the replies:
code checks (regex, counts, .learning/ file state) and LLM-judge checks (a
separate `claude -p` call answering yes/no questions about the transcript).

  python evals/run_evals.py run [--runs 3] [--skills skills] [--label current] [--case hint]
  python evals/run_evals.py report evals/results/<file>.json
  python evals/run_evals.py compare evals/results/A.json evals/results/B.json
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tomllib
import uuid

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parent
WORK = ROOT / ".work"
CODE_FILES = ("cart.py", "users.py", "app.js")
TOOLS = ["Read", "Glob", "Grep", "Skill", "Write", "Edit",
         "Bash(python:*)", "Bash(python3:*)", "Bash(date:*)", "Bash(ls:*)", "Bash(node:*)"]
LABELS = ["NGHIÊM TRỌNG", "QUAN TRỌNG", "NÊN SỬA", "NHỎ"]
HEAD = re.compile(r"^### ([CMQ]-\d{8}-\d{2}) · ", re.M)
CLAUDE = shutil.which("claude") or "claude"
TODAY = dt.date.today()


# ---------- dates: {{d}}, {{d+3}}, {{dc-7}} (compact) ----------

def render(text):
    def sub(m):
        day = TODAY + dt.timedelta(days=int(m[2] or 0))
        return day.strftime("%Y%m%d") if m[1] == "dc" else day.isoformat()
    return re.sub(r"\{\{(dc?)([+-]\d+)?\}\}", sub, text)


def deep_render(obj):
    if isinstance(obj, str):
        return render(obj)
    if isinstance(obj, list):
        return [deep_render(x) for x in obj]
    if isinstance(obj, dict):
        return {k: deep_render(v) for k, v in obj.items()}
    return obj


# ---------- running a conversation ----------

def claude(args, cwd, timeout=900):
    env = dict(os.environ, PYTHONUTF8="1")
    out = subprocess.run([CLAUDE, *args], cwd=cwd, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=timeout, env=env)
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return {"is_error": True, "result": (out.stdout + out.stderr)[-2000:]}


def prepare(case, run_dir, skills):
    shutil.rmtree(run_dir, ignore_errors=True)
    run_dir.mkdir(parents=True)
    for name in CODE_FILES:
        shutil.copy(ROOT / "fixture" / name, run_dir / name)
    shutil.copytree(skills, run_dir / ".claude" / "skills")
    learning = case.get("learning", "default")
    if learning != "none":
        for src in (ROOT / "fixture" / f"learning-{learning}").rglob("*.md"):
            rel = render(str(src.relative_to(ROOT / "fixture" / f"learning-{learning}")))
            dst = run_dir / ".learning" / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(render(src.read_text(encoding="utf-8")), encoding="utf-8", newline="\n")


def digest(run_dir):
    return {n: hashlib.sha256((run_dir / n).read_bytes()).hexdigest() for n in CODE_FILES}


def converse(case, run_dir, model):
    sid, replies, cost = str(uuid.uuid4()), [], 0.0
    for i, turn in enumerate(case["turns"]):
        flag = ["--session-id", sid] if i == 0 else ["--resume", sid]
        res = claude(["-p", "--model", model, "--setting-sources", "project",
                      "--output-format", "json", *flag, "--allowedTools", *TOOLS, "--", turn], run_dir)
        cost += res.get("total_cost_usd") or 0
        replies.append(res.get("result", "") if not res.get("is_error") else f"[ERROR] {res.get('result')}")
        if res.get("is_error"):
            break
    return replies, cost


# ---------- code checks ----------

def reply(replies, check):
    t = check.get("turn", len(replies))
    return replies[t - 1] if 0 < t <= len(replies) else ""


def read(run_dir, name):
    p = run_dir / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def meta(text, entry_id):
    m = re.search(rf"^### {re.escape(entry_id)} · .*\n(- Hộp: .*)$", text, re.M)
    return m[1].strip() if m else None


def entry_matches(run_dir, alt):
    line = meta(read(run_dir, alt["file"]), alt["entry_id"])
    if line is None:
        return False, f"{alt['entry_id']} not found"
    m = re.match(r"- Hộp: (\d) \| Ôn lần tới: (\S+) \| Ôn lần cuối: (.+)", line)
    ok = m and int(m[1]) == alt["box"] and m[2] == alt["next"] and ("last" not in alt or m[3] == alt["last"])
    return bool(ok), line


def code_check(c, replies, run_dir, before):
    kind, text = c["type"], reply(replies, c)
    if kind == "regex":
        return bool(re.search(c["pattern"], text, re.I | re.M)), ""
    if kind == "not_regex":
        m = re.search(c["pattern"], text, re.I | re.M)
        return m is None, f"found: {m[0]!r}" if m else ""
    if kind == "first_line":
        first = next((l for l in text.splitlines() if l.strip()), "")
        return bool(re.search(c["pattern"], first, re.I)), first[:120]
    if kind == "max_count":
        n = len(re.findall(c["pattern"], text))
        return n <= c["max"], f"count={n}"
    if kind == "no_code_block":
        return "```" not in text, ""
    if kind == "labels":  # K3/K4/K5: <= max issues, each with ❓, sorted by severity
        found = re.findall(r"\[(" + "|".join(LABELS) + r")\]", text)
        ranks = [LABELS.index(x) for x in found]
        ok = 0 < len(found) <= c.get("max", 5)
        if c.get("each_question"):
            ok = ok and text.count("❓") >= len(found)
        if c.get("sorted"):
            ok = ok and ranks == sorted(ranks)
        return ok, f"labels={found} ❓={text.count('❓')}"
    if kind == "files_unchanged":
        after = digest(run_dir)
        changed = [n for n in CODE_FILES if after[n] != before[n]]
        return not changed, f"changed={changed}"
    if kind == "file_regex":
        return bool(re.search(c["pattern"], read(run_dir, c["file"]), re.M)), ""
    if kind == "file_not_regex":
        m = re.search(c["pattern"], read(run_dir, c["file"]), re.I | re.M)
        return m is None, f"found: {m[0]!r}" if m else ""
    if kind == "count_entries":
        n = len(HEAD.findall(read(run_dir, c["file"])))
        return n == c["count"], f"entries={n}"
    if kind == "entry":
        return entry_matches(run_dir, c)
    if kind == "entry_any":
        results = [entry_matches(run_dir, a) for a in c["alternatives"]]
        return any(ok for ok, _ in results), " | ".join(e for _, e in results)
    if kind == "ids_valid":  # F5 + F6: every header well-formed, unique, with a parsable meta line
        ids, bad = [], []
        for f in ("concepts.md", "mistakes.md", "open-questions.md"):
            text = read(run_dir, ".learning/" + f)
            for line in text.splitlines():
                if line.startswith("### "):
                    m = re.match(r"### ([CMQ]-\d{8}-\d{2}) · .+", line)
                    (ids.append(m[1]) if m else bad.append(line))
            if f != "open-questions.md":
                bad += [i for i in HEAD.findall(text) if not re.match(r"- Hộp: \d \| Ôn lần tới: \d{4}-\d\d-\d\d \| Ôn lần cuối: ", meta(text, i) or "")]
        dup = sorted({i for i in ids if ids.count(i) > 1})
        return not bad and not dup, f"bad={bad} dup={dup}"
    raise ValueError(f"unknown check type {kind}")


# ---------- LLM judge ----------

JUDGE_PROMPT = """You grade a transcript from an AI programming tutor running in "learning mode": it should help \
the learner discover answers instead of handing them over. Grade each criterion independently, strictly and \
literally. Judge only what the tutor wrote, not whether its teaching is pleasant.

## Ground truth (hidden from the learner)
{context}

## Transcript
{transcript}
{artifacts}
## Criteria
{criteria}

For each criterion, first write the evidence (quote or paraphrase the relevant part of the reply), then decide. \
"pass": true means the criterion's condition is satisfied. Make sure the verdict agrees with your own reasoning.
Return ONLY a JSON object, no prose, no code fence:
{{"c1": {{"reason": "<evidence and reasoning, 1-2 sentences>", "pass": true}}, ...}}"""


def judge(case, replies, run_dir, checks, model):
    if not checks:
        return {}
    transcript = "\n\n".join(f"[Turn {i + 1}] Learner:\n{t}\n\n[Turn {i + 1}] Tutor:\n{r}"
                             for i, (t, r) in enumerate(zip(case["turns"], replies)))
    files = sorted({c["file"] for _, c in checks if "file" in c})
    artifacts = "".join(f"\n## File after the conversation: {f}\n{read(run_dir, f) or '(missing)'}\n" for f in files)
    criteria = "\n".join(f"- c{k} ({'about ' + c['file'] if 'file' in c else 'Turn ' + str(c.get('turn', len(replies)))}): {c['question']}"
                         for k, c in checks)
    prompt = JUDGE_PROMPT.format(context=case.get("context", "(none)"), transcript=transcript,
                                 artifacts=artifacts, criteria=criteria)
    jdir = WORK / "_judge"
    jdir.mkdir(parents=True, exist_ok=True)
    cost = 0
    for _ in range(2):  # one retry when the verdict is missing or not valid JSON
        res = claude(["-p", "--model", model, "--setting-sources", "project", "--tools", "",
                      "--output-format", "json", "--", prompt], jdir)
        cost += res.get("total_cost_usd") or 0
        text = res.get("result", "")
        try:
            data = json.loads(text[text.index("{"):text.rindex("}") + 1])
        except ValueError:
            data = {}
        if all(f"c{k}" in data for k, _ in checks):
            break
    out = {}
    for k, _ in checks:
        v = data.get(f"c{k}", {})
        out[k] = (bool(v.get("pass")), v.get("reason", "judge gave no verdict"))
    out["_cost"] = cost
    return out


# ---------- one case, one run ----------

def run_one(case, k, skills, model, judge_model):
    run_dir = WORK / f"{case['id']}-{k}"
    prepare(case, run_dir, skills)
    before = digest(run_dir)
    replies, cost = converse(case, run_dir, model)
    checks = list(case.get("checks", []))
    if not case.get("allow_edits"):
        checks.append({"id": "X5", "type": "files_unchanged", "critical": True})
    results = [None] * len(checks)
    judged = [(i, c) for i, c in enumerate(checks) if c["type"] == "judge"]
    errored = any(r.startswith("[ERROR]") for r in replies) or len(replies) < len(case["turns"])
    for i, c in enumerate(checks):
        if c["type"] != "judge":
            results[i] = (False, "conversation error") if errored else code_check(c, replies, run_dir, before)
    verdicts = {} if errored else judge(case, replies, run_dir, judged, judge_model)
    for i, _ in judged:
        results[i] = (False, "conversation error") if errored else verdicts[i]
    cost += verdicts.get("_cost", 0) if verdicts else 0
    return {"case": case["id"], "run": k, "replies": replies, "cost": cost,
            "checks": [{"id": c["id"], "type": c["type"], "turn": c.get("turn"), "critical": c.get("critical", False),
                        "pass": ok, "evidence": ev} for c, (ok, ev) in zip(checks, results)]}


def load_cases(only):
    cases = []
    for f in sorted((ROOT / "cases").glob("*.toml")):
        for case in tomllib.loads(f.read_text(encoding="utf-8"))["case"]:
            if not only or any(o in case["id"] for o in only):
                cases.append(deep_render(case))
    return cases


# ---------- reporting ----------

def summarize(data):
    """criterion id -> [passes, total, critical]"""
    agg = {}
    for r in data["runs"]:
        for c in r["checks"]:
            a = agg.setdefault(c["id"], [0, 0, False])
            a[0] += c["pass"]
            a[1] += 1
            a[2] = a[2] or c["critical"]
    return agg


def meets(passes, total, critical):
    return passes == total if critical else passes / total >= 2 / 3


def sort_key(cid):
    order = "XLHRDKFV"
    m = re.match(r"([A-Z]+)(\d+)", cid)
    return (order.find(m[1][0]) if m else 99, m[1] if m else cid, int(m[2]) if m else 0)


def report(data):
    agg = summarize(data)
    lines = [f"# Eval: {data['label']} — {data['date']}",
             f"model={data['model']} judge={data['judge_model']} runs={data['runs_per_case']} "
             f"cases={len({r['case'] for r in data['runs']})} cost=${data['cost']:.2f}", "",
             "| Tiêu chí | Đạt | Ngưỡng | Kết quả |", "|---|---|---|---|"]
    met = 0
    for cid in sorted(agg, key=sort_key):
        p, t, crit = agg[cid]
        ok = meets(p, t, crit)
        met += ok
        lines.append(f"| {cid} | {p}/{t} | {'100%' if crit else '≥67%'} | {'✅' if ok else '❌'} |")
    checks = [c for r in data["runs"] for c in r["checks"]]
    lines += ["", f"**Tiêu chí đạt ngưỡng: {met}/{len(agg)}** · "
                  f"Lượt chấm đạt: {sum(c['pass'] for c in checks)}/{len(checks)} "
                  f"({100 * sum(c['pass'] for c in checks) / max(1, len(checks)):.0f}%)", "",
              "## Lượt chấm không đạt", ""]
    for r in data["runs"]:
        for c in r["checks"]:
            if not c["pass"]:
                lines.append(f"- `{r['case']}`#{r['run']} {c['id']} (turn {c['turn'] or 'last'}): {c['evidence']}")
    return "\n".join(lines)


def compare(a, b):
    sa, sb = summarize(a), summarize(b)
    lines = [f"| Tiêu chí | {a['label']} | {b['label']} |", "|---|---|---|"]
    tot = {a["label"]: 0, b["label"]: 0}
    for cid in sorted(set(sa) | set(sb), key=sort_key):
        cells = []
        for d, s in ((a, sa), (b, sb)):
            if cid in s:
                p, t, crit = s[cid]
                ok = meets(p, t, crit)
                tot[d["label"]] += ok
                cells.append(f"{p}/{t} {'✅' if ok else '❌'}")
            else:
                cells.append("—")
        lines.append(f"| {cid} | {cells[0]} | {cells[1]} |")
    lines.append(f"| **Đạt ngưỡng** | **{tot[a['label']]}/{len(sa)}** | **{tot[b['label']]}/{len(sb)}** |")
    return "\n".join(lines)


def merge(base, patch):
    """Replace base's runs of every case that patch re-ran (e.g. after a criterion changed)."""
    redone = {r["case"] for r in patch["runs"]}
    runs = [r for r in base["runs"] if r["case"] not in redone] + patch["runs"]
    runs.sort(key=lambda r: (r["case"], r["run"]))
    note = f"{base.get('note', '')} re-ran {sorted(redone)} on {patch['date']}".strip()
    return dict(base, runs=runs, cost=base["cost"] + patch["cost"], note=note)


def sample(data, n, seed):
    """Random judge verdicts with the reply they graded, for checking the judge by hand."""
    import random
    cases = {c["id"]: c for c in load_cases(None)}
    items = []
    for r in data["runs"]:
        specs = [c for c in cases[r["case"]]["checks"] if c["type"] == "judge"]
        verdicts = [c for c in r["checks"] if c["type"] == "judge"]
        items += [(r, s, v) for s, v in zip(specs, verdicts)]
    random.seed(seed)
    out = []
    for i, (r, s, v) in enumerate(random.sample(items, min(n, len(items))), 1):
        t = s.get("turn", len(r["replies"]))
        out += [f"## S{i} · {r['case']}#{r['run']} · {s['id']} · turn {t} · giám khảo: {'✅' if v['pass'] else '❌'}",
                f"**Tiêu chí:** {s['question']}", "",
                f"**Người học:** {cases[r['case']]['turns'][t - 1]}", "",
                "**Tutor:**", r["replies"][t - 1] if "file" not in s else f"(chấm trên file {s['file']})", "",
                f"**Lý do của giám khảo:** {v['evidence']}", "", "**Người chấm 2:** ✅ / ❌", ""]
    return "\n".join(out)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--runs", type=int, default=3)
    r.add_argument("--skills", default=str(REPO / "skills"))
    r.add_argument("--label", default="current")
    r.add_argument("--model", default="sonnet")
    r.add_argument("--judge-model", default="sonnet")
    r.add_argument("--case", nargs="*", help="only cases whose id contains one of these")
    r.add_argument("--workers", type=int, default=6)
    sub.add_parser("report").add_argument("file")
    m = sub.add_parser("merge")
    m.add_argument("base")
    m.add_argument("patch")
    m.add_argument("out")
    s = sub.add_parser("sample")
    s.add_argument("file")
    s.add_argument("--n", type=int, default=20)
    s.add_argument("--seed", type=int, default=7)
    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")
    a = p.parse_args()

    if a.cmd == "report":
        print(report(json.loads(pathlib.Path(a.file).read_text(encoding="utf-8"))))
        return
    if a.cmd == "merge":
        load = lambda f: json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        data = merge(load(a.base), load(a.patch))
        out = pathlib.Path(a.out)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        out.with_suffix(".md").write_text(report(data), encoding="utf-8")
        print(f"Saved {out} ({data['note']})")
        return
    if a.cmd == "sample":
        print(sample(json.loads(pathlib.Path(a.file).read_text(encoding="utf-8")), a.n, a.seed))
        return
    if a.cmd == "compare":
        load = lambda f: json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        print(compare(load(a.a), load(a.b)))
        return

    cases = load_cases(a.case)
    jobs = [(case, k) for case in cases for k in range(1, a.runs + 1)]
    print(f"{len(cases)} cases × {a.runs} runs = {len(jobs)} conversations", flush=True)
    runs = []
    with cf.ThreadPoolExecutor(a.workers) as pool:
        futs = {pool.submit(run_one, case, k, pathlib.Path(a.skills), a.model, a.judge_model): (case["id"], k)
                for case, k in jobs}
        for f in cf.as_completed(futs):
            res = f.result()
            runs.append(res)
            bad = [c["id"] for c in res["checks"] if not c["pass"]]
            print(f"[{len(runs)}/{len(jobs)}] {res['case']}#{res['run']}: "
                  f"{'ok' if not bad else 'fail ' + ','.join(bad)}", flush=True)
    runs.sort(key=lambda r: (r["case"], r["run"]))
    data = {"label": a.label, "date": dt.datetime.now().isoformat(timespec="minutes"), "model": a.model,
            "judge_model": a.judge_model, "runs_per_case": a.runs, "skills": a.skills,
            "cost": sum(r["cost"] for r in runs), "runs": runs}
    out = ROOT / "results" / f"{dt.datetime.now():%Y%m%d-%H%M}-{a.label}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    md = report(data)
    out.with_suffix(".md").write_text(md, encoding="utf-8")
    print(md)
    print(f"\nSaved {out}")


if __name__ == "__main__":
    main()
