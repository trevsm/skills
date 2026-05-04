---
name: crucible
description: Vertical-slice test-driven development for prose claims. Hardens a thesis against adversarial objections one cycle at a time using adversary, proponent, and judge subagents; produces a regression-checkable transcript of which objections the thesis has survived. Use when the user says "crucible this thesis", "put this through the crucible", "engage crucible", "harden this argument", "stress-test this claim", "tdd this argument", or wants to subject a load-bearing technical, strategic, policy, or philosophical claim to the same RED/GREEN/refactor discipline as smart-mode's Phase 3.
---

# Crucible

Crucible is test-driven development for prose claims. It treats a thesis as the public interface, objections as tests, replies as minimal implementations, and the transcript as the regression suite. The loop is Lakatos-flavored: conjecture, counterexample, revision, re-test.

The user is the thesis owner. The agent orchestrates adversarial pressure, records the artifacts, and surfaces trade-offs instead of quietly weakening the thesis.

## Failure Modes

Crucible exists to guard against four failures common to LLM-assisted argumentation:

1. **Sycophancy** - the model agrees with the thesis-holder instead of testing them. Fixed by separating adversary, proponent, and judge roles.
2. **Drift** - the thesis quietly changes to survive objections. Fixed by explicit `THESIS.md` invariants and regression checks.
3. **Monster-barring** - definitions get gerrymandered to exclude hard cases. Fixed by `LAKATOS-CHEATS.md` and judge review.
4. **Argument sprawl** - many shallow points replace a few deep commitments. Fixed by vertical cycles and `COMMITMENTS.md`.

## When To Use

Use this skill for load-bearing, contested, or novel claims:

- Technical decisions: "We should adopt Rust for new backend services."
- Strategy or policy memos: "Usage-based pricing is the right packaging model."
- Philosophical theses: "Free will is incompatible with determinism."
- ADR drafts where the underlying claim needs adversarial hardening before implementation.

Do not use it for casual opinions, simple copy edits, code implementation, or bug/performance investigation. Use `smart-mode` for code design and `diagnose` for bugs.

## Vocabulary

Before running a cycle, read [LANGUAGE.md](LANGUAGE.md). Use its terms exactly: **Thesis**, **Objection**, **Reply**, **Defeater**, **Commitment**, **Granted arguendo**, **Suite**, **Drift**, **Convergence**.

## Suite Layout

Create or use a suite directory with this shape:

```
my-thesis/
  THESIS.md
  GLOSSARY.md
  TRANSCRIPT.md
  COMMITMENTS.md
  objections/
    001-example.md
  replies/
    001-example.reply.md
```

Use [THESIS-FORMAT.md](THESIS-FORMAT.md), [OBJECTION-FORMAT.md](OBJECTION-FORMAT.md), and [REPLY-FORMAT.md](REPLY-FORMAT.md). The worked examples in [examples](examples) are executable documentation.

## Cycle Protocol

Run vertical slices. One objection, one minimal reply, one adjudication, then regression. Do not generate a whole objection catalog before replying.

### 1. RED - Generate One Objection

Spawn an adversary subagent with [prompts/adversary.md](prompts/adversary.md). Provide:

- `THESIS.md`
- `GLOSSARY.md`
- existing objections
- any user-specified source material or tradition to prioritize

The adversary writes one strongest-available objection in `objections/NNN-slug.md`.

### 2. GREEN - Generate One Reply

Spawn a proponent subagent with [prompts/proponent.md](prompts/proponent.md). Provide:

- `THESIS.md`
- `GLOSSARY.md`
- `COMMITMENTS.md`
- the new objection

The proponent writes the smallest reply that satisfies the pass criteria. No speculative caveats. No undefined terms. Prefer <=200 words unless the objection format explicitly justifies more.

### 3. Adjudicate

Spawn three judge subagents in parallel with [prompts/judge.md](prompts/judge.md), preferably from different model families when the environment allows it. Provide:

- `THESIS.md`
- `GLOSSARY.md`
- the objection
- the reply
- [LAKATOS-CHEATS.md](LAKATOS-CHEATS.md)

Judges return one of: `PASS`, `FAIL`, `MONSTER-BARRED`, `DRIFT`, or `SPLIT`.

### 4. Regress

If the judges pass the reply, spawn a regression subagent with [prompts/regression.md](prompts/regression.md). Provide:

- all prior passing replies
- current `COMMITMENTS.md`
- the new reply's commitments

If regression passes, append the cycle to `TRANSCRIPT.md` and add deduplicated commitments to `COMMITMENTS.md`.

## Outcomes


| Outcome          | Trigger                                                          | Action                                                       |
| ---------------- | ---------------------------------------------------------------- | ------------------------------------------------------------ |
| `PASS`           | At least 2 of 3 judges pass, no cheat, no regression             | Append to transcript and update commitments                  |
| `FAIL`           | At least 2 of 3 judges fail                                      | Retry the reply up to 3 times, then return to the user       |
| `MONSTER-BARRED` | A judge cites an ad-hoc definition move and another judge agrees | Reject the reply; retry without that move                    |
| `DRIFT`          | Reply weakens or changes the thesis without editing `THESIS.md`  | Stop for human decision: revise thesis or revise reply       |
| `REGRESSION`     | New commitment contradicts a prior passing reply                 | Mark the conflict in transcript; reconcile before continuing |
| `SPLIT`          | No quorum or judges disagree on the failure type                 | Stop for human decision                                      |


## Transcript Format

`TRANSCRIPT.md` is append-only. Each entry should be short:

```markdown
## Cycle 003 - hiring-pool

- Objection: objections/003-hiring-pool.md
- Reply: replies/003-hiring-pool.reply.md
- Judges: PASS / PASS / FAIL
- Regression: PASS
- Outcome: PASS
- New commitments:
  - Rust hiring risk is acceptable only if adoption starts with a bounded service class and explicit training budget.
```

Never rewrite old cycles to make the thesis look cleaner. Add a correction entry instead.

## Convergence

Every 5-10 passing cycles, run a cold-adversary check with [prompts/cold-adversary.md](prompts/cold-adversary.md). The cold adversary sees the thesis and glossary, but not the existing objection list until after it proposes objections.

A suite is converged when a cold adversary fails to produce a novel objection above the chosen severity threshold after K attempts. Default: K=5, threshold=`medium`.

Record convergence in `TRANSCRIPT.md`:

```markdown
## Convergence Check - cycle 006

- Attempts: 5
- Novel objections above threshold: 0
- Result: converged at medium severity
```

Convergence is not certainty. It means this suite has stopped finding new high-value objections under the current adversary settings.

## Pre-Flight Checklist

Before each cycle:

```
- [ ] Read THESIS.md and confirm the scope and invariants
- [ ] Read GLOSSARY.md and enforce the vocabulary
- [ ] Read COMMITMENTS.md and prior passing replies
- [ ] Generate exactly one RED objection
- [ ] Generate exactly one minimal GREEN reply
- [ ] Run 3 judge subagents
- [ ] Run regression if judges pass
- [ ] Append TRANSCRIPT.md only after the outcome is known
```

## Composition

`smart-mode` can hand load-bearing ADR claims, contested interface decisions, or strategic technical recommendations to Crucible before implementation. Crucible returns a hardened thesis plus transcript; the resulting thesis can become the ADR's decision and consequences section.

`grill-with-docs` remains useful before Crucible when the domain language is fuzzy. Use it to clarify the thesis and glossary, then run Crucible cycles.

## Source

Crucible synthesizes ideas from Imre Lakatos's *Proofs and Refutations* (1976), Karl Popper's *Conjectures and Refutations* (1963), John Pollock's defeasible reasoning terminology, Daniel Dennett's Rapoport's rules, and Ryan Wright's "Dialectical Review" (2026). The vertical-slice RED/GREEN/refactor discipline is adapted from `smart-mode`'s TDD phase. This skill is original to this repo.