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
| `evolve review` | Walks pending proposals one at a time. **Default stance: reject when uncertain.** Repository-level context measurably moves agent behavior (Lulla et al. 2026 found −28.64% runtime / −16.58% tokens from AGENTS.md presence alone), so modifying it is consequential and should require articulable justification. For each proposal: show diff, ask approve/reject/defer. Approved → apply + move to `accepted/`. Rejected → ask for reason, move to `rejected/`. Deferred → leave in queue. Also lists stale preferences (>30 days unreferenced) for confirm-or-prune, and (when `PREFERENCES.md` is at soft cap) flags least-cited preferences for compaction. |
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

1. Apply the **positive-framing requirement** (see below). If the candidate cannot be reframed positively, do not promote — leave it in the journal as context.
2. Write the new entry to the appropriate section of `PREFERENCES.md` (e.g., `## Smart-mode`).
3. Update each cited journal entry's status from `pending (X/N)` to `promoted YYYY-MM-DD`.
4. Commit with message: `Promote: <one-line preference> (from N journal entries)`.
5. Announce in chat: *"Promoted to PREFERENCES.md: \[pattern]. Will be read by smart-mode at Phase 0 going forward."*

### Positive-framing requirement (the pink-elephant rule)

Research on negative constraints in agent prompts ([Semantic Gravity Wells, arXiv 2601.08070](https://www.arxiv.org/pdf/2601.08070)) shows that **negative framing fails 87.5% of the time** — telling an agent "don't do X" *activates* X in its attention 4.4× more than a positive instruction suppresses it. Every preference in `PREFERENCES.md` must be expressed positively or it actively makes the agent worse.

Reframe negative declarations to positive equivalents at promotion time:

| Negative declaration (rejected) | Positive reframe (promoted) |
|---|---|
| "Never grill me on small changes" | "Default to surgical-refactor classification for changes ≤5 lines" |
| "Don't set up testing for trivial work" | "Skip Phase 3 when Phase 0 classifies as trivial or surgical-refactor" |
| "Stop being verbose" | "Lead with the answer; full explanation only when asked" |
| "Don't propose deep modules until I ask" | "Surface deep-module candidates only when Phase 4 is selected" |

If a user signal **cannot** be cleanly reframed positively (e.g., a vague "I don't like this approach"), do not promote it. Capture it in the journal as context for `evolve review` and surface during the next review pass — the user can clarify with a positive equivalent or the entry can be discarded.

### Size policy

Research on AGENTS.md ([Princeton study, cited via asdlc.io](https://asdlc.io/practices/agents-md-spec/)) shows unnecessary context **actively harms** agent performance. Letta's memory-block architecture solves this with explicit size limits and recursive summarization. We do the same:

- **Soft cap: 30 active preferences across all sections.** When `PREFERENCES.md` reaches this size, the next `evolve review` flags the least-cited preferences (lowest occurrence count, oldest last-referenced date) for compaction or removal.
- **Hard cap: 60 active preferences.** Beyond this, every new promotion automatically supersedes the lowest-cited existing preference (moved to `## Superseded` with reason `auto-evicted at hard cap`). Announce the eviction in chat.
- **Compaction strategy:** when multiple preferences cover related territory, `evolve review` proposes merging them into a single positively-framed preference. The agent suggests the merged form; the user approves or edits.

The Superseded section has no cap — it's an audit trail, not active context. Smart-mode reads only the `## Smart-mode`, `## General`, and any other active section headers, never `## Superseded`.

### PREFERENCES.md → proposals/ (auto, but never applied)

### PREFERENCES.md → proposals/ (auto, but never applied)

**Bias toward rejection.** Repository-level agent context measurably changes agent behavior — Lulla et al. ([arXiv 2601.20404](https://arxiv.org/abs/2601.20404v1), Jan 2026, n=124 PRs) found that the presence of an AGENTS.md file alone shifts median runtime by **−28.64%** and output token use by **−16.58%**, holding task and repo constant. Context files have first-order effects on agent operation, which means modifying them is consequential. We do not have a published study isolating the effect of *auto-generated vs. human-written* preference content, but two factors argue for caution: (i) any change to `SKILL.md` immediately affects every future session, and (ii) auto-generated changes have not had a human in the loop to sanity-check framing, scope, or applicability.

The propose-only model exists because the cost of a bad change is ongoing (every session pays it) while the cost of a missed improvement is only the deferred upside. Asymmetric stakes → asymmetric stance.

`evolve review` should default-reject when uncertain. The user's bar for accepting a proposal should be: *"I can clearly see how this change makes the workflow better, and I can articulate the failure mode that motivated it."* If either is missing, reject.

A proposal file is generated when EITHER:

- The PREFERENCES.md entry has been active for **>7 days** (filters out fads), OR
- The pattern is cited in **>5 journal entries** (high-confidence)

Proposal generation:

1. Identify the target skill. If the target would be a forked skill, **retarget** to `smart-mode/SKILL.md` as a workflow-level adaptation. Never propose changes to forks.
2. Apply the positive-framing requirement to any prose introduced by the diff.
3. Generate `proposals/YYYY-MM-DD-<skill-name>-<short-summary>.md` using the format in `~/.cursor/skills-journal/proposals/README.md`.
4. Commit with message: `Propose: <short summary> targeting <skill-name>`.
5. Announce in chat: *"Proposal queued: review with `evolve review`. Note: default-reject when uncertain — research shows auto-modified context can degrade performance."* — non-blocking notice.

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

## Source and research lineage

Original to this repo, but not invented from whole cloth. The architecture matches several established research patterns:

- **Reflexion** ([Shinn et al., NeurIPS 2023](https://paperswithcode.com/paper/reflexion-language-agents-with-verbal)) — actor + evaluator + verbal self-reflection stored in episodic memory. Learning happens through context, not weight updates. Our `JOURNAL.md` is the episodic memory; promotion to `PREFERENCES.md` is the verbal reflection distillation.
- **Memento-Skills** ([arXiv 2603.18743](https://arxiv.org/pdf/2603.18743v1)) — markdown files as persistent, evolving memory; Read-Write Reflective Learning lets agents update their skill library based on new experience without modifying LLM parameters. Almost identical shape to evolve-skills.
- **MemSkill** ([arXiv 2602.02474](https://arxiv.org/pdf/2602.02474)) — controller selects relevant memory skills; a "designer" component periodically reviews difficult cases and evolves the skill set. Our `evolve review` plus auto-proposal generation is the designer.
- **MemMachine / Letta / MemGPT** — short-term + episodic + profile memory with explicit size limits and recursive summarization. Our PREFERENCES.md soft/hard caps and compaction strategy come directly from this.

Two empirical findings shape the safety design:

- **Negative-constraint backfire** ([Semantic Gravity Wells, arXiv 2601.08070](https://www.arxiv.org/pdf/2601.08070)): negative framing fails 87.5% of the time, with the forbidden behavior receiving 4.4× more attention than positive framing suppresses. → Positive-framing requirement at promotion time.
- **Repository-level agent context has first-order effects on agent behavior** ([Lulla et al., arXiv 2601.20404](https://arxiv.org/abs/2601.20404v1), Jan 2026, n=124 PRs): presence of AGENTS.md shifts median runtime by −28.64% and output tokens by −16.58% with comparable task completion. The paper does **not** measure auto-generated vs. human-written content, but it establishes that context files measurably move the agent — which means *changing* them is consequential. → Bias toward rejection at `evolve review` time; propose-only model is non-negotiable.

Author's note: an earlier draft cited a "Princeton study" finding auto-generated AGENTS.md degraded performance by 23%. That figure traced to a third-party blog summary and could not be verified against any peer-reviewed source. The citation was corrected; the principle (auto-modified context warrants human review) survives on the more conservative grounding above.

Calibration choices (thresholds N=1/2/3 by signal strength, >7-days/>5-citations for proposal generation, soft cap 30 / hard cap 60 for `PREFERENCES.md`) are tuned for resilience over speed: a single bad session cannot move the system, but repeated genuine signal does.
