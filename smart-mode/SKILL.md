---
name: smart-mode
description: Engage a disciplined design-first workflow for AI-assisted software engineering. Right-sizes the workflow to the request (Phase 0 triages first; small changes skip phases, large ones run them all). Treats code as a critical asset; the user is the strategic architect, the agent is the tactical programmer. Use when the user says "smart mode", "engage smart mode", or asks for a rigorous, design-first approach to building with AI.
---

# Smart Mode

Code is not cheap; it is a critical asset. Reject the specs-to-code reflex — it produces unmaintainable systems and high technical debt.

The user is the strategic architect. The agent is the tactical programmer. Surface trade-offs; always make choices visible.

**Smart mode is an orchestrator.** It assesses scope first (Phase 0), then runs only the phases the request actually warrants. A typo fix does not get the same treatment as a new module.

## Active across all phases: evolve-skills + stay-sharp

[`../evolve-skills/SKILL.md`](../evolve-skills/SKILL.md) is active during every smart-mode session. It captures friction, corrections, and declared preferences to `~/.cursor/skills-journal/JOURNAL.md` and promotes patterns into `PREFERENCES.md` once thresholds are met. Smart-mode reads `PREFERENCES.md` at Phase 0 (see below) and runs end-of-session reflection at checklist completion.

You don't need to invoke evolve-skills manually for the capture behavior — it watches for strong signals (preference declarations, repeated corrections, dissatisfaction, debugging cycles) and writes inline with one-line announcements. To review or apply learnings, say `evolve review`, `evolve promote`, `evolve propose`, `evolve undo`, or `evolve reset`.

[`../stay-sharp/SKILL.md`](../stay-sharp/SKILL.md) is also active during every smart-mode session, but pointed in the opposite direction: evolve-skills adapts the agent to the user; stay-sharp keeps the user adapting to the craft. It captures competency signals (topic frequency, deferrals, thrashing, debugging cycles, concept misuse, vibes-driven decisions) to `~/.cursor/skills-journal/COMPETENCY-JOURNAL.md` and intervenes with commit-first quizzes when the user defers on a `must-know` topic. Smart-mode reads `MUST-KNOW.md` at Phase 0 (see below) and runs end-of-session reflection at checklist completion.

To review or interact with stay-sharp, say `stay-sharp review`, `quiz me on <topic>`, `i know this` (in-session bypass for a commit-first quiz), `tier <topic> as <must-know|should-know|aware-of>`, or `stay-sharp status`.

**Positive framing applies to grilling, too.** When the user states a preference during Phase 1 grilling, capture it positively: *"prefer X for Y"*, not *"never X"*. Negative constraints in agent context have been measured to fail 87.5% of the time and increase forbidden-behavior attention 4.4×. If the user phrases a preference negatively, ask one clarifying question to elicit the positive reframe before evolve-skills captures it. (See evolve-skills' positive-framing requirement for the worked examples.)

## Scope: when to engage smart-mode vs. a sister skill

Smart-mode is for **new feature work and non-trivial design**. For two adjacent situations, hand off to a sister skill:

- **Bug or performance investigation** → `../diagnose/SKILL.md`. Different feedback-loop discipline (build a deterministic repro, rank 3–5 falsifiable hypotheses, change one variable at a time). Smart-mode's TDD loop is wasteful here.
- **Periodic architecture rescue** of an existing codebase → `../improve-codebase-architecture/SKILL.md`. Run every few days to surface deepening opportunities. Smart-mode's Phase 4 designs *new* deep modules; this skill *retroactively* deepens existing shallow ones.

If Phase 0 classifies the request as either of the above, exit smart-mode and invoke the sister skill.

## The four failure modes smart-mode guards against

This is *why* the workflow exists. Each phase prevents one of these.

1. **The agent didn't do what you wanted.** Misalignment between request and result. Fixed by Phase 1 (grill).
2. **The agent is way too verbose.** No shared vocabulary, so 20 words do the work of 1. Fixed by Phase 2 (ubiquitous language).
3. **The code doesn't work.** No feedback loop, so the agent flies blind. Fixed by Phase 3 (TDD vertical slices).
4. **You built a ball of mud.** Agents accelerate entropy if you don't actively design. Fixed by Phases 4–5 (deep modules + interface-first).

If you can name which failure mode you're guarding against, you know which phase you actually need.

## Vocabulary

Definitions, anti-aliases, and the three load-bearing tests live in **[LANGUAGE.md](LANGUAGE.md)** — read it once; it's the contract for the rest of this skill.

Quick reference for the terms used throughout: **module · interface · implementation · depth · seam · adapter · leverage · locality**. Avoid drift into "component," "service," "API," "boundary," or "signature."

The three tests referenced repeatedly below: **deletion test · interface-is-test-surface · two-adapters-make-a-real-seam**.

---

## Phase 0 — Scope Assessment

**Do this first, every time, before grilling.** The agent assesses the request in one pass (no user interview yet) and announces which phases will run. This is what makes smart-mode safe to invoke for small changes.

### Read learned preferences and topic tiers

Before classifying, read `~/.cursor/skills-journal/PREFERENCES.md` and `~/.cursor/skills-journal/MUST-KNOW.md` if they exist. From `PREFERENCES.md`, note any entries under `## Smart-mode` or `## General`. From `MUST-KNOW.md`, note the tier of any topic this request touches. **Only mention preferences or tiers in the announcement that actually affected this particular classification, phase application, or anticipated intervention** — not the full lists. If nothing applied, the reads are silent (no mention in the announcement).

If either file does not exist, evolve-skills / stay-sharp will bootstrap them on first capture. Proceed without them for now.

### Assess

Read the request and (if needed) explore the codebase. Then classify on four axes:

| Axis | Levels |
|---|---|
| **Size** | trivial · surgical · feature · system |
| **Type** | build · refactor · bug-or-perf · docs-or-config |
| **Reversibility** | easy-to-undo · load-bearing · irreversible |
| **Novelty** | boilerplate · follows-existing-pattern · novel |

### Decide — pick a profile

Phase 0's output is **a single profile name**. The four-axis classification is the derivation; the profile is the commitment.

| Profile | Phases that run | Use for |
|---|---|---|
| `quick` | none — just do the change | Typo, doc edit, config tweak, comment. |
| `surgical` | P1 (light, 1–3 Qs) · P2 (reuse glossary) · P3 (regression test only, if touching tested code) | Bounded refactor in one place; single small change. |
| `feature` | P1 (brief) · P2 (reuse + extend) · P3 (full TDD) · P5 (light) — and P4 only if a new module is genuinely justified | New functionality; usually one or two modules touched. |
| `architectural` | P1 (full) · P2 (full) · P3 (full) · P4 (full) · P5 (full, with Design-It-Twice on contested interfaces) | New system, multi-module change, contested interfaces. |
| `bug-handoff` | exit smart-mode → invoke [`../diagnose/SKILL.md`](../diagnose/SKILL.md) | Bug or performance investigation. |
| `rescue-handoff` | exit smart-mode → invoke [`../improve-codebase-architecture/SKILL.md`](../improve-codebase-architecture/SKILL.md) | Retroactive deepening of an existing shallow codebase. |

The level words (`light` / `brief` / `full` for grilling, `reuse` / `extend` / `full` for glossary, etc.) are defined inside each phase section — the profile just names which level applies.

**Escalate one tier** when reversibility is `load-bearing` or `irreversible`, or when novelty is `novel` and the profile would otherwise be `surgical` or below. (`surgical → feature`, `feature → architectural`.)

### Announce (unless `quick`)

For any profile above `quick`, emit one line before proceeding:

> *"Phase 0: `feature`. Will run P1 brief, P2 extend, P3 full TDD, P5 light; skipping P4. Adjust?"*

Only mention a preference from `PREFERENCES.md` when it actually changed the profile:

> *"Phase 0: `surgical` (preference `prefer surgical for changes ≤30 LoC` applied; this is ~25 LoC). Adjust?"*

For `quick`, just do the change — no announcement.

If the user says "just do it" → drop one tier and execute silently. If they want more rigor → escalate one tier. **The user's word overrides the profile.** If a later phase reveals you misclassified, return to Phase 0 and announce the new profile before continuing.

---

## Phase 1 — Establish a Design Concept

Triggered when Phase 0 selected `light`, `brief`, or `full` for grilling.

**Delegate to `../grill-with-docs/SKILL.md`** — that skill is the canonical workhorse for this phase and Phase 2 combined. It:

- Walks the design tree one question at a time, with a recommended answer for each
- Challenges new claims against the existing glossary in `CONTEXT.md`
- Sharpens fuzzy terms inline
- Cross-references claims with the actual code
- Updates the glossary and (when warranted) ADRs as decisions crystallize

If Phase 0 selected `light` or `brief`, cap the grilling to 1–3 questions on the highest-leverage uncertainty — enough for surgical work.

If a question can be answered by exploring the codebase, explore instead of asking.

Exit when the problem, constraints, and shape of the solution are explicit.

---

## Phase 2 — Establish Ubiquitous Language

Triggered when Phase 0 selected `reuse`, `extend`, or `full` for glossary work. (For `reuse`, the agent only reads the glossary; it doesn't add to it.)

You and the user must mean the same thing by the same words. This drastically reduces verbosity and miscommunication.

**Glossary lookup order** (use the first one that exists):

1. `CONTEXT.md` at repo root (single context).
2. `CONTEXT-MAP.md` pointing to per-context `CONTEXT.md` files (multi-context repo).
3. `CLAUDE.md` at repo root — Claude Code convention. Read for any glossary section.
4. `AGENTS.md` at repo root — cross-agent convention. Read for any glossary section.
5. `docs/glossary.md` or any other project-specific glossary file.

**File-creation rule:**

- If `CLAUDE.md` or `AGENTS.md` exists with no glossary section, append a `## Glossary` section there — extend the existing file rather than introducing a parallel one.
- Match the project's existing convention: extend whichever file is already present (`CLAUDE.md` or `AGENTS.md`, not both).
- Default to `CONTEXT.md` for greenfield repos. Default to extending `CLAUDE.md` if the project is clearly a Claude Code workspace.
- **Create lazily** — only when the first domain term is resolved during the grilling session, not preemptively.

**Keep domain terms and user preferences separate.** This file (`CLAUDE.md` / `AGENTS.md` / `CONTEXT.md`) is for the *project's domain language* — terms a domain expert would recognize. *User behavioral preferences* ("skip Phase 1 grilling for changes ≤5 lines") belong in `~/.cursor/skills-journal/PREFERENCES.md`, managed by `evolve-skills`. Domain glossary travels with the codebase; preferences travel with the user. If during grilling the user states a behavioral preference, route it to evolve-skills' strong-signal trigger; the project glossary stays focused on domain language.

**Format:** see [`../grill-with-docs/CONTEXT-FORMAT.md`](../grill-with-docs/CONTEXT-FORMAT.md) for the full template (`## Language` with `**Term**: definition / _Avoid_: aliases`, plus `## Relationships`, `## Example dialogue`, `## Flagged ambiguities`).

**ADRs:** when the user rejects a candidate with a load-bearing reason, or a non-obvious technical trade-off is made, offer to record an ADR — but only if it passes Pocock's three-condition test (hard to reverse + surprising without context + result of a real trade-off). Format: see [`../grill-with-docs/ADR-FORMAT.md`](../grill-with-docs/ADR-FORMAT.md).

Use the resolved terms verbatim in code, comments, tests, commits, and conversation thereafter.

---

## Phase 3 — Test-Driven Development (Vertical Slices)

Triggered when Phase 0 selected anything other than `skip` for TDD.

Tests are the feedback loop that prevents the agent from outrunning its headlights.

**Anti-pattern: horizontal slicing** — writing all tests first, then all implementation. Produces tests of imagined behavior, coupled to the shape of data structures rather than user-facing behavior. They pass when behavior breaks and fail when behavior is fine.

**Correct pattern: vertical slices via tracer bullets.** One test → one implementation → repeat. Each cycle responds to what you learned from the previous one.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  ...
```

**Worked example.** Adding a points/streaks gamification feature to a course platform.

*Horizontal (wrong):* the agent writes all schema migrations first, then all service methods, then all UI. Nothing is exercisable end-to-end until the third pass; the first integration bug surfaces hours in.

*Vertical (right) — first cycle:*

1. **RED:** `awardPoints("user-1", "lesson-completed").totalPoints === 10`
2. **GREEN:** add the `points_events` table migration, write the minimal `awardPoints()` body, render a `Points: 10` pill on the dashboard.
3. **Refactor:** none yet.

One slice has touched the schema, the service, *and* the UI. The next cycle adds streaks; the one after adds level thresholds. Each is fully exercisable end-to-end. You can ship after slice one if you have to — that is what makes it a tracer.

**Per cycle:**

- **RED:** write one failing test for the next behavior. Use glossary vocabulary in the test name. Test through the public interface only.
- **GREEN:** minimal code to pass. No speculative features.
- **Refactor only when GREEN.**

**Rules:**

- Test behavior through the public interface, not implementation details. The test should survive an internal refactor.
- Mock at system boundaries only (external APIs, time, randomness, third-party SDKs) — your own modules get exercised through their public interface.
- Prefer SDK-style interfaces over generic fetchers — each external operation gets its own function so each mock returns one specific shape.
- Project-level: check `package.json` (or equivalent) for an existing test script before adding tooling. If no test runner exists and the task warrants tests, set one up before continuing — but only if Phase 0 said TDD applies.

Confirm with the user **which behaviors matter most** before the first cycle. You can't test everything.

---

## Phase 4 — Design Deep Modules

Triggered when Phase 0 selected `yes` for deep modules.

Structure the codebase as fewer, larger modules with small interfaces. Push complexity inward; expose simplicity outward.

```
Deep module                       Shallow module (avoid)
┌─────────────────┐               ┌──────────────────────────┐
│ Small Interface │               │   Large Interface        │
├─────────────────┤               ├──────────────────────────┤
│                 │               │   Thin Implementation    │
│  Deep impl.     │               └──────────────────────────┘
│                 │
└─────────────────┘
```

**Before extracting a new module:**

- Apply the **deletion test**.
- A new module needs **two adapters** (typically production + test) to justify a seam. One adapter = indirection, not a seam.
- Internal seams (private to a module's implementation, used by its own tests) stay private to the implementation — they remain absent from the public interface.
- Resist premature extraction. Wait for real duplication or a real seam.

**Classify the module's dependencies** (`in-process` · `local-substitutable` · `remote-but-owned` · `true-external`) — the category drives test strategy and adapter shape. See [LANGUAGE.md § Dependency Categories](LANGUAGE.md) for the definitions and adapter recipes.

### File hygiene (forward-pressure during generation)

The deletion test answers *"is this module shape right?"* It does not answer *"should this thing be its own file?"* That is a separate judgment, and it is the one AI-assisted generation most often gets wrong. The failure mode has a name: **minimal-change bias** — the agent dumps every new addition into the file it was already editing because that is what was literally requested. Combined with sycophancy and limited full-file context, this drives slow drift toward 1500-line files where every individual change passed review but the cumulative shape is convoluted.

**Before adding more than ~20 lines to an existing file**, apply the forward checkpoint:

1. Note the file's current shape (approximate line count; how many top-level named concepts it already contains).
2. Name what you are about to add. A domain-meaningful name is itself a signal.
3. Apply the extract signals — **two-of-five** passes the threshold:
   - Own domain name (the kind of name that would appear in `CONTEXT.md`)
   - Multiple callers (≥2)
   - Wants its own tests
   - Different change cadence than the rest of the file
   - Conceptually independent (explainable without the surrounding file)
4. **Propose extraction; never silently extract.** The user decides.

The metric is **cohesion**, not line count. A 600-line file that's one deep module is healthy. A 200-line file mixing five concepts is already convoluted. For full criteria, stay-inline signals, and worked examples, see [`FILE-HYGIENE.md`](FILE-HYGIENE.md).

---

**For retroactive deepening of existing shallow modules** (i.e., the codebase is already a ball of mud), exit smart-mode and use [`../improve-codebase-architecture/SKILL.md`](../improve-codebase-architecture/SKILL.md). Run that every few days as a recurring practice.

---

## Phase 5 — Delegate Implementation, Design the Interface

Triggered when Phase 0 selected `light` or `full` for interface design.

Treat each module as a gray box. The user designs the **interface**; the agent fills the **implementation**.

The interface includes types, invariants, ordering constraints, error modes, and required config.

**Default workflow (light or full):**

1. Define the interface and its invariants in code (or a sketch).
2. Write tests against the interface from the outside (the test surface = the interface).
3. Only then implement internals.
4. Tests must survive internal refactors.

If the user has not specified an interface, return to Phase 1 and grill them on it.

**Worked example — interface sketch before implementation.** For the gamification module, the interface (the thing callers and tests see) is sketched first:

```ts
type GamificationService = {
  awardPoints(userId: UserId, source: PointSource, ref: EventRef): Promise<PointsResult>
  getProfile(userId: UserId): Promise<Profile>  // points, level, streak
}

type PointSource = "lesson-completed" | "quiz-passed"
type PointsResult = { totalPoints: number; leveledUp: boolean; newLevel?: Level }
```

Invariants — part of the interface even though the type signature can't carry them:

- `awardPoints` is **idempotent** per `(userId, source, ref)` — re-emitting the same event does not double-credit.
- Level transitions are **monotonic**; once a user has reached a level, their level never decreases.
- Errors throw `GamificationError` (typed); transient I/O failures are retried inside the service, not the caller's problem.

Tests are written against this surface — never against `points_events` rows or internal helpers. The implementation can be rewritten (Postgres → Redis, in-memory → CRDT) and the tests still pass. **The interface is the contract; the implementation is replaceable.**

### Opt-in: Design It Twice (parallel sub-agents)

Reach for this **only when** the interface is genuinely contested or load-bearing — typically marked by Phase 0 as `system / architectural`, or when the user explicitly asks to compare options.

From Ousterhout's *A Philosophy of Software Design*: your first idea is unlikely to be the best. Spawn 3+ sub-agents in parallel, each producing a **radically different** interface for the same module:

- Agent 1: minimize the interface — 1–3 entry points max; maximize leverage per entry point.
- Agent 2: maximize flexibility — support many use cases and extension.
- Agent 3: optimize for the most common caller — make the default case trivial.
- Agent 4 (when applicable): design around ports & adapters for cross-seam dependencies.

Each sub-agent outputs:

1. Interface (types, methods, params, invariants, ordering, error modes)
2. Usage example showing how callers use it
3. What the implementation hides behind the seam
4. Dependency strategy and adapters
5. Trade-offs — where leverage is high, where it's thin

Present designs sequentially. Compare in prose, contrasting **depth**, **locality**, and **seam placement**. Recommend a winner, or propose a hybrid if elements combine well. Be opinionated — the user wants a strong read, not a menu.

For the full spawn-and-compare recipe, see [`../improve-codebase-architecture/INTERFACE-DESIGN.md`](../improve-codebase-architecture/INTERFACE-DESIGN.md).

---

## Operating Principles

- **Architect vs. programmer.** User makes strategic decisions; agent executes tactical implementation. Surface trade-offs.
- **Code is a liability.** Less code that is well-shaped beats more code that sprawls. Lines-of-code is not an output metric.
- **Slow is smooth.** Small, deliberate, test-backed steps compound into a stable system.
- **Design every day.** Run `../improve-codebase-architecture/SKILL.md` periodically — Pocock recommends every few days — to keep entropy in check.
- **Use the vocabulary.** Drift into "component," "service," "API," or "boundary" and the design discussion gets fuzzy. Stay precise.

## Pre-Flight Checklist (calibrated to Phase 0)

Confirm only the phases Phase 0 selected. Skipped phases stay unchecked and that's correct.

```
- [ ] Phase 0: Classification announced (or skipped because trivial); user has not requested a different scope
- [ ] Phase 1: Design concept established (full / brief / light, per Phase 0)
- [ ] Phase 2: Active glossary read; new terms appended (if Phase 0 selected extend/full)
- [ ] Phase 3: First failing test written (if Phase 0 selected TDD)
- [ ] Phase 4: Module shape proposed; deletion test applied; seams justified by ≥2 adapters (if Phase 0 selected deep modules)
- [ ] Phase 5: Interface defined (if Phase 0 selected interface design)
```

If a selected box is unchecked, return to that phase before continuing. Leave skipped boxes unchecked — that's the point of Phase 0.

**On checklist completion** (all selected boxes checked), trigger end-of-session reflection for both sister skills:

1. **evolve-skills**: a single batched `JOURNAL.md` capture for any *weak* signals from the session (a phase that was skipped but turned out to matter; a workflow reordering; capability requested that no skill currently provides; phase output that was low-value).
2. **stay-sharp**: a single batched `COMPETENCY-JOURNAL.md` capture for any topics that crossed thresholds during the session, any tier-promotion candidates, and any deferrals on must-know topics that *didn't* trigger a commit-first quiz (a bug to investigate).

If neither skill has anything to capture, silent completion. Strong signals were already captured inline during the session.

## Related Skills (in this repo)

- [`../grill-with-docs/SKILL.md`](../grill-with-docs/SKILL.md) — phase 1+2 workhorse
- [`../diagnose/SKILL.md`](../diagnose/SKILL.md) — bug/perf investigation (smart-mode hands off here)
- [`../improve-codebase-architecture/SKILL.md`](../improve-codebase-architecture/SKILL.md) — retroactive deepening (run every few days)
- [`../evolve-skills/SKILL.md`](../evolve-skills/SKILL.md) — agent-side continuous learning (active during every smart-mode session)
- [`../stay-sharp/SKILL.md`](../stay-sharp/SKILL.md) — user-side competency tracking and atrophy intervention (active during every smart-mode session)

## Source

This skill encodes Matt Pocock's framework for software engineering fundamentals in the age of AI coding tools, adapted from his public skills repository ([`mattpocock/skills`](https://github.com/mattpocock/skills), MIT-licensed). The four-failure-modes framing, the architecture vocabulary, the vertical-slice TDD pattern, and Design-It-Twice are all his; Phase 0 (scope assessment) is original to this skill, added because smart-mode is an orchestrator that needs to right-size the workflow per request.
