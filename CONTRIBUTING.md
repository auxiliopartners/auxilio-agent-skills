# Contributing

Add new plugins or improve existing ones by opening a pull request.

## Adding a New Plugin

### 1. Create your plugin directory

Copy the template and rename it:

```bash
cp -r _template plugins/your-plugin-name
```

### 2. Configure plugin.json

Open `plugins/your-plugin-name/.claude-plugin/plugin.json` and fill in:

```json
{
  "name": "your-plugin-name",
  "description": "Describe what this plugin does and when an agent should use it.",
  "version": "1.0.0",
  "author": {
    "name": "Your Name or Organization"
  }
}
```

### 3. Rename and edit your skill

Rename the skill directory to match your plugin name:

```bash
mv plugins/your-plugin-name/skills/your-skill-name plugins/your-plugin-name/skills/your-plugin-name
```

Open `plugins/your-plugin-name/skills/your-plugin-name/SKILL.md` and fill in:

**Frontmatter** (required):

```yaml
---
name: your-plugin-name
description: Clearly describe what this skill does and when an agent should use it.
---
```

**Body** (required): Markdown instructions the agent will follow when the skill is activated.

### 4. Add optional resources

If your skill needs them, add subdirectories inside the skill folder:

```
plugins/your-plugin-name/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── your-plugin-name/
        ├── SKILL.md
        ├── scripts/       # Executable code (Python, Bash, JS)
        ├── references/    # Additional documentation
        └── assets/        # Templates, data files, schemas
```

### 5. Register in the marketplace

Add your plugin to the `plugins` array in `.claude-plugin/marketplace.json`:

```json
{
  "name": "your-plugin-name",
  "source": "./plugins/your-plugin-name",
  "description": "Brief description",
  "version": "1.0.0"
}
```

### 6. Update the README

Add a row to the **Available Plugins** table in [README.md](README.md):

```markdown
| [your-plugin-name](plugins/your-plugin-name) | Brief description | 1.0.0 |
```

### 7. Open a pull request

Push your branch and open a PR. Use the plugin name as the branch name prefix (e.g., `add/your-plugin-name`).

## Naming Rules

Plugin and skill names must:

- Be **lowercase** with **hyphens** only (`a-z`, `0-9`, `-`)
- Be 1–64 characters
- Not start or end with a hyphen
- Not contain consecutive hyphens (`--`)
- Match the parent directory name

Prefer **gerund form** (e.g., `reviewing-code`, `generating-reports`) or noun phrases (e.g., `code-review`, `pdf-processing`).

Avoid vague names like `helper`, `utils`, or `tools`.

## Writing Good Descriptions

The `description` field appears in both `plugin.json` and `SKILL.md` frontmatter. It is how agents decide whether to activate your skill. Make it count:

- **Be specific**: include key terms agents will match against
- **Write in third person**: "Generates commit messages by analyzing diffs" not "I help you write commits"
- **Include triggers**: "Use when the user asks about..." or "Use when working with..."
- **Max 1024 characters**

## Writing Good Instructions

- Keep `SKILL.md` body **under 500 lines** — move detailed content to `references/`
- Don't over-explain things the model already knows
- Provide concrete examples and step-by-step workflows
- Use consistent terminology throughout
- Keep file references **one level deep** from SKILL.md

## PR Checklist

Before submitting, verify:

- [ ] Plugin directory exists under `plugins/` with `.claude-plugin/plugin.json`
- [ ] `plugin.json` has `name`, `description`, `version`, and `author`
- [ ] `SKILL.md` has valid frontmatter with `name` and `description`
- [ ] Skill name matches directory name
- [ ] Name follows naming rules (lowercase, hyphens, 1–64 chars)
- [ ] Description is specific and under 1024 characters
- [ ] `SKILL.md` body is under 500 lines
- [ ] File references are one level deep
- [ ] Plugin is registered in `.claude-plugin/marketplace.json`
- [ ] Available Plugins table in README.md is updated
- [ ] Tested the skill with Claude Code
