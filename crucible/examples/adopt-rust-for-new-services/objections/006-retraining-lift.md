---
id: "006-retraining-lift"
challenges: adopt-rust-for-new-services
type: pragmatic-challenge
severity: high
source: "organizational adoption objection"
assumes:
  - most-engineers-are-not-rust-fluent
grants_arguendo:
  - rust-fits-the-service-class
introduced_in_cycle: 6
---

# Objection: Retraining Lift

## Objection (Steelmanned)

Rust's ownership model, lifetimes, async constraints, and ecosystem conventions impose a steep learning curve. If most engineers cannot confidently modify Rust services, the organization creates knowledge silos and pager risk.

## Pass Criteria

The reply MUST:

- Treat training and ownership as adoption requirements.
- Explain how the default avoids creating a specialist silo.

The reply MUST NOT:

- Say the compiler teaches everyone enough.
- Depend on a single Rust expert.

## Known Weak Replies

- "Rust has great error messages."
- "We can hire one Rust specialist."
