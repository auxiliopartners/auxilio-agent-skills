# Contributing Skills

Add new skills or improve existing ones by opening a pull request.

## Adding a New Skill

### 1. Create your skill directory

Copy the template and rename it:

```bash
cp -r _template skills/your-skill-name
```

### 2. Edit SKILL.md

Open `skills/your-skill-name/SKILL.md` and fill in:

**Frontmatter** (required):

```yaml
---
name: your-skill-name
description: Clearly describe what this skill does and when an agent should use it.
---
```

**Body** (required): Markdown instructions the agent will follow when the skill is activated.

### 3. Add optional resources

If your skill needs them, add subdirectories:

```
skills/your-skill-name/
├── SKILL.md
├── scripts/       # Executable code (Python, Bash, JS)
├── references/    # Additional documentation
└── assets/        # Templates, data files, schemas
```

### 4. Update the catalog

Add a row to the **Skill Catalog** table in [README.md](README.md):

```markdown
| your-skill-name | Brief description | Claude Code, Gemini CLI |
```

### 5. Open a pull request

Push your branch and open a PR. Use the skill name as the branch name prefix (e.g., `add/your-skill-name`).

## Naming Rules

Skill names must:

- Be **lowercase** with **hyphens** only (`a-z`, `0-9`, `-`)
- Be 1–64 characters
- Not start or end with a hyphen
- Not contain consecutive hyphens (`--`)
- Match the parent directory name

Prefer **gerund form** (e.g., `reviewing-code`, `generating-reports`) or noun phrases (e.g., `code-review`, `pdf-processing`).

Avoid vague names like `helper`, `utils`, or `tools`.

## Writing Good Descriptions

The `description` field is how agents decide whether to activate your skill. Make it count:

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

- [ ] `SKILL.md` has valid frontmatter with `name` and `description`
- [ ] Skill name matches directory name
- [ ] Name follows naming rules (lowercase, hyphens, 1–64 chars)
- [ ] Description is specific and under 1024 characters
- [ ] `SKILL.md` body is under 500 lines
- [ ] File references are one level deep
- [ ] Catalog table in README.md is updated
- [ ] Tested the skill with at least one agent (Claude Code, Cowork, or Gemini CLI)
