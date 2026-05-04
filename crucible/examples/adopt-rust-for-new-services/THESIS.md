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
- This does not claim Rust is universally better than TypeScript, Go, or Java.
- The first two Rust services must be incremental and reversible.
- Adoption must improve reliability or operating cost enough to justify training and tooling cost.

## What Would Defeat This

- Evidence that hiring and training costs exceed reliability and performance gains over an 18-month horizon.
- Evidence that our required libraries are immature enough to dominate delivery risk.
- Evidence that integration with existing Node services creates more operational risk than Rust removes.

## Out Of Scope

- Frontend language choice.
- Rewriting existing services.
- Mandating Rust for prototypes, scripts, or low-risk CRUD services.
