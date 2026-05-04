# Commitments

- Rust adoption is justified only for high-throughput, correctness-sensitive backend services.
- The first two Rust services must include build-cache setup, CI timing budgets, and a rollback path.
- Rust hiring risk is acceptable only if adoption starts with a bounded service class and explicit training budget.
- Library maturity must be assessed per service before Rust is selected.
- Integration with existing Node services should happen over network contracts, not embedded FFI, unless FFI is independently justified.
- The organization should standardize on one async runtime and one service template for pilot services.
- Training is part of the adoption cost, not an optional afterthought.
