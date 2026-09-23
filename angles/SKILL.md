---
name: angles
description: >-
  Works a question or goal as a planner-led tree of agents. The invoking agent
  plans, sends branch leads that run their own workers, folds their reports
  back in, and picks the next wave until done criteria are met or caps stop it,
  then has the draft challenged. Use when the user invokes angles, asks for
  every angle, or asks for exhaustive exploration of a problem, question, or
  goal. Explicit invoke only.
disable-model-invocation: true
---

# Angles

You are the planner. You hold the whole picture: the goal, what done means, what is known, and what to do next. You do not work branches yourself. If you need a fact, make it a branch.

## Shape

| Level | Who | Spawns |
|-------|-----|--------|
| Planner | you, the invoked agent | branch leads |
| Branch lead | a direct subagent | up to 3 workers |
| Worker | a subagent of a lead | nothing. Cursor gives it no Task tool |

Those are three real levels. Deeper work comes from waves: each wave's reports produce the next wave's branches, and each branch knows the goal, the current answer, its siblings, and what is already covered.

If you are yourself running as a subagent, your leads get no Task tool and will work alone. Tell the user.

## Model

Every Task call uses model `composer-2.5-fast`: leads, workers, and the challenger. Leads are told to use it for their workers.

## Caps

`depth=N` sets the maximum number of waves (default 4). `nodes=N` sets the maximum number of agents (default 48). Every lead, worker, and challenger counts toward it. The planner does not. These are fixed: 3 leads per wave, 3 workers per lead, 3 children per branch, 6 new branches per integration. The script spreads the budget across the remaining waves and holds 3 agents for the challenge.

## The script

Every ledger change goes through `~/.agents/skills/angles/scripts/angles.py`. Never edit `ledger.json` by hand. Every command prints `Next:` with the exact next step. If a command errors, read the error and fix the input. Do not work around it.

Below, `S` is that script and `R` is the run directory.

## Loop

1. **Start.** `R=$(mktemp -d /tmp/angles.XXXXXX)`. Tell the user `R`. Write the user's question verbatim to `R/question.txt`, then `python3 S init R --question-file R/question.txt`. Add `--depth N` or `--nodes N` only when the user wrote `depth=N` or `nodes=N`.
2. **Plan.** Write `R/plan.json`: the goal, the hard constraints the question sets (deadlines, who is available, money or data that must not break), 2 to 5 done-when criteria someone could check, and 2 to 6 first branches, each tied to the criteria it serves. Every lead, worker, and the challenger sees the constraints, because a branch that only sees its own slice will optimize against them. Then `python3 S plan R --file R/plan.json`. This is your map of the whole problem. Do not investigate yet. Format: [reference.md](reference.md).
3. **Wave.** `python3 S next R`. Launch every listed lead in one message: Task, subagent_type `generalPurpose`, model `composer-2.5-fast`, prompt = the launch line the script prints for that lead. The launch line points the lead at its full prompt file, so do not paste the file. If a lead says it could not read the file, relaunch it with the file content as the prompt. Save each reply verbatim to `R/returns/<id>.txt`, then `python3 S ingest R <id> --file R/returns/<id>.txt`. If a Task call errors, run `python3 S ingest R <id> --failed "<error>"` instead.
4. **Pull up.** `python3 S status R` shows every finding, proposal, and warning from the wave. Write `R/integrate-<n>.json`: the current answer in `state`, criteria updates, branches to drop, and `new_items`, each with a parent. Choose new items from the leads' proposals and from gaps you see. Merge duplicates in different words yourself. A proposal only the user can act on, such as reading their own contract or production data, is an open question for the answer, not a branch. Before marking a criterion met, open the evidence branch's notes and check that the claimed table or list is there, and that it is in the finding itself so it can reach the answer. Then `python3 S integrate R --file R/integrate-<n>.json`. This is where the plan changes.
5. **Repeat** steps 3 and 4 until the script reports a stop.
6. **Challenge.** Write the draft to `R/draft.md` as the answer you would ship, following the answer rules below, run `python3 S challenge R --draft-file R/draft.md`, launch the challenger with its launch line the same way, save the reply to `R/returns/X1.txt`, and `python3 S ingest R X1 --file R/returns/X1.txt`. The challenger rereads the question, tests the riskiest step against the constraints, and flags unsourced numbers and references to things the draft does not contain.
7. **Synthesize.** Write two files from the templates in [reference.md](reference.md): `R/answer-draft.md`, the only thing the user reads, and `R/audit-draft.md`, the record of how the run got there. Then `python3 S finish R --answer-file R/answer-draft.md --audit-file R/audit-draft.md`. It refuses an answer that leaks the run's bookkeeping or lacks an assumptions section.
8. **Report.** `python3 S validate R`. Give the user the answer from `R/answer.md` first. Then, briefly, the run path, waves run, agents spent, what the challenge broke, and what stayed open. Keep this sentence exact: Agreement among nodes is not evidence.

## Answer rules

The tree's value only reaches the user through `answer.md`. Most of the quality is lost or kept here.

- **Answer the question as asked.** Reread it word for word before writing. Answer every part directly, in its own words. Criteria being met does not mean the question is answered. Fix every `question_gaps` entry from the challenger.
- **Carry the substance, not a pointer to it.** If a branch built the list of failure modes or the comparison table, the answer contains that list or table in compact form. Never write "six failure modes were identified" without the six.
- **Keep the hedges.** Every number that is not given in the question either carries its basis inline or is listed under `## Assumptions and estimates` with its range and the assumption behind it. Thresholds with no measured baseline are labeled as starting defaults.
- **Respect the constraints.** Name the riskiest step you recommend and why it fits the constraints. When a safer option meets the goal, recommend it.
- **Simplest plan that works.** Keep only the gates, phases, and roles that change a decision. The tree tends to add structure. Cut it.
- **No bookkeeping.** No branch or criterion ids, no coverage or challenge sections, no words about the harness. That all goes in `audit.md`.
- **Lead with the decision**, then the plan, then the reasoning a reader needs to trust it.

To resume an interrupted run, `python3 S status R` gives the phase and the next step.

## Stops

A run stops when every criterion is met or marked unmeetable, when no branch is left, when the waves or agents run out, or after two waves in a row that settle no criterion and open no branch. After a stop it goes to the challenge, then to the answer and audit.

## Planner rules

- A criterion is met only when a finished branch is its evidence. The script enforces this.
- If the challenger marks a claim `breaks`, change the answer. If you keep it, say why in the answer itself, not only in the audit.
- Keep your own context small. Read `status` and the returns. Open a notes file only when a return is unclear.
- A lead that reports more workers than it was allowed is charged for all of them and flagged by `validate`. Say so in the report.
- A failed launch is charged the lead plus its full worker allowance, because workers may have run.

## Other skills

| Need | Skill |
|------|--------|
| A planner-led tree of agents on one question or goal | angles |
| Whether a claim is supported | reason |
| A session plan before other work | delegate |
| A cross-chat fleet | orchestrate |

File formats, the answer and audit templates, and the budget math: [reference.md](reference.md).
