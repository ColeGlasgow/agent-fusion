from pathlib import Path

import pytest

from agent_fusion.skills import (
    Skill,
    SkillValidationError,
    load_skill,
    load_skills_dir,
)

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def test_loads_every_real_skill_in_the_repo():
    skills = load_skills_dir(SKILLS_DIR)
    assert skills, "expected at least one skill in skills/"
    for name, skill in skills.items():
        assert isinstance(skill, Skill)
        assert skill.name == name
        assert skill.description


def test_pr_review_skill_has_expected_shape():
    skill = load_skill(SKILLS_DIR / "pr-review.md")
    assert skill.name == "pr-review"
    assert "review" in skill.tags
    assert skill.success_criteria, "pr-review should declare success_criteria"


def test_code_generation_skill_declares_filesystem_write():
    skill = load_skill(SKILLS_DIR / "code-generation.md")
    assert "filesystem.write" in skill.allowed_tools


def test_missing_required_field_is_rejected(tmp_path: Path):
    bad = tmp_path / "bad.md"
    bad.write_text(
        "---\n"
        "name: bad\n"
        "---\n"
        "## When to use\nx\n## Rules\n1. x\n"
    )
    with pytest.raises(SkillValidationError, match="missing required"):
        load_skill(bad)


def test_unknown_frontmatter_field_is_rejected(tmp_path: Path):
    bad = tmp_path / "bad.md"
    bad.write_text(
        "---\n"
        "name: bad\n"
        "description: x\n"
        "typo_field: y\n"
        "---\n"
        "## When to use\nx\n## Rules\n1. x\n"
    )
    with pytest.raises(SkillValidationError, match="unknown frontmatter"):
        load_skill(bad)


def test_filename_must_match_name(tmp_path: Path):
    bad = tmp_path / "wrong-name.md"
    bad.write_text(
        "---\n"
        "name: different-name\n"
        "description: x\n"
        "---\n"
        "## When to use\nx\n## Rules\n1. x\n"
    )
    with pytest.raises(SkillValidationError, match="must match name"):
        load_skill(bad)


def test_read_tier_tool_in_allowed_tools_is_rejected(tmp_path: Path):
    bad = tmp_path / "bad.md"
    bad.write_text(
        "---\n"
        "name: bad\n"
        "description: x\n"
        "allowed_tools:\n  - filesystem.read\n"
        "---\n"
        "## When to use\nx\n## Rules\n1. x\n"
    )
    with pytest.raises(SkillValidationError, match="read-tier tool"):
        load_skill(bad)


def test_unknown_tool_is_rejected(tmp_path: Path):
    bad = tmp_path / "bad.md"
    bad.write_text(
        "---\n"
        "name: bad\n"
        "description: x\n"
        "allowed_tools:\n  - made.up.tool\n"
        "---\n"
        "## When to use\nx\n## Rules\n1. x\n"
    )
    with pytest.raises(SkillValidationError, match="unknown tool"):
        load_skill(bad)


def test_missing_body_section_is_rejected(tmp_path: Path):
    bad = tmp_path / "bad.md"
    bad.write_text(
        "---\n"
        "name: bad\n"
        "description: x\n"
        "---\n"
        "## When to use\nx\n"
    )
    with pytest.raises(SkillValidationError, match="## Rules"):
        load_skill(bad)


def test_requires_cycle_is_rejected(tmp_path: Path):
    (tmp_path / "alpha.md").write_text(
        "---\n"
        "name: alpha\n"
        "description: x\n"
        "requires:\n  - beta\n"
        "---\n"
        "## When to use\nx\n## Rules\n1. x\n"
    )
    (tmp_path / "beta.md").write_text(
        "---\n"
        "name: beta\n"
        "description: x\n"
        "requires:\n  - alpha\n"
        "---\n"
        "## When to use\nx\n## Rules\n1. x\n"
    )
    with pytest.raises(SkillValidationError, match="cycle"):
        load_skills_dir(tmp_path)
