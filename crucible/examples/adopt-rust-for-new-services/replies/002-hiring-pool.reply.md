---
satisfies: "002-hiring-pool"
cycle: 2
status: PASSING
last_verified: 2026-05-04
judges_passed:
  - judge-a
  - judge-b
---

# Reply: Hiring Pool

## Reply

The hiring pool is smaller, so Rust should not be default for every new service. The thesis already limits the default to high-throughput, correctness-sensitive backend services, where the cost of a smaller pool can be offset by fewer runtime defects and lower operating risk. It remains rational only if the first pilots include explicit training budget, internal mentorship, and a hiring review before expanding the default.

## Commitments This Reply Locks In

- Rust hiring risk is acceptable only for the scoped service class.
- Rust adoption requires explicit training budget, internal mentorship, and a hiring review before expansion.
