"""Export agent-fusion skills to Claude Code's `SKILL.md` directory format.

Composes any `requires:` dependencies into the body, remaps frontmatter from
agent-fusion's schema to Claude Code's, and copies the `.sources.md` sidecar
alongside the exported skill so the audit trail follows the content.

Run as:
    python -m agent_fusion.export.claude_code --output-dir ~/.claude/skills
"""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_fusion.skills.loader import (
    Skill,
    compose_skill_body,
    load_skills_dir,
)

# agent-fusion write-tier tool names -> Claude Code tool names.
# Read-tier tools (filesystem.read, grep, glob, web_search, shell.read) are
# governed by Claude Code's permission settings, not pre-approved per skill.
TOOL_MAPPING: dict[str, tuple[str, ...]] = {
    "filesystem.write": ("Edit", "Write"),
    "shell.exec": ("Bash",),
    "network.post": ("Bash",),
    "git.commit": ("Bash(git commit *)", "Bash(git add *)"),
    "code_executor": ("Bash",),
}


def _map_allowed_tools(allowed_tools: frozenset[str]) -> list[str]:
    mapped: set[str] = set()
    for tool in allowed_tools:
        for cc_tool in TOOL_MAPPING.get(tool, ()):
            mapped.add(cc_tool)
    return sorted(mapped)


def _render_frontmatter(skill: Skill) -> str:
    lines = ["---", f"name: {skill.name}", f"description: {skill.description}"]
    cc_tools = _map_allowed_tools(skill.allowed_tools)
    if cc_tools:
        lines.append("allowed-tools:")
        for tool in cc_tools:
            lines.append(f"  - {tool}")
    if skill.paths:
        lines.append("paths:")
        for glob in skill.paths:
            lines.append(f'  - "{glob}"')
    lines.append("---")
    return "\n".join(lines)


def _render_success_criteria(skill: Skill) -> str:
    if not skill.success_criteria:
        return ""
    lines = ["## Success criteria", ""]
    for criterion in skill.success_criteria:
        lines.append(f"- {criterion}")
    return "\n".join(lines)


def export_skill(
    skill_name: str,
    skills: dict[str, Skill],
    output_dir: Path,
) -> Path:
    """Write one composed SKILL.md (plus copied sources sidecar) to output_dir.

    Returns the path to the written SKILL.md.
    """
    skill = skills[skill_name]
    composed_body = compose_skill_body(skills, skill_name)

    parts = [_render_frontmatter(skill), "", composed_body.rstrip()]
    criteria = _render_success_criteria(skill)
    if criteria:
        parts.extend(["", criteria])
    content = "\n".join(parts) + "\n"

    skill_dir = output_dir / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(content, encoding="utf-8")

    sources_src = skill.source_path.with_name(f"{skill_name}.sources.md")
    if sources_src.exists():
        (skill_dir / "sources.md").write_text(
            sources_src.read_text(encoding="utf-8"), encoding="utf-8"
        )

    return skill_md


def export_all(skills_dir: Path, output_dir: Path) -> list[Path]:
    """Export every skill in skills_dir as a Claude Code SKILL.md directory."""
    skills = load_skills_dir(skills_dir)
    return [export_skill(name, skills, output_dir) for name in sorted(skills)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export agent-fusion skills to Claude Code's SKILL.md format.",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=Path("skills"),
        help="Source directory of agent-fusion skills (default: ./skills)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Target directory, typically ~/.claude/skills",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.expanduser()
    written = export_all(args.skills_dir, output_dir)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
