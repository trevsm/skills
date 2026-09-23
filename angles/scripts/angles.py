#!/usr/bin/env python3
"""Whiteboard for the angles harness. Python 3 standard library only.

A run is a graph of questions. A framer pins down terms and lays out the graph.
Pieces are settled bottom-up: a piece runs once everything it depends on is
settled, and it can send a weak dependency back, ask for a missing one, or say
its own question is framed wrong. A matcher links new requests to pieces that
already exist, so a shared dependency is settled once. A writer turns the
settled graph into the answer, a challenger attacks it, and a reviser fixes it.

Agents write their own replies to returns/<id>.md. The planner only runs the
next command, launches what it prints, and ingests. Every command checks the
ledger, applies the budget, writes the ledger atomically, and prints Next.
"""

import argparse
import datetime as dt
import json
import os
import re
import shutil
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
AGREEMENT = "Agreement among nodes is not evidence."
DEFAULT_CHEAP = "composer-2.5-fast"
DEFAULT_STRONG = "claude-opus-5-5-high"
BASE_COST = {"composer-2.5-fast": 0.25, "claude-opus-5-5-high": 0.40}
UNKNOWN_COST = 0.40
ROLE_WEIGHT = {
    "framer": 1.5,
    "leaf": 1.0,
    "integrator": 1.0,
    "matcher": 0.5,
    "writer": 1.5,
    "challenger": 1.0,
    "reviser": 1.0,
}
STRONG_ROLES = ("framer", "integrator", "matcher", "writer", "challenger", "reviser")
ENDGAME = (("W1", "writer"), ("X1", "challenger"), ("W2", "reviser"))
DEFAULT_BUDGET = 8.0
DEFAULT_MAX_NODES = 24
DEFAULT_MAX_DEPTH = 5
MIN_FRAMED, MAX_FRAMED = 3, 14
MAX_PARALLEL = 6
MAX_FAILURES = 2
MAX_DISPATCHES = 4
MAX_REOPENS = 1
MAX_REFRAMES = 1
KINDS = ("fact", "judgment")
CONFIDENCE = ("low", "medium", "high")
SEVERITY = ("breaks", "weakens", "ok")
PHASES = ("framing", "working", "writing", "challenging", "revising", "finishing", "done")
SETTLED = ("resolved", "failed")
ANSWER_REQUIRED_HEADINGS = ("## Assumptions", "## What would change this")
ANSWER_BANNED = (
    (r"\bQ-\d+\b", "piece ids"),
    (r"\b(F1|M\d+|W[12]|X1)\b", "agent ids"),
    (r"(?im)^#+\s*(claim map|graph|challenge|run|audit|terms used)\b", "an audit heading"),
    (r"(?i)\b(the framer|the matcher|integrator|the challenger|the reviser|ledger|notes file|whiteboard)\b", "harness vocabulary"),
    (r"(?i)\bangles\b", "the harness name"),
    (r"(?i)\b(this|the) run\b", "talk about the run"),
)


class HarnessError(Exception):
    pass


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def text_of(value, limit):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()[:limit]


def short(value, limit=220):
    s = text_of(value, 100000)
    if len(s) <= limit:
        return s
    cut = s[: limit - 1]
    if " " in cut[limit // 2 :]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,;:") + "…"


def run_path(run):
    return Path(run).expanduser().resolve()


def ledger_file(run):
    return run_path(run) / "ledger.json"


def load(run):
    path = ledger_file(run)
    if not path.exists():
        raise HarnessError(f"no ledger at {path}; run init first")
    return json.loads(path.read_text())


def save(run, led):
    path = ledger_file(run)
    tmp = path.with_name("ledger.json.tmp")
    tmp.write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def read_file(path):
    p = Path(path).expanduser()
    if not p.exists():
        raise HarnessError(f"missing file {p}")
    return p.read_text()


def parse_reply(text):
    """Split a reply into its JSON header and free-prose body."""
    text = text.lstrip("\ufeff").strip()
    fence = re.match(r"```(?:json)?\s*\n(.*?)\n```", text, re.S)
    if fence:
        raw, body = fence.group(1), text[fence.end() :]
    else:
        start = text.find("{")
        if start == -1:
            raise HarnessError("reply has no JSON header")
        try:
            _, end = json.JSONDecoder().raw_decode(text[start:])
        except json.JSONDecodeError as e:
            raise HarnessError(f"reply header is not valid JSON: {e}")
        raw, body = text[start : start + end], text[start + end :]
    try:
        header = json.loads(raw)
    except json.JSONDecodeError as e:
        raise HarnessError(f"reply header is not valid JSON: {e}")
    if not isinstance(header, dict):
        raise HarnessError("reply header must be a JSON object")
    return header, body.strip()


def cost_of(led, role, kind=None):
    model = model_for(led, role, kind)
    return round(BASE_COST.get(model, UNKNOWN_COST) * ROLE_WEIGHT[role], 3)


def model_for(led, role, kind=None):
    if role == "leaf" and kind != "judgment":
        return led["models"]["cheap"]
    if role in STRONG_ROLES or role == "leaf":
        return led["models"]["strong"]
    return led["models"]["cheap"]


def endgame_left(led):
    return sum(cost_of(led, role) for jid, role in ENDGAME if jid not in led["jobs"] and jid not in led["flight"])


def available(led):
    return led["budget"]["limit"] - led["budget"]["spent"] - led["budget"]["reserved"] - endgame_left(led)


def node(led, nid):
    if nid not in led["nodes"]:
        raise HarnessError(f"unknown piece {nid}")
    return led["nodes"][nid]


def new_node(led, text, kind, why, parent, depth):
    led["counter"]["node"] += 1
    nid = f"Q-{led['counter']['node']}"
    led["nodes"][nid] = {
        "id": nid,
        "text": text,
        "kind": kind if kind in KINDS else "fact",
        "why": why,
        "depends_on": [],
        "parents": [parent] if parent else [],
        "depth": depth,
        "status": "pending",
        "dispatches": 0,
        "failures": 0,
        "reopens": 0,
        "refreshes": 0,
        "reframes": 0,
        "old_texts": [],
        "objection": None,
        "partials": [],
        "assume": [],
        "force": False,
        "result": None,
        "error": None,
        "stale_parents": [],
    }
    return nid


def reaches(led, start, target):
    stack, seen = [start], set()
    while stack:
        cur = stack.pop()
        if cur == target:
            return True
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(led["nodes"][cur]["depends_on"])
    return False


def recompute_depths(led):
    root = led["root"]
    if not root:
        return
    depth = {root: 1}
    order = [root]
    while order:
        cur = order.pop(0)
        for d in led["nodes"][cur]["depends_on"]:
            if depth.get(d, 0) < depth[cur] + 1:
                depth[d] = depth[cur] + 1
                order.append(d)
    for nid, n in led["nodes"].items():
        n["depth"] = depth.get(nid, n["depth"])


def link(led, parent_id, child_id):
    """Add parent -> child. Returns an error string or None."""
    parent, child = node(led, parent_id), node(led, child_id)
    if child_id == parent_id or reaches(led, child_id, parent_id):
        return "cycle"
    if child_id not in parent["depends_on"]:
        parent["depends_on"].append(child_id)
    if parent_id not in child["parents"]:
        child["parents"].append(parent_id)
    recompute_depths(led)
    return None


def pending_needs_from(led, nid):
    return [n for n in led["needs"] if n["from"] == nid]


def is_ready(led, n):
    if n["status"] != "pending" or pending_needs_from(led, n["id"]):
        return False
    return all(led["nodes"][d]["status"] in SETTLED for d in n["depends_on"])


def ready_nodes(led):
    ready = [n for n in led["nodes"].values() if is_ready(led, n)]
    return sorted(ready, key=lambda n: (-n["depth"], n["kind"] != "fact", int(n["id"][2:])))


def in_flight(led):
    return dict(led["flight"])


def role_of_node(n):
    return "integrator" if n["depends_on"] else "leaf"


def remaining_graph_cost(led):
    total = 0.0
    for n in led["nodes"].values():
        if n["status"] == "pending":
            total += cost_of(led, role_of_node(n), n["kind"])
    if led["needs"]:
        total += cost_of(led, "matcher")
    return total


def log(led, event):
    led["log"].append({"at": now(), "event": event})


def launch_line(led, run, aid):
    run = run_path(run)
    return (
        f"You are an angles agent. Read {run}/prompts/{aid}.md with your Read tool and follow it exactly. "
        f"Write your reply to {run}/returns/{aid}.md as that file instructs, then reply with just the word done."
    )


def archive_return(run, aid, tag):
    run = run_path(run)
    src = run / "returns" / f"{aid}.md"
    if not src.exists():
        return None
    dst = run / "returns" / "archive" / f"{aid}-{tag}.md"
    dst.parent.mkdir(exist_ok=True)
    shutil.move(str(src), str(dst))
    return str(dst)


def dispatch(led, run, aid, role, kind=None, prompt=""):
    run = run_path(run)
    archive_return(run, aid, f"stale-{len(led['log'])}")
    cost = cost_of(led, role, kind)
    model = model_for(led, role, kind)
    (run / "prompts" / f"{aid}.md").write_text(prompt)
    led["flight"][aid] = {"role": role, "model": model, "cost": cost, "at": now()}
    led["budget"]["reserved"] += cost
    return model, cost


# ---------------------------------------------------------------- prompts


def framing_block(led):
    f = led["framing"] or {}
    terms = "\n".join(
        f"- {t['term']}: {t['meaning']}" + (f" (flag: {t['flag']})" if t.get("flag") else "")
        for t in f.get("terms", [])
    )
    constraints = "\n".join(f"- {c}" for c in f.get("constraints", [])) or "- none stated"
    assumptions = "\n".join(f"- {a}" for a in f.get("assumptions", [])) or "- none found"
    return (
        f"The whole question:\n{led['question']}\n\n"
        f"The real question, as framed:\n{f.get('real_question', led['question'])}\n\n"
        f"Terms, as this work uses them:\n{terms or '- none flagged'}\n\n"
        f"Hidden assumptions in the framing:\n{assumptions}\n\n"
        f"Hard constraints. Anything you conclude must respect every one:\n{constraints}\n\n"
        f"What the answer probably turns on:\n{f.get('crux', 'not identified')}\n"
    )


REPLY_RULE = (
    "Write your reply to {path}. It starts with a JSON header in a ```json fence, followed by free prose. "
    "Then reply with just the word done."
)


def framer_prompt(led, run):
    path = run_path(run) / "returns" / "F1.md"
    return f"""You are the framer. You go first. Your job is to make sure the work answers the right question, in the right terms, in the right order. You do not answer the question.

Question:
{led['question']}

Do this:
1. Terms. For each load-bearing word or phrase in the question, say what it must mean for the question to make sense. Flag any term used loosely or wrongly, such as a category error (asking to replace one kind of thing with a different kind of thing that does a different job), and say what the question should mean instead.
2. Hidden assumptions. What does the framing take for granted that might be false?
3. The real question. Restate what actually needs answering or deciding, in one or two sentences. Keep every part of the question.
4. The crux. Your best guess at the single decision, fact, or disagreement the answer will turn on.
5. Hard constraints the question sets: deadlines, who is available, money or data that must not break.
6. The question graph. Break the real question into pieces. Each piece is a question someone could settle. A piece depends on another when it cannot be settled well until that one is.
   - The root is the real question. It depends on the pieces needed to answer it.
   - Settle terms and premises first. When a definition or a factual premise changes the answer to other pieces, make it a piece they depend on.
   - When two pieces need the same thing, make that thing one piece both depend on. Never duplicate it.
   - Leaves are small enough for one careful agent to settle in one pass.
   - Mark each piece kind "fact" (findable, checkable) or "judgment" (a weighing or decision). Use judgment sparingly for leaves.
   - Between {MIN_FRAMED} and {MAX_FRAMED} pieces including the root, at most {led['caps']['max_depth']} levels deep, no cycles.

You may read files, search, and fetch pages if the question needs grounding. Keep it brief. Do not launch agents.

{REPLY_RULE.format(path=path)} The header:
```json
{{"id": "F1", "status": "framed",
 "terms": [{{"term": "...", "meaning": "...", "flag": "empty, or what is wrong with how the question uses it"}}],
 "assumptions": ["..."],
 "real_question": "...",
 "crux": "...",
 "constraints": ["..."],
 "questions": [{{"key": "A", "text": "...", "kind": "fact", "depends_on": ["B", "C"], "why": "what this unlocks"}}],
 "root": "A"}}
```
"""


def dep_block(led, n):
    lines = []
    for d in n["depends_on"]:
        c = led["nodes"][d]
        r = c["result"] or {}
        if c["status"] == "resolved":
            lines.append(
                f"{d} [{r.get('confidence', '?')} confidence] {c['text']}\n"
                f"  Resolution: {r.get('resolution', '')}\n"
                f"  Rests on: {', '.join(r.get('rests_on') or []) or 'not stated'}\n"
                f"  Full reasoning: {r.get('body_path', 'none')}"
            )
        else:
            lines.append(f"{d} [could not be settled] {c['text']}\n  State the assumption you make in its place.")
    return "\n".join(lines)


def node_prompt(led, run, n):
    path = run_path(run) / "returns" / f"{n['id']}.md"
    role = role_of_node(n)
    parents = "\n".join(f"- {p}: {led['nodes'][p]['text']}" for p in n["parents"]) or "- none: this is the root"
    parts = [
        "You are one agent on a larger question. You own one piece of it. Other agents own the other pieces. "
        "When you settle yours, the pieces that depend on it build on your answer, so it has to hold.\n",
        framing_block(led),
        f"\nYour piece: {n['id']} ({n['kind']})\n{n['text']}\nWhy it matters: {n['why'] or 'not stated'}\n"
        f"Pieces that depend on yours:\n{parents}\n",
    ]
    if n["depends_on"]:
        parts.append(f"\nWhat your piece rests on:\n{dep_block(led, n)}\n")
    if n["objection"]:
        parts.append(
            f"\nYour earlier answer to this piece was sent back by {n['objection']['from']}: {n['objection']['reason']}. "
            f"Your earlier answer is in {n['objection']['previous']}. Address this directly.\n"
        )
    if n["partials"]:
        parts.append(f"\nYour earlier work on this piece, before you asked for help: {n['partials'][-1]}. Read it and continue from it.\n")
    if n["assume"]:
        items = "\n".join(f"- {a}" for a in n["assume"])
        parts.append(f"\nThese will not be settled for you. Proceed without them and state the assumption you make for each:\n{items}\n")
    if n["force"] or led["converge"]:
        parts.append("\nThe budget is closing. You must settle your piece now. Do not return blocked, reframe, or reject. State your assumptions instead.\n")
    parts.append(
        "\nHow to work: however you judge best. Read, search, fetch pages, reason, run read-only commands. "
        "Do not launch agents. If your piece is too big, or rests on something unsettled, return blocked and name what "
        "you need. It will be settled and you will be sent back here with the answer.\n"
    )
    if role == "integrator":
        parts.append(
            "\nYou are building on settled pieces. First check each one: does it actually answer what your piece needs, "
            "and does it hold up? If one does not, reject it with the reason and it goes back for another pass. You can "
            "do this once per piece. Then do the thinking this level needs: resolve the tensions between the pieces, "
            "weigh them, and decide. Do not just restate them.\n"
        )
    parts.append(
        "\nSettled means you could defend it to a skeptic who knows the domain. What it rests on is stated. Every "
        "number not given in the question says whether it is measured, sourced, an estimate (with a range and the "
        "assumption behind it), or an assumption. Uncertainty is explicit. If you cannot reach that bar without "
        "another piece settled first, you are blocked, not settled. If your piece is framed wrong, say so: return "
        "reframe with the better question.\n\n"
        f"{REPLY_RULE.format(path=path)} Put the substance in the prose: the argument, lists, tables, numbers. "
        "Pieces above you read the resolution first and your prose when they need it. The header:\n"
        "```json\n"
        f'{{"id": "{n["id"]}", "status": "resolved | blocked | reframe",\n'
        ' "resolution": "150 words or fewer: your answer to this piece as a standalone statement others can build on",\n'
        ' "confidence": "low | medium | high",\n'
        ' "rests_on": ["Q-5", "assumption: ..."],\n'
        ' "needs": [{"question": "a piece that must be settled first", "why": "..."}],\n'
        ' "reframe": {"text": "the better question", "why": "..."},\n'
        ' "reject": [{"id": "Q-5", "reason": "..."}]}\n'
        "```\n"
        "Fill needs only when blocked, reframe only when reframing, reject only when rejecting a dependency.\n"
    )
    return "".join(parts)


def matcher_prompt(led, run, jid, needs):
    path = run_path(run) / "returns" / f"{jid}.md"
    existing = "\n".join(f"{nid} [{n['status']}] {n['text']}" for nid, n in led["nodes"].items())
    reqs = "\n".join(f"{x['id']} from {x['from']}: {x['question']} (why: {x['why']})" for x in needs)
    return f"""You are the matcher. Pieces of a larger question have asked for other pieces to be settled first. For each request, decide whether it is the same question as a piece that already exists, even if worded differently, or a new piece.

Same means settling the existing piece would give the requester what it needs. Close but different is new. When two requests ask for the same new thing, make one new piece and point the other request at it with same_as.

The question being worked:
{led['question']}

Existing pieces:
{existing}

Requests:
{reqs}

Do not launch agents.

{REPLY_RULE.format(path=path)} The header has one entry per request:
```json
{{"id": "{jid}", "status": "matched",
 "links": [{{"need": "N1", "to": "Q-4"}},
           {{"need": "N2", "new": {{"text": "a crisp question", "kind": "fact"}}}},
           {{"need": "N3", "same_as": "N2"}}]}}
```
"""


def settled_block(led):
    lines = []
    for nid, n in sorted(led["nodes"].items(), key=lambda kv: (kv[1]["depth"], int(kv[0][2:]))):
        r = n["result"] or {}
        if n["status"] == "resolved":
            lines.append(
                f"{nid} (depth {n['depth']}, {r.get('confidence', '?')} confidence) {n['text']}\n"
                f"  Resolution: {r.get('resolution', '')}\n  Full reasoning: {r.get('body_path', '')}"
            )
        else:
            lines.append(f"{nid} (not settled: {n['status']}) {n['text']}")
    return "\n".join(lines)


ANSWER_RULES = """Answer rules:
- Lead with the decision or answer in one line. Then the plan or explanation. Then the reasoning a reader needs to trust it.
- Answer every part of the question as asked, directly.
- If a term in the question was used wrongly, say so plainly in one or two sentences, then answer the corrected question too.
- Say what the answer turns on and why.
- Carry the substance. Include the lists and tables the pieces built, in compact form. Never mention something ("six failure modes") without including it.
- Keep the hedges. Every number not given in the question has its basis inline, or is listed under "## Assumptions and estimates" with its range and the assumption behind it.
- Recompute every derived number, duration, and date yourself: sums, engineer-weeks from people and weeks, days between two events. They must add up.
- Put in each category only what belongs there. A reason not to act is not a reason to act.
- Name the riskiest thing you recommend and why it fits the constraints.
- Simplest version that works. Cut any step, gate, or role that would not change a decision.
- No bookkeeping. No piece ids, and no mention of agents, pieces, the process, or how the answer was produced.
- End with "## What would change this": the facts only the reader can check, and how each would change the answer.

Template:
# <the decision or answer in one line>
<body>
## Assumptions and estimates
<every estimate and assumption, with range and basis>
## What would change this
<facts the reader can check, and how each changes the answer>
"""


def writer_prompt(led, run, jid, draft_path, challenge=None, previous=None):
    path = run_path(run) / "returns" / f"{jid}.md"
    root = led["nodes"].get(led["root"], {})
    rr = (root.get("result") or {})
    parts = [
        "You write the final answer. Many agents settled the pieces of this question, from the bottom up. "
        "Your job is to turn what they settled into the answer a smart, busy reader acts on.\n\n",
        framing_block(led),
        f"\nThe root piece: {root.get('text', '')}\nIts resolution: {rr.get('resolution', 'not settled')}\n"
        f"Its full reasoning: {rr.get('body_path', 'none')}\n\n"
        f"Every piece, deepest last. Read the full reasoning of any piece you rely on:\n{settled_block(led)}\n\n",
    ]
    if challenge is not None:
        parts.append(
            f"You are revising. The current draft is {previous}. A challenger attacked it:\n{challenge}\n\n"
            "Fix every problem marked breaks or weakens, or keep the claim and say in the answer why it holds. "
            "Answer every question gap. Keep what the challenge did not touch.\n\n"
        )
    parts.append(ANSWER_RULES)
    parts.append(
        f"\nWrite the answer itself to {draft_path}, overwriting it. Then write your reply to {path}: a JSON header in a "
        "```json fence, followed by any notes. The claim map is for the audit, never the answer: each load-bearing "
        "claim in the answer and the pieces it comes from. Then reply with just the word done.\n"
        "```json\n"
        f'{{"id": "{jid}", "status": "written",\n'
        ' "claim_map": [{"claim": "...", "from": ["Q-2", "Q-5"]}],\n'
        ' "changes": [{"challenge": "only when revising: what the challenger said", "change": "what you did"}]}\n'
        "```\n"
    )
    return "".join(parts)


def challenger_prompt(led, run, draft_path):
    path = run_path(run) / "returns" / "X1.md"
    return f"""You are the challenger. There is a draft answer. Your job is to break it before anyone relies on it.

{framing_block(led)}
The draft is {draft_path}. Read it.

The settled pieces it was built from, with their full reasoning, so you can check the draft against them:
{settled_block(led)}

Run these checks yourself. Each one that finds a problem becomes a challenge.
a. Question check. Reread the question word for word. List every part it asks. Is each answered completely and directly? Put every part answered only partly, or not at all, in question_gaps.
b. Riskiest step. Name the single riskiest thing the draft recommends. Check it against every hard constraint. If a safer option meets the goal, that is a challenge.
c. Unsourced numbers. Every number not given in the question needs a basis, or a label as an estimate or starting default with its assumption.
d. Dangling references. The draft must contain whatever it refers to.
e. Consistency. Recompute every derived number, duration, and date: engineer-weeks from people and weeks, days between two events, totals. Check that each item sits in the right category or column. Check that the draft does not contradict itself or the pieces it was built from.
f. Load-bearing claims. Pick the two or three claims the answer most depends on and try hard to refute them. Read the relevant pieces' reasoning, search, or reason from first principles.

Do not launch agents. Severity ok means the claim survived a real attempt to break it; say what you tried.

{REPLY_RULE.format(path=path)} The header:
```json
{{"id": "X1", "status": "challenged",
 "question_gaps": ["a part of the question the draft does not fully answer"],
 "challenges": [{{"claim": "...", "problem": "...", "severity": "breaks | weakens | ok", "basis": "..."}}]}}
```
"""


# ---------------------------------------------------------------- ingest


def norm_list(value, limit=400):
    if not isinstance(value, list):
        return []
    return [text_of(v, limit) for v in value if text_of(v, 1)]


def ingest_framer(led, header, body_path):
    qs = header.get("questions")
    root_key = text_of(header.get("root"), 40)
    if not isinstance(qs, list) or not MIN_FRAMED <= len(qs) <= MAX_FRAMED:
        raise HarnessError(f"framer: questions must be a list of {MIN_FRAMED} to {MAX_FRAMED}")
    keys = {}
    for q in qs:
        if not isinstance(q, dict) or not text_of(q.get("key"), 1) or not text_of(q.get("text"), 1):
            raise HarnessError("framer: every question needs a key and text")
        keys[text_of(q["key"], 40)] = q
    if root_key not in keys:
        raise HarnessError(f"framer: root {root_key!r} is not one of the question keys")
    for q in qs:
        for d in q.get("depends_on") or []:
            if text_of(d, 40) not in keys:
                raise HarnessError(f"framer: {q['key']} depends on unknown key {d!r}")
    led["framing"] = {
        "terms": [
            {"term": text_of(t.get("term"), 120), "meaning": text_of(t.get("meaning"), 400), "flag": text_of(t.get("flag"), 400)}
            for t in header.get("terms") or []
            if isinstance(t, dict) and text_of(t.get("term"), 1)
        ],
        "assumptions": norm_list(header.get("assumptions")),
        "real_question": text_of(header.get("real_question"), 1200) or led["question"],
        "crux": text_of(header.get("crux"), 800),
        "constraints": norm_list(header.get("constraints")),
        "notes": body_path,
    }
    ids = {}
    for key, q in keys.items():
        ids[key] = new_node(led, text_of(q["text"], 800), text_of(q.get("kind"), 20).lower(), text_of(q.get("why"), 400), None, 1)
    led["root"] = ids[root_key]
    warnings = []
    for key, q in keys.items():
        for d in q.get("depends_on") or []:
            err = link(led, ids[key], ids[text_of(d, 40)])
            if err:
                warnings.append(f"framer edge {key}->{d} dropped: {err}")
    orphans = [nid for nid in ids.values() if nid != led["root"] and not led["nodes"][nid]["parents"]]
    for nid in orphans:
        link(led, led["root"], nid)
        warnings.append(f"{nid} had no parent; attached to the root")
    too_deep = [nid for nid, n in led["nodes"].items() if n["depth"] > led["caps"]["max_depth"]]
    if too_deep:
        warnings.append(f"deeper than max_depth: {', '.join(too_deep)}")
    led["phase"] = "working"
    return warnings


def add_need(led, nid, need):
    led["counter"]["need"] += 1
    led["needs"].append(
        {"id": f"N{led['counter']['need']}", "from": nid, "question": text_of(need.get("question"), 600), "why": text_of(need.get("why"), 300), "assigned": None}
    )


def ingest_node(led, nid, header, body_path):
    n = node(led, nid)
    status = text_of(header.get("status"), 20).lower()
    warnings = []
    rejects = [r for r in header.get("reject") or [] if isinstance(r, dict)]
    valid_rejects = []
    for r in rejects:
        rid = text_of(r.get("id"), 20)
        if rid not in n["depends_on"] or led["nodes"][rid]["status"] != "resolved":
            warnings.append(f"reject of {rid} ignored: not a settled dependency")
        elif led["nodes"][rid]["reopens"] >= MAX_REOPENS:
            warnings.append(f"reject of {rid} ignored: already sent back once")
        else:
            valid_rejects.append((rid, text_of(r.get("reason"), 600)))
    if valid_rejects and not led["converge"]:
        for rid, reason in valid_rejects:
            c = led["nodes"][rid]
            c["reopens"] += 1
            c["objection"] = {"from": nid, "reason": reason, "previous": (c["result"] or {}).get("body_path")}
            c["status"] = "pending"
            c["stale_parents"] = [p for p in c["parents"] if p != nid and led["nodes"][p]["status"] == "resolved"]
            c["result"] = None
            log(led, f"{nid} sent {rid} back: {short(reason, 160)}")
        n["partials"].append(body_path)
        n["status"] = "pending"
        return "sent a dependency back", warnings
    if status == "reframe" and not (n["force"] or led["converge"]):
        rf = header.get("reframe") if isinstance(header.get("reframe"), dict) else {}
        new_text = text_of(rf.get("text"), 800)
        if new_text and n["reframes"] < MAX_REFRAMES:
            n["reframes"] += 1
            n["old_texts"].append(n["text"])
            n["text"] = new_text
            n["partials"].append(body_path)
            n["status"] = "pending"
            log(led, f"{nid} reframed: {short(rf.get('why'), 160)}")
            return "reframed", warnings
        warnings.append("reframe refused; the piece must be settled as stated")
        n["force"] = True
        n["status"] = "pending"
        n["partials"].append(body_path)
        return "reframe refused", warnings
    if status == "blocked" and not (n["force"] or led["converge"]):
        needs = [x for x in header.get("needs") or [] if isinstance(x, dict) and text_of(x.get("question"), 1)]
        if needs and n["dispatches"] < MAX_DISPATCHES:
            for x in needs[:4]:
                add_need(led, nid, x)
            n["partials"].append(body_path)
            n["status"] = "pending"
            log(led, f"{nid} blocked on {len(needs[:4])} need(s)")
            return "blocked", warnings
        warnings.append("blocked with no needs, or too many passes; must settle next time")
        n["force"] = True
        n["partials"].append(body_path)
        n["status"] = "pending"
        return "forced to settle", warnings
    resolution = text_of(header.get("resolution"), 1500)
    if not resolution:
        raise HarnessError("resolution missing")
    if status not in ("resolved",):
        warnings.append(f"status {status!r} recorded as resolved")
    confidence = text_of(header.get("confidence"), 20).lower()
    if confidence not in CONFIDENCE:
        warnings.append(f"confidence {confidence!r} recorded as low")
        confidence = "low"
    n["result"] = {
        "resolution": resolution,
        "confidence": confidence,
        "rests_on": norm_list(header.get("rests_on"), 300),
        "body_path": body_path,
        "at": now(),
    }
    n["status"] = "resolved"
    n["objection"] = None
    refreshed = refresh_stale(led, n)
    if refreshed:
        warnings.append(f"sent back to recheck against the revision: {', '.join(refreshed)}")
    return "resolved", warnings


def refresh_stale(led, n):
    """A revised piece sends the pieces that already built on its old answer back once."""
    stale, n["stale_parents"] = n["stale_parents"], []
    if led["converge"]:
        return []
    refreshed = []
    for pid in stale:
        p = led["nodes"][pid]
        if p["status"] != "resolved" or p["refreshes"] >= MAX_REOPENS:
            continue
        p["refreshes"] += 1
        p["objection"] = {
            "from": n["id"],
            "reason": f"{n['id']}, which your answer builds on, was revised after you settled. Recheck your answer against its new resolution and change what no longer holds",
            "previous": (p["result"] or {}).get("body_path"),
        }
        p["stale_parents"] = [q for q in p["parents"] if led["nodes"][q]["status"] == "resolved"]
        p["status"] = "pending"
        p["result"] = None
        refreshed.append(pid)
        log(led, f"{pid} sent back to recheck after {n['id']} was revised")
    return refreshed


def ingest_matcher(led, jid, header):
    assigned = [x for x in led["needs"] if x["assigned"] == jid]
    by_id = {x["id"]: x for x in assigned}
    links = {text_of(l.get("need"), 20): l for l in header.get("links") or [] if isinstance(l, dict)}
    created, notes = {}, []

    def refuse(x, reason):
        led["nodes"][x["from"]]["assume"].append(f"{x['question']} ({reason})")
        notes.append(f"{x['id']} not linked: {reason}")

    def make_new(x, text, kind):
        if len(led["nodes"]) >= led["caps"]["max_nodes"]:
            refuse(x, "piece cap reached")
            return None
        depth = led["nodes"][x["from"]]["depth"] + 1
        if depth > led["caps"]["max_depth"]:
            refuse(x, "depth cap reached")
            return None
        nid = new_node(led, text, kind, x["why"], None, depth)
        err = link(led, x["from"], nid)
        if err:
            refuse(x, err)
            return None
        created[x["id"]] = nid
        notes.append(f"{x['id']} -> new {nid}")
        return nid

    later = []
    for x in assigned:
        l = links.get(x["id"], {})
        if text_of(l.get("to"), 20) in led["nodes"]:
            target = text_of(l["to"], 20)
            err = link(led, x["from"], target)
            if err:
                refuse(x, f"linking {target} would create a {err}; settle both together in your answer")
            else:
                notes.append(f"{x['id']} -> existing {target}")
        elif isinstance(l.get("new"), dict) and text_of(l["new"].get("text"), 1):
            make_new(x, text_of(l["new"]["text"], 800), text_of(l["new"].get("kind"), 20).lower())
        elif text_of(l.get("same_as"), 20) in by_id:
            later.append((x, text_of(l["same_as"], 20)))
        else:
            make_new(x, x["question"], "fact")
    for x, other in later:
        target = created.get(other)
        if target:
            err = link(led, x["from"], target)
            if err:
                refuse(x, err)
            else:
                notes.append(f"{x['id']} -> {target} (same as {other})")
        else:
            make_new(x, x["question"], "fact")
    led["needs"] = [x for x in led["needs"] if x["assigned"] != jid]
    led["links"].extend(notes)
    return notes


def ingest_challenger(led, header):
    challenges = []
    for c in header.get("challenges") or []:
        if not isinstance(c, dict) or not text_of(c.get("claim"), 1):
            continue
        sev = text_of(c.get("severity"), 20).lower()
        challenges.append(
            {
                "claim": text_of(c.get("claim"), 600),
                "problem": text_of(c.get("problem"), 900),
                "severity": sev if sev in SEVERITY else "weakens",
                "basis": text_of(c.get("basis"), 500),
            }
        )
    return {"question_gaps": norm_list(header.get("question_gaps")), "challenges": challenges}


def cmd_ingest(a):
    led = load(a.run)
    run = run_path(a.run)
    if not led["flight"]:
        raise HarnessError(f"nothing in flight. Next: {next_action(led, run)}")
    targets = [a.failed] if a.failed else list(led["flight"])
    report, missing = [], []
    for aid in targets:
        if aid not in led["flight"]:
            raise HarnessError(f"{aid} is not in flight")
        info = led["flight"][aid]
        ret = run / "returns" / f"{aid}.md"
        if not a.failed and not ret.exists():
            missing.append(aid)
            continue
        led["budget"]["reserved"] -= info["cost"]
        led["budget"]["spent"] += info["cost"]
        led["spend_log"].append({"id": aid, "role": info["role"], "model": info["model"], "cost": info["cost"]})
        del led["flight"][aid]
        warnings, outcome = [], ""
        try:
            if a.failed:
                raise HarnessError(f"task failed: {a.reason or 'no reason given'}")
            text = ret.read_text()
            tag = len(led["spend_log"])
            body_path = archive_return(run, aid, str(tag))
            header, _ = parse_reply(text)
            role = info["role"]
            if role == "framer":
                warnings = ingest_framer(led, header, body_path)
                outcome = f"framed: {len(led['nodes'])} pieces, root {led['root']}"
                led["jobs"]["F1"] = {"status": "done", "body": body_path}
            elif role in ("leaf", "integrator"):
                outcome, warnings = ingest_node(led, aid, header, body_path)
            elif role == "matcher":
                warnings = ingest_matcher(led, aid, header)
                outcome = "matched"
                led["jobs"][aid] = {"status": "done", "body": body_path}
            elif role == "writer":
                led["jobs"]["W1"] = {"status": "done", "body": body_path, "claim_map": header.get("claim_map") or []}
                led["phase"] = "challenging"
                outcome = "draft written"
            elif role == "challenger":
                led["jobs"]["X1"] = {"status": "done", "body": body_path, **ingest_challenger(led, header)}
                led["phase"] = "revising"
                outcome = "challenged"
            elif role == "reviser":
                led["jobs"]["W2"] = {
                    "status": "done",
                    "body": body_path,
                    "claim_map": header.get("claim_map") or [],
                    "changes": header.get("changes") or [],
                }
                led["phase"] = "finishing"
                outcome = "revised"
        except HarnessError as e:
            outcome = f"failed: {e}"
            fail(led, aid, info["role"], str(e))
        report.append((aid, outcome, warnings))
    save(a.run, led)
    for aid, outcome, warnings in report:
        print(f"{aid}: {outcome}")
        for w in warnings:
            print(f"  {w}")
    if missing:
        print(f"no reply file yet from: {', '.join(missing)}. Relaunch them, or run: python3 {SCRIPT} ingest {run} --failed <id> --reason \"...\"")
    print(budget_line(led))
    print(f"Next: {next_action(led, run)}")


def fail(led, aid, role, error):
    if role in ("leaf", "integrator"):
        n = led["nodes"][aid]
        n["failures"] += 1
        n["error"] = error
        n["status"] = "pending" if n["failures"] < MAX_FAILURES else "failed"
    else:
        job = led["jobs"].setdefault(aid, {"status": "pending", "failures": 0})
        job["failures"] = job.get("failures", 0) + 1
        job["error"] = error
        if job["failures"] >= MAX_FAILURES:
            job["status"] = "failed"
            if role == "matcher":
                for x in led["needs"]:
                    if x["assigned"] == aid:
                        x["assigned"] = None
            if role == "writer":
                led["phase"] = "challenging"
            if role == "challenger":
                led["phase"] = "revising"
            if role == "reviser":
                led["phase"] = "finishing"
        else:
            del led["jobs"][aid]
            if role == "matcher":
                for x in led["needs"]:
                    if x["assigned"] == aid:
                        x["assigned"] = None


# ---------------------------------------------------------------- next


def update_converge(led):
    if led["converge"]:
        return
    if available(led) < remaining_graph_cost(led) or len(led["nodes"]) >= led["caps"]["max_nodes"]:
        led["converge"] = True
        log(led, "converging: budget or piece cap reached; no new pieces, every piece must settle")
        for x in list(led["needs"]):
            if x["assigned"] is None:
                led["nodes"][x["from"]]["assume"].append(f"{x['question']} (not settled: budget closing)")
                led["needs"].remove(x)


def cmd_next(a):
    led = load(a.run)
    run = run_path(a.run)
    if led["flight"]:
        raise HarnessError(f"{', '.join(led['flight'])} still in flight. Ingest first. Next: {next_action(led, run)}")
    launches = []
    phase = led["phase"]
    if phase == "framing":
        if led["jobs"].get("F1", {}).get("status") == "failed":
            raise HarnessError(f"the framer failed twice: {led['jobs']['F1'].get('error')}. Fix the prompt or start over")
        launches.append(("F1",) + dispatch(led, run, "F1", "framer", prompt=framer_prompt(led, run)))
    elif phase == "working":
        launches = work_step(led, run)
    elif phase == "writing":
        draft = run / "answer-draft.md"
        launches.append(("W1",) + dispatch(led, run, "W1", "writer", prompt=writer_prompt(led, run, "W1", draft)))
    elif phase == "challenging":
        draft = run / "answer-draft.md"
        if not draft.exists():
            raise HarnessError(f"{draft} missing; the writer did not write the draft. Relaunch W1 or write it by hand.")
        launches.append(("X1",) + dispatch(led, run, "X1", "challenger", prompt=challenger_prompt(led, run, draft)))
    elif phase == "revising":
        draft = run / "answer-draft.md"
        prev = run / "drafts" / "answer-draft-1.md"
        prev.parent.mkdir(exist_ok=True)
        if draft.exists():
            shutil.copy(draft, prev)
        x = led["jobs"].get("X1", {})
        challenge = json.dumps({"question_gaps": x.get("question_gaps", []), "challenges": x.get("challenges", [])}, indent=1)
        launches.append(("W2",) + dispatch(led, run, "W2", "reviser", prompt=writer_prompt(led, run, "W2", draft, challenge, prev)))
    elif phase in ("finishing", "done"):
        print(f"Next: {next_action(led, run)}")
        return
    save(a.run, led)
    if not launches:
        print(f"nothing to launch. Next: {next_action(led, run)}")
        return
    led["counter"]["step"] = led["counter"].get("step", 0) + 1
    save(a.run, led)
    print(f"step {led['counter']['step']}: launch every agent below in one message. Task, subagent_type generalPurpose, with the model shown:")
    for aid, model, cost in launches:
        print(f"  {aid} [{led['flight'][aid]['role']}, model {model}, est ${cost:.2f}]: {launch_line(led, run, aid)}")
    print(budget_line(led))
    print(f"Next: after they all reply done, run: python3 {SCRIPT} ingest {run}")


def work_step(led, run):
    launches = []
    root = led["nodes"][led["root"]]
    if root["status"] in SETTLED:
        led["phase"] = "writing"
        log(led, f"root {root['status']}; moving to writing")
        draft = run_path(run) / "answer-draft.md"
        return [("W1",) + dispatch(led, run, "W1", "writer", prompt=writer_prompt(led, run, "W1", draft))]
    update_converge(led)
    unassigned = [x for x in led["needs"] if x["assigned"] is None]
    if unassigned and not led["converge"]:
        led["counter"]["matcher"] += 1
        jid = f"M{led['counter']['matcher']}"
        for x in unassigned:
            x["assigned"] = jid
        launches.append((jid,) + dispatch(led, run, jid, "matcher", prompt=matcher_prompt(led, run, jid, unassigned)))
    for n in ready_nodes(led):
        if len(launches) >= MAX_PARALLEL:
            break
        role = role_of_node(n)
        cost = cost_of(led, role, n["kind"])
        if cost > available(led) + 1e-9:
            if not led["converge"]:
                led["converge"] = True
                log(led, "converging: the next piece does not fit the budget")
            continue
        if n["dispatches"] >= MAX_DISPATCHES:
            n["force"] = True
        n["dispatches"] += 1
        n["status"] = "dispatched"
        launches.append((n["id"],) + dispatch(led, run, n["id"], role, n["kind"], node_prompt(led, run, n)))
    if launches:
        return launches
    unsettled = [n for n in led["nodes"].values() if n["status"] not in SETTLED]
    if not led["converge"]:
        led["converge"] = True
        log(led, "converging: nothing was ready")
        return work_step(led, run)
    stuck = sorted((n for n in unsettled if n["status"] == "pending"), key=lambda n: -n["depth"])
    if stuck and cost_of(led, role_of_node(stuck[0]), stuck[0]["kind"]) <= available(led) + 1e-9:
        n = stuck[0]
        for d in list(n["depends_on"]):
            if led["nodes"][d]["status"] not in SETTLED:
                n["assume"].append(f"{led['nodes'][d]['text']} (not settled in time)")
                n["depends_on"].remove(d)
        n["force"] = True
        n["dispatches"] += 1
        n["status"] = "dispatched"
        log(led, f"forcing {n['id']} to settle on assumptions")
        return [(n["id"],) + dispatch(led, run, n["id"], role_of_node(n), n["kind"], node_prompt(led, run, n))]
    for n in unsettled:
        n["status"] = "failed"
        n["error"] = n["error"] or "not settled before the budget ran out"
    led["phase"] = "writing"
    log(led, "budget exhausted before the root settled; writing from what is settled")
    draft = run_path(run) / "answer-draft.md"
    return [("W1",) + dispatch(led, run, "W1", "writer", prompt=writer_prompt(led, run, "W1", draft))]


# ---------------------------------------------------------------- finish


def answer_problems(answer, question):
    problems = []
    if not answer.strip():
        return ["answer is empty"]
    for heading in ANSWER_REQUIRED_HEADINGS:
        if heading not in answer:
            problems.append(f"answer needs a heading starting {heading!r}")
    for pattern, label in ANSWER_BANNED:
        if re.search(pattern, question):
            continue
        hits = sorted({m.group(0) for m in re.finditer(pattern, answer)})
        if hits:
            problems.append(f"answer contains {label}: {', '.join(hits[:6])}")
    return problems


def build_audit(led):
    f = led["framing"] or {}
    out = ["# Audit", "", "## Framing", "", f"Real question: {f.get('real_question', '')}", "", f"Crux: {f.get('crux', '')}", ""]
    for t in f.get("terms", []):
        out.append(f"- Term {t['term']}: {t['meaning']}" + (f" Flag: {t['flag']}" if t.get("flag") else ""))
    for c in f.get("constraints", []):
        out.append(f"- Constraint: {c}")
    for s in f.get("assumptions", []):
        out.append(f"- Hidden assumption: {s}")
    out += ["", "## Graph", ""]
    seen = set()

    def walk(nid, indent):
        n = led["nodes"][nid]
        shared = f" (shared by {', '.join(n['parents'])})" if len(n["parents"]) > 1 else ""
        mark = " (see above)" if nid in seen else ""
        r = n["result"] or {}
        conf = f", {r.get('confidence')} confidence" if r else ""
        out.append(f"{'  ' * indent}- {nid} [{n['status']}{conf}] {short(n['text'], 200)}{shared}{mark}")
        if nid in seen:
            return
        seen.add(nid)
        if r:
            out.append(f"{'  ' * indent}  Resolution: {short(r.get('resolution'), 600)}")
        for d in n["depends_on"]:
            walk(d, indent + 1)

    if led["root"]:
        walk(led["root"], 0)
    events = [e["event"] for e in led["log"]]
    out += ["", "## Changes to the graph", ""]
    out += [f"- {e}" for e in events] or ["- none"]
    out += [f"- link: {l}" for l in led["links"]]
    for n in led["nodes"].values():
        if n["old_texts"]:
            out.append(f"- {n['id']} was reframed from: {' / '.join(short(t, 200) for t in n['old_texts'])}")
        if n["assume"]:
            out.append(f"- {n['id']} proceeded on assumptions for: {'; '.join(short(x, 160) for x in n['assume'])}")
    claim_map = (led["jobs"].get("W2") or led["jobs"].get("W1") or {}).get("claim_map") or []
    out += ["", "## Claim map", ""]
    for c in claim_map:
        if isinstance(c, dict):
            out.append(f"- {short(c.get('claim'), 300)}: {', '.join(map(str, c.get('from') or [])) or 'no piece named'}")
    if not claim_map:
        out.append("- none given")
    x = led["jobs"].get("X1") or {}
    out += ["", "## Challenge", ""]
    if x.get("status") == "done":
        for g in x.get("question_gaps", []):
            out.append(f"- Question gap: {g}")
        for c in x.get("challenges", []):
            out.append(f"- [{c['severity']}] {short(c['claim'], 300)}: {short(c['problem'], 500)}")
        for c in (led["jobs"].get("W2") or {}).get("changes") or []:
            if isinstance(c, dict):
                out.append(f"- Change: {short(c.get('change'), 400)} (for: {short(c.get('challenge'), 200)})")
    else:
        out.append(f"- challenge {x.get('status', 'not run')}")
    unsettled = [n for n in led["nodes"].values() if n["status"] != "resolved"]
    out += ["", "## Open questions", ""]
    out += [f"- {n['id']} not settled ({n['status']}): {short(n['text'], 200)}" for n in unsettled] or ["- every piece settled"]
    b = led["budget"]
    by_role = {}
    for s in led["spend_log"]:
        key = f"{s['role']} on {s['model']}"
        by_role[key] = by_role.get(key, 0) + s["cost"]
    out += [
        "",
        "## Run",
        "",
        f"Run directory {led['run_dir']}. {len(led['nodes'])} pieces, {len(led['spend_log'])} agent replies. "
        f"Estimated spend ${b['spent']:.2f} of ${b['limit']:.2f}. Converged early: {'yes' if led['converge'] else 'no'}.",
    ]
    out += [f"- {k}: ${v:.2f}" for k, v in sorted(by_role.items())]
    out += ["", AGREEMENT, ""]
    return "\n".join(out)


def cmd_finish(a):
    led = load(a.run)
    run = run_path(a.run)
    if led["phase"] not in ("finishing",):
        raise HarnessError(f"phase is {led['phase']}. Next: {next_action(led, run)}")
    draft = run / "answer-draft.md"
    answer = read_file(draft)
    problems = answer_problems(answer, led["question"])
    if problems:
        raise HarnessError("; ".join(problems) + f". Fix {draft} and run finish again")
    (run / "answer.md").write_text(answer)
    (run / "audit.md").write_text(build_audit(led))
    led["phase"] = "done"
    led["finished_at"] = now()
    save(a.run, led)
    errors = validate_ledger(led, run)
    print(f"finished: answer {run / 'answer.md'} ({len(answer.split())} words), audit {run / 'audit.md'}")
    print(budget_line(led))
    print("validate: OK" if not errors else "validate: " + "; ".join(errors))


def cmd_assume(a):
    led = load(a.run)
    n = node(led, a.piece)
    if n["status"] in SETTLED:
        raise HarnessError(f"{a.piece} is already {n['status']}")
    if n["status"] == "dispatched":
        raise HarnessError(f"{a.piece} is in flight")
    n["result"] = {"resolution": text_of(a.text, 1500), "confidence": "low", "rests_on": ["assumption set by the planner"], "body_path": None, "at": now()}
    n["status"] = "resolved"
    led["needs"] = [x for x in led["needs"] if x["from"] != a.piece]
    log(led, f"{a.piece} settled by assumption: {short(a.text, 160)}")
    save(a.run, led)
    print(f"{a.piece} settled by assumption")
    print(f"Next: {next_action(led, run_path(a.run))}")


# ---------------------------------------------------------------- report


def budget_line(led):
    b = led["budget"]
    return (
        f"budget (estimates): spent ${b['spent']:.2f}, in flight ${b['reserved']:.2f}, held for the ending ${endgame_left(led):.2f}, "
        f"free ${max(0.0, available(led)):.2f} of ${b['limit']:.2f}" + (" | converging" if led["converge"] else "")
    )


def next_action(led, run):
    cmd = f"python3 {SCRIPT}"
    r = str(run_path(run))
    if led["flight"]:
        return f"launch {', '.join(led['flight'])} if not yet launched, then run: {cmd} ingest {r}"
    if led["phase"] == "finishing":
        return f"run: {cmd} finish {r}"
    if led["phase"] == "done":
        return f"done. Answer {r}/answer.md, audit {r}/audit.md. Check with: {cmd} validate {r}"
    return f"run: {cmd} next {r}"


def cmd_status(a):
    led = load(a.run)
    print(f"phase: {led['phase']} | {len(led['nodes'])} pieces | {budget_line(led)}")
    f = led["framing"]
    if f:
        print(f"real question: {short(f['real_question'], 400)}")
        print(f"crux: {short(f['crux'], 300)}")
        for t in f["terms"]:
            if t.get("flag"):
                print(f"  flagged term {t['term']}: {short(t['flag'], 200)}")
    if led["root"]:
        seen = set()

        def walk(nid, indent):
            n = led["nodes"][nid]
            extra = f" <- also {', '.join(p for p in n['parents'][1:])}" if len(n["parents"]) > 1 else ""
            print(f"{'  ' * indent}{nid} [{n['status']}] {short(n['text'], 140)}{extra}{' (above)' if nid in seen else ''}")
            if a.full and n["result"] and nid not in seen:
                print(f"{'  ' * indent}   = {short(n['result']['resolution'], 400)}")
            if nid in seen:
                return
            seen.add(nid)
            for d in n["depends_on"]:
                walk(d, indent + 1)

        walk(led["root"], 1)
    if led["needs"]:
        print("requests waiting for the matcher:")
        for x in led["needs"]:
            print(f"  {x['id']} from {x['from']}: {short(x['question'], 160)}")
    if led["flight"]:
        print("in flight: " + ", ".join(f"{k} ({v['role']})" for k, v in led["flight"].items()))
    for e in led["log"][-8:]:
        print(f"  event: {short(e['event'], 200)}")
    print(f"Next: {next_action(led, run_path(a.run))}")


def validate_ledger(led, run):
    errors = []
    b = led["budget"]
    if b["spent"] > b["limit"] + 0.01:
        errors.append(f"over budget: ${b['spent']:.2f} of ${b['limit']:.2f}")
    if b["reserved"] < -0.001:
        errors.append("reserved went negative")
    if led["phase"] not in PHASES:
        errors.append(f"unknown phase {led['phase']}")
    for nid, n in led["nodes"].items():
        for d in n["depends_on"]:
            if d not in led["nodes"]:
                errors.append(f"{nid} depends on missing {d}")
            elif nid not in led["nodes"][d]["parents"]:
                errors.append(f"{d} does not list {nid} as a parent")
            elif reaches(led, d, nid):
                errors.append(f"cycle through {nid} and {d}")
    if led["phase"] == "done":
        run = Path(run)
        for name in ("answer.md", "audit.md"):
            if not (run / name).exists():
                errors.append(f"{name} missing")
        if (run / "answer.md").exists():
            errors += answer_problems((run / "answer.md").read_text(), led["question"])
        if (run / "audit.md").exists() and AGREEMENT not in (run / "audit.md").read_text():
            errors.append("audit lacks the agreement sentence")
        if led["flight"]:
            errors.append("agents still in flight at finish")
    return errors


def cmd_validate(a):
    led = load(a.run)
    errors = validate_ledger(led, run_path(a.run))
    for e in errors:
        print(f"error: {e}")
    if errors:
        raise SystemExit(1)
    print("OK")


def cmd_init(a):
    run = run_path(a.run)
    run.mkdir(parents=True, exist_ok=True)
    if ledger_file(run).exists() and not a.force:
        raise HarnessError(f"ledger already exists at {ledger_file(run)}; use status to resume")
    question = (a.question if a.question is not None else read_file(a.question_file)).strip()
    if not question:
        raise HarnessError("question is empty")
    for sub in ("returns", "prompts", "drafts"):
        (run / sub).mkdir(exist_ok=True)
    led = {
        "version": 4,
        "skill": "angles",
        "created_at": now(),
        "question": question,
        "run_dir": str(run),
        "phase": "framing",
        "caps": {"max_nodes": a.max_nodes, "max_depth": a.max_depth},
        "models": {"cheap": a.cheap, "strong": a.strong},
        "budget": {"limit": float(a.budget), "spent": 0.0, "reserved": 0.0},
        "framing": None,
        "root": None,
        "nodes": {},
        "needs": [],
        "links": [],
        "jobs": {},
        "flight": {},
        "converge": False,
        "counter": {"node": 0, "need": 0, "matcher": 0},
        "spend_log": [],
        "log": [],
    }
    if a.budget < endgame_left(led) + cost_of(led, "framer") + 1.0:
        raise HarnessError(f"budget ${a.budget:.2f} is too small; the framing and the ending alone need about ${endgame_left(led) + cost_of(led, 'framer'):.2f}")
    save(run, led)
    print(f"initialized {run}")
    print(f"models: cheap {a.cheap} for fact pieces, strong {a.strong} for framing, judgment, and the ending")
    print(budget_line(led))
    print(f"Next: {next_action(led, run)}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="angles.py", description="Whiteboard for the angles harness.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init", help="create a run")
    s.add_argument("run")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--question")
    g.add_argument("--question-file")
    s.add_argument("--budget", type=float, default=DEFAULT_BUDGET, help="estimated dollars")
    s.add_argument("--max-nodes", type=int, default=DEFAULT_MAX_NODES)
    s.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH)
    s.add_argument("--cheap", default=DEFAULT_CHEAP)
    s.add_argument("--strong", default=DEFAULT_STRONG)
    s.add_argument("--force", action="store_true")
    s = sub.add_parser("next", help="launch the next step")
    s.add_argument("run")
    s = sub.add_parser("ingest", help="read every reply file from the agents in flight")
    s.add_argument("run")
    s.add_argument("--failed", help="mark one agent failed instead")
    s.add_argument("--reason")
    s = sub.add_parser("assume", help="settle a stuck piece by assumption")
    s.add_argument("run")
    s.add_argument("piece")
    s.add_argument("--text", required=True)
    s = sub.add_parser("finish", help="check the answer and write the audit")
    s.add_argument("run")
    s = sub.add_parser("status", help="show the graph and the next action")
    s.add_argument("run")
    s.add_argument("--full", action="store_true")
    s = sub.add_parser("validate", help="check ledger invariants")
    s.add_argument("run")
    a = p.parse_args(argv)
    handlers = {
        "init": cmd_init,
        "next": cmd_next,
        "ingest": cmd_ingest,
        "assume": cmd_assume,
        "finish": cmd_finish,
        "status": cmd_status,
        "validate": cmd_validate,
    }
    try:
        handlers[a.cmd](a)
    except HarnessError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
