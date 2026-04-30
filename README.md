# skills

A collection of [Cursor Agent Skills](https://docs.cursor.com/) I use day-to-day. Each skill is a directory containing a `SKILL.md` file (plus optional reference docs and scripts) that Cursor's agent can invoke when triggered by name or context.

## Skills

- **[smart-mode](./smart-mode/SKILL.md)** — A disciplined design-first workflow for AI-assisted software engineering. Code is a critical asset; the user is the strategic architect, the agent is the tactical programmer. Triggered by saying "smart mode".

## Install

Skills are loaded by Cursor from `~/.cursor/skills/` (personal) or `.cursor/skills/` (project-scoped). The simplest setup is to clone this repo somewhere stable and symlink the skills you want into `~/.cursor/skills/`.

```bash
git clone https://github.com/trevsm/skills.git ~/skills
ln -s ~/skills/smart-mode ~/.cursor/skills/smart-mode
```

Repeat the `ln -s` line for each skill you want enabled. Restart Cursor (or start a new agent session) to pick up new skills.

## Layout

```
skills/
├── README.md
└── <skill-name>/
    ├── SKILL.md         # required — main instructions and YAML frontmatter
    └── *.md             # optional — reference docs loaded on demand
```

Each `SKILL.md` declares its trigger conditions in YAML frontmatter:

```yaml
---
name: skill-name
description: What it does and when to use it.
disable-model-invocation: true   # only loads when explicitly named
---
```

## Credits

The `smart-mode` skill is heavily inspired by Matt Pocock's [`mattpocock/skills`](https://github.com/mattpocock/skills) — particularly his architecture vocabulary (module / interface / seam / adapter / depth / leverage / locality) and his TDD vertical-slice workflow.
