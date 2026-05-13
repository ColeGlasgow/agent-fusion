from pathlib import Path

import pytest

from agent_fusion.export.claude_code import export_all, export_skill
from agent_fusion.skills import load_skills_dir

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def _write_skill(
    path: Path,
    name: str,
    body_marker: str,
    requires: tuple[str, ...] = (),
    paths: tuple[str, ...] = (),
    allowed_tools: tuple[str, ...] = (),
    success_criteria: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
) -> None:
    extras = ""
    if requires:
        extras += "requires:\n" + "".join(f"  - {dep}\n" for dep in requires)
    if paths:
        extras += "paths:\n" + "".join(f'  - "{glob}"\n' for glob in paths)
    if allowed_tools:
        extras += "allowed_tools:\n" + "".join(f"  - {tool}\n" for tool in allowed_tools)
    if success_criteria:
        extras += "success_criteria:\n" + "".join(f"  - {item}\n" for item in success_criteria)
    if tags:
        extras += "tags:\n" + "".join(f"  - {tag}\n" for tag in tags)
    path.write_text(
        "---\n"
        f"name: {name}\n"
        "description: x\n"
        f"{extras}"
        "---\n"
        "## When to use\n"
        f"Use {name}.\n"
        "## Rules\n"
        f"1. {body_marker}\n",
        encoding="utf-8",
    )


def test_export_writes_skill_md_under_named_directory(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(skills_dir / "solo.md", "solo", "solo rule")
    skills = load_skills_dir(skills_dir)

    out = tmp_path / "out"
    skill_md = export_skill("solo", skills, out)

    assert skill_md == out / "solo" / "SKILL.md"
    assert skill_md.exists()


def test_export_composes_required_skill_body(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(skills_dir / "foundation.md", "foundation", "foundation rule")
    _write_skill(
        skills_dir / "specialized.md",
        "specialized",
        "specialized rule",
        requires=("foundation",),
    )
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    skill_md = export_skill("specialized", skills, out)
    body = skill_md.read_text(encoding="utf-8")

    assert body.index("foundation rule") < body.index("specialized rule")


def test_export_remaps_allowed_tools_to_claude_code_names(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(
        skills_dir / "writes.md",
        "writes",
        "rule",
        allowed_tools=("filesystem.write", "shell.exec"),
    )
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    body = export_skill("writes", skills, out).read_text(encoding="utf-8")

    assert "allowed-tools:" in body
    assert "Edit" in body
    assert "Write" in body
    assert "Bash" in body
    assert "filesystem.write" not in body


def test_export_preserves_paths_field(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(skills_dir / "py.md", "py", "rule", paths=("**/*.py",))
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    body = export_skill("py", skills, out).read_text(encoding="utf-8")

    assert "paths:" in body
    assert '"**/*.py"' in body


def test_export_drops_tags_and_preferred_models(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(skills_dir / "tagged.md", "tagged", "rule", tags=("foundation",))
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    body = export_skill("tagged", skills, out).read_text(encoding="utf-8")

    assert "tags:" not in body
    assert "preferred_models:" not in body
    assert "requires:" not in body


def test_export_appends_success_criteria_as_body_section(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(
        skills_dir / "verified.md",
        "verified",
        "rule",
        success_criteria=("Tests pass", "Docs updated"),
    )
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    body = export_skill("verified", skills, out).read_text(encoding="utf-8")

    assert "## Success criteria" in body
    assert "- Tests pass" in body
    assert "- Docs updated" in body
    assert body.index("## Rules") < body.index("## Success criteria")


def test_export_copies_sources_sidecar_when_present(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(skills_dir / "cited.md", "cited", "rule")
    (skills_dir / "cited.sources.md").write_text("# sources\n- ref\n", encoding="utf-8")
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    export_skill("cited", skills, out)

    sidecar = out / "cited" / "sources.md"
    assert sidecar.exists()
    assert "ref" in sidecar.read_text(encoding="utf-8")


def test_export_all_writes_every_real_skill(tmp_path: Path):
    out = tmp_path / "out"
    written = export_all(SKILLS_DIR, out)

    skill_names = {p.parent.name for p in written}
    assert "code-generation" in skill_names
    assert "python-backend" in skill_names
    assert "frontend-react" in skill_names
    assert "pr-review" in skill_names
    assert "debugging" in skill_names

    for skill_md in written:
        text = skill_md.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        assert "## When to use" in text
        assert "## Rules" in text
