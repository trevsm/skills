# skills

A small, opinionated set of [Cursor Agent Skills](https://docs.cursor.com/) for AI-assisted software engineering. Each skill is a directory with a `SKILL.md` file (plus optional reference docs and scripts) that Cursor's agent can invoke when triggered by name or context.

The headline skill is **`smart-mode`**, an orchestrator that scope-assesses your request and right-sizes the workflow — small changes skip phases, large ones run them all. It composes with three sister skills (`grill-with-docs`, `improve-codebase-architecture`, `diagnose`) forked from [`mattpocock/skills`](https://github.com/mattpocock/skills) under MIT.

## Skills

- **[smart-mode](./smart-mode/SKILL.md)** — A disciplined design-first workflow for AI-assisted software engineering. Phase 0 classifies the request (trivial / surgical / feature / system) and selects which downstream phases run. Triggered by saying *"smart mode"*.
- **[grill-with-docs](./grill-with-docs/SKILL.md)** — Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates `CONTEXT.md` and ADRs inline as decisions crystallize. Used by smart-mode for phases 1–2.
- **[improve-codebase-architecture](./improve-codebase-architecture/SKILL.md)** — Surface deepening opportunities (refactors that turn shallow modules into deep ones) in an existing codebase. Run every few days as a periodic practice. Smart-mode hands off here for retroactive rescue.
- **[diagnose](./diagnose/SKILL.md)** — Disciplined diagnosis loop for hard bugs and performance regressions: build a deterministic feedback loop → reproduce → rank 3–5 falsifiable hypotheses → instrument → fix with regression test → post-mortem. Smart-mode hands off here for bug/perf work.

## How they compose

```
                       (you say "smart mode")
                                 │
                                 ▼
                       ┌──────────────────┐
                       │   smart-mode     │
                       │  (Phase 0:       │
                       │   classify)      │
                       └────────┬─────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
   build / refactor      bug / perf            architecture rescue
        │                       │                       │
        ▼                       ▼                       ▼
  ┌──────────────┐      ┌──────────────┐      ┌──────────────────┐
  │ Phase 1+2:   │      │  diagnose    │      │ improve-codebase-│
  │ grill-with-  │      │              │      │ architecture     │
  │ docs         │      └──────────────┘      └──────────────────┘
  └──────┬───────┘
         │
         ▼
  Phase 3 (TDD), 4 (deep modules), 5 (interface) — only the ones Phase 0 selected
```

## Install

Skills are loaded by Cursor from `~/.cursor/skills/` (personal) or `.cursor/skills/` (project-scoped). Clone this repo somewhere stable and symlink the skills you want.

```bash
git clone https://github.com/trevsm/skills.git ~/skills

# Symlink each skill you want enabled:
ln -s ~/skills/smart-mode                    ~/.cursor/skills/smart-mode
ln -s ~/skills/grill-with-docs               ~/.cursor/skills/grill-with-docs
ln -s ~/skills/improve-codebase-architecture ~/.cursor/skills/improve-codebase-architecture
ln -s ~/skills/diagnose                      ~/.cursor/skills/diagnose
```

Restart Cursor (or start a new agent session) to pick up new skills.

If you only want `smart-mode` and the sister skills it hands off to, install all four. Smart-mode hard-references the others, so installing it alone leaves dangling pointers.

## Layout

```
skills/
├── README.md
├── LICENSE
├── smart-mode/
│   ├── SKILL.md
│   └── LANGUAGE.md
├── grill-with-docs/
│   ├── SKILL.md
│   ├── CONTEXT-FORMAT.md
│   └── ADR-FORMAT.md
├── improve-codebase-architecture/
│   ├── SKILL.md
│   ├── DEEPENING.md
│   ├── INTERFACE-DESIGN.md
│   └── LANGUAGE.md
└── diagnose/
    ├── SKILL.md
    └── scripts/
        └── hitl-loop.template.sh
```

Each `SKILL.md` declares its trigger conditions in YAML frontmatter:

```yaml
---
name: skill-name
description: What it does and when to use it.
disable-model-invocation: true   # only loads when explicitly named
---
```

## Attribution

`grill-with-docs/`, `improve-codebase-architecture/`, and `diagnose/` are forked verbatim from [`mattpocock/skills`](https://github.com/mattpocock/skills) under MIT. Each forked `SKILL.md` carries a `Source` footer linking to its upstream location. The upstream copyright notice is preserved in this repo's [`LICENSE`](./LICENSE).

`smart-mode/` is original, but heavily inspired by Pocock's framework — particularly the architecture vocabulary (module / interface / seam / adapter / depth / leverage / locality), the four-failure-modes framing in his repo's README, and the vertical-slice TDD pattern.
