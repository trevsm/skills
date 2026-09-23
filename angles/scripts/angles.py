#!/usr/bin/env python3
"""Ledger and prompt builder for the angles harness. Python 3 standard library only.

The planner calls one command per step. Each command checks the ledger, applies
the caps, writes the ledger atomically, and prints the next action.
"""

import argparse
import datetime as dt
import json
import math
import os
import re
import string
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
MODEL = "composer-2.5-fast"
AGREEMENT = "Agreement among nodes is not evidence."
MAX_LEADS = 3
MAX_WORKERS = 3
MAX_CHILDREN_PER_PARENT = 3
MAX_NEW_ITEMS_PER_WAVE = 6
MAX_PLAN_ITEMS = 6
MAX_CRITERIA = 6
MAX_FINDINGS = 6
MAX_OPEN_ITEMS = 3
MAX_ATTEMPTS = 2
STALL_LIMIT = 2
MIN_WAVE_BUDGET = 6
DEFAULT_WAVES = 4
DEFAULT_AGENTS = 48
STOPWORDS = frozenset(
    "a an the of to and or for in on with by from that this is are was were be as at if we they it".split()
)
CONFIDENCE = ("low", "medium", "high")
SOURCE_KINDS = ("measured", "sourced", "estimate", "assumption", "reasoning")
MAX_CONSTRAINTS = 8
CRITERION_STATUS = ("open", "met", "unmeetable")
SEVERITY = ("breaks", "weakens", "ok")
ITEM_STATUS = ("frontier", "dispatched", "done", "failed", "dropped")
PHASES = ("planning", "waves", "challenge", "synthesize", "done")
CAP_REFUSALS = ("depth_exhausted", "breadth_cap", "layer_cap")
AUDIT_HEADINGS = ("## Claim map", "## Challenge", "## Open questions")
ANSWER_REQUIRED_HEADING = "## Assumptions"
ANSWER_BANNED = (
    (r"\b[TX]\d+(-w\d+)?\b", "branch or challenger ids"),
    (r"\bC\d+\b", "criterion ids"),
    (r"(?im)^#+\s*(coverage|criteria|challenge|run|divergences|claim map)\b", "an audit heading"),
    (r"(?i)\bcriteri(on|a) (met|partial|unmeetable)\b", "criteria bookkeeping"),
    (r"(?i)\b(the challenger|challenge pass|review pass|branch lead|planner|ledger|notes file)\b", "harness vocabulary"),
    (r"(?i)\bangles\b", "the harness name"),
    (r"(?i)\bwaves? \d", "wave numbers"),
)


class HarnessError(Exception):
    pass


def now():
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def claim_key(text):
    return re.sub(r"\s+", " ", str(text).strip().lower()).rstrip(".?! ")


def token_key(text):
    tokens = re.findall(r"[a-z0-9$%]+", claim_key(text))
    return " ".join(sorted({t for t in tokens if t not in STOPWORDS}))


def id_number(item_id):
    digits = re.sub(r"\D", "", str(item_id))
    return int(digits) if digits else 0


def as_text(value, limit):
    if value is None:
        return ""
    return str(value).strip()[:limit]


def criterion_id(value):
    s = str(value).strip().upper()
    return f"C{s}" if s.isdigit() else s


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


def read_input(path):
    p = Path(path).expanduser()
    if not p.exists():
        raise HarnessError(f"missing file {p}")
    return p.read_text()


def extract_json(text):
    text = text.strip()
    candidates = [text]
    candidates += [m.group(1) for m in re.finditer(r"```(?:json)?\s*\n(.*?)```", text, re.S)]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise HarnessError("no JSON object found")


def challenge_reserve(max_agents):
    if max_agents >= 12:
        return 3
    if max_agents >= 6:
        return 2
    return 0


def available(led):
    agents = led["agents"]
    reserve = led["caps"]["challenge_reserve"] if led["challenge"] is None else 0
    return led["caps"]["max_agents"] - agents["spent"] - agents["reserved"] - reserve


def get_item(led, item_id):
    for it in led["items"]:
        if it["id"] == item_id:
            return it
    raise HarnessError(f"unknown item {item_id}")


def open_criteria(led):
    return {c["id"] for c in led["criteria"] if c["status"] == "open"}


def current_wave(led):
    return led["waves"][-1] if led["waves"] else None


def require_phase(led, run, *phases):
    if led["phase"] not in phases:
        raise HarnessError(
            f"phase is {led['phase']}; this command needs {' or '.join(phases)}. Next: {next_action(led, run)}"
        )


def new_item(item_id, kind, parent, depth, text, why, criteria, created_wave):
    return {
        "id": item_id,
        "kind": kind,
        "parent": parent,
        "depth": depth,
        "text": text,
        "why": why,
        "criteria": criteria,
        "status": "frontier",
        "created_wave": created_wave,
        "dispatched_wave": None,
        "claim_key": claim_key(text),
        "token_key": token_key(text),
        "children": [],
        "allowance": None,
        "attempts": 0,
        "agents_charged": 0,
        "result": None,
        "error": None,
        "warnings": [],
    }


def try_open(led, spec, created_wave, opened_this_call):
    if not isinstance(spec, dict):
        return None, "not_an_object"
    text = as_text(spec.get("text"), 600)
    if not text:
        return None, "empty_item"
    parent = None
    parent_id = spec.get("parent")
    if parent_id:
        try:
            parent = get_item(led, str(parent_id))
        except HarnessError:
            return None, "unknown_parent"
        if parent["status"] != "done":
            return None, "parent_not_done"
    ck, tk = claim_key(text), token_key(text)
    if ck in led["claim_index"] or (tk and tk in led["token_index"]):
        return None, "duplicate_item"
    depth = parent["depth"] + 1 if parent else 1
    if depth > led["caps"]["max_waves"]:
        return None, "depth_exhausted"
    if parent and len(parent["children"]) >= MAX_CHILDREN_PER_PARENT:
        return None, "breadth_cap"
    if opened_this_call >= MAX_NEW_ITEMS_PER_WAVE:
        return None, "layer_cap"
    known = {c["id"] for c in led["criteria"]}
    crits = [criterion_id(c) for c in spec.get("criteria") or [] if criterion_id(c) in known]
    number = sum(1 for i in led["items"] if i["kind"] == "branch") + 1
    it = new_item(
        f"T{number}",
        "branch",
        parent["id"] if parent else None,
        depth,
        text,
        as_text(spec.get("why"), 400),
        crits,
        created_wave,
    )
    led["items"].append(it)
    led["claim_index"][ck] = it["id"]
    if tk:
        led["token_index"][tk] = it["id"]
    if parent:
        parent["children"].append(it["id"])
    return it, None


def stop_reasons(led):
    reasons = []
    if led["criteria"] and all(c["status"] != "open" for c in led["criteria"]):
        reasons.append("criteria_met")
    if not any(i["status"] == "frontier" for i in led["items"]):
        reasons.append("frontier_empty")
    if len(led["waves"]) >= led["caps"]["max_waves"]:
        reasons.append("waves_exhausted")
    if available(led) < 1:
        reasons.append("budget_exhausted")
    if led["stall"] >= STALL_LIMIT:
        reasons.append("stalled")
    return reasons


def maybe_stop(led):
    reasons = stop_reasons(led)
    if reasons:
        led["stopped"]["reasons"] = reasons
        if led["caps"]["challenge_reserve"] > 0 and led["challenge"] is None:
            led["phase"] = "challenge"
        else:
            led["phase"] = "synthesize"
    return reasons


def ordered_frontier(led):
    open_c = open_criteria(led)

    def score(it):
        return (-len(set(it["criteria"]) & open_c), it["depth"], id_number(it["id"]))

    frontier = sorted((i for i in led["items"] if i["status"] == "frontier"), key=score)
    groups = {}
    for it in frontier:
        groups.setdefault(it["parent"] or "", []).append(it)
    queues = sorted(groups.values(), key=lambda g: score(g[0]))
    ordered = []
    while any(queues):
        for queue in queues:
            if queue:
                ordered.append(queue.pop(0))
    return ordered


def next_action(led, run):
    cmd = f"python3 {SCRIPT}"
    r = str(run_path(run))
    phase = led["phase"]
    if phase == "planning":
        return f"write {r}/plan.json, then run: {cmd} plan {r} --file {r}/plan.json"
    if phase == "waves":
        wave = current_wave(led)
        if wave and wave["status"] == "dispatched":
            out = [i for i in wave["items"] if get_item(led, i)["status"] == "dispatched"]
            return (
                f"launch a lead for each of {', '.join(out)} with the launch line for {r}/prompts/<id>.md, "
                f"save each reply to {r}/returns/<id>.txt, then run: {cmd} ingest {r} <id> --file {r}/returns/<id>.txt"
            )
        if wave and wave["status"] == "returned":
            n = wave["n"]
            return (
                f"run: {cmd} status {r}; write {r}/integrate-{n}.json; "
                f"then run: {cmd} integrate {r} --file {r}/integrate-{n}.json"
            )
        return f"run: {cmd} next {r}"
    if phase == "challenge":
        if led["challenge"] is None:
            return f"write the draft answer to {r}/draft.md, then run: {cmd} challenge {r} --draft-file {r}/draft.md"
        return (
            f"launch the challenger with the launch line for {r}/prompts/X1.md, save the reply to {r}/returns/X1.txt, "
            f"then run: {cmd} ingest {r} X1 --file {r}/returns/X1.txt"
        )
    if phase == "synthesize":
        return (
            f"write {r}/answer-draft.md and {r}/audit-draft.md from the templates, then run: "
            f"{cmd} finish {r} --answer-file {r}/answer-draft.md --audit-file {r}/audit-draft.md"
        )
    return f"done. Answer at {r}/answer.md, audit at {r}/audit.md. Check with: {cmd} validate {r}"


LEAD_TEMPLATE = string.Template(
    """You are an angles branch lead. You own one branch of a larger investigation. A planner above you owns the overall plan. It will fold your report in with the other branches and decide what happens next.

Question:
$question

Goal:
$goal

Done when:
$criteria

Hard constraints. Anything you recommend must respect every one of them. If your branch's best local answer breaks one, say so and give the option that fits:
$constraints

What the planner knows so far:
$state

Your branch: $item_id (depth $depth)
$text
Why it matters: $why
Serves: $serves

Other branches running now. Do not duplicate them:
$siblings

Already covered by earlier branches:
$covered

Deferred by caps. Do not propose these again:
$deferred

How to work:
1. Split your branch into at most $workers sub-questions that together answer it. Use fewer when the branch is small.
2. Launch one worker per sub-question, all in a single message so they run in parallel. Use the Task tool with subagent_type generalPurpose and model $model. If Task is not a top-level tool, look it up with GetDynamicTools (namespace "cursor", toolName "Task") and call it through CallDynamicTool. Launch at most $workers workers in total.
3. Give each worker the worker prompt below with the placeholders filled. Workers cannot launch agents.
4. If your allowance is 0 workers, or you have no Task tool, work the branch yourself. Report workers_used and had_task honestly.
5. When the workers return, fold their results together. Resolve the conflicts you can. Report the ones you cannot as open. Agreement between workers is not evidence.
6. Write your full branch notes to $notes. Tell worker k to write its notes to $notes_stem-w<k>.md.
7. Do not modify any other file. Never write ledger.json.

Every finding needs a basis: a file you read, a command you ran, a page you fetched, or the word "reasoning" when it is inference. Every finding also has a kind: measured (you observed it), sourced (a document or page says it), estimate (your own number), assumption (taken as given to proceed), or reasoning.

Numbers: every number that is not given in the question carries its kind and basis. An estimate keeps its range and the assumption it rests on, in the claim itself: "about 10 to 13 weeks, assuming 3 engineers and no existing queue". Never state an estimate as a fact. Never invent a threshold without saying it is a starting default to replace with a measured baseline.

Substance: put the actual content in the findings, not a pointer to it. If the branch produced a list or a table, the claim holds the items themselves in compact form. "Six failure modes identified, see notes" is not a finding.

Simplicity: prefer the smallest plan that meets the criteria. Do not add gates, phases, roles, or steps that would not change a decision.

Worker prompt:
---
You are an angles worker. Answer one sub-question. Do not launch agents.

Question: $question
Branch: $text
Sub-question: <SUB_QUESTION>
Notes file: <NOTES_PATH>
Hard constraints:
$constraints

You may read files, search, fetch web pages, and run read-only commands. Do not modify anything except your notes file. Write your full notes there.

Every number not given in the question states its kind (measured, sourced, estimate, assumption) and basis. An estimate keeps its range and assumption. Put the actual items in your findings, not a pointer to your notes.

Return ONLY this JSON object:
{"sub_question": "<SUB_QUESTION>", "summary": "<80 words or fewer>", "findings": [{"claim": "...", "basis": "...", "kind": "measured|sourced|estimate|assumption|reasoning", "confidence": "low|medium|high", "source": "..."}], "gaps": ["..."]}
---

Return ONLY this JSON object to the planner:
{
  "item_id": "$item_id",
  "summary": "<120 words or fewer: what this branch established>",
  "findings": [{"claim": "...", "basis": "...", "kind": "measured|sourced|estimate|assumption|reasoning", "confidence": "low|medium|high", "source": "..."}],
  "criteria_progress": [{"criterion": "C1", "status": "met|partial|none", "note": "..."}],
  "open_items": [{"text": "a next branch worth running", "why": "...", "criteria": ["C1"]}],
  "settled": false,
  "workers_used": 0,
  "had_task": true,
  "notes_path": "$notes"
}

At most $max_findings findings and $max_open open_items. Set settled to true when this branch needs no follow-up. Propose open_items only for gaps that serve an open criterion and are not already covered, running, or deferred.
"""
)

CHALLENGE_TEMPLATE = string.Template(
    """You are the angles challenger. The planner has a draft answer. Your job is to break it before anyone relies on it.

Question:
$question

Goal:
$goal

Done when:
$criteria

Hard constraints:
$constraints

Draft answer:
$draft

How to work:
1. Run these four checks yourself before anything else. Each one that finds a problem becomes a challenge.
   a. Question check. Reread the question word for word. List every part it asks. For each part, is the draft's answer complete and direct? Put every part answered only partly or not at all in question_gaps. Criteria being met does not mean the question is answered.
   b. Riskiest step. Name the single riskiest action the draft recommends. Check it against every hard constraint, especially deadlines, staffing, and anything touching money or data. If a safer option would meet the goal, that is a challenge.
   c. Unsourced numbers. Every number not given in the question needs a basis, or must be labeled as an estimate or starting default with its assumption. Each bare number is a challenge with severity weakens at least.
   d. Dangling references. The draft must contain what it refers to. "Six failure modes", "the table", or "the gates" with no list or table in the draft is a challenge.
2. List the claims the draft depends on. A claim is load-bearing when the answer changes if it is wrong. Pick at most $workers of the weakest load-bearing claims. Launch one worker per claim, all in a single message, with the Task tool, subagent_type generalPurpose, model $model. If Task is not a top-level tool, look it up with GetDynamicTools (namespace "cursor", toolName "Task") and call it through CallDynamicTool. Launch at most $workers workers in total.
3. Give each worker this prompt with the placeholders filled:
---
You are an angles challenge worker. Try to refute one claim. Do not launch agents.

Question: $question
Claim: <CLAIM>
Notes file: <NOTES_PATH>

You may read files, search, fetch web pages, and run read-only commands. Modify nothing except your notes file.

Return ONLY this JSON object:
{"claim": "<CLAIM>", "problem": "<what is wrong, or none found>", "severity": "breaks|weakens|ok", "basis": "..."}
---
4. If your allowance is 0 workers, or you have no Task tool, run the checks yourself.
5. Write your full notes to $notes. Tell worker k to write its notes to $notes_stem-w<k>.md. Modify nothing else. Never write ledger.json.

Return ONLY this JSON object:
{"item_id": "X1", "summary": "<120 words or fewer>", "question_gaps": ["a part of the question the draft does not fully answer"], "challenges": [{"claim": "...", "problem": "...", "severity": "breaks|weakens|ok", "basis": "..."}], "workers_used": 0, "had_task": true, "notes_path": "$notes"}

Severity ok means the claim survived a real attempt to break it. Say what was tried. Agreement is not a refutation attempt.
"""
)


def criteria_block(led):
    if not led["criteria"]:
        return "none"
    return "\n".join(f"{c['id']} [{c['status']}] {c['text']}" for c in led["criteria"])


def constraints_block(led):
    constraints = (led["plan"] or {}).get("constraints") or []
    return "\n".join(f"- {c}" for c in constraints) or "none stated"


def write_lead_prompt(led, run, it, wave_items):
    run = run_path(run)
    siblings = [f"{s['id']}: {s['text']}" for s in wave_items if s["id"] != it["id"]]
    done = [i for i in led["items"] if i["kind"] == "branch" and i["status"] == "done"]
    covered = [f"{i['id']}: {short(i['text'], 320)}" for i in done[-30:]]
    deferred = [f"{short(d['text'], 320)} ({d['reason']})" for d in led["deferred"][-12:]]
    notes = run / "notes" / f"{it['id']}.md"
    text = LEAD_TEMPLATE.substitute(
        question=led["question"],
        goal=led["plan"]["goal"],
        criteria=criteria_block(led),
        constraints=constraints_block(led),
        state=led["state"] or "Nothing integrated yet. This is the first wave.",
        item_id=it["id"],
        depth=it["depth"],
        text=it["text"],
        why=it["why"] or "not stated",
        serves=", ".join(it["criteria"]) or "none",
        siblings="\n".join(siblings) or "none",
        covered="\n".join(covered) or "none",
        deferred="\n".join(deferred) or "none",
        workers=it["allowance"],
        model=MODEL,
        notes=notes,
        notes_stem=notes.with_suffix(""),
        max_findings=MAX_FINDINGS,
        max_open=MAX_OPEN_ITEMS,
    )
    path = run / "prompts" / f"{it['id']}.md"
    path.write_text(text)
    return path


def write_challenge_prompt(led, run, it, draft):
    run = run_path(run)
    notes = run / "notes" / "X1.md"
    text = CHALLENGE_TEMPLATE.substitute(
        question=led["question"],
        goal=led["plan"]["goal"],
        criteria=criteria_block(led),
        constraints=constraints_block(led),
        draft=draft,
        workers=it["allowance"],
        model=MODEL,
        notes=notes,
        notes_stem=notes.with_suffix(""),
    )
    path = run / "prompts" / "X1.md"
    path.write_text(text)
    return path


def normalize_workers_used(data, errors):
    used = data.get("workers_used")
    if isinstance(used, str) and used.strip().isdigit():
        used = int(used.strip())
    if isinstance(used, bool) or not isinstance(used, int) or used < 0:
        errors.append("workers_used must be a non-negative integer")
        return 0
    return used


def normalize_had_task(data, warnings):
    had = data.get("had_task")
    if not isinstance(had, bool):
        warnings.append("had_task missing or not true/false")
        return None
    return had


def normalize_findings(raw, warnings):
    if not isinstance(raw, list):
        return None
    out = []
    for f in raw[:MAX_FINDINGS]:
        if not isinstance(f, dict) or not as_text(f.get("claim"), 1):
            warnings.append("dropped a finding without a claim")
            continue
        confidence = as_text(f.get("confidence"), 20).lower()
        if confidence not in CONFIDENCE:
            warnings.append(f"confidence {confidence!r} recorded as low")
            confidence = "low"
        kind = as_text(f.get("kind"), 20).lower()
        if kind not in SOURCE_KINDS:
            warnings.append(f"kind {kind!r} recorded as reasoning")
            kind = "reasoning"
        out.append(
            {
                "claim": as_text(f.get("claim"), 900),
                "basis": as_text(f.get("basis"), 500) or "none given",
                "kind": kind,
                "confidence": confidence,
                "source": as_text(f.get("source"), 300),
            }
        )
    if len(raw) > MAX_FINDINGS:
        warnings.append(f"kept the first {MAX_FINDINGS} findings")
    return out


def normalize_branch(data, it):
    errors, warnings = [], []
    reported = as_text(data.get("item_id"), 20)
    if reported and reported != it["id"]:
        warnings.append(f"reply named {reported}; bound to {it['id']}")
    summary = as_text(data.get("summary"), 1500)
    if not summary:
        errors.append("summary missing")
    findings = normalize_findings(data.get("findings"), warnings)
    if findings is None:
        errors.append("findings must be a list")
        findings = []
    raw_open = data.get("open_items", [])
    if not isinstance(raw_open, list):
        errors.append("open_items must be a list")
        raw_open = []
    open_items = []
    for o in raw_open:
        if isinstance(o, dict) and as_text(o.get("text"), 1):
            open_items.append(
                {
                    "text": as_text(o.get("text"), 500),
                    "why": as_text(o.get("why"), 300),
                    "criteria": [criterion_id(c) for c in o.get("criteria") or []],
                }
            )
    if len(open_items) > MAX_OPEN_ITEMS:
        warnings.append(f"kept the first {MAX_OPEN_ITEMS} open_items")
        open_items = open_items[:MAX_OPEN_ITEMS]
    progress = []
    raw_progress = data.get("criteria_progress", [])
    if isinstance(raw_progress, list):
        for p in raw_progress:
            if isinstance(p, dict):
                progress.append(
                    {
                        "criterion": criterion_id(p.get("criterion", "")),
                        "status": as_text(p.get("status"), 20).lower(),
                        "note": as_text(p.get("note"), 400),
                    }
                )
    result = {
        "summary": summary,
        "findings": findings,
        "criteria_progress": progress,
        "open_items": open_items,
        "settled": bool(data.get("settled", False)),
        "workers_used": normalize_workers_used(data, errors),
        "had_task": normalize_had_task(data, warnings),
        "notes_path": as_text(data.get("notes_path"), 500),
    }
    return result, errors, warnings


def normalize_challenge(data):
    errors, warnings = [], []
    summary = as_text(data.get("summary"), 1500)
    if not summary:
        errors.append("summary missing")
    raw = data.get("challenges")
    challenges = []
    if not isinstance(raw, list):
        errors.append("challenges must be a list")
        raw = []
    for c in raw:
        if not isinstance(c, dict) or not as_text(c.get("claim"), 1):
            warnings.append("dropped a challenge without a claim")
            continue
        severity = as_text(c.get("severity"), 20).lower()
        if severity not in SEVERITY:
            warnings.append(f"severity {severity!r} recorded as weakens")
            severity = "weakens"
        challenges.append(
            {
                "claim": as_text(c.get("claim"), 500),
                "problem": as_text(c.get("problem"), 800),
                "severity": severity,
                "basis": as_text(c.get("basis"), 500) or "none given",
            }
        )
    raw_gaps = data.get("question_gaps", [])
    if not isinstance(raw_gaps, list):
        warnings.append("question_gaps was not a list")
        raw_gaps = []
    gaps = [as_text(g, 400) for g in raw_gaps if as_text(g, 1)]
    result = {
        "summary": summary,
        "question_gaps": gaps,
        "challenges": challenges,
        "workers_used": normalize_workers_used(data, errors),
        "had_task": normalize_had_task(data, warnings),
        "notes_path": as_text(data.get("notes_path"), 500),
    }
    return result, errors, warnings


def cmd_init(a):
    run = run_path(a.run)
    run.mkdir(parents=True, exist_ok=True)
    if ledger_file(run).exists() and not a.force:
        raise HarnessError(f"ledger already exists at {ledger_file(run)}; use status to resume")
    question = a.question if a.question is not None else read_input(a.question_file)
    question = question.strip()
    if not question:
        raise HarnessError("question is empty")
    waves = a.depth if a.depth is not None else DEFAULT_WAVES
    agents = a.nodes if a.nodes is not None else DEFAULT_AGENTS
    if not 1 <= waves <= 8:
        raise HarnessError("depth must be between 1 and 8")
    if not 2 <= agents <= 200:
        raise HarnessError("nodes must be between 2 and 200")
    for sub in ("notes", "returns", "prompts"):
        (run / sub).mkdir(exist_ok=True)
    led = {
        "version": 3,
        "skill": "angles",
        "created_at": now(),
        "question": question,
        "run_dir": str(run),
        "phase": "planning",
        "caps": {
            "max_waves": waves,
            "max_agents": agents,
            "max_leads_per_wave": MAX_LEADS,
            "max_workers_per_lead": MAX_WORKERS,
            "max_children_per_parent": MAX_CHILDREN_PER_PARENT,
            "max_new_items_per_wave": MAX_NEW_ITEMS_PER_WAVE,
            "challenge_reserve": challenge_reserve(agents),
        },
        "overrides": {"depth": a.depth, "nodes": a.nodes},
        "plan": None,
        "criteria": [],
        "items": [],
        "claim_index": {},
        "token_index": {},
        "deferred": [],
        "waves": [],
        "state": "",
        "stall": 0,
        "agents": {"spent": 0, "reserved": 0},
        "challenge": None,
        "stopped": {"complete": False, "reasons": []},
    }
    save(run, led)
    print(f"initialized {run}")
    print(f"caps: {waves} waves, {agents} agents, {led['caps']['challenge_reserve']} held for the challenge")
    print(f"Next: {next_action(led, run)}")


def cmd_plan(a):
    led = load(a.run)
    require_phase(led, a.run, "planning")
    data = extract_json(read_input(a.file))
    goal = as_text(data.get("goal"), 1500)
    if not goal:
        raise HarnessError("plan.goal is required")
    criteria = data.get("criteria")
    if not isinstance(criteria, list) or not 1 <= len(criteria) <= MAX_CRITERIA:
        raise HarnessError(f"plan.criteria must be a list of 1 to {MAX_CRITERIA} checkable statements")
    items = data.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_PLAN_ITEMS:
        raise HarnessError(f"plan.items must be a list of 1 to {MAX_PLAN_ITEMS} branches")
    constraints = data.get("constraints")
    if not isinstance(constraints, list) or len(constraints) > MAX_CONSTRAINTS:
        raise HarnessError(
            f"plan.constraints must be a list of 0 to {MAX_CONSTRAINTS} hard limits from the question "
            "(deadlines, staffing, money, what must not break). Use [] only when the question sets none."
        )
    constraints = [as_text(c, 300) for c in constraints if as_text(c, 1)]
    led["plan"] = {
        "goal": goal,
        "approach": as_text(data.get("approach"), 1500),
        "constraints": constraints,
    }
    led["criteria"] = []
    for n, c in enumerate(criteria, 1):
        text = as_text(c.get("text") if isinstance(c, dict) else c, 500)
        if not text:
            raise HarnessError(f"criterion {n} is empty")
        led["criteria"].append({"id": f"C{n}", "text": text, "status": "open", "evidence": [], "note": ""})
    opened, refused = [], []
    for spec in items:
        spec = dict(spec) if isinstance(spec, dict) else {"text": spec}
        spec["parent"] = None
        it, reason = try_open(led, spec, 0, len(opened))
        if it:
            opened.append(it["id"])
        else:
            refused.append(f"{as_text(spec.get('text'), 80)!r}: {reason}")
    if not opened:
        raise HarnessError("no plan item opened: " + "; ".join(refused))
    led["phase"] = "waves"
    save(a.run, led)
    print(
        f"plan recorded: {len(led['criteria'])} criteria, {len(constraints)} constraints, "
        f"branches {', '.join(opened)}"
    )
    for r in refused:
        print(f"refused {r}")
    print(f"Next: {next_action(led, a.run)}")


def cmd_next(a):
    led = load(a.run)
    require_phase(led, a.run, "waves")
    wave = current_wave(led)
    if wave and wave["status"] != "integrated":
        raise HarnessError(f"wave {wave['n']} is {wave['status']}. Next: {next_action(led, a.run)}")
    reasons = maybe_stop(led)
    if reasons:
        save(a.run, led)
        print(f"stopped: {', '.join(reasons)}")
        print(f"Next: {next_action(led, a.run)}")
        return
    n = len(led["waves"]) + 1
    remaining = led["caps"]["max_waves"] - n + 1
    avail = available(led)
    if remaining <= 1:
        wave_budget = avail
    else:
        wave_budget = min(avail, max(math.ceil(avail / remaining), MIN_WAVE_BUDGET))
    ordered = ordered_frontier(led)
    leads = min(MAX_LEADS, len(ordered), max(1, wave_budget // 3))
    if a.leads is not None:
        leads = max(1, min(a.leads, MAX_LEADS, len(ordered), avail))
    workers = max(0, min(MAX_WORKERS, (wave_budget - leads) // leads))
    if a.workers is not None:
        workers = max(0, min(a.workers, MAX_WORKERS, (avail - leads) // leads))
    chosen = ordered[:leads]
    for it in chosen:
        it["status"] = "dispatched"
        it["dispatched_wave"] = n
        it["allowance"] = workers
        it["attempts"] += 1
    led["agents"]["reserved"] += leads * (1 + workers)
    led["waves"].append(
        {
            "n": n,
            "items": [it["id"] for it in chosen],
            "workers_per_lead": workers,
            "status": "dispatched",
            "started_at": now(),
            "integration": None,
        }
    )
    paths = [write_lead_prompt(led, a.run, it, chosen) for it in chosen]
    save(a.run, led)
    print(f"wave {n} of {led['caps']['max_waves']}: {leads} lead(s), up to {workers} worker(s) each")
    print(f"launch every lead in one message: Task, subagent_type generalPurpose, model {MODEL}, prompt = the launch line below")
    for it, path in zip(chosen, paths):
        print(f"  {it['id']} (depth {it['depth']}): {launch_line(path)}")
    print(f"agents: spent {led['agents']['spent']}, reserved {led['agents']['reserved']}, available {available(led)}")
    print(f"Next: {next_action(led, a.run)}")


def cmd_ingest(a):
    led = load(a.run)
    require_phase(led, a.run, "waves", "challenge")
    it = get_item(led, a.item)
    if it["status"] != "dispatched":
        raise HarnessError(f"{it['id']} is {it['status']}, not dispatched")
    run = run_path(a.run)
    allowance = it["allowance"] or 0
    held = 1 + allowance
    errors, warnings, result = [], [], None
    if a.failed:
        errors.append(f"task failed: {a.failed}")
    else:
        text = read_input(a.file)
        (run / "returns" / f"{it['id']}.attempt{it['attempts']}.txt").write_text(text)
        try:
            data = extract_json(text)
        except HarnessError as e:
            errors.append(str(e))
        else:
            if it["kind"] == "challenge":
                result, errors, warnings = normalize_challenge(data)
            else:
                result, errors, warnings = normalize_branch(data, it)
    led["agents"]["reserved"] -= held
    if errors:
        led["agents"]["spent"] += held
        it["agents_charged"] += held
        it["error"] = "; ".join(errors)
        if it["kind"] == "branch" and it["attempts"] < MAX_ATTEMPTS:
            it["status"] = "frontier"
            it["allowance"] = None
            outcome = "requeued for one retry"
        else:
            it["status"] = "failed"
            outcome = "failed"
    else:
        used = result["workers_used"]
        if used > allowance:
            warnings.append(f"overspend: {used} workers used, {allowance} allowed")
        charge = 1 + used
        led["agents"]["spent"] += charge
        it["agents_charged"] += charge
        it["status"] = "done"
        it["result"] = result
        it["error"] = None
        outcome = "done"
    it["warnings"].extend(warnings)
    if it["kind"] == "challenge":
        led["challenge"]["status"] = "returned" if outcome == "done" else "failed"
        led["phase"] = "synthesize"
    else:
        wave = next(w for w in led["waves"] if it["id"] in w["items"] and w["status"] == "dispatched")
        if not any(get_item(led, i)["status"] == "dispatched" for i in wave["items"]):
            wave["status"] = "returned"
    save(a.run, led)
    print(f"{it['id']}: {outcome}")
    for e in errors:
        print(f"  error: {e}")
    for w in warnings:
        print(f"  warning: {w}")
    print(f"agents: spent {led['agents']['spent']}, reserved {led['agents']['reserved']}, available {available(led)}")
    print(f"Next: {next_action(led, a.run)}")


def cmd_integrate(a):
    led = load(a.run)
    require_phase(led, a.run, "waves")
    wave = current_wave(led)
    if not wave or wave["status"] != "returned":
        raise HarnessError(f"no returned wave to integrate. Next: {next_action(led, a.run)}")
    data = extract_json(read_input(a.file))
    state = as_text(data.get("state"), 4000)
    if not state:
        raise HarnessError("integrate.state is required: the current answer as it stands")
    done_ids = {i["id"] for i in led["items"] if i["status"] == "done"}
    warnings, changes = [], []
    newly_settled = 0
    for upd in data.get("criteria") or []:
        if not isinstance(upd, dict):
            continue
        cid = criterion_id(upd.get("id", ""))
        crit = next((c for c in led["criteria"] if c["id"] == cid), None)
        if crit is None:
            warnings.append(f"unknown criterion {cid}")
            continue
        status = as_text(upd.get("status"), 20).lower()
        if status not in CRITERION_STATUS:
            warnings.append(f"{cid}: status {status!r} ignored")
            continue
        evidence = [str(e) for e in upd.get("evidence") or [] if str(e) in done_ids]
        if status == "met" and not evidence and not crit["evidence"]:
            warnings.append(f"{cid} left {crit['status']}: met needs a done branch as evidence")
            continue
        if crit["status"] == "open" and status != "open":
            newly_settled += 1
        crit["status"] = status
        crit["evidence"] = sorted(set(crit["evidence"]) | set(evidence), key=id_number)
        crit["note"] = as_text(upd.get("note"), 600)
        changes.append(f"{cid} -> {status}")
    dropped = []
    for d in data.get("drop") or []:
        did = d.get("id") if isinstance(d, dict) else d
        reason = as_text(d.get("reason"), 300) if isinstance(d, dict) else ""
        try:
            target = get_item(led, str(did))
        except HarnessError:
            warnings.append(f"drop: unknown item {did}")
            continue
        if target["status"] != "frontier":
            warnings.append(f"drop: {did} is {target['status']}, not frontier")
            continue
        target["status"] = "dropped"
        target["error"] = f"dropped: {reason or 'no reason given'}"
        dropped.append(target["id"])
    opened, refused = [], []
    for spec in data.get("new_items") or []:
        it, reason = try_open(led, spec, wave["n"], len(opened))
        if it:
            opened.append(it["id"])
            continue
        text = as_text(spec.get("text") if isinstance(spec, dict) else spec, 500)
        refused.append({"text": text, "reason": reason})
        if reason in CAP_REFUSALS and isinstance(spec, dict):
            led["deferred"].append(
                {"text": text, "parent": spec.get("parent"), "reason": reason, "wave": wave["n"]}
            )
    led["stall"] = 0 if (newly_settled or opened) else led["stall"] + 1
    led["state"] = state
    wave["integration"] = {
        "at": now(),
        "state": state,
        "criteria_changes": changes,
        "newly_settled": newly_settled,
        "opened": opened,
        "refused": refused,
        "dropped": dropped,
        "warnings": warnings,
    }
    wave["status"] = "integrated"
    reasons = maybe_stop(led)
    save(a.run, led)
    print(f"wave {wave['n']} integrated: {newly_settled} criteria settled, opened {', '.join(opened) or 'none'}")
    for c in changes:
        print(f"  {c}")
    for r in refused:
        print(f"  refused {short(r['text'], 80)!r}: {r['reason']}")
    for d in dropped:
        print(f"  dropped {d}")
    for w in warnings:
        print(f"  warning: {w}")
    if opened and len(led["waves"]) >= led["caps"]["max_waves"]:
        print("  note: no waves left; the branches just opened stay unexplored. List them under Open questions.")
    if reasons:
        print(f"stopped: {', '.join(reasons)}")
    print(f"Next: {next_action(led, a.run)}")


def cmd_challenge(a):
    led = load(a.run)
    require_phase(led, a.run, "challenge")
    if led["challenge"] is not None:
        raise HarnessError(f"challenge already {led['challenge']['status']}")
    pool = led["caps"]["max_agents"] - led["agents"]["spent"] - led["agents"]["reserved"]
    if a.skip or pool < 1:
        reason = a.skip or "no agents left"
        led["challenge"] = {"item": None, "status": "skipped", "reason": reason}
        led["phase"] = "synthesize"
        save(a.run, led)
        print(f"challenge skipped: {reason}")
        print(f"Next: {next_action(led, a.run)}")
        return
    draft = read_input(a.draft_file).strip()
    if not draft:
        raise HarnessError("draft is empty")
    workers = max(0, min(MAX_WORKERS, led["caps"]["challenge_reserve"] - 1, pool - 1))
    it = new_item("X1", "challenge", None, 0, "Challenge the draft answer", "", [], len(led["waves"]))
    it["status"] = "dispatched"
    it["allowance"] = workers
    it["attempts"] = 1
    led["items"].append(it)
    led["challenge"] = {"item": "X1", "status": "dispatched", "draft": draft}
    led["agents"]["reserved"] += 1 + workers
    path = write_challenge_prompt(led, a.run, it, draft)
    save(a.run, led)
    print(f"challenger X1: up to {workers} workers")
    print(f"launch it: Task, subagent_type generalPurpose, model {MODEL}, prompt = {launch_line(path)}")
    print(f"Next: {next_action(led, a.run)}")


def answer_problems(answer, question):
    problems = []
    if not answer.strip():
        return ["answer is empty"]
    if ANSWER_REQUIRED_HEADING not in answer:
        problems.append(f"answer needs a heading starting {ANSWER_REQUIRED_HEADING!r} listing every estimate and assumption")
    for pattern, label in ANSWER_BANNED:
        if re.search(pattern, question):
            continue
        hits = sorted({m.group(0) for m in re.finditer(pattern, answer)})
        if hits:
            problems.append(f"answer contains {label}: {', '.join(hits[:6])}. Move it to the audit")
    return problems


def audit_problems(audit):
    problems = []
    if AGREEMENT not in audit:
        problems.append(f"audit missing the exact sentence: {AGREEMENT}")
    for heading in AUDIT_HEADINGS:
        if heading not in audit:
            problems.append(f"audit missing heading {heading}")
    return problems


def cmd_finish(a):
    led = load(a.run)
    require_phase(led, a.run, "synthesize")
    answer = read_input(a.answer_file)
    audit = read_input(a.audit_file)
    problems = answer_problems(answer, led["question"]) + audit_problems(audit)
    if problems:
        raise HarnessError("; ".join(problems))
    run = run_path(a.run)
    (run / "answer.md").write_text(answer)
    (run / "audit.md").write_text(audit)
    led["phase"] = "done"
    led["stopped"]["complete"] = True
    led["finished_at"] = now()
    save(a.run, led)
    errors = validate_ledger(led, run)
    print(f"finished: answer {run / 'answer.md'} ({len(answer.split())} words), audit {run / 'audit.md'}")
    print("validate: OK" if not errors else "validate: " + "; ".join(errors))


def validate_ledger(led, run):
    errors = []
    caps = led["caps"]
    if led["phase"] not in PHASES:
        errors.append(f"unknown phase {led['phase']}")
    if led["agents"]["spent"] > caps["max_agents"]:
        errors.append(f"over budget: spent {led['agents']['spent']} of {caps['max_agents']}")
    if led["agents"]["reserved"] < 0:
        errors.append("reserved went negative")
    if led["phase"] == "done" and led["agents"]["reserved"] != 0:
        errors.append(f"{led['agents']['reserved']} agents still reserved at finish")
    ids = [i["id"] for i in led["items"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate item ids")
    if len(led["waves"]) > caps["max_waves"]:
        errors.append("more waves than max_waves")
    for w in led["waves"]:
        if len(w["items"]) > MAX_LEADS:
            errors.append(f"wave {w['n']} has {len(w['items'])} leads")
        if w["workers_per_lead"] > MAX_WORKERS:
            errors.append(f"wave {w['n']} allowed {w['workers_per_lead']} workers per lead")
    for it in led["items"]:
        if it["status"] not in ITEM_STATUS:
            errors.append(f"{it['id']} has status {it['status']}")
        if it["kind"] == "branch":
            if not 1 <= it["depth"] <= caps["max_waves"]:
                errors.append(f"{it['id']} depth {it['depth']} outside 1..{caps['max_waves']}")
            if led["claim_index"].get(it["claim_key"]) != it["id"]:
                errors.append(f"{it['id']} missing from claim_index")
        if len(it["children"]) > MAX_CHILDREN_PER_PARENT:
            errors.append(f"{it['id']} has {len(it['children'])} children")
        if it["status"] == "done":
            if not it["result"]:
                errors.append(f"{it['id']} done without a result")
            elif it["result"]["workers_used"] > (it["allowance"] or 0):
                errors.append(
                    f"{it['id']} overspent: {it['result']['workers_used']} workers, {it['allowance']} allowed"
                )
    done_ids = {i["id"] for i in led["items"] if i["status"] == "done"}
    for c in led["criteria"]:
        if c["status"] == "met" and not (set(c["evidence"]) & done_ids):
            errors.append(f"{c['id']} met without a done branch as evidence")
    if led["phase"] == "done":
        run = Path(run)
        answer, audit = run / "answer.md", run / "audit.md"
        if answer.exists() or audit.exists():
            missing = [p.name for p in (answer, audit) if not p.exists()]
            errors += [f"{name} missing" for name in missing]
            if not missing:
                errors += answer_problems(answer.read_text(), led["question"])
                errors += audit_problems(audit.read_text())
        elif not (run / "synthesis.md").exists():
            errors.append("answer.md and audit.md missing")
        elif AGREEMENT not in (run / "synthesis.md").read_text():
            errors.append("synthesis.md lacks the agreement sentence")
    return errors


def cmd_validate(a):
    led = load(a.run)
    errors = validate_ledger(led, run_path(a.run))
    if errors:
        for e in errors:
            print(f"error: {e}")
        raise SystemExit(1)
    print("OK")


def launch_line(path):
    return (
        f"You are an angles agent. Read {path} with your Read tool and follow it exactly. "
        "Your final message must be only the JSON object that file asks for."
    )


def short(text, limit=220):
    text = re.sub(r"\s+", " ", str(text)).strip()
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    if " " in cut[limit // 2:]:
        cut = cut[: cut.rindex(" ")]
    return cut.rstrip(" ,;:") + "…"


def cmd_status(a):
    led = load(a.run)
    caps, agents = led["caps"], led["agents"]
    wave = current_wave(led)
    wave_text = f"wave {wave['n']} {wave['status']}" if wave else "no wave yet"
    print(f"phase: {led['phase']} | {wave_text} | max waves {caps['max_waves']}")
    reserve = caps["challenge_reserve"] if led["challenge"] is None else 0
    print(
        f"agents: spent {agents['spent']}, reserved {agents['reserved']}, available {available(led)}, "
        f"challenge reserve {reserve}, max {caps['max_agents']}"
    )
    if led["plan"]:
        print(f"goal: {short(led['plan']['goal'], 400)}")
        for c in led["plan"].get("constraints") or []:
            print(f"  constraint: {short(c, 200)}")
    if led["criteria"]:
        print("criteria:")
        for c in led["criteria"]:
            ev = f" (evidence {', '.join(c['evidence'])})" if c["evidence"] else ""
            print(f"  {c['id']} [{c['status']}] {short(c['text'], 200)}{ev}")
    if led["state"]:
        print(f"state: {short(led['state'], 600)}")
    frontier = ordered_frontier(led)
    if frontier:
        print("frontier, in the order the next wave picks:")
        for it in frontier:
            parent = f" <- {it['parent']}" if it["parent"] else ""
            print(f"  {it['id']} d{it['depth']}{parent} [{', '.join(it['criteria']) or '-'}] {short(it['text'], 160)}")
    if wave:
        print(f"wave {wave['n']} returns:")
        for iid in wave["items"]:
            it = get_item(led, iid)
            r = it["result"]
            if not r:
                print(f"  {iid} {it['status']}{': ' + it['error'] if it['error'] else ''}")
                continue
            print(
                f"  {iid} {it['status']} | workers {r['workers_used']}/{it['allowance']} | "
                f"had_task {r['had_task']} | settled {r['settled']}"
            )
            print(f"    branch: {short(it['text'], 160)}")
            print(f"    summary: {short(r['summary'], 700)}")
            for f in r["findings"]:
                kind = f.get("kind", "reasoning")
                print(
                    f"    - [{f['confidence']}, {kind}] {short(f['claim'], 400)} (basis: {short(f['basis'], 140)})"
                )
            for p in r["criteria_progress"]:
                print(f"    {p['criterion']} {p['status']}: {short(p['note'], 160)}")
            for o in r["open_items"]:
                print(f"    proposes [{', '.join(o['criteria']) or '-'}] {short(o['text'], 200)} — {short(o['why'], 140)}")
            if r["notes_path"]:
                print(f"    notes: {r['notes_path']}")
            for w in it["warnings"]:
                print(f"    warning: {w}")
    ch = led["challenge"]
    if ch and ch.get("item"):
        it = get_item(led, ch["item"])
        print(f"challenge: {ch['status']}")
        if it["result"]:
            print(f"  summary: {short(it['result']['summary'], 600)}")
            for g in it["result"].get("question_gaps") or []:
                print(f"  question gap: {short(g, 300)}")
            for c in it["result"]["challenges"]:
                print(f"  - [{c['severity']}] {short(c['claim'], 200)}: {short(c['problem'], 300)}")
    elif ch:
        print(f"challenge: {ch['status']} ({ch.get('reason', '')})")
    if led["deferred"]:
        print("deferred by caps:")
        for d in led["deferred"][-12:]:
            print(f"  {short(d['text'], 160)} ({d['reason']})")
    if led["stopped"]["reasons"]:
        print(f"stop reasons: {', '.join(led['stopped']['reasons'])}")
    if a.tree:
        print("tree:")
        children = {}
        for it in led["items"]:
            if it["kind"] == "branch":
                children.setdefault(it["parent"], []).append(it)

        def walk(parent, indent):
            for it in sorted(children.get(parent, []), key=lambda i: id_number(i["id"])):
                print(f"{'  ' * indent}{it['id']} [{it['status']}] {short(it['text'], 140)}")
                walk(it["id"], indent + 1)

        walk(None, 1)
    print(f"Next: {next_action(led, a.run)}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="angles.py", description="Ledger for the angles harness.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="create a run")
    s.add_argument("run")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--question")
    g.add_argument("--question-file")
    s.add_argument("--depth", type=int, help="max waves")
    s.add_argument("--nodes", type=int, help="max agents")
    s.add_argument("--force", action="store_true")

    s = sub.add_parser("plan", help="record goal, criteria, first branches")
    s.add_argument("run")
    s.add_argument("--file", required=True)

    s = sub.add_parser("next", help="dispatch the next wave")
    s.add_argument("run")
    s.add_argument("--leads", type=int)
    s.add_argument("--workers", type=int)

    s = sub.add_parser("ingest", help="record one lead or challenger reply")
    s.add_argument("run")
    s.add_argument("item")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--file")
    g.add_argument("--failed")

    s = sub.add_parser("integrate", help="fold a returned wave into the plan")
    s.add_argument("run")
    s.add_argument("--file", required=True)

    s = sub.add_parser("challenge", help="dispatch the challenger")
    s.add_argument("run")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--draft-file")
    g.add_argument("--skip")

    s = sub.add_parser("finish", help="record the answer and its audit")
    s.add_argument("run")
    s.add_argument("--answer-file", required=True)
    s.add_argument("--audit-file", required=True)

    s = sub.add_parser("status", help="show state and the next action")
    s.add_argument("run")
    s.add_argument("--tree", action="store_true")

    s = sub.add_parser("validate", help="check ledger invariants")
    s.add_argument("run")

    a = p.parse_args(argv)
    handlers = {
        "init": cmd_init,
        "plan": cmd_plan,
        "next": cmd_next,
        "ingest": cmd_ingest,
        "integrate": cmd_integrate,
        "challenge": cmd_challenge,
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
