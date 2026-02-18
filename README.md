# Agent Skills

A curated collection of [Agent Skills](https://agentskills.io) maintained by [Auxilio Partners](https://github.com/auxiliopartners). Skills give AI agents specialized capabilities and domain knowledge they can load on demand.

These skills follow the open [Agent Skills specification](https://agentskills.io/specification) and work with **Claude Code**, **Gemini CLI**, and any agent that supports the standard. Browse the available skills below and install them for your platform.

## Available Plugins

| Plugin | Description | Version |
|--------|-------------|---------|
| [check-deposit-reader](plugins/check-deposit-reader) | Extract structured data from scanned check deposit PDFs — payer name, address, amount, date, check number, and memo | 1.0.0 |
| [planning-center-sermon-series](plugins/planning-center-sermon-series) | Create sermon series in Planning Center Publishing with title, description, and artwork uploads | 1.0.0 |
| [planning-center-sermon-episodes](plugins/planning-center-sermon-episodes) | Create sermon episodes in Planning Center Publishing with audio, artwork, speakers, and Subsplash migration support | 1.0.0 |

## Installation

### Claude Code

Add this marketplace in Claude Code:

```
/plugin marketplace add auxiliopartners/auxilio-agent-skills
```

Then install a plugin:

```
/plugin install check-deposit-reader@auxilio-agent-skills
```

### Gemini CLI

Gemini CLI supports the same Agent Skills format. Install a skill directly from this repository using `--path` to target the specific skill directory:

```bash
gemini skills install https://github.com/auxiliopartners/auxilio-agent-skills.git --path plugins/check-deposit-reader/skills/check-deposit-reader
```

Replace `check-deposit-reader` with any skill name from the table above. Available paths:

| Skill | Install path |
|-------|-------------|
| check-deposit-reader | `plugins/check-deposit-reader/skills/check-deposit-reader` |
| planning-center-sermon-series | `plugins/planning-center-sermon-series/skills/planning-center-sermon-series` |
| planning-center-sermon-episodes | `plugins/planning-center-sermon-episodes/skills/planning-center-sermon-episodes` |

**Alternative: manual installation**

Clone the repo and copy a skill to your Gemini skills directory:

```bash
git clone https://github.com/auxiliopartners/auxilio-agent-skills.git
cp -r auxilio-agent-skills/plugins/check-deposit-reader/skills/check-deposit-reader ~/.gemini/skills/
```

Skills placed in `~/.gemini/skills/` are available across all projects. For project-scoped skills, copy to `.gemini/skills/` in your workspace instead.

**Verify installation** by running `/skills list` in a Gemini CLI session — the installed skill should appear in the list.

See the [Gemini CLI Agent Skills documentation](https://geminicli.com/docs/cli/skills/) for more details.

## What Are Agent Skills?

Skills follow the open [Agent Skills specification](https://agentskills.io/specification) — a cross-platform standard supported by Claude Code, Gemini CLI, and other compatible agents. Each skill consists of:

- A `SKILL.md` file with YAML frontmatter (`name` and `description` required)
- Optional `scripts/`, `references/`, and `assets/` directories

For Claude Code distribution, skills are packaged into **plugins** with a `.claude-plugin/plugin.json` manifest. For Gemini CLI, skill directories can be installed directly into `~/.gemini/skills/` or `.gemini/skills/`.

See the [best practices guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) for skill authoring tips.

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a new plugin or improve an existing one.
