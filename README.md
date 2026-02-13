# Agent Skills

A curated collection of [Agent Skills](https://agentskills.io) for Claude Code, maintained by [Auxilio Partners](https://github.com/auxiliopartners). Skills give AI agents specialized capabilities and domain knowledge they can load on demand.

This repository is a **Claude Code plugin marketplace** — browse the available plugins below and install them with a single command.

## Available Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [check-deposit-reader](plugins/check-deposit-reader) | Extract structured data from scanned check deposit PDFs — payer name, address, amount, date, check number, and memo | 1.0.0 |

## Installation

Add this marketplace in Claude Code:

```
/plugin marketplace add auxiliopartners/auxilio-agent-skills
```

Then install a plugin:

```
/plugin install check-deposit-reader@auxilio-agent-skills
```

## What Are Agent Skills?

Skills follow the open [Agent Skills specification](https://agentskills.io/specification). Each skill consists of:

- A `SKILL.md` file with YAML frontmatter (`name` and `description` required)
- Optional `scripts/`, `references/`, and `assets/` directories

Skills are packaged into **plugins** for distribution through Claude Code marketplaces. Each plugin wraps one or more skills in its `skills/` directory alongside a `.claude-plugin/plugin.json` manifest.

See the [best practices guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) for skill authoring tips.

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a new plugin or improve an existing one.
