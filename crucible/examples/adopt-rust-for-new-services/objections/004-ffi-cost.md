---
id: "004-ffi-cost"
challenges: adopt-rust-for-new-services
type: pragmatic-challenge
severity: medium
source: "integration risk objection"
assumes:
  - existing-services-are-mostly-node
grants_arguendo:
  - rust-pilots-are-technically-successful
introduced_in_cycle: 4
---

# Objection: FFI Cost

## Objection (Steelmanned)

New services do not live alone. If most existing systems are Node-based, Rust may force awkward FFI, duplicated client libraries, and more complex local development, making integration risk higher than the runtime benefits.

## Pass Criteria

The reply MUST:

- Explain the integration strategy with existing Node services.
- Avoid pretending new services are isolated.

The reply MUST NOT:

- Depend on embedded FFI as the default integration path.
- Treat integration cost as someone else's problem.

## Known Weak Replies

- "Rust can call C, so interop is solved."
- "They are new services, so they do not integrate."
