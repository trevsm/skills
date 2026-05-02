# Plan Format Templates

Read this file when creating or updating the plan doc. Three templates:

1. **`VISION.md`** — single-doc, vision-pass output
2. **`INNOVATE.md`** — single-doc, first-milestone-scoped output (vision + first leaf scoped)
3. **Doc tree** — `VISION.md` at top, `PHASE-{n}.md` per phase, used in stay-resident sessions

Pick the template at Phase 0; the agent populates and updates it inline as primitives fire.

---

## Template 1 — `VISION.md` (vision-pass)

For sessions that produce a written vision and stop. Output is meant to be human-readable; can be re-opened later and grown into `INNOVATE.md` or a doc tree.

```markdown
# {Project / Vision Name}

> One-sentence statement of the vision. The most ambitious framing the user actually means.

## Origin

What the user brought to innovate-mode (paraphrased, 1–2 paragraphs). Useful for the future you who's forgotten the original framing.

## Framing

The lens this plan adopts. Includes the persona (if any) and what's *out of scope* under this framing.

- **Framing:** {chosen framing in one sentence}
- **Persona:** {persona, if adopted}
- **Out of scope under this framing:** {bullets — important; constrains future drift}
- **Alternative framings considered:** {1-line summaries of rejected framings + why}

## Phases (rough)

A coarse phase structure. Each phase has a *purpose* and an *exit criterion*. No leaves yet — that's `INNOVATE.md` / `PHASE-N.md` work.

### Phase 1: {name}
- **Purpose:** {one sentence}
- **Exit criterion:** {observable signal that this phase is done}
- **Open questions:** {what we don't yet know that the phase will resolve}

### Phase 2: {name}
- ... (same shape)

## Prior Art

(If research-synthesis ran. Otherwise omit.)

- **Settled ground:** {bullets}
- **Open problems:** {bullets}
- **Adjacent work:** {bullets}

## Ideas Parking Lot

Pruned branches, kept for resurrection.

- {idea} — pruned {date}. Revisit if {trigger}.

## Decision Log

Load-bearing decisions made during the session, in order.

| # | Decision | Reasoning | Reversibility |
|---|---|---|---|
| 1 | Adopted {framing} | {one line} | medium — costly after Phase 2 |
| 2 | Persona: {persona} | {one line} | low — can shift between sessions |

## Next session

If re-invoking innovate-mode: {what to do next — typically "scope first milestone of Phase 1"}.
If handing to another skill: see the handoff section.
```

---

## Template 2 — `INNOVATE.md` (first-milestone-scoped)

For sessions that produce a vision *and* a fully-scoped first leaf ready for handoff. Strict superset of `VISION.md` plus an `## Active Leaf` section.

```markdown
# {Project / Vision Name}

> One-sentence vision.

## Origin
(as VISION.md)

## Framing
(as VISION.md)

## Phases (rough)
(as VISION.md, with the first phase decomposed one level)

### Phase 1: {name}
- **Purpose:** {one sentence}
- **Exit criterion:** {one sentence}
- **Children:**
  - ★ {child 1} — depth-first; see Active Leaf below
  - {child 2} — pending
  - {child 3} — pending

## Active Leaf

The single leaf scoped this session. Ready to hand to smart-mode (or named alternative).

### Leaf: {leaf name}

- **Definition of done:** {observable, testable criterion}
- **In scope:** {bullets}
- **Out of scope:** {bullets}
- **Inputs required:** {existing artifacts, prior decisions, dependencies}
- **Effort estimate:** S / M / L
- **Handoff target:** smart-mode (default) or {named alternative}
- **Context smart-mode needs to know:**
  - Vision: {one sentence}
  - This leaf is part of: Phase 1, child #1
  - Persona scoped under: {persona, if any}
  - Constraints not in the leaf: {bullets}

## Critique pass(es)

Each iteration of critique-and-revise that fired during the session.

### Iteration 1
- {critique} → {revision applied}

## Prior Art
(as VISION.md, if applicable)

## Ideas Parking Lot
(as VISION.md)

## Decision Log
(as VISION.md)

## Handoff

This document is being handed to smart-mode for the **Active Leaf** above. Innovate-mode is exiting. Re-invoke innovate-mode when the leaf is shipped and the next leaf needs scoping.
```

---

## Template 3 — Doc tree (stay-resident)

For long-running sessions that scope multiple phases over time. File layout:

```
{project-root}/
├── VISION.md           ← top-level vision + framing + phase list (template 1, no leaves)
├── PHASE-1.md          ← decomposition + leaves for phase 1
├── PHASE-2.md          ← created when Phase 1 is mostly shipped and innovate-mode is re-invoked
├── PARKING-LOT.md      ← pruned ideas across all phases (extracted out for visibility)
└── DECISIONS.md        ← decision log across all phases (extracted out for visibility)
```

`VISION.md` keeps the high-level shape; `PHASE-{n}.md` files are the decomposed working docs. `PARKING-LOT.md` and `DECISIONS.md` are extracted because they grow across phases and benefit from a stable home.

### `PHASE-{n}.md` template

```markdown
# Phase {n}: {name}

> Purpose: {one sentence}.
> Exit criterion: {one sentence}.

Parent: [VISION.md](VISION.md) → Phase {n}

## Children

- ★ {child 1} — Active Leaf below
- {child 2} — pending
- {child 3} — done (handed off {date}, completed {date})

## Active Leaf

(structure as INNOVATE.md `## Active Leaf` section)

## Completed Leaves

| Leaf | Handed off | Completed | Outcome |
|---|---|---|---|
| {child 3} | {date} | {date} | {one-line — what shipped, what we learned} |

## Critique passes
(structure as INNOVATE.md)

## Notes

Free-form notes the user or agent want to capture mid-phase but that don't yet fit the structure above. Periodically promote stable notes into the structured sections.
```

---

## Updating the plan during the loop

The agent updates the plan doc *inline* as primitives fire. Conventions:

- **Reframing** → updates `## Framing`. Moves the old framing to "Alternative framings considered."
- **Decomposition** → updates `## Phases` or adds children under a phase.
- **Critique-and-revise** → appends to `## Critique pass(es)`; if a critique caused a structural change, update the structural section AND record the critique.
- **Diverge-converge** → records the synthesis in the relevant section; worker outputs are summarized, not pasted in full.
- **Tree-search-and-prune** → updates `## Phases` (active branches) and `## Ideas Parking Lot`.
- **Persona-adoption** → updates `## Framing`'s `Persona` field.
- **Worker-spawning** → no direct doc update; outputs flow through the parent primitive.
- **Research-synthesis** → updates `## Prior Art`.
- **Concretization-check** → if it passes, materializes `## Active Leaf` (or completes a child entry). If it fails, no doc update — back to decomposition.
- **Handoff** → finalizes `## Handoff` section; closes the doc for this session.

Don't bury inline edits in long messages — when an edit is meaningful, mention it in chat ("Updated `Framing` to reflect the research-program lens"). The user should always know the doc state without re-reading the whole file.
