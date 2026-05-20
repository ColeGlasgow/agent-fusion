"""Export agent-fusion skills to Cursor's `.mdc` rule format.

Composes any `requires:` dependencies into the body, remaps frontmatter from
agent-fusion's schema to Cursor's rule fields, and copies the `.sources.md`
sidecar alongside the exported rule so the audit trail follows the content.

Run as:
    python -m agent_fusion.export.cursor --output-dir .cursor/rules
"""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_fusion.skills.loader import (
    Skill,
    compose_skill_body,
    load_skills_dir,
)


def _render_frontmatter(skill: Skill) -> str:
    lines = ["---", f"description: {skill.description}"]
    if skill.paths:
        lines.append(f"globs: {','.join(skill.paths)}")
    lines.append("alwaysApply: false")
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
    """Write one composed Cursor .mdc rule plus copied sources sidecar."""
    skill = skills[skill_name]
    composed_body = compose_skill_body(skills, skill_name)

    parts = [_render_frontmatter(skill), "", composed_body.rstrip()]
    criteria = _render_success_criteria(skill)
    if criteria:
        parts.extend(["", criteria])
    content = "\n".join(parts) + "\n"

    output_dir.mkdir(parents=True, exist_ok=True)
    rule_path = output_dir / f"{skill_name}.mdc"
    rule_path.write_text(content, encoding="utf-8")

    sources_src = skill.source_path.with_name(f"{skill_name}.sources.md")
    if sources_src.exists():
        (output_dir / f"{skill_name}.sources.md").write_text(sources_src.read_text(encoding="utf-8"), encoding="utf-8")

    return rule_path


def export_all(skills_dir: Path, output_dir: Path) -> list[Path]:
    """Export every skill in skills_dir as a flat Cursor .mdc rule."""
    skills = load_skills_dir(skills_dir)
    return [export_skill(name, skills, output_dir) for name in sorted(skills)]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export agent-fusion skills to Cursor's .mdc rule format.",
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
        help="Target directory, typically .cursor/rules",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.expanduser()
    written = export_all(args.skills_dir, output_dir)
    for path in written:
        print(path)


if __name__ == "__main__":
    main()
