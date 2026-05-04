---
id: "003-ecosystem-maturity"
challenges: adopt-rust-for-new-services
type: undercutting-defeater
severity: high
source: "common platform risk objection"
assumes:
  - delivery-risk-includes-library-risk
grants_arguendo:
  - rust-core-language-fits
introduced_in_cycle: 3
---

# Objection: Ecosystem Maturity

## Objection (Steelmanned)

Rust's core language may fit, but service delivery depends on libraries, observability, data tooling, and operational conventions. If the ecosystem for our domain is less mature than Node, Go, or Java, Rust shifts risk from runtime bugs to library gaps and bespoke infrastructure.

## Pass Criteria

The reply MUST:

- Address domain-specific library maturity, not Rust in general.
- Preserve the thesis's defeat condition around immature required libraries.

The reply MUST NOT:

- Equate crates.io volume with production maturity.
- Ignore observability and operations.

## Known Weak Replies

- "Rust has libraries for everything."
- "We can build missing pieces ourselves."
