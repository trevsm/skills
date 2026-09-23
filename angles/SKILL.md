---
name: angles
description: >-
  Works a hard question as a graph of smaller questions, settled bottom-up the
  way a careful person reasons: pin down terms and premises first, settle the
  pieces they unlock, then the real question. Pieces can ask for missing
  dependencies, send weak ones back, or say they are framed wrong; shared
  dependencies are settled once. Every subagent runs on Composer 2.5 Fast.
  Use when the user invokes angles,
  asks for every angle, or asks for exhaustive work on a hard problem, question,
  or goal. Explicit invoke only.
disable-model-invocation: true
---

# Angles

You run a loop. You do not think about the question. The script decides what runs next, writes every agent's prompt, reads every agent's reply from disk, and keeps the budget. Your job is to launch what it prints, wait, and ingest. That keeps your context small, and it is most of what keeps a run cheap.

## How it works

1. **Frame.** One agent pins down the terms, flags category errors and hidden assumptions, restates the real question, names the likely crux, lists the hard constraints, and lays out the question as a graph: the root depends on pieces, which depend on smaller pieces, down to leaves one agent can settle. Two pieces that need the same thing share one piece.
2. **Settle bottom-up.** A piece runs once everything it rests on is settled, deepest first, up to 6 at once. Each agent is asked its question in ordinary language, with the situation and the settled answers under it, and answers in prose. At the end it classifies its own answer: settled, missing something, a dependency that does not hold, or a question framed wrong. The outcomes are:
   - **blocked**, naming what it needs. A matcher links each need to an existing piece when it is the same question, or makes a new piece. The blocked piece runs again once that is settled, with its earlier work.
   - **reject**, on a weak dependency. That piece goes back once with the objection. Anything that already built on it is sent back once to recheck against the revision.
   - **reframe**, when its question is framed wrong. Once per piece.
   A piece that still contains two claims that could fail separately asks for them to be split. A piece that affirms or denies a claim has to mark that reply as a verdict. The script refuses the verdict unless a rescue piece is already settled underneath it, and it creates that piece: the strongest account on which the claim still holds, with no verdict. The rescue piece states the account and stops. The claim then answers it. Pieces above check that the claim answered its rescue. They steelman only the inference they are drawing, not the claim again.
3. **Converge.** When the free budget no longer covers the rest of the graph, no new pieces are made, and every remaining piece must settle on stated assumptions. A request that would create a loop or break a cap also becomes a stated assumption.
4. **Write, challenge, revise.** A writer turns the settled graph into the answer. A challenger rereads the question, tests the riskiest step, checks numbers and dates for consistency, and attacks the load-bearing claims. A reviser fixes what it found.
5. **Finish.** The script checks the answer for leaked bookkeeping and required sections, and builds `audit.md` itself from the graph.

## Models and budget

Every subagent runs on `composer-2.5-fast`: the framer, every piece, the matcher, the writer, the challenger, and the reviser. Launch with the model the script prints. That model is Composer unless the user names a different one.

The budget is in estimated dollars, $8 by default. The script holds back enough for the writer, challenger, and reviser from the start, so a run always ends with an answer. Estimates are rough, about $0.25 per agent before role weight. They are not a bill.

User overrides: `budget=N` becomes `--budget N`, `nodes=N` becomes `--max-nodes N`, `depth=N` becomes `--max-depth N`. `cheap=<model>` and `strong=<model>` override the model only when the user names one.

## The loop

`S` is `~/.agents/skills/angles/scripts/angles.py` and `R` is the run directory. Every command prints `Next:` with the exact next step. If a command errors, read the error and fix the input. Never edit `ledger.json` by hand.

1. `R=$(mktemp -d /tmp/angles.XXXXXX)`. Tell the user `R`. Write the user's question verbatim to `R/question.txt`, then `python3 S init R --question-file R/question.txt` with any overrides.
2. `python3 S next R`. It prints one launch line per agent. Launch all of them in one message: Task, subagent_type `generalPurpose`, `model` as printed, prompt = the launch line exactly. Do not paste prompt files or add context.
3. When every agent has replied, run `python3 S ingest R`. It reads each reply file from `R/returns/`. If an agent's Task call errored, or it replied without writing its file, relaunch it once. If it fails again, run `python3 S ingest R --failed <id> --reason "<error>"`.
4. Repeat steps 2 and 3 until `Next:` says to finish. Use `python3 S status R` to see the graph at any time.
5. `python3 S finish R`. If it refuses the answer, fix `R/answer-draft.md` exactly as the error says, and nothing else, then run finish again.
6. Report. Give the user `R/answer.md` in full, first. Then say briefly: the run path, how many pieces and agents, the estimated spend, any term the framing corrected, what the challenge broke, and what stayed open. The audit is at `R/audit.md`. Keep this sentence exact: Agreement among nodes is not evidence.

`python3 S assume R <piece> --text "..."` settles a stuck piece with a stated assumption. Use it only when the user supplies the fact, or a piece has failed and the user wants to proceed.

To resume an interrupted run, `python3 S status R` shows the phase and the next step.

## Rules

- Do not read the returns or prompt files unless something is broken. Reading them fills your context and costs more than the agents.
- Do not answer from your own knowledge, and do not add findings. If you know a fact that matters, tell the user and let them decide whether to restart with it in the question.
- If you are running as a subagent yourself, you cannot launch agents. Tell the user and stop.

## Other skills

| Need | Skill |
|------|--------|
| A hard question worked as a graph of agents | angles |
| Whether a claim is supported | reason |
| A session plan before other work | delegate |
| A cross-chat fleet | orchestrate |

Reply formats, the answer lint, the audit, and the budget math: [reference.md](reference.md).
