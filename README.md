# RAG Ops Agent — n8n

An internal IT and Operations assistant built as a single n8n workflow. It answers
staff questions from a company handbook, cites the document every answer came from,
declines when the handbook does not cover the question, and calls tools when the
person needs something done rather than just told.

It ships with a **25-question evaluation set** that scores three things separately —
facts, citations, and tool choice — and reads tool use from the n8n execution record
rather than from what the agent claims it did.

**Everything here is synthetic.** The handbook is invented. No client data was used.

---

## Results

25 questions. Model: `gemini-3.1-flash-lite`. Reproduce with `python eval/run_eval.py`.

| Dimension | Result |
|---|---|
| Facts correct | **25/25 = 100%** |
| Sources cited correctly | **22/25 = 88%** |
| Tool choice correct | **24/25 = 96%** |
| **All three at once** | **21/25 = 84%** |

| Category | Perfect |
|---|---|
| Plain retrieval | 10/10 |
| Confusable documents ("traps") | 3/3 |
| Declining what isn't covered | 4/4 |
| Booking a slot | 2/2 |
| Escalating a security incident | 1/2 |
| Raising a ticket | 1/2 |
| Answers spanning two documents | 0/2 |

## How it got there

Five evaluation runs. The interesting part is run 2, which went backwards.

| Run | Facts | Sources | Tool | All three | What changed |
|---|---|---|---|---|---|
| 1 | 72% | 72% | 80% | **52%** | baseline |
| 2 | 84% | 60% | 88% | **52%** | fixed eval bugs; told the agent to act, not ask |
| 3 | 88% | 84% | 88% | **64%** | made search unconditional; fixed citation format |
| 4 | 92% | 88% | 92% | **80%** | topK 4 → 8; separated requests from questions |
| 5 | 100% | 88% | 96% | **84%** | action must not replace the answer; more retries |

### Run 1 tested the eval as much as the agent

Five of the twelve first-run failures were the evaluation's fault, not the agent's.

Three "failures" were the agent correctly declining — *"the handbook does not cover
annual leave entitlements"* — scored wrong because the pattern list contained
`not covered` but not `does not cover`.

Two more expected no tool call on questions where the handbook explicitly demands
one. `06-onboarding-and-offboarding` says, in as many words, that a former
contractor with working access is *"a security incident, not a ticket"*. The agent
escalated. The eval called that wrong. The eval was wrong.

Both expectations were corrected against the source documents, and `eval/check_questions.py`
now validates every expected answer against the handbook before a run starts.
Expectations were changed **once**, with a documented reason in each question's
`note`. They were not touched again in runs 3 to 5, because adjusting expectations
after seeing scores stops measuring the agent and starts flattering it.

### Run 2: the over-correction

Telling the agent to act decisively made it stop searching. Measured, not guessed:
**8 of 25 answers skipped the retrieval tool entirely, and 7 of those 8 were the
questions where it called an action tool.** Deciding to act had become a reason to
skip looking things up — so citations collapsed from 72% to 60%, and only 1 of 8
action answers cited anything at all.

The fix was to make search unconditional and put it first in the prompt, above
everything about acting. Citations recovered to 84% in the next run.

This is the single most useful thing in this repository. Without an eval, run 2
looks like an improvement: facts up, tool choice up, and the one dimension that
regressed is invisible.

### Run 4: retrieval, not prompting

Three failures had the agent claiming the handbook did not cover BYOD, working
abroad, or the home-office stipend — all of which it does cover. The stipend answer
gave it away: the agent quoted the sentence *"the ongoing and internet amounts are
paid automatically"* from the right document, but could not state the amounts.
That sentence and the table holding `$45` and `$30` had landed in **different
chunks**, and `topK: 4` retrieved one without the other.

Raising `topK` to 8 — a third of a 24-chunk handbook — fixed all four. A larger
handbook would need table-aware chunking instead; this is the cheap correct answer
at this size, not the general one.

## What is still wrong

Four questions still fail, and the reasons are known rather than mysterious.

**Two-document citations (q14, q15).** When one document defines the situation and
another says what to do, the agent cites the first and drops the second. The
instruction to list both is explicit in the prompt and is not followed. This looks
like an instruction-following ceiling on `flash-lite`; a stronger model is the
obvious thing to test, and this repository deliberately reports one model's honest
number rather than shopping for a better one.

**Approval gating (q21).** Asked for a second monitor, the agent replies that it
needs the manager's written approval first, instead of raising the ticket and
noting the approval still to come. The prompt says to do the latter.

**q25** cited `08-data-classification-and-retention` for a misdirected customer
list. Defensible — that document does govern customer data — but the escalation
came from `05-security-incident-response`, and that is what should be cited.
This one moves between runs, which makes it variance rather than a fixed defect.

**Reliability.** Roughly 1 execution in 30 fails on a transient
`Service unavailable` from the model, which the user experiences as no answer at
all. Retries are set to 5 attempts at 5-second intervals, which reduced it from
~7% but has not eliminated it on the free tier.

## Architecture

```
POST /webhook/kb-ingest ─> fetch 8 docs from GitHub ─> split ─> embed ─> vector store
                                                        (source name kept per chunk)

POST /webhook/kb-agent  ─> AI Agent ─┬─ search_handbook   (retrieval + citations)
                                     ├─ create_ticket
                                     ├─ book_slot
                                     └─ escalate_to_human
```

Ingestion and the agent are **one workflow**, and that is not a stylistic choice.
n8n's in-memory vector store is scoped per workflow: data written by one workflow is
invisible to another, even with the same memory key. Splitting them produced an
agent whose every search returned empty. Diagnosis was four experiments:

| Test | Result |
|---|---|
| Did ingestion run? | 8 documents, 24 chunks, success |
| Did the agent call the tool? | 4 times, all empty |
| Insert and read in one execution | works |
| Insert and read in separate executions, same workflow | works |
| Insert and read in different workflows | **empty** |

One workflow also means a client imports one file and it runs — no Pinecone
account, no Qdrant container, no external vector database at all. That holds for a
handbook this size. Past a few hundred documents, move to a real vector store.

### Why the agent's tool use is read from the execution record

An agent will happily write *"I have raised a ticket for you"* without having called
anything. Run 1 produced exactly that. Scoring tool use from the answer text would
have recorded it as a pass. `eval/run_eval.py` instead fetches the n8n execution and
checks which tool nodes actually ran.

## Running it

```bash
pip install -r requirements.txt
```

Put your n8n URL and API key in `.env` (see `.env.example`), add a
**Google Gemini(PaLM) Api** credential named `Gemini case2` in n8n, then:

```bash
python deploy.py                 # push workflows/kb-agent.json and activate it
python eval/check_questions.py   # validate the eval set against the handbook
python eval/run_eval.py          # index, ask 25 questions, score
```

Ask it something directly:

```bash
curl -X POST "$N8N_API_URL/webhook/kb-agent" -H "Content-Type: application/json" \
  -d '{"question":"I clicked a link in an email and typed my password."}'
```

## Files

| File | |
|---|---|
| `workflows/kb-agent.json` | The whole system. Import into any n8n. |
| `kb/*.md` | Synthetic handbook, 8 documents |
| `eval/questions.json` | 25 questions with expected facts, sources and tool |
| `eval/check_questions.py` | Validates expectations against the handbook |
| `eval/run_eval.py` | Runs and scores; reads tool use from executions |
| `eval/matching.py` | Text matching shared by checker and scorer |
| `deploy.py` | Pushes workflow JSON to a running n8n |

`eval/matching.py` exists because the checker and the scorer must agree. If the
checker accepts a phrase as present in a document but the scorer would not accept
it in an answer, every score is quietly wrong. It also handles two things naive
substring matching gets wrong: markdown wrapping a phrase across a line break, and
table pipes gluing unrelated cells into a false match.
