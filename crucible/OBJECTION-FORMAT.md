# Objection Format

An objection is one RED test. It should be strong, charitable, and adjudicable.

## Frontmatter

```yaml
---
id: "001-short-slug"
challenges: thesis-id
type: undercutting-defeater
severity: high
source: "author, text, lived constraint, or generated"
assumes:
  - assumption-id
grants_arguendo:
  - premise-granted-for-this-cycle
introduced_in_cycle: 1
---
```

Fields:

- `id`: three-digit cycle number plus slug.
- `challenges`: matching `THESIS.md` id.
- `type`: `rebutting-defeater`, `undercutting-defeater`, `counterexample`, `scope-challenge`, or `pragmatic-challenge`.
- `severity`: `low`, `medium`, `high`, or `critical`.
- `source`: citation or explanation for where the objection comes from.
- `assumes`: background assumptions the judge should track.
- `grants_arguendo`: premises the reply should not fight in this cycle.
- `introduced_in_cycle`: numeric cycle.

## Body

Use these sections:

```markdown
# Objection: [short title]

## Objection (Steelmanned)

[One strong version of the objection. Make the thesis work hard.]

## Pass Criteria

The reply MUST:

- [Specific condition the reply must satisfy.]
- [Another condition if needed.]

The reply MUST NOT:

- [Known dodge or cheat.]
- [Forbidden drift.]

## Known Weak Replies

- [Reply that sounds plausible but should fail.]
- [Another weak reply.]
```

## Minimal Example

```markdown
---
id: "001-compile-times"
challenges: adopt-rust-for-new-services
type: pragmatic-challenge
severity: high
source: "generated from common Rust adoption concerns"
assumes:
  - delivery-speed-matters
grants_arguendo:
  - rust-can-improve-runtime-reliability
introduced_in_cycle: 1
---

# Objection: Compile Times

## Objection (Steelmanned)

Even if Rust improves runtime reliability, compile times and borrow-checker iteration can slow feature delivery enough to erase the benefit for new services.

## Pass Criteria

The reply MUST:

- Address development-cycle speed directly, not only runtime performance.
- Explain why the risk is acceptable for the scoped service class.

The reply MUST NOT:

- Claim Rust compile times are irrelevant.
- Redefine "new services" to exclude the hard cases.

## Known Weak Replies

- "Developers will get used to it."
- "Rust is fast at runtime, so compile time does not matter."
```
