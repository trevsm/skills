---
id: "001-compile-times"
challenges: adopt-rust-for-new-services
type: pragmatic-challenge
severity: high
source: "common Rust adoption concern"
assumes:
  - delivery-speed-matters
grants_arguendo:
  - rust-can-improve-runtime-reliability
introduced_in_cycle: 1
---

# Objection: Compile Times

## Objection (Steelmanned)

Even if Rust improves runtime reliability, compile times and borrow-checker iteration can slow feature delivery enough to erase the benefit for new services. A default language should optimize total delivery speed, not only production behavior.

## Pass Criteria

The reply MUST:

- Address development-cycle speed directly.
- Explain why the risk is acceptable for the scoped service class.

The reply MUST NOT:

- Claim compile times are irrelevant.
- Redefine "new backend service" to exclude difficult services.

## Known Weak Replies

- "Developers will get used to it."
- "Rust is fast at runtime, so compile time does not matter."
