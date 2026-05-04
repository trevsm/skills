---
satisfies: "004-ffi-cost"
cycle: 4
status: PASSING
last_verified: 2026-05-04
judges_passed:
  - judge-a
  - judge-b
  - judge-c
---

# Reply: FFI Cost

## Reply

The adoption thesis does not require embedding Rust inside Node or making FFI the default seam. New Rust services should integrate with existing Node systems over existing network contracts, queues, or generated clients, the same way services in any other language integrate. If a candidate service requires tight in-process interop with Node, that is evidence against choosing Rust for that service under the ecosystem and integration defeat conditions.

## Commitments This Reply Locks In

- Integration with existing Node services should happen over network contracts, queues, or generated clients.
- Embedded FFI is not the default integration path for Rust adoption.
