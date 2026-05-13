# Exporting skills

agent-fusion's skills live in `skills/<name>.md` with a `.sources.md` sidecar. To use them in another tool, run an exporter for that tool.

## Claude Code

```bash
python -m agent_fusion.export.claude_code --output-dir ~/.claude/skills
```

This writes one Claude Code skill directory per agent-fusion skill:

```
~/.claude/skills/
├── code-generation/
│   ├── SKILL.md
│   └── sources.md
├── debugging/
│   ├── SKILL.md
│   └── sources.md
├── frontend-react/
│   ├── SKILL.md
│   └── sources.md
├── pr-review/
│   ├── SKILL.md
│   └── sources.md
└── python-backend/
    ├── SKILL.md
    └── sources.md
```

Each `SKILL.md` contains the composed body (a skill with `requires:` gets its foundation prepended) plus a Claude Code-compatible frontmatter block. The `sources.md` sidecar travels with the skill so the citation trail is preserved; Claude Code does not auto-load it, but it remains readable in the skill directory.

### What the exporter does

- **Composition.** `python-backend` declares `requires: [code-generation]`. The exported `python-backend/SKILL.md` includes the full `code-generation` body before the `python-backend` body, in the same order the skill loader produces.
- **Frontmatter remapping.**
  - `name`, `description`, `paths` are preserved verbatim — Claude Code uses the same field names.
  - `allowed_tools` is remapped: agent-fusion's tier names (`filesystem.write`, `shell.exec`, `git.commit`, `network.post`, `code_executor`) become Claude Code tool names (`Edit`, `Write`, `Bash`, `Bash(git commit *)`, etc.).
  - `success_criteria` is appended as a `## Success criteria` section at the end of the body so the verification checklist follows the skill into Claude Code.
  - `requires`, `preferred_models`, `tags` are dropped — Claude Code has no equivalent fields, and `requires` is already resolved via composition.

### Where to put the output

- `~/.claude/skills/` — personal skills, available in every project on your machine.
- `<project>/.claude/skills/` — project-scoped skills, checked into the project repo.

See [Claude Code's skill documentation](https://code.claude.com/docs/en/skills) for details on skill scoping, invocation, and the `SKILL.md` format.
