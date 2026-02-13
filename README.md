# Agent Skills

An internal catalog of [Agent Skills](https://agentskills.io) for our team. Skills give AI agents specialized capabilities and domain knowledge they can load on demand.

## Skill Catalog

| Skill | Description | Compatibility |
|-------|-------------|---------------|
| *No skills yet — be the first to [contribute one](CONTRIBUTING.md)!* | | |

## Installing Skills

Each skill is a folder containing a `SKILL.md` file. To install a skill, clone this repo and copy (or symlink) the skill folder into your agent's skills directory.

```bash
git clone git@github.com:auxiliopartners/agent-skills.git
```

### Claude Code

Copy a skill folder into your project or user-level skills directory:

```bash
# Project-level (available in one project)
cp -r skills/my-skill .claude/skills/my-skill

# User-level (available everywhere)
cp -r skills/my-skill ~/.claude/skills/my-skill
```

Or symlink to stay in sync with the repo:

```bash
ln -s "$(pwd)/skills/my-skill" ~/.claude/skills/my-skill
```

### Claude Cowork

In Claude Cowork, add the skill through the project settings or copy the skill folder into the project's `.claude/skills/` directory.

### Gemini CLI

Copy the skill folder into your Gemini CLI skills directory:

```bash
cp -r skills/my-skill ~/.gemini/skills/my-skill
```

## Spec Reference

Skills follow the open [Agent Skills specification](https://agentskills.io/specification). Each skill must have:

- A `SKILL.md` file with YAML frontmatter (`name` and `description` required)
- Optional `scripts/`, `references/`, and `assets/` directories

See the [best practices guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) for authoring tips.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add or update skills via pull request.
