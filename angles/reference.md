# Angles reference

The script `scripts/angles.py` owns the ledger, the caps, and the lead and challenger prompts. This file covers the files the planner writes and what the script checks.

## plan.json

```json
{
  "goal": "what the user needs, in one or two sentences",
  "approach": "optional: how you intend to break it down",
  "criteria": [
    "a checkable statement of done",
    "another one"
  ],
  "items": [
    {"text": "a branch to run", "why": "what it unlocks", "criteria": ["C1"]},
    {"text": "another branch", "why": "...", "criteria": ["C2", "C3"]}
  ]
}
```

Criteria become `C1`, `C2`, and so on, in order. There are 1 to 6 criteria and 1 to 6 items. Branches become `T1`, `T2`, and so on. A branch whose text matches an existing branch, after lowercasing and dropping punctuation and common words, is refused as `duplicate_item`.

Good criteria can be checked by someone who was not in the run. "The rollback cost is estimated with its main drivers" is a criterion. "Think about rollback" is not.

## integrate-N.json

```json
{
  "state": "the current answer as it stands, in 200 words or fewer",
  "criteria": [
    {"id": "C1", "status": "met", "evidence": ["T1", "T4"], "note": "why"},
    {"id": "C3", "status": "unmeetable", "evidence": [], "note": "needs data we cannot get"}
  ],
  "drop": [{"id": "T6", "reason": "made moot by T2"}],
  "new_items": [
    {"text": "the next branch", "why": "the gap it closes", "criteria": ["C2"], "parent": "T2"}
  ]
}
```

- `state` is required. The next leads receive it as what the planner knows so far.
- `met` needs at least one finished branch in `evidence`. Otherwise the criterion stays open and the script warns.
- `drop` applies only to branches that have not run.
- `parent` must be a finished branch. Use `null` for a new top-level branch. Depth is the parent's depth plus 1 and may not exceed the wave cap.
- Refusals: `duplicate_item`, `empty_item`, `unknown_parent`, `parent_not_done`, `depth_exhausted`, `breadth_cap` (the parent already has 3 children), `layer_cap` (6 new branches already opened in this integration). The three cap refusals are kept on a deferred list, shown to later leads, and belong in the synthesis.

## Lead reply

The script writes this schema into every lead prompt. Findings are capped at 6 and proposals at 3. Confidence is `low`, `medium`, or `high`. `workers_used` is required. Anything that is not valid JSON counts as a failed attempt. A branch gets one retry in a later wave, then stays failed.

```json
{
  "item_id": "T1",
  "summary": "what this branch established",
  "findings": [{"claim": "...", "basis": "...", "confidence": "medium", "source": "..."}],
  "criteria_progress": [{"criterion": "C1", "status": "met|partial|none", "note": "..."}],
  "open_items": [{"text": "...", "why": "...", "criteria": ["C1"]}],
  "settled": false,
  "workers_used": 2,
  "had_task": true,
  "notes_path": "/tmp/angles.X/notes/T1.md"
}
```

Leads and workers write full notes under `R/notes/`. Replies stay short so the planner's context stays small.

## Challenger reply

```json
{
  "item_id": "X1",
  "summary": "...",
  "challenges": [{"claim": "...", "problem": "...", "severity": "breaks|weakens|ok", "basis": "..."}],
  "workers_used": 2,
  "had_task": true,
  "notes_path": "..."
}
```

## Budget

Each wave gets the agents still available divided by the waves left, with a floor of 6, and the last wave gets everything left. Within a wave, the number of leads is the wave budget divided by 3, capped at 3 and at the number of open branches. Each lead's worker allowance is what is left, split evenly and capped at 3. Agents are reserved when a wave is sent and settled when each reply is ingested.

At the defaults of 48 agents and 4 waves, a run can send 3 leads with 3 workers each, then 3 leads with 2 each, and so on. Pass `nodes=24` for a cheaper run with fewer workers per lead.

The next wave takes branches that serve the most open criteria first, then shallower ones, then older ones. It alternates between parents, so one branch's children cannot fill a wave by themselves.

## Synthesis template

```markdown
# Angles synthesis

## Question
<the question verbatim>

## Answer
<the answer, with each load-bearing claim followed by the branch ids behind it>

## Criteria
<each criterion, its status, and its evidence>

## Divergences
<disagreements left standing>

## Challenge
<what the challenger tried, what broke, what weakened, and what changed because of it>

## Open questions
<unmet criteria, failed branches, deferred and unexplored branches>

## Run
<run dir, waves, agents spent of the cap, stop reasons>

Agreement among nodes is not evidence.
```

`finish` refuses a synthesis without `## Answer`, `## Challenge`, `## Open questions`, and that exact sentence. If the challenge was skipped, say why under `## Challenge`.
