# Angles reference

The script `scripts/angles.py` owns the ledger, the graph, the budget, and every prompt. Agents write their replies to `R/returns/<id>.md`: the substance in prose first, then one ```` ```json ```` fence that classifies it. The fence drives the graph. The prose is the reasoning that pieces above it and the writer read. A fence at the top still ingests. After ingest, each reply moves to `R/returns/archive/`.

## Ids

| Id | Agent |
|----|-------|
| `F1` | framer |
| `Q-n` | a piece of the question; the agent that settles it has the same id |
| `M<k>` | matcher |
| `W1` | writer |
| `X1` | challenger |
| `W2` | reviser |

## Framer header

```json
{"id": "F1", "status": "framed",
 "terms": [{"term": "...", "meaning": "...", "flag": "what is wrong with how the question uses it, or empty"}],
 "assumptions": ["hidden assumptions in the framing"],
 "real_question": "...",
 "crux": "...",
 "constraints": ["deadlines, who is available, what must not break"],
 "questions": [{"key": "A", "text": "...", "kind": "fact|judgment", "depends_on": ["B"], "why": "..."}],
 "root": "A"}
```

3 to 14 questions. Unknown keys in `depends_on` fail the reply. Edges that would form a cycle are dropped with a warning. A question with no parent is attached to the root.

## Piece header

```json
{"id": "Q-4", "status": "resolved|blocked|reframe",
 "resolution": "150 words or fewer, standalone",
 "confidence": "low|medium|high",
 "rests_on": ["Q-5", "assumption: ..."],
 "needs": [{"question": "...", "why": "..."}],
 "reframe": {"text": "the better question", "why": "..."},
 "reject": [{"id": "Q-5", "reason": "..."}]}
```

What the script does with it, in this order:

1. **reject** a settled dependency: that dependency goes back with the objection, and this piece waits and reruns with its earlier work. Each piece can be sent back once. Rejects are ignored while converging.
2. **reframe**: the piece's text is replaced and it reruns. Once per piece. A second reframe forces it to settle as stated.
3. **blocked** with needs (at most 4): the needs go to the matcher and the piece waits. After 4 passes, or with no needs, it is forced to settle.
4. Otherwise the piece is **resolved**. A resolution is required. If the piece had been sent back, every piece that already built on its old answer is sent back once to recheck.

A missing or invalid reply is a failure. A piece gets two tries, then is marked failed, and pieces above it are told to assume in its place.

## Matcher header

```json
{"id": "M1", "status": "matched",
 "links": [{"need": "N1", "to": "Q-4"},
           {"need": "N2", "new": {"text": "...", "kind": "fact"}},
           {"need": "N3", "same_as": "N2"}]}
```

A link to an existing piece that would form a cycle, and a new piece past `max_nodes` or `max_depth`, are refused. The asking piece is then told to proceed and state its assumption. A need the matcher skips becomes a new piece with the need's own wording.

## Writer and reviser header

The writer writes the answer to `R/answer-draft.md`. The reviser overwrites it; the previous version is kept in `R/drafts/`.

```json
{"id": "W1", "status": "written",
 "claim_map": [{"claim": "...", "from": ["Q-2", "Q-5"]}],
 "changes": [{"challenge": "only for W2", "change": "..."}]}
```

## Challenger header

```json
{"id": "X1", "status": "challenged",
 "question_gaps": ["..."],
 "challenges": [{"claim": "...", "problem": "...", "severity": "breaks|weakens|ok", "basis": "..."}]}
```

Checks: every part of the question answered, the riskiest step against the constraints, unsourced numbers, dangling references, consistency of every derived number, duration, date, and category, and an attack on the two or three load-bearing claims.

## Scheduling

Ready pieces are those whose dependencies are all settled and that have no request waiting on the matcher. They launch deepest first, facts before judgments, up to 6 per step. A matcher launches in the same step whenever requests are waiting. The root settling moves the run to writing.

## Budget

| Role | Weight | Default model | Estimate |
|------|--------|---------------|----------|
| framer | 1.5 | composer-2.5-fast | $0.38 |
| fact leaf | 1 | composer-2.5-fast | $0.25 |
| judgment leaf | 1 | composer-2.5-fast | $0.25 |
| piece that builds on others | 1 | composer-2.5-fast | $0.25 |
| matcher | 0.5 | composer-2.5-fast | $0.13 |
| writer | 1.5 | composer-2.5-fast | $0.38 |
| challenger | 1 | composer-2.5-fast | $0.25 |
| reviser | 1 | composer-2.5-fast | $0.25 |

Base cost per agent: `composer-2.5-fast` $0.25, any other model $0.40. Every subagent uses Composer unless a run is started with `--cheap` or `--strong`. An agent's cost is reserved at launch and moved to spent at ingest. The ending (writer, challenger, reviser) is held back from the start. Free budget is the limit minus spent, in flight, and the held ending.

The run converges when the free budget is less than the estimated cost of every pending piece plus a matcher, or when the piece cap is reached. While converging: requests waiting for the matcher become stated assumptions, no matcher runs, and every piece is told to settle now. If nothing is ready, the deepest stuck piece drops its unsettled dependencies as assumptions and runs. If the budget cannot cover even that, every unsettled piece is marked failed and the writer works from what is settled.

A typical run of 8 to 12 pieces with a few passes costs $4 to $7 in estimates.

## Answer lint

`finish` refuses an answer that lacks a heading starting `## Assumptions` or `## What would change this`, or that contains piece ids (`Q-3`), agent ids (`F1`, `M2`, `W1`, `W2`, `X1`), audit headings (Claim map, Graph, Challenge, Run, Audit, Terms used), or harness words (the framer, the matcher, integrator, the challenger, the reviser, ledger, notes file, whiteboard, angles, "this run" or "the run"). A pattern is skipped when the question itself contains it.

## Audit

The script writes `audit.md` at finish: the framing (real question, crux, terms and flags, constraints, hidden assumptions), the graph with each resolution and which pieces are shared, every change to the graph (blocks, links, rejections, rechecks, reframes, assumptions), the claim map, the challenge and what changed because of it, the unsettled pieces, estimated spend by role and model, and the sentence: Agreement among nodes is not evidence.
