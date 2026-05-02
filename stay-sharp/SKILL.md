---
name: stay-sharp
description: Tracks user-side competency signals during engineering sessions (topic frequency, deferrals, thrashing, debugging cycles, concept misuse, vibes-driven decisions) to fight skill atrophy from LLM-assisted coding. Maintains a user-curated topic tier list (`must-know` / `should-know` / `aware-of`); intervenes with commit-first quizzes when deferring on must-know topics. Active during every smart-mode session; invoke directly with `stay-sharp review`, `quiz me on <topic>`, `i know this`, `tier <topic> as <bucket>`, or `stay-sharp status`.
---

# Stay Sharp

A skill that watches for signs **you** are decaying as the agent scales your output, and pushes back at the moments where decay is cheapest to fix. Sister skill to `evolve-skills`: that one keeps the agent learning your style; this one keeps you learning your craft.

Three principles, in order of priority:

1. **The user is the lead engineer.** The point is not to gate work — the point is to keep the user in shape to *be* the lead engineer, even as the agent does more of the typing.
2. **Catch atrophy at the moment of deferral.** A commit-first quiz at the moment you're about to say "do whatever" is dramatically cheaper than studying after the fact. Most signals are captured silently; the active intervention is reserved for that moment.
3. **The user owns the tier list.** What counts as "must-know" is none of the agent's business. The agent suggests; the user classifies.

## Storage

Lives in `~/.cursor/skills-journal/` alongside the `evolve-skills` data — single git repo, single backup point, sibling files:

```
~/.cursor/skills-journal/
├── JOURNAL.md                (evolve-skills, agent-side learning — read by stay-sharp for `debugging-cycle` signals)
├── PREFERENCES.md            (evolve-skills)
├── COMPETENCY-JOURNAL.md     (stay-sharp, append-only signals)
├── MUST-KNOW.md              (stay-sharp, user-curated tier list)
├── proposals/                (evolve-skills)
└── .git/                     (shared)
```

Both `COMPETENCY-JOURNAL.md` and `MUST-KNOW.md` are bootstrapped by `evolve-skills`' first-run logic if they're missing — same `git init -b main`, same commit history.

## Vocabulary

- **Signal** — a structured observation captured to `COMPETENCY-JOURNAL.md`. Six types (see below).
- **Topic** — a domain bucket the signal belongs to (e.g., `redis-pub-sub`, `postgres-isolation-levels`, `react-suspense`). Free-form, agent-inferred from context.
- **Tier** — one of three buckets in `MUST-KNOW.md`: `must-know` (gatekeeper-mode), `should-know` (nudge mid-session), `aware-of` (silent capture only). Untagged topics default to `should-know`.
- **Deferral** — the user explicitly delegates a decision to the agent ("do whatever", "you decide", "I don't know", "your call", "I trust you", "whatever's best").
- **Justified override** — the user invokes `i know this` or `proceed` to bypass a commit-first quiz; logged as a deferral with `override: justified` so the journal accurately reflects the moment without penalising it.
- **Commit-first quiz** — at the moment of deferral on a tracked topic, the agent says: *"Before I answer, what's *your* approach? Commit to one."* The user names a direction; the agent then reveals its choice and contrasts.

## Signal types (capture inline, announced)

The agent watches for the following during smart-mode sessions and *immediately captures* them to `COMPETENCY-JOURNAL.md`. Each capture emits a one-line announcement: *"Captured to competency journal: \[signal-type] on \[topic] — \[one-sentence summary]."* Append-only, reversible via `git revert` in the journal repo.

| Signal type | What it looks like | Confidence |
|---|---|---|
| **topic-touch** | Domain mentioned/edited in the session (incremented per session, not per message) | high |
| **deferral** | "Do whatever / you decide / I don't know / your call / I trust you" in response to an agent question | high |
| **thrashing** | User re-prompts the same task with different approaches ≥3 times in one session, or asks "try something else" repeatedly without articulating *why* the previous attempt was wrong | high |
| **debugging-cycle** | ≥10 exchanges resolving a single bug where the user couldn't help diagnose. Read from `evolve-skills`' `JOURNAL.md` rather than dual-captured | high |
| **concept-misuse** | User uses a term incorrectly that the agent has to silently work around (e.g., calling Redis "a database", treating Promises as parallel execution) | low — flag as `low-confidence: true` |
| **vibes-decision** | User picks an approach without articulating why; when grilled, can't justify it | low — flag as `low-confidence: true` |

Low-confidence entries are filtered out of `stay-sharp review` by default; user can include them with `stay-sharp review --include-low-confidence`. They still count toward thresholds at half weight.

## Tier classification

`MUST-KNOW.md` has three sections: `## Must-know`, `## Should-know`, `## Aware-of`. Each entry is a single line: `- <topic-name> — <one-sentence reason>`.

**Bootstrap rule.** A topic that accumulates 3+ signals while *untagged* gets a one-time tier-suggestion prompt the next time it's touched: *"`redis-pub-sub` has 4 signals over the past 11 days, mostly architecture decisions. Tier as `must-know`, `should-know`, or `aware-of`?"* The agent's recommendation is based on the kind of signals (architecture/design decisions → suggest `must-know`; bug fixes/glue code → suggest `should-know`; one-off API lookups → suggest `aware-of`). The user picks; the answer is written verbatim to `MUST-KNOW.md`.

**Manual classification.** `tier <topic> as <bucket>` writes/moves the entry directly. Editing `MUST-KNOW.md` by hand is also fine.

**Promotion drift.** If a `should-know` topic accumulates 3+ deferrals or 2+ thrashing patterns in 30 days, the agent suggests promoting it: *"`postgres-isolation-levels` is hitting deferral patterns typical of a `must-know` topic — promote?"* Demotion is user-initiated only.

## Nudge thresholds (when interventions fire)

Tiered, with a hard rate limit so the skill never feels like nagging:

| Tier | Trigger | Action |
|---|---|---|
| **must-know** | Any deferral | Commit-first quiz fires immediately. No bypass without `i know this`. |
| **should-know** | 3 deferrals OR 2 thrashing patterns within 14 days | One-line in-chat nudge: *"Noticed 3 deferrals on `redis-pub-sub` over the past 9 days. Quick quiz now or defer to `stay-sharp review`?"* |
| **aware-of** | Any | Silent capture only. Surfaced in `stay-sharp review`. |
| **untagged** | 3 signals total | Tier-suggestion prompt (see Bootstrap rule above). |

**Hard rate-limit: max 1 mid-session nudge per 30 minutes**, regardless of triggers. Excess triggers still get captured to the journal; only the in-chat surfacing is rate-limited. Commit-first quizzes on must-know topics are exempt from the rate limit (they're tied to the moment of deferral and can't be deferred without losing the teaching opportunity).

## Quiz mechanisms

Three modes, each tied to a specific trigger:

### Commit-first interception (default for must-know deferrals)

At the moment of deferral on a must-know topic:

1. Agent: *"Before I answer, what's your approach to \[specific decision]? Commit to one. (Type your answer, or `i know this` to skip and proceed with my recommendation.)"*
2. User commits to a direction in 1–3 sentences.
3. Agent reveals its own recommendation and contrasts: *"You said X. I would have said Y. Here's where they agree and where they diverge: \[concrete contrast]."*
4. User accepts, modifies, or asks follow-up. Original deferral logged with `commit-first: <user's answer summarized>`.

Total time: typically under 2 minutes. The point is the *commitment*, not the quiz score.

### Deep Socratic (`quiz me on <topic>`)

Explicit, user-invoked. Agent:

1. Reads the last 30 days of `COMPETENCY-JOURNAL.md` entries for the topic to focus the questions on areas the user actually deferred on.
2. Asks 3–5 open Socratic questions, one at a time, waiting for each answer before proceeding.
3. After each answer: brief feedback (correct / partially correct + what's missing / common misconception detected), and a follow-up question if the answer surfaced new uncertainty.
4. At the end: a one-paragraph summary of what looked solid, what looked shaky, and a suggested 1–2-resource study list (links to specific docs or papers, not generic "read about X").

### Explain-back (opt-in for must-know topics on non-trivial changes)

When the user has flagged a topic as `must-know`, after a non-trivial change in that topic area, agent asks: *"In your own words, what did we just change and why?"* User answers; agent checks for accuracy. Captures `explain-back: accurate` / `explain-back: partial` / `explain-back: confused` to the journal. Off by default; opt in by appending `quiz-on-change: true` to the topic line in `MUST-KNOW.md`.

## Active commands (user-invoked)

| Command | What it does |
|---|---|
| `stay-sharp review` | Generates the dashboard from `COMPETENCY-JOURNAL.md`: top 10 topics by signal count, deferral hotspots, untiered topics awaiting classification, must-know topics with recent atrophy, and (if any) suggested study resources. Read-only; emits markdown to chat. |
| `quiz me on <topic>` | Runs a deep Socratic session on `<topic>`. See "Quiz mechanisms" above. |
| `i know this` (or `proceed`) | In-session bypass for a commit-first quiz. Logged as `deferral` with `override: justified`. Counts toward deferral metrics but flagged differently in the dashboard so genuine fluency doesn't pollute atrophy signal. |
| `tier <topic> as <must-know\|should-know\|aware-of>` | Writes or moves the entry in `MUST-KNOW.md`. Idempotent. |
| `stay-sharp status` | One-liner: total signals captured, untiered topics awaiting tiering, must-know topics with deferrals in the last 14 days, last review date. |

To revert a journal write, use `git revert HEAD` in `~/.cursor/skills-journal/` directly, or `evolve undo` (which works on the same shared repo).

## Smart-mode integration

`stay-sharp` is referenced from `smart-mode/SKILL.md` and is *active during every smart-mode session* via that reference. Two specific touchpoints:

### Phase 0 read

At the start of Phase 0, after `evolve-skills` reads `PREFERENCES.md`, the agent also reads `MUST-KNOW.md`. **Only mention tiers in the announcement that are relevant to this particular request's topic** — not the full list. If no must-know topics are touched, no announcement; the read is silent.

Example:

> *"Reading this as a small feature in the `redis-pub-sub` area, which is `must-know` for you. Commit-first quiz will fire on any deferral. Adjust?"*

### Continuous capture

During the session, signals are captured inline per the table above. The capture itself is silent except for the one-line announcement. Mid-session nudges follow the rate-limit rules.

### End-of-session reflection

When smart-mode's pre-flight checklist is fully checked, after `evolve-skills`' weak-signal capture, `stay-sharp` runs a single reflection write: any topics that crossed thresholds during the session, any tier-promotion candidates, any deferrals on must-know topics that *didn't* trigger a commit-first quiz (a bug to investigate). One batched journal entry, no chat output unless something requires user action.

## Outside smart-mode

The skill's commands (`stay-sharp review`, `quiz me on X`, `i know this`, `tier X as Y`, `stay-sharp status`) work in any session where the skill is loaded. Continuous capture and gatekeeper-mode interventions only fire inside smart-mode (where there's a workflow to gate). Outside smart-mode, the skill is review-only.

## Dashboard format (`stay-sharp review`)

Output template:

```markdown
# Competency review — <date range>

## Top topics by signal count
1. `<topic>` — N signals (D deferrals, T thrashing, ...) — tier: `<tier>`
...

## Deferral hotspots (must-know topics with recent atrophy)
- `<topic>`: 4 deferrals in last 14d — last quiz: <date or "never"> — suggested action: <quiz / study / re-tier>
...

## Untiered topics needing classification
- `<topic>`: <N> signals — agent recommendation: `<tier>`. Run `tier <topic> as <bucket>` to set.
...

## Suggested next focus
1–2 sentences identifying the single highest-leverage thing to study, based on signal density × tier.
```

If there's nothing actionable in a section, omit the section entirely (no "no entries" placeholders).

## Failure modes (and what we do about them)

| Failure mode | Mitigation |
|---|---|
| Skill nags too much, user mutes it | Hard rate-limit (1 nudge / 30 min); `aware-of` tier exists explicitly to silence noise topics; user can edit `MUST-KNOW.md` directly to demote anything |
| Agent misclassifies `concept-misuse` or `vibes-decision` | Both tagged `low-confidence`, filtered from review by default, only count at half weight toward thresholds |
| User games `i know this` to skip every quiz | Justified overrides are *flagged differently* in the dashboard, not hidden — pattern of "always overrides on must-know X" surfaces as its own signal in review |
| Topic taxonomy fragments (`redis-pubsub` vs `redis-pub-sub` vs `redis_pubsub`) | At capture time, agent normalizes to kebab-case and checks for ≥80% string-similarity matches in the existing journal before creating a new bucket; on near-match, asks: *"merge with existing topic `redis-pub-sub`?"* |
| User declares topics they don't actually work on | Stale `must-know` entries (no signals in 60+ days) flagged at next `stay-sharp review` for keep / demote / remove |
| Skill captures during casual chat that isn't real engineering | Continuous capture is gated to smart-mode sessions only — that's the workflow filter |
| Two machines, divergent journals | Shared repo with `evolve-skills`, so the same opt-in `git remote add` solves both |

## What's immutable (never auto-modified)

- `MUST-KNOW.md` is **only** modified via the `tier` command, the bootstrap-tier prompt (with explicit user choice), or direct user edit. The agent never writes to `MUST-KNOW.md` autonomously.
- The `stay-sharp/SKILL.md` file itself. The skill cannot rewrite itself.

## Source

Original to this repo. Architecturally inspired by `evolve-skills` (same `~/.cursor/skills-journal/` storage, same append-only journal + curated overlay pattern, same one-line-announcement capture style), but pointed in the opposite direction: `evolve-skills` adapts the agent to the user; `stay-sharp` keeps the user adapting to the craft.

The commit-first quiz mechanism draws on the spaced-retrieval research literature (e.g., Roediger & Karpicke 2006, *Test-Enhanced Learning*): retrieval attempts before being told the answer produce ~50% better long-term retention than re-reading, even when the retrieval attempt fails. The "fight atrophy at the moment of deferral" framing is the application of that finding to the AI-assisted-coding workflow.
