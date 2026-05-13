"""Load and validate skill files against the spec in docs/SKILL_AUTHORING.md."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import yaml

READ_TIER_TOOLS = frozenset({
    "filesystem.read", "grep", "glob", "web_search", "shell.read",
})
WRITE_TIER_TOOLS = frozenset({
    "filesystem.write", "shell.exec", "network.post", "git.commit", "code_executor",
})

REQUIRED_FIELDS = {"name", "description"}
OPTIONAL_FIELDS = {
    "preferred_models", "allowed_tools", "success_criteria", "tags", "requires",
}
KNOWN_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS

KEBAB_CASE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
FRONTMATTER_DELIMITER = "---"


class SkillValidationError(ValueError):
    """Raised when a skill file fails validation. Message names the file and the problem."""


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    source_path: Path
    body: str
    preferred_models: tuple[str, ...] = ()
    allowed_tools: frozenset[str] = field(default_factory=frozenset)
    success_criteria: tuple[str, ...] = ()
    tags: frozenset[str] = field(default_factory=frozenset)
    requires: tuple[str, ...] = ()


def load_skill(path: Path) -> Skill:
    """Parse one skill file and validate it. Raise SkillValidationError on failure."""
    text = path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(text, path)
    data = _parse_yaml(frontmatter, path)
    _check_fields(data, path)
    _check_name(data["name"], path)
    _check_allowed_tools(data.get("allowed_tools", []), path)
    _check_body_sections(body, path)
    return Skill(
        name=data["name"],
        description=data["description"],
        source_path=path,
        body=body,
        preferred_models=tuple(data.get("preferred_models", []) or []),
        allowed_tools=frozenset(data.get("allowed_tools", []) or []),
        success_criteria=tuple(data.get("success_criteria", []) or []),
        tags=frozenset(data.get("tags", []) or []),
        requires=tuple(data.get("requires", []) or []),
    )


def load_skills_dir(directory: Path) -> dict[str, Skill]:
    """Load every `*.md` skill under `directory`, skipping `*.sources.md` sidecars.

    Validates each skill individually, then checks the cross-skill constraints
    (no unknown `requires:` targets, no cycles).
    """
    skills: dict[str, Skill] = {}
    for path in sorted(directory.rglob("*.md")):
        if path.name.endswith(".sources.md"):
            continue
        skill = load_skill(path)
        if skill.name in skills:
            raise SkillValidationError(
                f"duplicate skill name {skill.name!r} in {path} and {skills[skill.name].source_path}"
            )
        skills[skill.name] = skill
    _check_requires_graph(skills)
    return skills


def compose_skill_body(skills: Mapping[str, Skill], name: str) -> str:
    """Return a skill body with `requires` dependencies prepended in order."""
    if name not in skills:
        raise SkillValidationError(f"skill {name!r}: unknown skill")

    bodies: list[str] = []
    seen: set[str] = set()

    def append_body(skill_name: str) -> None:
        if skill_name in seen:
            return
        if skill_name not in skills:
            raise SkillValidationError(f"skill {skill_name!r}: unknown skill")
        skill = skills[skill_name]
        for dependency in skill.requires:
            append_body(dependency)
        seen.add(skill_name)
        bodies.append(skill.body.rstrip())

    append_body(name)
    return "\n\n".join(bodies) + "\n"


def _split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    if not text.startswith(FRONTMATTER_DELIMITER + "\n"):
        raise SkillValidationError(f"{path}: file must start with YAML frontmatter delimited by '---'")
    closing = text.find("\n" + FRONTMATTER_DELIMITER + "\n", len(FRONTMATTER_DELIMITER) + 1)
    if closing == -1:
        raise SkillValidationError(f"{path}: frontmatter is not closed with '---'")
    return text[len(FRONTMATTER_DELIMITER) + 1:closing], text[closing + len(FRONTMATTER_DELIMITER) + 2:]


def _parse_yaml(frontmatter: str, path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as exc:
        raise SkillValidationError(f"{path}: frontmatter YAML failed to parse: {exc}") from exc
    if not isinstance(data, dict):
        raise SkillValidationError(f"{path}: frontmatter must be a YAML mapping")
    return data


def _check_fields(data: dict[str, Any], path: Path) -> None:
    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        raise SkillValidationError(f"{path}: missing required frontmatter fields: {sorted(missing)}")
    unknown = data.keys() - KNOWN_FIELDS
    if unknown:
        raise SkillValidationError(f"{path}: unknown frontmatter fields: {sorted(unknown)}")
    if not isinstance(data["name"], str) or not isinstance(data["description"], str):
        raise SkillValidationError(f"{path}: 'name' and 'description' must be strings")


def _check_name(name: str, path: Path) -> None:
    if not KEBAB_CASE.fullmatch(name):
        raise SkillValidationError(f"{path}: name {name!r} must be lowercase kebab-case")
    if path.stem != name:
        raise SkillValidationError(f"{path}: filename stem {path.stem!r} must match name {name!r}")


def _check_allowed_tools(tools: list[str], path: Path) -> None:
    if not isinstance(tools, list):
        raise SkillValidationError(f"{path}: allowed_tools must be a list")
    for tool in tools:
        if tool in READ_TIER_TOOLS:
            raise SkillValidationError(
                f"{path}: {tool!r} is a read-tier tool and is implicit; remove it from allowed_tools"
            )
        if tool not in WRITE_TIER_TOOLS:
            raise SkillValidationError(
                f"{path}: unknown tool {tool!r} in allowed_tools; "
                f"known write-tier tools are {sorted(WRITE_TIER_TOOLS)}"
            )


def _check_body_sections(body: str, path: Path) -> None:
    for required in ("## When to use", "## Rules"):
        if required not in body:
            raise SkillValidationError(f"{path}: body must contain '{required}' section")


def _check_requires_graph(skills: dict[str, Skill]) -> None:
    for skill in skills.values():
        for dep in skill.requires:
            if dep not in skills:
                raise SkillValidationError(
                    f"{skill.source_path}: requires unknown skill {dep!r}"
                )
    # Cycle detection via DFS.
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {name: WHITE for name in skills}

    def visit(name: str, stack: list[str]) -> None:
        color[name] = GRAY
        for dep in skills[name].requires:
            if color[dep] == GRAY:
                cycle = " -> ".join(stack + [dep])
                raise SkillValidationError(f"requires cycle: {cycle}")
            if color[dep] == WHITE:
                visit(dep, stack + [dep])
        color[name] = BLACK

    for name in skills:
        if color[name] == WHITE:
            visit(name, [name])
