# Lakatos Cheats

Judges use this reference to distinguish legitimate thesis refinement from evasive rescue. A reply can pass while revising the thesis only if `THESIS.md` is explicitly updated by the human owner. Silent revision is `DRIFT`.

## Monster-Barring

**Definition:** Redefining a term so the counterexample is declared not to count.

**Lakatos-style example:** A strange polyhedron breaks Euler's formula, so the defender says it is not a "real" polyhedron by a new definition chosen after the fact.

**Modern manifestation:** A thesis says "new services should use Rust"; when compile-time risk appears, the reply says "new services" only means tiny internal tools where compile time is irrelevant.

**Detection heuristic:**

- Did the reply narrow a term used in `THESIS.md`?
- Was that narrower definition absent from `GLOSSARY.md` or `THESIS.md`?
- Would the objection still land under the original wording?

If yes, return `MONSTER-BARRED` or `DRIFT`.

## Exception-Barring

**Definition:** Preserving the thesis by adding bespoke exceptions rather than improving the thesis or replying to the objection.

**Lakatos-style example:** A theorem is kept by listing every known counterexample as excluded, without a principled classification.

**Modern manifestation:** "Rust should be default for new services, except services with deadlines, teams with juniors, data-heavy services, integration-heavy services, or anything customer-facing."

**Detection heuristic:**

- Does the reply add a list of exclusions?
- Are the exclusions unified by a stable principle?
- Would a future objection likely require another exception?

If exceptions are unprincipled, return `FAIL` or `MONSTER-BARRED`.

## Concept-Stretching

**Definition:** Broadening a term so the thesis absorbs a counterexample that should have forced revision.

**Lakatos-style example:** Expanding "polyhedron" or "proof" so both the original cases and awkward cases fit without acknowledging that the original concept changed.

**Modern manifestation:** A thesis about "free will" begins as libertarian agency, then a reply treats any behavior matching a person's desires as "free will" without updating the thesis.

**Detection heuristic:**

- Did the reply preserve a word while changing its extension?
- Would a reader of the original `THESIS.md` have expected the new meaning?
- Does the changed meaning weaken the objection by semantic shift rather than argument?

If yes, return `DRIFT`.

## Ad-Hoc Rescue

**Definition:** Adding an unsupported auxiliary premise only because the current objection threatens the thesis.

**Popper-style example:** A theory survives a failed prediction by adding a hidden force that has no independent evidence and predicts nothing new.

**Modern manifestation:** "The hiring risk is fine because Rust developers are uniquely fast learners," with no evidence and no prior commitment making that premise available.

**Detection heuristic:**

- Is the new premise introduced only in response to this objection?
- Does it have independent support in `THESIS.md`, `GLOSSARY.md`, sources, or prior commitments?
- Does it create testable implications, or only protect the thesis?

If the auxiliary has no independent support, return `FAIL`.

## Legitimate Moves

Not every revision is a cheat. These are allowed when explicit:

- **Scope clarification:** `THESIS.md` is updated before or during adjudication, and prior replies are re-run.
- **Principled restriction:** A narrower scope follows from an invariant already present in `THESIS.md`.
- **Premise rejection:** The reply rejects an objection premise with independent grounds.
- **Inference block:** The reply accepts the objection's premises but denies the step to its conclusion.
- **Arguendo concession:** The reply grants the objection's conclusion in a form compatible with the thesis.
