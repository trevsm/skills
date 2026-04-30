# Architecture Language

Shared vocabulary used throughout `smart-mode`. Use these terms exactly. Adapted from `mattpocock/skills`.

## Terms

**Module**
Anything with an interface and an implementation. Scale-agnostic — applies equally to a function, class, package, or tier-spanning slice.
_Avoid_: unit, component, service.

**Interface**
Everything a caller must know to use the module correctly: type signature, invariants, ordering constraints, error modes, required configuration, performance characteristics.
_Avoid_: API, signature (too narrow — those refer only to the type-level surface).

**Implementation**
The code inside a module. Distinct from **Adapter**: a module can be a small adapter with a large implementation (a Postgres repo) or a large adapter with a small implementation (an in-memory fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise.

**Depth**
Leverage at the interface — how much behavior a caller (or test) can exercise per unit of interface they have to learn. **Deep** = a lot of behavior behind a small interface. **Shallow** = interface nearly as complex as implementation.

**Seam** _(Michael Feathers)_
A place where you can alter behavior without editing in that place. The location at which a module's interface lives. Choosing where to put the seam is its own design decision, distinct from what goes behind it.
_Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter**
A concrete thing that satisfies an interface at a seam. Describes role (what slot it fills), not substance (what's inside).

**File** _(physical, distinct from Module)_
A unit of source code in the filesystem. A module can span multiple files (e.g., a deep module split into `index.ts` plus an `internal/` directory); a file can contain multiple modules. File boundaries are decisions about cohesion and lifecycle, not arbitrary size limits — a 600-line single-purpose file is healthy; a 200-line file mixing five concepts is convoluted. See [FILE-HYGIENE.md](FILE-HYGIENE.md) for the judgment.

**Leverage**
What callers get from depth. More capability per unit of interface they have to learn. One implementation pays back across N call sites and M tests.

**Locality**
What maintainers get from depth. Change, bugs, knowledge, and verification concentrate at one place rather than spreading across callers. Fix once, fixed everywhere.

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small, mockable, swappable parts — they just aren't part of the interface. A module can have **internal seams** (private to its implementation, used by its own tests) as well as the **external seam** at its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test past the interface, the module is the wrong shape.
- **One adapter = hypothetical seam. Two adapters = real seam.** Introduce a port only when something actually varies across it (typically production + test).

## Dependency Categories (for deepening)

When deepening a module, classify its dependencies:

1. **In-process** — pure computation, in-memory state, no I/O. Always deepenable. No adapter needed.
2. **Local-substitutable** — has a local test stand-in (PGLite for Postgres, in-memory FS). Test with the stand-in. Internal seam; no port at the external interface.
3. **Remote but owned** — your own services across a network. Define a port at the seam; inject HTTP/gRPC adapter in production, in-memory adapter in tests.
4. **True external** — third-party services (Stripe, Twilio). Inject as a port; tests use a mock adapter.

## Rejected Framings

- **Depth as ratio of impl-lines to interface-lines** (Ousterhout): rewards padding implementation. Use depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public methods**: too narrow — interface here includes every fact a caller must know.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.
