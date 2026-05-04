---
id: "005-async-fragmentation"
challenges: adopt-rust-for-new-services
type: undercutting-defeater
severity: medium
source: "Rust service architecture concern"
assumes:
  - async-services-are-likely
grants_arguendo:
  - rust-runtime-performance-is-valuable
introduced_in_cycle: 5
---

# Objection: Async Fragmentation

## Objection (Steelmanned)

Rust async has multiple runtimes, conventions, and library compatibility traps. A team adopting Rust as a default may lose consistency across services and create subtle operational differences that undermine the supposed reliability benefits.

## Pass Criteria

The reply MUST:

- Name a governance mechanism for async/runtime choices.
- Preserve the incremental adoption invariant.

The reply MUST NOT:

- Claim fragmentation does not exist.
- Leave every team to choose independently.

## Known Weak Replies

- "Everyone uses Tokio anyway."
- "Fragmentation is just flexibility."
