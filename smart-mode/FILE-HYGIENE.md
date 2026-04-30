# File Hygiene

When and how to make file-vs.-module decisions during code generation. Sister to [LANGUAGE.md](LANGUAGE.md) — that doc defines the vocabulary; this one defines the judgment that uses it.

## The problem this solves

AI-assisted code generation has a specific failure mode that produces files that are unnecessarily large and convoluted. Naming it makes it visible.

**Minimal-change bias.** When asked to add feature X to file Y, the agent's default is to dump it into file Y — because that's what was literally requested. Splitting requires deciding to do work the user did not ask for.

Combined with sycophancy (avoid surprising the user), limited full-file context (the agent may not realize the file is already 1200 lines), and the absence of immediate feedback (tests still pass; lints still pass), this drives slow drift toward bloated files. Every individual change passed review. The cumulative shape did not.

This document counteracts that drift with **forward-pressure judgment**: before adding code, the agent asks whether the addition belongs in this file or its own.

## File vs. Module — they are not the same

- **Module** (logical) — anything with an interface and an implementation. Scale-agnostic.
- **File** (physical) — a unit of source code in the filesystem.

A module can span multiple files (e.g., a deep module split into `index.ts` plus an `internal/` directory of private helpers). A file can contain multiple modules (e.g., a small utility file with three independent pure functions). The two questions are independent:

- *"Should this be its own module?"* → answered by the deletion test plus the two-adapter rule (LANGUAGE.md).
- *"Should this live in its own file?"* → answered here.

Treating them as the same question is itself an error. A module that's correctly shaped can still live in the wrong file.

## The metric is cohesion, not line count

A 600-line file that's **one deep module** is healthy. A 200-line file with **five unrelated concepts** is already convoluted. Length is a weak signal; conceptual coherence is the strong one.

The right question: *"Does this file have one coherent reason to exist?"* If yes, the file can be large and still earning its keep. If no, it is already wrong and should be split, even at 200 lines.

## Extract signals — five tests, two-of-five threshold

If something inside a file matches **two or more** of these, propose extracting it to its own file:

1. **Own domain name.** A name a domain expert would recognize — the kind of name that would appear in `CONTEXT.md`. "OrderRefundCalculator" passes; "calculateRefund_internal" does not.
2. **Multiple callers.** Used in two or more places, not just by the immediately surrounding code.
3. **Wants its own tests.** Testing it requires reaching past the surrounding file's public interface, or the test logic would clearly belong in a separate test file.
4. **Different change cadence.** Changes for different reasons than the rest of the file. (The cohesion test from Single Responsibility — things that change together belong together.)
5. **Conceptually independent.** Can be explained without referring to the rest of the file. If a new engineer could read this thing alone and understand it, that is a strong signal.

Two-of-five is the threshold deliberately. One signal alone is usually weak — a domain name without callers is just labeling; a single test does not justify a new file.

## Stay-inline signals — resist extraction when

- **Single caller, simple helper.** A 20-line function used in exactly one place. Extracting creates a one-adapter seam — indirection, not a seam.
- **No domain name.** It is a private detail of the surrounding logic, not a concept worth naming.
- **Tightly coupled to surrounding state.** Reaches into closures or shared variables that would have to become parameters at the seam.
- **Premature.** Would-be tests do not exist yet; would-be other callers do not exist yet. Wait for real evidence of the seam.
- **Under 30 lines and coherent with neighbors.** Even when it has a name, sometimes a small concept is best read in context.

The stay-inline signals are not numerical — any one of them is usually enough to keep the thing inline, because each is evidence the seam is hypothetical, not real.

## The forward checkpoint

Before adding more than roughly 20 lines to an existing file, pause and apply this loop:

1. **Read the file's current shape.** Approximate line count. Approximate concept count: how many top-level named things does the file already contain?
2. **Name what you are about to add.** If a domain-meaningful name comes naturally, that is itself signal #1. If you can only describe it as *"the helper for X,"* the helper is fine where it is.
3. **Apply the extract signals.** Two-of-five passes the threshold.
4. **Propose; do not unilaterally extract.** Always offer the user the choice:

   > *"This addition introduces a new concept (`OrderRefundCalculator`) with its own tests and a different change cadence than the rest of `checkout-routes.ts`. I'd suggest a new file `order-refund-calculator.ts`. Extract or keep inline?"*

The proposal is the artifact. Extraction without proposal is itself a failure mode — the agent imposing structural choices the user did not ask for.

## Worked examples

### Example 1 — bloating that should split

A `routes/checkout.ts` file is 850 lines. It contains: HTTP routing, request validation, cart total calculation, tax calculation, inventory reservation, and email confirmation.

Asked to add tax rules for a new jurisdiction. Apply signals to "tax calculation":

| Signal | Match? |
|---|---|
| Own domain name (`TaxCalculator`) | ✓ |
| Multiple callers | ✗ (only checkout uses it today) |
| Wants its own tests (tax rules are complex) | ✓ |
| Different change cadence (tax rules shift quarterly; routing barely) | ✓ |
| Conceptually independent (uses cart shape from checkout) | ✗ |

Three-of-five → propose extracting `tax-calculator.ts`. The single-caller signal does not block — three other signals carry it.

### Example 2 — premature extraction to resist

A `user-routes.ts` file is 180 lines. The agent considers extracting a 15-line `parseUserId` helper.

| Signal | Match? |
|---|---|
| Own domain name | ✗ — `parseUserId` is a function name, not a domain concept |
| Multiple callers | ✗ — used in two route handlers within the same file |
| Wants its own tests | ✗ — it's a one-liner returning a number |
| Different change cadence | ✗ — changes whenever route shape changes |
| Conceptually independent | ✗ — couples to the request shape |

Zero-of-five → keep inline. Extraction would create indirection without seam.

### Example 3 — big and right

A `payment-processor.ts` file is 720 lines but cohesive: payment intent creation, charge handling, retry logic, idempotency tracking, refund processing — all about payments. Asked to add a 100-line dispute handler.

Apply signals to "dispute handler":

| Signal | Match? |
|---|---|
| Own domain name (`DisputeHandler`) | ✓ |
| Multiple callers | ✗ (called only from the webhook handler today) |
| Wants its own tests | ✓ (chargeback flow is complex) |
| Different change cadence (chargebacks follow their own compliance lifecycle) | ✓ |
| Conceptually independent (a dispute does not depend on a successful charge) | ✓ |

Four-of-five → propose `dispute-handler.ts`. The original 720-line file stays focused on the payment success path. Length was never the issue; mixing two concepts would have been.

## Anti-pattern: the section-comment smell

When you find yourself reaching for comment headers to organize a file (`// ===== Validation =====`, `// ===== Routing =====`, `// ===== Helpers =====`), those comments are usually telling you where the file boundaries should be. Each section is asking to leave.

Section comments inside a single deep module are fine — they document internal structure for one cohesive thing. Section comments separating multiple unrelated concepts are misleading: they make the file *look* organized while the underlying problem is that it should be more than one file.

## Source

Original to this repo. The forward-pressure pattern is a direct response to the *minimal-change bias* failure mode that becomes visible only with AI-assisted generation: human authors rarely produce 1500-line files by accident, but AI-driven sessions do, because the default is "add it where I was told to add it."
