# Capabilities — Detailed Recipes

Read this file when invoking a primitive for the first time in a session, or when one isn't producing. SKILL.md has the *short blurb*; this file has the *recipe*.

Each capability follows the same shape:

- **Trigger conditions** — when this is the right move (more specific than the SKILL.md blurb)
- **Recipe** — step-by-step
- **Output template** — what to put in the plan doc / chat
- **Anti-patterns** — failure modes to watch for
- **Composition notes** — what pairs well before/after

---

## Reframing

### Trigger conditions

- Phase 0 classified `starting-clarity` as `vague-urge` or `abstract-vision`
- A decomposition attempt is producing leaves that all feel "off" or trivially generic
- A critique surfaces "we may be solving the wrong problem"
- The user uses unstable vocabulary describing their own vision (sign the framing isn't yet load-bearing in their head)

### Recipe

1. Restate the user's vision in your own words in one sentence. Confirm.
2. Generate **2–4 distinct framings**. Each framing must:
   - Use a different *category of endeavor* (research / product / engineering / artistic / pedagogical / community / commercial)
   - Imply a different *first phase* of work
   - Imply a different *success criterion*
   - Imply a different *expert persona* who would naturally lead it
3. Present them as a comparison (table or short prose). For each, state:
   - The framing in one sentence
   - What the first concrete deliverable looks like under it
   - Who the natural expert lens is
   - The biggest risk of choosing this framing
4. **Recommend one** with reasoning. Don't be neutral — pick.
5. Wait for the user to choose, hybridize, or push back.

### Output template

```markdown
## Candidate framings

| # | Framing | First deliverable | Persona | Biggest risk |
|---|---|---|---|---|
| 1 | Vision-as-research-program | Falsifiable hypothesis + experiment design | Principal researcher | Slow; depends on results to direction |
| 2 | Vision-as-product | MVP that one user can try | Senior PM | May solve the wrong problem fast |
| 3 | Vision-as-platform | Minimal API others can build on | Platform engineer | Demand risk; build-it-they-may-not-come |

**Recommendation:** #1 — your vision references "real intelligence through environment interaction," which is a research claim, not a product claim. Building a product would force premature commitments to architecture.
```

### Anti-patterns

- **Framing inflation.** Producing 7 framings to look thorough. Stop at 4. Three is often best.
- **Strawman framings.** Including a framing you know the user will reject just to make your favorite look better. Each must be defensible.
- **Sycophantic recommendation.** "Whichever you prefer." Pick one and say why.

### Composition notes

- **Before:** usually the first primitive after Phase 0 announcement.
- **After:** typically decomposition under the chosen framing. Sometimes persona-adoption first if the framing strongly implies one.

---

## Decomposition

### Trigger conditions

- Framing is set
- The current node (vision, phase, milestone) is not yet a leaf (fails concretization-check)

### Recipe

1. State the parent node clearly.
2. Propose **2–5 children**. Each child must:
   - Have a name in the agreed vocabulary
   - Be a distinct *type of work* from its siblings (parallelize-able or strictly-ordered)
   - Move the parent meaningfully toward "done"
3. Mark dependencies between children (which must precede which).
4. **Depth-first the most uncertain or load-bearing child** — don't decompose all branches in parallel; that produces a wide shallow tree of equally-vague nodes.
5. After expanding one branch one level, *stop and apply concretization-check* on its frontier. If passed → leaf. If not → decompose again.

### Output template

```markdown
## Phase 1: {parent name}

Children (depth-first; expanding ★ first):

- ★ {child 1}  — {one-line purpose} — depends on: none
- {child 2}    — {one-line purpose} — depends on: {child 1}
- {child 3}    — {one-line purpose} — depends on: {child 1}
```

### Anti-patterns

- **Breadth-first soup.** Decomposing every branch one level, ending with 12 vague nodes and no actionable one. Always go deep on one branch before widening.
- **Symmetric decomposition.** Forcing every parent to have exactly 3 children. Use 2–5; some parents naturally split into 2, others 5.
- **Decomposing past the leaf.** If concretization-check passes, *stop*. Further decomposition is the agent inventing work.

### Composition notes

- **Before:** reframing (to set the framing) or critique (to confirm the parent is the right thing to decompose).
- **After:** concretization-check on new leaves; or further decomposition on uncertain branches.

---

## Critique-and-revise

### Trigger conditions

- A draft plan or sub-plan exists
- The user asks "is this right?" or "what could go wrong?"
- About to commit to a load-bearing decomposition or framing
- Concretization-check has passed but you have a nagging sense the leaf is wrong

### Recipe

1. Name what's being critiqued (the plan, this phase, this leaf).
2. Generate critiques across these standard angles (or a domain-appropriate subset):
   - **Feasibility** — is any leaf undeliverable in practice?
   - **Sequencing** — does any phase need an output a later phase produces?
   - **Hidden assumptions** — what is the plan quietly assuming about resources, users, environment, technology?
   - **Novelty** — is the plan reinventing something already solved? (If yes, route to research-synthesis.)
   - **Dependency risk** — what fails the whole tree if it doesn't land?
   - **Goal drift** — does the plan still serve the original vision, or has it morphed into something easier-but-different?
3. Optionally, spawn persona'd critic workers (see Worker-spawning) when angles benefit from independent voices — typical: a *senior practitioner* worker, a *skeptical reviewer* worker, a *user-advocate* worker.
4. Rank critiques by severity (load-bearing > nice-to-have).
5. Propose revisions for the top 2–3. User approves which to apply.

### Output template

```markdown
## Critique pass — {timestamp/iteration}

**Severity 1 (load-bearing):**
- {critique} — proposed revision: {revision}

**Severity 2 (worth addressing):**
- {critique} — proposed revision: {revision}

**Severity 3 (parking-lot):**
- {critique} — defer to {when}
```

### Anti-patterns

- **Critique inflation.** Producing 15 critiques to look rigorous. Cap at 5–7; rank ruthlessly.
- **Vague critiques.** "This might not scale." Make each critique specific enough to act on, or drop it.
- **Critique without revision.** Every critique above severity 3 needs a proposed fix.

### Composition notes

- **Before:** any major commit (locking a framing, finishing decomposition, declaring a leaf ready for handoff).
- **After:** revise the plan; if a severity-1 critique is fundamental, return to reframing or higher-level decomposition.

---

## Diverge-converge

### Trigger conditions

- A high-leverage decision has multiple plausible directions
- Early in a `vision-pass` and want to scout the design space
- Stuck — same primitive isn't producing new signal

### Recipe

1. State the question being explored — clearly, in one sentence.
2. Define **3+ radically different** approaches. They must differ on a meaningful axis (not "approach A in red vs. approach A in blue"). Useful axes:
   - Maximize simplicity vs. maximize flexibility vs. optimize for one specific user
   - Build vs. buy vs. delegate vs. avoid
   - Top-down deductive vs. bottom-up empirical vs. analogical-from-X
3. Spawn one worker per approach with a *highly detailed* prompt. Include: the vision, the framing, the question, the assigned approach, the output format. (Workers don't share your context.)
4. Workers return; manager **synthesizes**:
   - Extract the strongest element from each
   - Note where they agree (high-confidence ground) and where they disagree (genuine trade-offs)
   - Propose a unified direction OR present 2 finalists for the user to choose
5. **Synthesis is not voting.** If two of three workers agree, that's not a majority — it's three samples of a noisy process. Reason about the *content*, not the *count*.

### Output template

```markdown
## Diverge-converge: {question}

### Worker A (approach: minimize)
{summary of worker output, ~3–5 bullets}

### Worker B (approach: maximize flexibility)
{summary}

### Worker C (approach: optimize common case)
{summary}

### Synthesis
- **High-confidence ground:** all three agreed on {X}. Treat as decided.
- **Genuine trade-off:** A vs. B disagree on {Y}. Choosing A means {tradeoff}.
- **Recommendation:** {direction}, with {one element from B} retained because {reason}.
```

### Anti-patterns

- **Fake divergence.** Three workers exploring near-identical approaches because the axes weren't truly different. Spend the time defining the axes.
- **Concatenation as synthesis.** Pasting all three reports back-to-back. The manager's job is to *reduce* them.
- **Synthesis without recommendation.** Leaving the user with three options and no opinion. Pick.

### Composition notes

- **Before:** reframing (to ensure the question is well-posed) or critique (to identify what's contested).
- **After:** the chosen direction usually unlocks decomposition under it.

---

## Tree-search-and-prune

### Trigger conditions

- The plan is a tree with multiple competing branches
- Effort is fragmenting across too many active branches
- A branch has consistently failed to produce leaves and is consuming attention

### Recipe

1. List active branches (leaves and partially-decomposed sub-trees).
2. Score each on three axes (1–5):
   - **Leverage** — how much does this branch advance the vision if it succeeds?
   - **Confidence** — how likely is this branch to actually deliver, given current understanding?
   - **User interest** — does the user care about this one, or has it gone cold?
3. Compute leverage × confidence × interest (or just rank by combined judgment).
4. **Expand the highest-scoring branch** — apply decomposition or critique to it.
5. **Prune low-scoring branches** — move to a `## Ideas Parking Lot` section in the plan doc. Don't delete; the user may resurrect them.
6. Re-score after each iteration; the active branch shifts as you learn.

### Output template

```markdown
## Active branches (scored)

| Branch | Leverage | Confidence | Interest | Action |
|---|---|---|---|---|
| {A} | 5 | 4 | 5 | ★ Expanding |
| {B} | 4 | 3 | 3 | Holding |
| {C} | 3 | 2 | 1 | → Parking lot |

## Ideas Parking Lot

- {C} — pruned {date}. Revisit if {trigger condition}.
```

### Anti-patterns

- **Premature pruning.** Killing a branch on the first low score. Wait for two consecutive iterations before parking.
- **Hoarding.** Refusing to prune anything because "it might be useful." The parking lot exists to make pruning emotionally cheap.
- **Score theater.** Producing precise numbers ("4.2") when the underlying judgment is rough. Use 1–5 integers; the differences matter, not the decimals.

### Composition notes

- **Before:** decomposition (which often produces too many branches).
- **After:** decomposition or concretization-check on the active branch's frontier.

---

## Persona-adoption (manager-side)

### Trigger conditions

- The vision lives in a domain where a specific expert lens dramatically improves plan quality
- The user explicitly requests a persona ("approach this as a principal researcher")
- The reframing primitive surfaced a framing whose natural persona is unambiguous

### Recipe

1. Name the persona explicitly. Use a real-sounding role title (*principal AI researcher at a top lab*, *senior product manager at a consumer-app company*, *applied cryptographer with deployment experience*).
2. State *what changes* under this persona:
   - Vocabulary (use the field's terms)
   - Success criteria (a researcher cares about novel reproducible result; a PM cares about user outcome)
   - What counts as a leaf (an experiment with falsifiable prediction; a feature with usability test)
   - Common rituals (literature review; user interview; threat model)
3. **Announce the adoption.** *"Adopting principal AI researcher lens for the rest of this session — milestones will be framed as experiments with falsifiable predictions, not features."*
4. Apply the persona consistently in subsequent primitive invocations.
5. Drop the persona only on explicit user signal or session change.

### Output template

```markdown
## Persona: principal AI researcher

- **What this changes:**
  - Plans frame phases as *research questions*, not features.
  - Leaves are *experiments* with falsifiable predictions and a clear measurement protocol.
  - Critique includes "is this novel?" and "is this reproducible?"
  - Handoff to smart-mode means "build the experiment harness", not "build the product".
```

### Anti-patterns

- **Costume-only persona.** Stating the persona but not changing vocabulary, criteria, or what counts as a leaf. Theater without substance.
- **Switching personas mid-loop.** Producing a plan with mixed standards. If you're going to switch, close out the current pass first.
- **Inventing a persona that doesn't exist.** "Senior vibes engineer" — use real roles real people hold.

### Composition notes

- **Before:** reframing (the chosen framing usually implies a persona).
- **After:** all subsequent primitives operate under the persona's lens.

---

## Worker-spawning (delegate-side)

### Trigger conditions

- Diverge-converge with 3+ truly distinct approaches
- Critique-and-revise where independent voices add value beyond manager simulation
- Research-synthesis across multiple angles in parallel

### Recipe

1. **Decide it's worth it.** Workers cost tokens and synthesis effort. If the manager can answer in one head with comparable quality, don't spawn.
2. **Pick the right tool.** Use the `Task` tool with `subagent_type`:
   - `generalPurpose` — for synthesis, drafting, writing
   - `explore` — for read-only investigation of code or docs
   - `shell` — for command execution (rare in innovate-mode)
3. **Write a self-contained prompt.** Workers don't share conversation context. Include:
   - The full vision in 1–2 sentences
   - The chosen framing
   - The current persona (if adopted)
   - The specific question for *this* worker
   - The assigned approach/lens (so workers diverge meaningfully)
   - The exact output format you need back
4. **Spawn in parallel** when independence matters (diverge-converge, multi-angle critique). Spawn sequentially only when one worker's output informs another's prompt.
5. **Synthesize** the returns yourself — don't outsource synthesis to a worker.

### Output template (prompt to a worker)

```
You are operating as a {persona} for one focused task. Do not generalize.

Vision: {one sentence}
Framing: {one sentence}
Question: {one sentence}
Your assigned lens: {one sentence — what makes you different from other workers on this question}

Produce:
1. {Specific deliverable 1, e.g. "5-bullet summary of your approach"}
2. {Specific deliverable 2, e.g. "Top 3 risks under this lens"}
3. {Specific deliverable 3, e.g. "What would success look like in 3 months"}

Be opinionated. Do not hedge. ≤300 words.
```

### Anti-patterns

- **Worker for worker's sake.** Spawning when the manager could answer directly. Wasteful.
- **Vague worker prompts.** "Think about this and report back." Workers without context produce generic output. Specify the lens.
- **Recursive spawning.** Workers spawning workers in this skill. Don't — the cost explodes and synthesis becomes unmanageable. (If you genuinely need it, pull control back to the manager and re-spawn at the manager level.)
- **More than 4 workers per spawn.** Synthesis quality drops faster than worker count rises.

### Composition notes

- **Before:** the parent primitive (diverge-converge, critique, research-synthesis) decides workers are warranted.
- **After:** synthesis (manager-side, never delegated).

---

## Research-synthesis

### Trigger conditions

- Vision touches an established field where prior art shapes what's worth building
- A leaf would benefit from knowing what's already been tried
- Novelty critique surfaced "is this reinventing X?"

### Recipe

1. Identify 2–4 angles worth surveying (e.g. "current SOTA on agent learning", "open problems in reward specification", "production deployments of similar systems").
2. Spawn `explore`-type workers, one per angle. Worker prompt asks for:
   - Top 3–5 references / projects / papers
   - One-line summary of each
   - What's settled vs. what's still contested
   - Direct relevance to our vision
3. Synthesize into a *Prior Art* section of the plan:
   - **Settled ground:** don't reinvent.
   - **Open problems:** legitimate places to invest.
   - **Adjacent work:** could be partnered with, forked from, or learned from.
4. **Re-evaluate the framing** if the survey reveals the vision overlaps heavily with an existing project. Reframing is cheaper now than after building.

### Output template

```markdown
## Prior Art

### Settled ground (don't reinvent)
- {topic} — established approaches: {refs}

### Open problems (legitimate investment areas)
- {problem} — current attempts: {refs}; gap: {what's missing}

### Adjacent / overlapping work
- {project} — overlap: {what}; differentiator if we proceed: {what}
```

### Anti-patterns

- **Survey paralysis.** Surveying 8 angles and never using the findings. Cap at 4 angles.
- **Citation dump.** Listing references without "what this means for our plan." Always synthesize.
- **Survey-then-ignore.** Doing the survey and proceeding with the original plan unchanged. If the survey didn't change anything, you didn't need it (or didn't read it).

### Composition notes

- **Before:** reframing (to know what to survey) or critique (which surfaced novelty concerns).
- **After:** reframing (if the survey shifted understanding) or decomposition (now constrained by what's settled).

---

## Concretization-check

### Trigger conditions

- Before declaring any node a leaf
- Before handing anything off to smart-mode
- The user asks "is this concrete enough yet?"

### Recipe

1. State the candidate leaf in plain language.
2. Apply the test: *"Could a competent {persona} start work on this Monday morning, knowing what done looks like?"*
3. If **yes**, confirm the leaf has:
   - A clear name
   - A definition-of-done (DoD) — observable, testable
   - A scoped problem statement (what's in, what's out)
   - The needed input artifacts (data, prior decisions, dependencies)
   - An estimated effort range (T-shirt sizing is enough)
4. If **no**, name what's missing and route back to decomposition or sharpening.
5. **Don't gold-plate.** A leaf doesn't need a full spec — it needs enough that smart-mode's Phase 0 can pick it up.

### Output template

```markdown
## Leaf: {name}

- **Definition of done:** {observable criterion}
- **In scope:** {bullets}
- **Out of scope:** {bullets}
- **Inputs required:** {list}
- **Effort estimate:** {S / M / L}
- **Handoff target:** smart-mode (or named alternative)
```

### Anti-patterns

- **False positive (declaring a leaf prematurely).** Test fails the "Monday morning" check but agent moves on anyway. Defaults to optimistic; correct toward skeptical.
- **False negative (refusing to declare a leaf).** Endless decomposition. If the leaf already passes the test, *stop* and hand off — further decomposition is the agent inventing work.
- **DoD by activity, not outcome.** "Spend a week researching" is an activity, not a DoD. "Produce a 1-page memo answering question X" is a DoD.

### Composition notes

- **Before:** decomposition has produced a candidate leaf.
- **After:** handoff (if passed) or further decomposition / sharpening (if not).

---

## Handoff

### Trigger conditions

- A leaf passes concretization-check and the user wants to start executing
- The session's stopping criterion is met
- The user explicitly closes the innovate-mode session

### Recipe

1. Name the artifact being handed off — the specific leaf, the section of the plan doc, or the whole plan.
2. Name the receiving skill — typically smart-mode, sometimes diagnose, occasionally a domain-specific skill.
3. State the definition-of-done one more time, explicitly.
4. Identify any *context* the receiving skill needs that isn't in the artifact (constraints, persona, parent vision).
5. Issue the closing message; for `stay-resident` sessions, note the re-invocation trigger.
6. Exit innovate-mode for this session.

### Output template

```markdown
## Handoff

- **Artifact:** {leaf name or doc path}
- **Receiving skill:** smart-mode
- **Definition of done:** {restated}
- **Context smart-mode needs to know:**
  - Vision: {one sentence}
  - This leaf is part of: {phase / parent}
  - Persona this was scoped under: {persona}
  - Constraints not in the artifact: {bullets}

Innovate-mode is exiting. Re-invoke when {next trigger} — {e.g. "this leaf is shipped and we need to scope the next one"}.
```

### Anti-patterns

- **Silent handoff.** Just calling smart-mode without the closing structure. Smart-mode loses context; the user loses the seam.
- **Handoff without DoD.** The receiving skill doesn't know when it's done.
- **Premature handoff.** Concretization-check hadn't actually passed; agent rushed to hand off. The receiving skill will fail or guess.

### Composition notes

- **Before:** concretization-check has passed.
- **After:** none in this skill — control passes to the receiving skill.
