---
name: innovate-mode
description: Take an abstract, open-ended, ambitious vision and progressively materialize it into a concrete plan with phases, milestones, and tangible next steps that downstream skills (smart-mode, etc.) can execute. Capabilities catalog the agent composes meta-ly — not a fixed workflow. Use when the user says "innovate mode", "engage innovate mode", or brings an open-ended vision (e.g. "build AGI from scratch", "rethink how X works", "I have this fuzzy idea I want to make real") and needs help turning it into a plan.
disable-model-invocation: true
---

# Innovate Mode

Visions are cheap; plans are valuable; executable plans are rare. Innovate-mode bridges the gap between an ambitious abstract idea and a plan with first concrete next steps.

The user is the **visionary**. The agent is the **principal-grade collaborator**: shape-shifts into the right expert lens for the domain, drives the planning loop, and surfaces every meaningful choice. The user steers; the agent guides.

**Innovate-mode is a capabilities catalog, not a fixed workflow.** It lists primitives the agent composes meta-ly — reframings, decompositions, critiques, parallel diverge-converge with persona'd workers, tree-search-and-prune, concretization checks, handoff. Phase 0 triages the session shape; from there the agent picks and chains capabilities based on what the plan needs next. The user can always override.

## Active across all phases: evolve-skills + stay-sharp

[`../evolve-skills/SKILL.md`](../evolve-skills/SKILL.md) is active during every innovate-mode session. It captures friction, corrections, and declared preferences to `~/.cursor/skills-journal/JOURNAL.md` and promotes patterns into `PREFERENCES.md`. Innovate-mode reads `PREFERENCES.md` at Phase 0 (look under `## Innovate-mode` and `## General`) and runs end-of-session reflection at checklist completion.

[`../stay-sharp/SKILL.md`](../stay-sharp/SKILL.md) is also active. It captures competency signals to `~/.cursor/skills-journal/COMPETENCY-JOURNAL.md` and intervenes with commit-first quizzes when the user defers on a `must-know` topic. Innovate-mode reads `MUST-KNOW.md` at Phase 0 — particularly relevant here, because innovating in a domain you've tiered as `must-know` should not silently outsource your judgment to the agent.

**Positive framing applies to brainstorming, too.** When the user states a preference during the loop ("prefer to keep options open early"), capture it positively, not as a prohibition. Negative constraints in agent context fail at high rates and inflate forbidden-behavior attention.

## Scope: when to engage innovate-mode vs. a sister skill

Innovate-mode is for **vision → plan**, not plan → code or bug → fix. Hand off when scope changes:

- **Plan exists, you want to build it well** → [`../smart-mode/SKILL.md`](../smart-mode/SKILL.md). Smart-mode's Phase 0 right-sizes design rigor for known work.
- **Bug or performance investigation** → [`../diagnose/SKILL.md`](../diagnose/SKILL.md).
- **Existing codebase needs architectural deepening** → [`../improve-codebase-architecture/SKILL.md`](../improve-codebase-architecture/SKILL.md).

If Phase 0 classifies the request as one of the above, exit innovate-mode and invoke the sister skill. Conversely, if a smart-mode session reveals the *plan itself* is wrong (not the code), pivot up to innovate-mode.

## The three failure modes innovate-mode guards against

This is *why* the workflow exists. Each capability category prevents one of these.

1. **Premature concretization.** Vision collapses too early into a specific implementation that misses the actual goal. Fixed by reframing + diverge-converge primitives early.
2. **Permanent abstraction.** Vision stays poetic forever; the plan never produces a leaf the user can actually execute on Monday morning. Fixed by decomposition + concretization-check primitives.
3. **Untested assumptions in the plan tree.** Plan is decomposed top-down without checking whether early phases will produce the inputs later phases need. First milestone fails and the whole tree is wrong. Fixed by critique-and-revise + tree-search-and-prune primitives, and by handing off the **first** concrete leaf to smart-mode early to test the plan in reality.

If you can name which failure mode you're guarding against, you know which capability to reach for.

## Vocabulary

Use these terms exactly. Drift undermines the loop.

- **Vision** — the ambitious, open-ended, abstract input the user brought. *Not*: idea, concept, dream.
- **Plan** — the evolving artifact (a doc, or chat-resident structure) that materializes the vision into phases, milestones, and leaves.
- **Framing** — the lens through which the vision is interpreted (e.g. *scientific research program*, *product launch*, *engineering system*, *artistic exploration*). The same vision under different framings produces radically different plans.
- **Primitive** — a named capability the agent invokes (reframe, decompose, critique, etc.). Composable.
- **Persona** — an expert lens the manager *adopts* (top-of-session) or the manager *spawns into a worker* (mid-loop).
- **Worker** — a sub-agent the manager spawns to do parallel exploration, critique, or research. Workers report back; the manager synthesizes.
- **Synthesis** — the act of merging parallel worker outputs into one updated plan. Not voting; not concatenation.
- **Leaf** — a node in the plan tree that's been decomposed enough to be executable (has a definition-of-done; could be handed to smart-mode).
- **Stopping criterion** — what the user wants out of *this* session: vision pass, first milestone scoped, or stay-resident across phases.
- **Handoff** — the explicit transition out of innovate-mode into a sister skill, with the named artifact.

Three checks applied throughout:

- **Concretization-check** — for any leaf, ask: *could a competent engineer or researcher start work on this Monday?* If no, decompose further or sharpen the framing. If yes, it's a handoff candidate.
- **Reversibility-check** — before locking a framing or major decomposition, ask: *if we're wrong about this in a month, what's the cost of unwinding?* Heavy reversibility cost = grill harder before committing.
- **Budget-check** — for any loop primitive, ask: *am I about to invoke this for the third+ time in a row?* If yes, escalate to the user instead of grinding.

---

## Phase 0 — Session Triage

**Do this first, every time, before any capability fires.** Innovate-mode's right-sizing happens here.

### Read learned preferences and topic tiers

Before classifying, read `~/.cursor/skills-journal/PREFERENCES.md` (under `## Innovate-mode` and `## General`) and `~/.cursor/skills-journal/MUST-KNOW.md` if they exist. Mention only entries that *actually affect* this session's classification or capability selection — not the full lists. Silent if nothing applies.

### Classify

| Axis | Levels |
|---|---|
| **Stopping criterion** | vision-pass · first-milestone-scoped · stay-resident |
| **State strategy** | chat-only · single-doc · doc-tree |
| **Starting clarity** | vague-urge · abstract-vision · half-baked-plan |
| **Domain framing seed** | (free-form, agent-proposed: research, product, system, art, etc.) |

### Decide

Map classification to defaults — the agent uses these unless the user overrides:

| Stopping criterion | Default state | Likely opening primitives | Typical handoff |
|---|---|---|---|
| **vision-pass** | single-doc (`VISION.md`) | reframing → diverge-converge → light decomposition | Hand the doc to user; suggest re-invoke later for first-milestone |
| **first-milestone-scoped** | single-doc (`INNOVATE.md` or named) | reframing → decomposition → critique → concretization-check on leftmost leaf | Hand first leaf to smart-mode |
| **stay-resident** | doc-tree (`VISION.md` + `PHASE-{n}.md`) | full primitive set, used iteratively across multiple sessions | Hand each leaf to smart-mode; resume innovate-mode between phases |

When **starting clarity** is `vague-urge`, lead with reframing (the user doesn't yet know which lens applies). When `half-baked-plan`, lead with critique-and-revise (sharpen what's already there).

### Announce

For anything above a casual brainstorm, emit one line before proceeding:

> *"Reading this as a {stopping-criterion} session, {starting-clarity}, framing seed: {domain}. Plan will live in {state}. I'll start with {primitive}. Adjust?"*

If a preference from `PREFERENCES.md` materially changed the defaults, name it. Otherwise omit.

If the user says *"just start"* → skip the announcement and execute. If they want a different stopping criterion → use theirs. The user's word overrides the matrix.

---

## Capabilities

The agent picks and composes these meta-ly based on plan state. Each entry below is a *short blurb* — when to use, how it shapes output, what typically follows. **Detailed recipes for each capability live in [`CAPABILITIES.md`](CAPABILITIES.md); read it on demand when invoking a primitive for the first time in a session, or when one isn't producing.**

### Reframing

**When:** Starting clarity is `vague-urge` or `abstract-vision`; or the current framing is producing a stuck plan; or the critique primitive surfaced "we may be solving the wrong problem."

**How:** Propose 2–4 distinct framings of the vision (e.g. "build AGI" → *as a research program* / *as an open-source platform* / *as an embodied robotics project* / *as a cognitive-science thesis*). Each framing implies different first phases, success criteria, and personas.

**Output:** A short comparison; user picks one (or asks for a hybrid). Locks the **framing** for the rest of the session unless re-opened.

**Typical follow-on:** Decomposition under the chosen framing.

### Decomposition

**When:** Framing is set; the vision needs to be broken into phases, phases into milestones, milestones into leaves.

**How:** Recursive — each level produces 2–5 children. Stop a branch when the concretization-check passes (it's a leaf). Don't decompose all branches in parallel; depth-first the most uncertain or load-bearing branch.

**Output:** Updated plan doc (or chat tree) with new nodes named in the agreed vocabulary.

**Typical follow-on:** Concretization-check on new leaves; critique-and-revise on the structure.

### Critique-and-revise

**When:** A draft plan exists and you want to stress-test it before committing further; or the user says "is this right?"

**How:** Manager either red-teams itself across N angles (feasibility, novelty, sequencing, hidden assumptions, dependency risk) or **spawns persona'd critic workers** (see Worker-spawning) when angles benefit from independent voices.

**Output:** A list of critiques, ranked by severity. Manager proposes revisions; user approves which to apply.

**Typical follow-on:** Revise the plan; if a critique is fundamental, return to reframing.

### Diverge-converge

**When:** A high-leverage decision has multiple plausible directions and the right answer isn't obvious; or you're early in a `vision-pass` and want to scout the design space.

**How:** Manager spawns 3+ workers in parallel, each with a *radically different* persona/approach to the same question. Workers produce their take independently. Manager synthesizes — not by voting or concatenating, but by extracting the strongest elements and proposing a unified direction (or asking the user to pick a winner).

**Output:** Workers' takes (summarized), a synthesis, and a recommendation.

**Typical follow-on:** Decomposition under the chosen direction.

### Tree-search-and-prune

**When:** The plan is a tree with multiple competing branches and you need to focus effort.

**How:** Score branches on (potential leverage × confidence × user interest); expand the highest-scoring branch; prune branches that fail the reversibility-check or that the user explicitly deprioritizes. Keep pruned branches in an "Ideas Parking Lot" section, not deleted.

**Output:** A focused plan with one (or few) active branches and a parking lot.

**Typical follow-on:** Decomposition or concretization-check on the active branch's frontier.

### Persona-adoption (manager-side)

**When:** The vision lives in a domain where a specific expert lens dramatically improves the plan's quality (e.g. "build AGI" → *principal AI researcher*; "rethink onboarding" → *senior product manager*; "novel cryptosystem" → *applied cryptographer*).

**How:** Manager *adopts* the persona for the rest of the session: vocabulary, concerns, success criteria, and what counts as a "concrete leaf" all shift. Announce the adoption: *"Adopting principal AI researcher lens for the rest of this session — milestones will be framed as experiments with falsifiable predictions, not features."*

**Output:** A reframed plan written in that expert's idiom.

**Typical follow-on:** Decomposition or critique under the persona's standards.

### Worker-spawning (delegate-side)

**When:** Diverge-converge, critique-and-revise, or research-synthesis would benefit from independent voices rather than the manager simulating them in one head.

**How:** Manager spawns N parallel sub-agents (`Task` tool with the appropriate `subagent_type`, typically `generalPurpose` for synthesis tasks or `explore` for read-only investigation). Each worker gets a *highly detailed* prompt — workers don't have the conversation context; they need the full framing, the question, and the output format.

**Output:** Worker reports, returned to the manager for synthesis.

**Typical follow-on:** Synthesis (the manager's job, not delegated).

**Budget rule:** Spawn at most 4 workers per call; don't recursively spawn (workers don't spawn workers in this skill); set a clear deliverable ("return a 5-bullet summary of …") to keep cost bounded.

### Research-synthesis

**When:** The vision touches an established field where prior art shapes what's worth building (e.g. AGI architectures, distributed-consensus protocols, design systems).

**How:** Spawn `explore`-type workers to investigate angles in parallel ("survey existing X approaches", "find SOTA on Y", "identify open problems in Z"). Manager synthesizes findings into a *Prior Art* section of the plan and uses them to constrain decomposition (don't reinvent solved problems; do invest in genuinely open ones).

**Output:** A *Prior Art* section in the plan; sometimes a reframing if the survey reveals the vision overlaps heavily with an existing project.

**Typical follow-on:** Reframing, or decomposition that respects the surveyed constraints.

### Concretization-check

**When:** Before declaring any node a leaf; before handing anything off to smart-mode.

**How:** Apply the test in plain language: *"Could a competent {persona} start work on this Monday morning, knowing what done looks like?"* If no, name what's missing (definition-of-done? success criteria? input artifact? scoped problem statement?) and decompose or sharpen until yes.

**Output:** Either a confirmed leaf (handoff candidate) or a list of missing-pieces driving the next loop.

**Typical follow-on:** Handoff (if leaf) or decomposition (if not).

### Handoff

**When:** A leaf passes concretization-check and the user wants to start executing; or the stopping criterion is met.

**How:** Name the artifact (the leaf, or the whole plan), name the receiving skill, and transition cleanly. *"This leaf is ready: `{name}`. Definition of done: `{DoD}`. Handing to smart-mode now — its Phase 0 will pick up from here."* Then exit innovate-mode for this session.

**Output:** A clean closing message; for stay-resident sessions, a reminder of what to re-invoke innovate-mode for after the smart-mode session completes.

**Typical follow-on:** None within innovate-mode — control passes to the next skill.

---

## Operating Principles

- **The user is the visionary; the agent is the principal-grade collaborator.** Surface every meaningful choice. Recommend strongly, but don't decide on the user's behalf when the cost of being wrong is meaningful.
- **The plan is an asset.** When state lives in a doc, treat it as a versioned artifact: clear sections, named decisions, parking lot for pruned ideas, change log if the session is long.
- **Avoid decomposition drift.** Recursion is cheap to invoke and expensive to unwind. Apply concretization-check before going deeper; if a node is already actionable, *stop decomposing it*.
- **Avoid worker drift.** Workers cost tokens and synthesis effort. Don't spawn them for problems the manager can answer in one head. Use the budget rule (≤4 per call, no recursive spawning).
- **Surface uncertainty.** Better one good question than three confident wrong directions. If a primitive returns ambiguous output, ask the user before pressing on.
- **Recurse with budget.** Each loop primitive has an iteration cap (≤3 in a row by default). At the cap, escalate to the user with what's blocking convergence.
- **Use the vocabulary.** Drift into "thing," "task," "section," "subagent" without a role and the loop turns mushy. Stay precise.
- **Keep options open early; commit hard once committed.** Reframing is cheap before decomposition; expensive after. Don't lock framings before exploring 2–3.

## Pre-Flight Checklist (calibrated to Phase 0)

Confirm only the items the chosen stopping criterion warrants. Skipped items stay unchecked — that's the point of triage.

```
- [ ] Phase 0: Session shape announced (or skipped per "just start"); user has not requested a different shape
- [ ] Framing: at least one framing has been explicitly named and adopted
- [ ] Plan state: doc created (if state ≠ chat-only) at the agreed path; updated inline as primitives fire
- [ ] Primitive budgets respected: no primitive invoked >3× in a row without user check-in; no >4 workers per spawn
- [ ] Concretization-check: passed on every leaf marked as handoff candidate
- [ ] Handoff (if reached): receiving skill named, artifact named, definition-of-done stated
```

If a required box is unchecked, return to the relevant capability before continuing. Skipped boxes stay unchecked.

**On checklist completion** (all required boxes checked, or user explicitly closes the session), trigger end-of-session reflection for both sister skills:

1. **evolve-skills**: a single batched `JOURNAL.md` capture for any *weak* signals (a primitive that was skipped but turned out to matter; a workflow ordering that recurred; capability requested that no primitive currently provides).
2. **stay-sharp**: a single batched `COMPETENCY-JOURNAL.md` capture for any topics that crossed thresholds during the session, deferrals on must-know topics that *didn't* trigger a commit-first quiz, and any tier-promotion candidates.

If neither has anything to capture, silent completion. Strong signals were captured inline.

## Related Skills

- [`../smart-mode/SKILL.md`](../smart-mode/SKILL.md) — plan → code (the primary handoff target)
- [`../grill-with-docs/SKILL.md`](../grill-with-docs/SKILL.md) — interview/grilling discipline; innovate-mode borrows the one-question-at-a-time cadence for user check-ins
- [`../diagnose/SKILL.md`](../diagnose/SKILL.md) — bug/perf investigation
- [`../improve-codebase-architecture/SKILL.md`](../improve-codebase-architecture/SKILL.md) — retroactive architectural deepening
- [`../evolve-skills/SKILL.md`](../evolve-skills/SKILL.md) — agent-side continuous learning
- [`../stay-sharp/SKILL.md`](../stay-sharp/SKILL.md) — user-side competency tracking

## Source

Original to this repo. Spine borrowed from [`../smart-mode/SKILL.md`](../smart-mode/SKILL.md): Phase 0 triage, capabilities-not-workflow framing, evolve-skills + stay-sharp integration, pre-flight checklist. Diverge-converge with persona'd workers builds on smart-mode Phase 5's *Design It Twice* and on Ousterhout's broader argument that the first idea is rarely the best.
