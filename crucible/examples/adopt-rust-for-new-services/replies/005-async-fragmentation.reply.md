---
satisfies: "005-async-fragmentation"
cycle: 5
status: PASSING
last_verified: 2026-05-04
judges_passed:
  - judge-a
  - judge-b
  - judge-c
---

# Reply: Async Fragmentation

## Reply

Async fragmentation is a platform risk, so Rust should not be adopted as unmanaged team choice. The pilot should standardize one runtime, one HTTP stack, one tracing setup, and one service template before the second service starts. That keeps the adoption incremental: the organization tests a specific Rust service platform, not an open-ended menu of Rust ecosystem decisions.

## Commitments This Reply Locks In

- The organization should standardize on one async runtime and one service template for pilot services.
- The pilot tests a specific Rust service platform, not unconstrained Rust usage.
