# skills

A small, opinionated set of [Cursor Agent Skills](https://docs.cursor.com/) for AI-assisted software engineering. Each skill is a directory with a `SKILL.md` file (plus optional reference docs and scripts) that Cursor's agent can invoke when triggered by name or context.

The headline skill is **`smart-mode`**, an orchestrator that scope-assesses your request and right-sizes the workflow — small changes skip phases, large ones run them all. It composes with three sister skills (`grill-with-docs`, `improve-codebase-architecture`, `diagnose`) forked from [`mattpocock/skills`](https://github.com/mattpocock/skills) under MIT, plus two original learning systems: `evolve-skills` (adapts the agent to you — captures patterns from your sessions and feeds them back into smart-mode's classifier) and `stay-sharp` (keeps you sharp as the agent scales — captures competency signals and intervenes with commit-first quizzes when you defer on topics you've marked as must-know).

## Skills

- **[smart-mode](./smart-mode/SKILL.md)** — A disciplined design-first workflow for AI-assisted software engineering. Phase 0 classifies the request and commits to a single profile (`quick` / `surgical` / `feature` / `architectural`, or a handoff to `diagnose` / `improve-codebase-architecture`) that determines which downstream phases run. Includes [`FILE-HYGIENE.md`](./smart-mode/FILE-HYGIENE.md) — explicit forward-pressure judgment for when to extract a concept into its own file, countering AI's minimal-change bias toward bloated files. Triggered by saying *"smart mode"*.
- **[grill-with-docs](./grill-with-docs/SKILL.md)** — Grilling session that challenges your plan against the existing domain model, sharpens terminology, and updates `CONTEXT.md` and ADRs inline as decisions crystallize. Used by smart-mode for phases 1–2.
- **[improve-codebase-architecture](./improve-codebase-architecture/SKILL.md)** — Surface deepening opportunities (refactors that turn shallow modules into deep ones) in an existing codebase. Run every few days as a periodic practice. Smart-mode hands off here for retroactive rescue.
- **[diagnose](./diagnose/SKILL.md)** — Disciplined diagnosis loop for hard bugs and performance regressions: build a deterministic feedback loop → reproduce → rank 3–5 falsifiable hypotheses → instrument → fix with regression test → post-mortem. Smart-mode hands off here for bug/perf work.
- **[evolve-skills](./evolve-skills/SKILL.md)** — Tiered learning system that captures friction, corrections, and declared preferences from your sessions, promotes patterns into a curated `PREFERENCES.md`, and queues `SKILL.md` change proposals for your review. Append-only journal + threshold-based pref promotion + propose-only skill edits = grows with the user without going off the rails. Active during every smart-mode session.
- **[stay-sharp](./stay-sharp/SKILL.md)** — Sister skill to `evolve-skills`, pointed in the opposite direction: keeps the **user** sharp as LLM-assisted coding scales output. Captures competency signals (topic frequency, deferrals, thrashing, debugging cycles, concept misuse, vibes-driven decisions) into a shared journal; intervenes with commit-first quizzes when you defer on a topic you've classified as `must-know` in your tier list. User-curated tier list (`must-know` / `should-know` / `aware-of`) gates which interventions fire. Active during every smart-mode session.

## How they compose

```
                       (you say "smart mode")
                                 │
                                 ▼
                       ┌──────────────────┐
                       │   smart-mode     │      ┌──────────────────────┐
                       │  (Phase 0:       │ ←──reads──┤ evolve-skills        │
                       │   classify,      │      │ PREFERENCES.md       │
                       │   apply prefs    │      └──────────────────────┘
                       │   + topic tiers) │                  ▲
                       │                  │ ←──reads──┐      │ continuous capture
                       └────────┬─────────┘           │      │ of strong signals
                                │              ┌─────┴─────────┐
        ┌───────────────────────┼─────────┐    │ stay-sharp    │
        │                       │         │    │ MUST-KNOW.md  │
        ▼                       ▼         ▼    └───────┬───────┘
   build / refactor      bug / perf    architecture    │
        │                       │       rescue         │ continuous capture
        ▼                       ▼         ▼            │ of competency signals
  ┌──────────────┐      ┌──────────────┐  ┌──────────────┐  │ + commit-first
  │ Phase 1+2:   │      │  diagnose    │  │ improve-     │  │ quizzes on
  │ grill-with-  │      │              │  │ codebase-    │  │ must-know deferrals
  │ docs         │      └──────────────┘  │ architecture │  │
  └──────┬───────┘                        └──────────────┘  │
         │                                                  │
         ▼                                                  │
  Phase 3 (TDD), 4 (deep modules), 5 (interface) — only the ones Phase 0 selected
  └──→ Checklist complete → both sister skills write end-of-session reflections
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
ln -s ~/skills/evolve-skills                 ~/.cursor/skills/evolve-skills
ln -s ~/skills/stay-sharp                    ~/.cursor/skills/stay-sharp
```

`evolve-skills` and `stay-sharp` share `~/.cursor/skills-journal/` as their data store; `evolve-skills` bootstraps the directory on first use, and `stay-sharp` adds two sibling files (`COMPETENCY-JOURNAL.md` and `MUST-KNOW.md`). The whole directory is local-only and never committed to this repo. You can opt in to private cross-machine sync by adding a private remote: `cd ~/.cursor/skills-journal && git remote add origin <your-private-url>`.

Restart Cursor (or start a new agent session) to pick up new skills.

If you only want `smart-mode` and the sister skills it hands off to, install all four. Smart-mode hard-references the others, so installing it alone leaves dangling pointers.

## Layout

```
skills/
├── README.md
├── LICENSE
├── smart-mode/
│   ├── SKILL.md
│   ├── LANGUAGE.md
│   └── FILE-HYGIENE.md          (file-vs.-module judgment; counters AI's minimal-change bias)
├── grill-with-docs/
│   ├── SKILL.md
│   ├── CONTEXT-FORMAT.md
│   └── ADR-FORMAT.md
├── improve-codebase-architecture/
│   ├── SKILL.md
│   ├── DEEPENING.md
│   ├── INTERFACE-DESIGN.md
│   └── LANGUAGE.md
├── diagnose/
│   ├── SKILL.md
│   └── scripts/
│       └── hitl-loop.template.sh
├── evolve-skills/
│   └── SKILL.md
└── stay-sharp/
    └── SKILL.md
```

`evolve-skills` and `stay-sharp` have no supporting files in the repo because all their data lives in the local-only `~/.cursor/skills-journal/`:

```
~/.cursor/skills-journal/             (LOCAL ONLY — never committed to this public repo)
├── JOURNAL.md                        (evolve-skills; append-only; agent writes; you can read or edit)
├── PREFERENCES.md                    (evolve-skills; curated; auto-updated under threshold rules; smart-mode reads at Phase 0)
├── COMPETENCY-JOURNAL.md             (stay-sharp; append-only; agent writes; you can read or edit)
├── MUST-KNOW.md                      (stay-sharp; user-curated topic tier list; smart-mode reads at Phase 0)
├── proposals/                        (evolve-skills; pending SKILL.md change proposals; you approve via `evolve review`)
└── .git/                             (revertable history; optional private remote for sync)
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

`smart-mode/`, `evolve-skills/`, and `stay-sharp/` are original to this repo, but `smart-mode/` is heavily inspired by Pocock's framework — particularly the architecture vocabulary (module / interface / seam / adapter / depth / leverage / locality), the four-failure-modes framing in his repo's README, and the vertical-slice TDD pattern.
