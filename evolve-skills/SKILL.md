---
name: evolve-skills
description: Captures friction, corrections, and declared preferences from your sessions, promotes patterns into a curated PREFERENCES.md, and queues SKILL.md change proposals for your review. Smart-mode reads PREFERENCES.md at Phase 0. Triggered automatically during a smart-mode session, or invoked directly by saying "evolve review", "evolve promote", "evolve propose", "evolve undo", or "evolve reset".
---

# Evolve Skills

A skill that lets the agent learn from your specific usage and adapt over time, **without going off the rails**. Three guardrails are non-negotiable:

1. **Tiered safety.** `JOURNAL.md` is append-only (always safe). `PREFERENCES.md` auto-updates with thresholds. `SKILL.md` files are propose-only — never autonomously edited.
2. **Forks are immutable.** `grill-with-docs/`, `diagnose/`, and `improve-codebase-architecture/` are MIT-licensed forks pinned to upstream. Proposals targeting them are auto-retargeted to `smart-mode/` as workflow-level adaptations.
3. **Everything is reversible.** All learnings live in a git-tracked directory. `evolve undo` is `git revert`. You can wipe with `evolve reset`.

## Storage

Per-user, local, git-tracked: `~/.cursor/skills-journal/`

```
~/.cursor/skills-journal/             (NEVER committed to public skills repo)
├── JOURNAL.md                        (append-only, newest first)
├── PREFERENCES.md                    (curated, threshold-promoted, read by smart-mode P0)
├── proposals/                        (pending SKILL.md diffs awaiting review)
│   ├── accepted/                     (audit trail of approved proposals)
│   └── rejected/                     (audit trail of rejected proposals + reason)
└── .git/                             (commit history; revertable; optionally remoted)
```

If the directory does not exist when the skill is first invoked, create it and `git init -b main`. Bootstrap files: `JOURNAL.md`, `PREFERENCES.md`, `proposals/{accepted,rejected}/.gitkeep`, `.gitignore`, `README.md`. Optional: user may set `git config user.name/email` inside the journal repo and add a private remote for cross-machine sync.

## Vocabulary

- **Capture** — append a structured entry to `JOURNAL.md`. Always safe (append-only).
- **Promote** — copy a pattern from `JOURNAL.md` to `PREFERENCES.md` once it crosses a threshold. Auto under tier rules.
- **Propose** — generate a `SKILL.md` change proposal as a markdown file in `proposals/`. Auto-generated, but never applied without your approval.
- **Apply** — execute an approved proposal: edit the target `SKILL.md`, commit it, move the proposal file to `proposals/accepted/`. Only happens after `evolve review` approval.
- **Signal strength** — explicit-strong / explicit-medium / implicit. Drives promotion thresholds (see below).

## Continuous behaviors (active during smart-mode and any conversation that loads this skill)

The agent watches for the following signals and *immediately captures* them to `JOURNAL.md`. Each capture emits a one-line announcement: *"Captured to journal: \[signal-type] — \[one-sentence summary]."* No confirmation gate; the journal is append-only and reversible.

### Strong-signal triggers (capture inline, announced)

| Signal type | What it looks like | Strength |
|---|---|---|
| **preference-declaration** | "I always want X", "from now on Y", "never Z", "I prefer Q", "remember this", "for next time" | explicit-strong |
| **correction-with-reason** | "Don't do X because Y", "this should have been a refactor not a feature", "skip the grilling, the change is small" | explicit-medium |
| **repeated-correction** | The user corrects the same point ≥2 times in a single session | explicit-medium |
| **dissatisfaction** | "That's not what I wanted", "this is wrong", "I don't like this approach", "you went too deep" | explicit-medium |
| **friction** | 3+ "no/stop/wait" responses in a row, OR user re-prompts the same task asking for less | implicit |
| **debugging-cycle** | More than 10 exchanges resolving a single bug or test failure | implicit |

### Weak-signal capture (batched at session-end)

When the smart-mode pre-flight checklist is fully checked, OR the user signals "done" / "ship it" / "merge it", emit a *single* batched journal entry summarizing weak signals:

- A phase that smart-mode skipped turned out to be needed (or vice versa)
- The user reordered the workflow
- The user asked for capability not present in any current skill
- A phase produced low-value output

Format the batched entry as one journal entry with a `## ... — smart-mode — workflow-failure` header containing a bulleted list of weak signals.

### Active commands (user-invoked)

| Command | What it does |
|---|---|
| `evolve review` | Walks pending proposals one at a time. For each: show diff, ask approve/reject/defer. Approved → apply + move to `accepted/`. Rejected → ask for reason, move to `rejected/`. Deferred → leave in queue. Also lists stale preferences (>30 days unreferenced) for confirm-or-prune. |
| `evolve promote <one-line preference>` | Manually escalate a journal observation to `PREFERENCES.md` immediately, bypassing thresholds. |
| `evolve propose <skill-name> <description>` | Manually generate a proposal targeting a specific skill. Bypasses pattern-detection. |
| `evolve undo` | `git revert HEAD` in the journal repo. Reverts the last auto-write. |
| `evolve reset` | Two-step destructive operation. First call: confirm intent + show what would be wiped. Second call within 5 minutes: actually wipe (delete `JOURNAL.md` content, delete `PREFERENCES.md` content, move all `proposals/` to `proposals/rejected/` with reason "reset"). |
| `evolve status` | Quick summary: journal entry count, preferences count, pending proposals count, last activity date. |

## Promotion rules

### Journal → PREFERENCES.md (auto, threshold-based)

| Signal strength | Threshold |
|---|---|
| explicit-strong | **N=1** — promote immediately on first occurrence |
| explicit-medium | **N=2** — promote after second occurrence within 14 days |
| implicit | **N=3** — promote after third occurrence within 30 days |

When a promotion fires:

1. Write the new entry to the appropriate section of `PREFERENCES.md` (e.g., `## Smart-mode`).
2. Update each cited journal entry's status from `pending (X/N)` to `promoted YYYY-MM-DD`.
3. Commit with message: `Promote: <one-line preference> (from N journal entries)`.
4. Announce in chat: *"Promoted to PREFERENCES.md: \[pattern]. Will be read by smart-mode at Phase 0 going forward."*

### PREFERENCES.md → proposals/ (auto, but never applied)

A proposal file is generated when EITHER:

- The PREFERENCES.md entry has been active for **>7 days** (filters out fads), OR
- The pattern is cited in **>5 journal entries** (high-confidence)

Proposal generation:

1. Identify the target skill. If the target would be a forked skill, **retarget** to `smart-mode/SKILL.md` as a workflow-level adaptation. Never propose changes to forks.
2. Generate `proposals/YYYY-MM-DD-<skill-name>-<short-summary>.md` using the format in `~/.cursor/skills-journal/proposals/README.md`.
3. Commit with message: `Propose: <short summary> targeting <skill-name>`.
4. Announce in chat: *"Proposal queued: review with `evolve review`."* — non-blocking notice.

## Conflict resolution

When a new `PREFERENCES.md` entry contradicts an existing one (e.g., "always TDD for refactors" → "skip TDD for refactors under 20 lines"):

1. The newer entry replaces the older.
2. The older entry moves to `## Superseded` at the bottom of `PREFERENCES.md` with a date and a back-reference to the entry that replaced it.
3. The journal keeps both entries forever (full history).
4. Announce: *"Preference superseded: \[old]. Replaced by: \[new]. See PREFERENCES.md ## Superseded for the audit trail."*

## Stale handling

Any `PREFERENCES.md` entry not referenced in any journal entry for >30 days is **flagged** at the next `evolve review` invocation. The user is asked: *"This preference hasn't surfaced in 30 days — keep, prune, or refresh?"* No automatic deletion.

## Smart-mode integration

`evolve-skills` is referenced from `smart-mode/SKILL.md` and is *active during every smart-mode session* via that reference. Two specific touchpoints:

### Phase 0 read

At the start of Phase 0, the agent reads `PREFERENCES.md` (if it exists). When announcing the classification, **only** mention preferences that *actually affected* this particular request's classification or phase application — not the full preference list. If no preferences applied, no announcement; the read is silent.

Example:

> *"Reading this as a surgical refactor. Applied preference: 'skip Phase 1 grilling for changes <5 lines.' Will apply Phase 3 (regression test only); skipping Phases 1, 2, 4, 5. Adjust?"*

### Checklist-completion reflection

When the smart-mode pre-flight checklist is fully checked, the agent runs the **weak-signal batched capture** described above. This captures the things that wouldn't have triggered an inline capture: phases that were skipped but turned out to matter, workflow reorderings, etc.

If no weak signals, no reflection — silent completion.

## What's immutable (never auto-modified)

- `grill-with-docs/`, `diagnose/`, `improve-codebase-architecture/` — MIT forks pinned to upstream. Proposals retarget to `smart-mode/`.
- The `evolve-skills/SKILL.md` file itself. The skill cannot rewrite itself. (You can edit it manually; it just can't propose changes to itself.)
- `LICENSE` and the repo's top `README.md`.

## Starting state and first run

On first invocation, if `~/.cursor/skills-journal/` does not exist:

1. Create the directory and subdirectories per the storage diagram.
2. `git init -b main`.
3. Write the bootstrap files (see this repo's commit history for the canonical templates).
4. First commit: `Bootstrap skills-journal`.
5. Print: *"Skills journal initialized at ~/.cursor/skills-journal/. Optional: set `git config user.name/email` inside the journal repo if you want your identity attached, or add a private remote for cross-machine sync."*

If the directory exists, just confirm it's a git repo and proceed.

## Failure modes (and what we do about them)

| Failure mode | Mitigation |
|---|---|
| Bad pattern cemented in PREFERENCES.md | `evolve undo` reverts last write; user can also edit `PREFERENCES.md` directly; supersession resolves contradictions |
| Journal grows unwieldy | Newest-first ordering keeps recent context accessible; older entries never break correctness |
| Multiple machines, divergent journals | User opt-in: `git remote add origin <private-url>` and pull/push manually. Out of scope for v1: automated sync. |
| Skill misclassifies a signal | User edits `JOURNAL.md` directly, or the false promotion gets superseded when correct signal accumulates |
| Forked skill gets a real bug that PREFERENCES.md works around | The workaround lives in `smart-mode` (workflow-level), not the fork. Fork can be re-synced to upstream cleanly. |
| User wants to start fresh | `evolve reset` (two-step, deliberate) |

## Source

Original to this repo. Designed as a tiered learning system: append-only capture (always safe), threshold-based preference promotion (auto with tier rules), propose-only skill modification (always user-approved). The thresholds (N=1/2/3 by signal strength) and the >7-days/>5-citations criteria for proposal generation are calibrated for resilience over speed: a single bad session cannot move the system, but repeated genuine signal does.
