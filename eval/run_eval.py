"""Score the agent against the eval set.

Three things are scored separately, because they fail separately:
  facts   - did the answer contain what the handbook actually says
  sources - did it cite the document the answer came from
  tool    - did it take the right action, or correctly take none

Tool use is read from the n8n execution, not from the answer text. An agent that
says "I have raised a ticket" without calling the tool must score zero for that
question, and only the execution record can tell the difference.

Run: python eval/run_eval.py [--limit N]
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from matching import missing_groups, normalize  # noqa: E402

load_dotenv(ROOT / ".env")
N8N = os.environ.get("N8N_API_URL", "").rstrip("/")
KEY = os.environ.get("N8N_API_KEY", "")
ASK = N8N + "/webhook/kb-agent"
INGEST = N8N + "/webhook/kb-ingest"
THROTTLE = float(os.environ.get("EVAL_THROTTLE", "3"))
TOOLS = ("create_ticket", "book_slot", "escalate_to_human")


def post(url, payload, timeout=240):
    req = urllib.request.Request(
        url, method="POST", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read() or b"{}")


def execution_tools(execution_id):
    """Which action tools actually ran. None of them is a legitimate outcome."""
    req = urllib.request.Request(
        "{}/api/v1/executions/{}?includeData=true".format(N8N, execution_id),
        headers={"X-N8N-API-KEY": KEY, "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return None, "execution {} unreadable ({})".format(execution_id, e.code)
    run = data.get("data", {}).get("resultData", {}).get("runData", {})
    used = [t for t in TOOLS if t in run]
    searched = "search_handbook" in run
    return {"tools": used, "searched": searched}, None


def cited_sources(answer):
    """Documents named on the trailing 'Sources:' line."""
    line = None
    for raw in answer.splitlines():
        if raw.strip().lower().startswith("sources:"):
            line = raw.split(":", 1)[1]
    if line is None:
        return []
    if normalize(line) in ("none", "n/a", "-", ""):
        return []
    return [s.strip(" .`*") for s in re.split(r"[,;]| and ", line) if s.strip(" .`*")]


def score_one(q, answer, run):
    e = q["expect"]
    missing = missing_groups(e["must_include"], answer)
    facts_ok = not missing

    cites = cited_sources(answer)
    if e["sources"]:
        # Every expected document must be cited. Extra citations are not punished:
        # an answer can legitimately draw on more than the question anticipated.
        norm = [normalize(c) for c in cites]
        sources_ok = all(any(normalize(exp) in c for c in norm) for exp in e["sources"])
    else:
        sources_ok = not cites  # a refusal must not invent a citation

    used = run["tools"] if run else []
    if e["tool"]:
        tool_ok = used == [e["tool"]]
    else:
        tool_ok = used == []

    return {
        "facts": facts_ok, "sources": sources_ok, "tool": tool_ok,
        "missing": missing, "cited": cites, "used_tools": used,
        "searched": run["searched"] if run else False,
    }


def main():
    if not N8N or not KEY:
        sys.exit("N8N_API_URL / N8N_API_KEY missing from .env")
    questions = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    if "--limit" in sys.argv:
        questions = questions[:int(sys.argv[sys.argv.index("--limit") + 1])]

    print("re-indexing the handbook ...")
    post(INGEST, {}, timeout=300)

    rows, failures = [], []
    for i, q in enumerate(questions, 1):
        if i > 1:
            time.sleep(THROTTLE)
        started = time.time()
        try:
            res = post(ASK, {"question": q["question"]})
        except Exception as ex:
            print("  {:4} ERROR {}".format(q["id"], str(ex)[:80]))
            rows.append({"id": q["id"], "category": q["category"],
                         "facts": False, "sources": False, "tool": False})
            continue
        answer = res.get("answer", "")
        run, err = execution_tools(res.get("execution_id"))
        s = score_one(q, answer, run)
        s.update(id=q["id"], category=q["category"], seconds=round(time.time() - started, 1))
        rows.append(s)

        marks = "".join(("+" if s[k] else "-") for k in ("facts", "sources", "tool"))
        print("  {:4} {:14} {}  {:5.1f}s  {}".format(
            q["id"], q["category"], marks, s["seconds"],
            ",".join(s["used_tools"]) or "-"))
        if not all(s[k] for k in ("facts", "sources", "tool")):
            failures.append((q, answer, s))

    n = len(rows)
    print("\n{:<24}{:>10}".format("DIMENSION", "PASS"))
    print("-" * 34)
    for k in ("facts", "sources", "tool"):
        c = sum(1 for r in rows if r[k])
        print("{:<24}{:>6}/{:<3} {:.0%}".format(k, c, n, c / n))
    perfect = sum(1 for r in rows if all(r[k] for k in ("facts", "sources", "tool")))
    print("{:<24}{:>6}/{:<3} {:.0%}".format("all three", perfect, n, perfect / n))

    print("\n{:<16}{:>8}".format("CATEGORY", "PERFECT"))
    print("-" * 26)
    by_cat = Counter(r["category"] for r in rows)
    ok_cat = Counter(r["category"] for r in rows
                     if all(r[k] for k in ("facts", "sources", "tool")))
    for c in sorted(by_cat):
        print("{:<16}{:>4}/{:<3}".format(c, ok_cat[c], by_cat[c]))

    if failures:
        print("\n" + "=" * 60)
        print("{} QUESTION(S) NOT FULLY CORRECT".format(len(failures)))
        for q, answer, s in failures:
            bad = [k for k in ("facts", "sources", "tool") if not s[k]]
            print("\n{} [{}] failed: {}".format(q["id"], q["category"], ", ".join(bad)))
            print("  Q: {}".format(q["question"]))
            if not s["facts"]:
                print("  missing: {}".format(s["missing"]))
            if not s["sources"]:
                print("  cited {}, expected {}".format(s["cited"], q["expect"]["sources"]))
            if not s["tool"]:
                print("  called {}, expected {}".format(
                    s["used_tools"] or "nothing", q["expect"]["tool"] or "nothing"))
            print("  A: {}".format(answer.replace("\n", " ")[:220]))

    (HERE / "results.json").write_text(json.dumps(rows, indent=2))
    print("\nper-question results written to eval/results.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
