# Reply Format

A reply is one GREEN implementation. It answers exactly one objection with the smallest coherent move that preserves the thesis.

## Frontmatter

```yaml
---
satisfies: "001-short-slug"
cycle: 1
status: PASSING
last_verified: YYYY-MM-DD
judges_passed:
  - judge-1
  - judge-2
---
```

Fields:

- `satisfies`: objection id.
- `cycle`: numeric cycle.
- `status`: `DRAFT`, `PASSING`, `FAILING`, `MONSTER-BARRED`, `DRIFT`, or `REGRESSION`.
- `last_verified`: date of the last judge/regression run.
- `judges_passed`: judge identifiers or model-family labels that passed the reply.

## Body

Use these sections:

```markdown
# Reply: [short title]

## Reply

[Prefer <=200 words. Reject a premise, block an inference, or accept the conclusion in a thesis-compatible form.]

## Commitments This Reply Locks In

- [Commitment phrased as a stable claim.]
- [Another commitment if needed.]
```

## Minimal Example

```markdown
---
satisfies: "001-compile-times"
cycle: 1
status: PASSING
last_verified: 2026-05-04
judges_passed:
  - judge-a
  - judge-b
---

# Reply: Compile Times

## Reply

Compile-time cost is a real adoption cost, but the thesis scopes Rust to new high-throughput, correctness-sensitive services rather than all product work. For that service class, local iteration speed is only one delivery variable; production incident rate, runtime predictability, and confidence in refactors also affect delivery speed over the service lifetime. The adoption remains acceptable only if the first two services include build-cache setup, CI timing budgets, and a rollback path to the current stack before Rust becomes the default.

## Commitments This Reply Locks In

- Rust adoption is justified only for high-throughput, correctness-sensitive backend services.
- The first two Rust services must include build-cache setup, CI timing budgets, and a rollback path.
```

## Judge Notes

A reply should fail if it wins by changing `THESIS.md`, introducing undefined load-bearing terms, or adding a commitment that contradicts prior passing replies.
