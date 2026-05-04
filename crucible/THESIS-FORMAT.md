# Thesis Format

`THESIS.md` is the public interface of a suite. Judges evaluate replies against this file, not against the proponent's private intent.

## Frontmatter

```yaml
---
id: short-kebab-case-id
scope: one-sentence scope boundary
status: active
last_revised_in_cycle: 0
commitments:
  - commitment-id-if-any
---
```

Fields:

- `id`: stable suite identifier.
- `scope`: the domain where the thesis applies.
- `status`: `draft`, `active`, `revised`, or `retired`.
- `last_revised_in_cycle`: `0` for the initial thesis; update when a human explicitly revises it.
- `commitments`: optional identifiers from `COMMITMENTS.md` that are part of the thesis itself.

## Body

Use these sections:

```markdown
# Thesis: [short title]

## Claim

[One clear paragraph. Avoid hedging that belongs in invariants.]

## Invariants

- [What must stay true across all replies.]
- [What the thesis is committed to even under pressure.]

## What Would Defeat This

- [Evidence, argument, or scenario that would force revision.]
- [Be specific enough for judges to detect drift.]

## Out Of Scope

- [Nearby claims this suite is not testing.]
- [Terms or traditions deliberately excluded.]
```

## Minimal Example

```markdown
---
id: adopt-rust-for-new-services
scope: backend services started after Q3 in this organization
status: active
last_revised_in_cycle: 0
commitments: []
---

# Thesis: Adopt Rust For New Services

## Claim

Our organization should use Rust as the default language for new backend services that handle high-throughput, correctness-sensitive workflows starting in Q3.

## Invariants

- This does not require rewriting existing Node services.
- This does not claim Rust is universally superior.
- The adoption path must be incremental and reversible for the first two services.

## What Would Defeat This

- Evidence that hiring and training costs exceed reliability and performance gains over an 18-month horizon.
- Evidence that our required libraries are immature enough to dominate delivery risk.

## Out Of Scope

- Frontend language choice.
- Existing service rewrites.
```
