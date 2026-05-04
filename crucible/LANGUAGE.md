# Crucible Language

Shared vocabulary used throughout `crucible`. Use these terms exactly; most failures in prose arguments hide inside term drift.

## Terms

**Thesis**
The load-bearing claim under test, including its scope, invariants, defeat conditions, and exclusions.
_Avoid_: argument, position, claim.

**Objection**
A single challenge the thesis must survive in one cycle. It should be steelmanned and specific enough to adjudicate.
_Avoid_: test, counterargument, rebuttal.

**Reply**
The minimal coherent response to one objection. A reply may reject a premise, block an inference, or accept the conclusion in a form compatible with the thesis.
_Avoid_: rebuttal, defense.

**Defeater**
An objection that, if unanswered, defeats the thesis or its support. From John Pollock's defeasible reasoning vocabulary.

**Rebutting defeater**
A defeater that directly contradicts the thesis or one of its commitments.

**Undercutting defeater**
A defeater that removes support for the thesis without directly contradicting it.

**Cycle**
One RED -> GREEN -> adjudicate -> regress iteration. A cycle starts with exactly one objection and ends with an outcome in `TRANSCRIPT.md`.

**Commitment**
A claim a reply locks in. Commitments are reusable across the suite and must be checked for contradiction when new replies are added.

**Steelman**
The strongest charitable form of an objection. The adversary should make the thesis work hard, not win cheaply.
_Avoid_: strawman.

**Granted arguendo**
A premise stipulated for one objection only, so the reply cannot dodge by fighting every premise at once. This is the prose-substrate analog of mocking at a system boundary.

**Suite**
The directory containing `THESIS.md`, `GLOSSARY.md`, `COMMITMENTS.md`, `TRANSCRIPT.md`, `objections/`, and `replies/`.

**Vertical slice**
One cycle that leaves the thesis end-to-end defensible against a specific objection. Inherited from `smart-mode`'s tracer-bullet TDD vocabulary.

**Convergence**
The state where a cold adversary cannot produce a novel objection above the chosen severity threshold after K attempts.

**Drift**
The thesis quietly mutating to survive an objection without explicitly revising `THESIS.md`.

## Lakatos Cheats

Full definitions and detection heuristics live in [LAKATOS-CHEATS.md](LAKATOS-CHEATS.md).

**Monster-barring**
Gerrymandering a definition so the counterexample no longer counts.

**Exception-barring**
Adding ad-hoc exceptions to preserve the thesis.

**Concept-stretching**
Broadening a term so it absorbs a counterexample that should have forced revision.

**Ad-hoc rescue**
Adding an unsupported auxiliary premise only to save the thesis from the present objection.

## Principles

- **The thesis is the interface.** Objections and replies must engage the thesis through `THESIS.md`, not through the proponent's private intent.
- **The glossary is part of the interface.** A reply that introduces undefined load-bearing terms fails until those terms are defined.
- **Commitments are regression surfaces.** Every new commitment can break an earlier reply.
- **One objection = one slice.** Do not write a catalog of objections before the first reply passes.
- **Depth is leverage per commitment.** Prefer a few commitments that answer many objections over many bespoke replies.

## Rejected Framings

- **"Just steelman it."** Steelmanning is useful, but without a transcript, regression, and convergence criterion it does not compound.
- **"Argument mapping."** Toulmin, Carneades, and related systems provide useful data structures; Crucible is an authoring loop.
- **Pseudo-code tests.** Prose claims do not have executable `assert`s. Use structured prose with explicit pass criteria.
- **Debate club scoring.** The goal is not winning a round; it is making the thesis harder to break without hiding drift.
