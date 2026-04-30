---
name: smart-mode
description: Engage a disciplined design-first workflow for AI-assisted software engineering. Treats code as a critical asset; the user is the strategic architect, the agent is the tactical programmer. Use when the user says "smart mode", "engage smart mode", or asks for a rigorous, design-first approach to building with AI.
disable-model-invocation: true
---

# Smart Mode

Code is not cheap; it is a critical asset. Reject the specs-to-code reflex — it produces unmaintainable systems and high technical debt. Slow down and run the workflow below.

The user is the strategic architect. The agent is the tactical programmer. Surface trade-offs; never silently choose.

## Vocabulary (use these terms, not substitutes)

Use this vocabulary exactly. See [LANGUAGE.md](LANGUAGE.md) for full definitions.

- **Module** — anything with an interface and an implementation (function, class, package, slice). _Not_: unit, component, service.
- **Interface** — everything a caller must know to use the module: types, invariants, ordering, error modes, required config. _Not_: signature, API.
- **Implementation** — the code inside.
- **Depth** — leverage at the interface. **Deep** = a lot of behavior behind a small interface. **Shallow** = interface nearly as complex as implementation.
- **Seam** — where an interface lives; a place behavior can be altered without editing in place. _Not_: boundary.
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Leverage** — what callers get from depth.
- **Locality** — what maintainers get from depth: change, bugs, knowledge concentrated in one place.

Key tests applied throughout:

- **Deletion test** — imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** If you want to test past the interface, the module is the wrong shape.
- **One adapter = hypothetical seam. Two adapters = real seam.** Don't introduce a port unless something actually varies across it.

## The Workflow

Run these phases in order for any non-trivial task. Do not skip ahead.

### 1. Establish a Design Concept

Before writing any code, run a grilling session against the user to reach a shared understanding of the problem.

- Apply `~/.cursor/skills/grill-me/SKILL.md`: walk each branch of the design tree, one question at a time, providing your recommended answer.
- If a question can be answered by exploring the codebase, explore instead of asking.
- Resolve dependencies between decisions before moving on.

Exit only when problem, constraints, and shape of the solution are explicit.

### 2. Establish Ubiquitous Language

Inspired by Domain-Driven Design. You and the user must mean the same thing by the same words. This drastically reduces verbosity and miscommunication.

Look for an existing domain glossary first, in this preference order:

1. `CONTEXT.md` at repo root (single context).
2. `CONTEXT-MAP.md` at root pointing to per-context `CONTEXT.md` files (multi-context repo).
3. `CLAUDE.md` at repo root (Claude Code convention) — read it for any glossary section.
4. `AGENTS.md` at repo root (cross-agent convention) — read it for any glossary section.
5. `docs/glossary.md` or any other project-specific glossary file.

If a `CLAUDE.md` or `AGENTS.md` exists but contains no glossary section, treat that as the canonical location for domain terms going forward — append a `## Glossary` section there rather than creating a separate `CONTEXT.md`. Match the user's existing convention; don't introduce a new file when one already serves the purpose.

If **none** of the above exists in the area you're touching, **create lazily** — only when the first domain term is resolved during the grilling session, not preemptively. Default to `CONTEXT.md` for greenfield repos; default to extending `CLAUDE.md` if the project is clearly a Claude Code workspace.

During the session:

- **Challenge against the glossary.** If the user uses a term that conflicts with the active glossary file, call it out: "Your glossary defines X as Y, but you seem to mean Z — which is it?"
- **Sharpen fuzzy terms.** "You're saying 'account' — Customer or User? Those are different."
- **Update inline.** When a term is resolved, write it to the active glossary file right there. Don't batch.
- **Don't couple to implementation.** Only include terms meaningful to domain experts.

Use these terms verbatim in code, comments, tests, commits, and conversation thereafter.

### 3. Test-Driven Development (Vertical Slices)

Tests are the feedback loop that prevents the agent from outrunning its headlights.

**Anti-pattern: horizontal slicing** — writing all tests first, then all implementation. This produces tests of imagined behavior, coupled to the shape of data structures rather than user-facing behavior. They pass when behavior breaks and fail when behavior is fine.

**Correct pattern: vertical slices via tracer bullets.** One test → one implementation → repeat. Each cycle responds to what you learned from the previous one.

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  ...
```

Per cycle:

- **RED:** write one failing test for the next behavior. Use `CONTEXT.md` vocabulary in the test name. Test through the public interface only.
- **GREEN:** minimal code to pass. No speculative features. No anticipating future tests.
- **Refactor only when GREEN.** Never refactor while RED.

Test rules:

- Test behavior through the public interface, not implementation details.
- Test would survive an internal refactor.
- Mock at system boundaries only (external APIs, time, randomness). Do not mock your own modules.
- Project-level: check `package.json` (or equivalent) for an existing test script before adding tooling. If no test runner exists, set one up before continuing.

Confirm with the user **which behaviors matter most** before the first cycle. You can't test everything.

### 4. Design Deep Modules

Structure the codebase as fewer, larger modules with small interfaces. Push complexity inward; expose simplicity outward. Avoid the trap of many shallow modules — they fragment the system and increase navigation cost for both human and AI.

```
Deep module                       Shallow module (avoid)
┌─────────────────┐               ┌──────────────────────────┐
│ Small Interface │               │   Large Interface        │
├─────────────────┤               ├──────────────────────────┤
│                 │               │   Thin Implementation    │
│  Deep impl.     │               └──────────────────────────┘
│                 │
└─────────────────┘
```

When proposing structure:

- Apply the **deletion test** before extracting a new module.
- A new module needs **two adapters** (typically production + test) to justify a seam. One adapter = indirection, not a seam.
- Internal seams (private to a module's implementation, used by its own tests) are fine. Don't expose them through the public interface.
- Resist premature extraction. Wait for real duplication or a real seam.

### 5. Delegate Implementation, Design the Interface

Treat each module as a gray box. The user designs the **interface**; the agent fills the **implementation**.

The interface includes:

- Types and method shapes
- Invariants the module preserves
- Ordering constraints
- Error modes
- Required configuration

Steps:

1. Define the interface and its invariants in code (or a sketch).
2. Write tests against the interface from the outside (the test surface = the interface).
3. Only then implement internals — this is where the agent moves quickly with low risk.
4. Tests must survive internal refactors.

If the user has not specified an interface, return to phase 1 and grill them on it.

## Operating Principles

- **Architect vs. programmer.** User makes strategic decisions; agent executes tactical implementation. Surface trade-offs.
- **Code is a liability.** Less code that is well-shaped beats more code that sprawls. Lines-of-code is not an output metric.
- **Slow is smooth.** Small, deliberate, test-backed steps compound into a stable system. Large speculative jumps create debt.
- **Design every day.** System design is not a one-time event. Every change is a design decision.
- **Use the vocabulary.** Drift into "component," "service," "API," or "boundary" and the design discussion gets fuzzy. Stay precise.

## Pre-Flight Checklist

Confirm each item before generating implementation code:

```
- [ ] Phase 1: Design concept established via grill-me interview
- [ ] Phase 2: Domain terms captured in the active glossary (CONTEXT.md / CLAUDE.md / AGENTS.md), created lazily if absent
- [ ] Phase 3: First failing test written for the next vertical slice
- [ ] Phase 4: Module shape proposed; deletion test applied; seams justified by ≥2 adapters
- [ ] Phase 5: Interface defined (types + invariants + ordering + error modes + config)
```

If any box is unchecked, return to that phase before continuing.

## Source

This skill encodes Matt Pocock's framework for software engineering fundamentals in the age of AI coding tools, adapted from his public skills repository (`mattpocock/skills`).
