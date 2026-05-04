# Glossary

**New backend service**: A production service started after Q3 that is not a rewrite of an existing service.
_Avoid_: migration, prototype, script.

**High-throughput**: A service where request volume, queue volume, or data volume makes runtime performance materially affect operating cost or reliability.

**Correctness-sensitive**: A service where type, memory, concurrency, or state-machine errors are costly enough that stronger compile-time guarantees matter.

**Default language**: The first option considered for scoped services. It is not a mandate when explicit defeat conditions apply.

**Incremental adoption**: Starting with bounded services, measured outcomes, and an explicit rollback path before broadening the default.

**Rollback path**: A documented decision point where the organization can return to the current stack for future services without rewriting the pilot services.

**Training cost**: The time and budget required to make the first teams productive enough to own Rust services without specialist rescue.
