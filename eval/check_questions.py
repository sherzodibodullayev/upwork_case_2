"""Validate the eval set against the knowledge base before it is ever used.

An eval question whose expected answer is not actually in the documents will fail
the agent forever, and the failure looks like a model problem. Catch it here.

Run: python eval/check_questions.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from matching import missing_groups  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "kb"
QUESTIONS = ROOT / "eval" / "questions.json"


def load():
    docs = {p.stem: p.read_text(encoding="utf-8").lower() for p in KB.glob("*.md")}
    questions = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    return docs, questions


def check():
    docs, questions = load()
    problems = []
    ids = Counter(q["id"] for q in questions)

    for dup, n in ids.items():
        if n > 1:
            problems.append("{}: duplicate id ({} times)".format(dup, n))

    for q in questions:
        e = q["expect"]

        for src in e["sources"]:
            if src not in docs:
                problems.append("{}: cites missing document {!r}".format(q["id"], src))

        if e["tool"] not in (None, "create_ticket", "book_slot", "escalate_to_human"):
            problems.append("{}: unknown tool {!r}".format(q["id"], e["tool"]))

        # Refusal questions assert how the agent should decline, which is a property
        # of the answer, not of the documents. Only check the grounded ones.
        if q["category"] == "refusal":
            if e["sources"] and q["id"] != "q16":
                problems.append("{}: a refusal should not cite a source".format(q["id"]))
            continue

        if not e["sources"]:
            problems.append("{}: non-refusal question cites no source".format(q["id"]))
            continue

        text = "\n".join(docs[s] for s in e["sources"])
        for group in missing_groups(e["must_include"], text):
            problems.append("{}: none of {} appear in {}".format(
                q["id"], group, ", ".join(e["sources"])))

    print("{} questions across {} documents".format(len(questions), len(docs)))
    print(dict(Counter(q["category"] for q in questions)))
    tools = Counter(q["expect"]["tool"] or "none" for q in questions)
    print("tools:", dict(tools))

    unused = sorted(set(docs) - {s for q in questions for s in q["expect"]["sources"]})
    if unused:
        print("\nnot exercised by any question:", unused)

    if problems:
        print("\n{} PROBLEM(S):".format(len(problems)))
        for p in problems:
            print("  -", p)
        return 1
    print("\nevery expected answer is present in the cited documents")
    return 0


if __name__ == "__main__":
    sys.exit(check())
