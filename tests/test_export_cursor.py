from pathlib import Path

from agent_fusion.export.cursor import export_all, export_skill
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
    preferred_models: tuple[str, ...] = (),
) -> None:
    extras = ""
    if preferred_models:
        extras += "preferred_models:\n" + "".join(f"  - {model}\n" for model in preferred_models)
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
        f"---\nname: {name}\ndescription: x\n{extras}---\n## When to use\nUse {name}.\n## Rules\n1. {body_marker}\n",
        encoding="utf-8",
    )


def test_export_writes_mdc_flat_file(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(skills_dir / "solo.md", "solo", "solo rule")
    skills = load_skills_dir(skills_dir)

    out = tmp_path / "out"
    rule_path = export_skill("solo", skills, out)

    assert rule_path == out / "solo.mdc"
    assert rule_path.exists()
    assert not (out / "solo").exists()


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

    rule_path = export_skill("specialized", skills, out)
    body = rule_path.read_text(encoding="utf-8")

    assert body.index("foundation rule") < body.index("specialized rule")


def test_export_maps_paths_to_cursor_globs(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(
        skills_dir / "web.md",
        "web",
        "rule",
        paths=("src/**/*.tsx", "tests/**/*.tsx"),
    )
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    body = export_skill("web", skills, out).read_text(encoding="utf-8")

    assert body.startswith("---\ndescription: x\n")
    assert "globs: src/**/*.tsx,tests/**/*.tsx\n" in body
    assert "alwaysApply: false\n---\n" in body
    assert "name:" not in body


def test_export_omits_globs_when_skill_has_no_paths(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(skills_dir / "generic.md", "generic", "rule")
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    body = export_skill("generic", skills, out).read_text(encoding="utf-8")

    assert "\nglobs:" not in body


def test_export_drops_agent_fusion_only_fields(tmp_path: Path):
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    _write_skill(skills_dir / "foundation.md", "foundation", "foundation rule")
    _write_skill(
        skills_dir / "tagged.md",
        "tagged",
        "tagged rule",
        requires=("foundation",),
        allowed_tools=("filesystem.write", "shell.exec"),
        tags=("backend-only",),
        preferred_models=("claude-opus",),
    )
    skills = load_skills_dir(skills_dir)
    out = tmp_path / "out"

    body = export_skill("tagged", skills, out).read_text(encoding="utf-8")

    assert "allowed_tools:" not in body
    assert "filesystem.write" not in body
    assert "shell.exec" not in body
    assert "requires:" not in body
    assert "preferred_models:" not in body
    assert "claude-opus" not in body
    assert "tags:" not in body
    assert "backend-only" not in body


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

    sidecar = out / "cited.sources.md"
    assert sidecar.exists()
    assert "ref" in sidecar.read_text(encoding="utf-8")


def test_export_all_writes_every_real_skill(tmp_path: Path):
    out = tmp_path / "out"
    written = export_all(SKILLS_DIR, out)

    skill_files = {p.name for p in written}
    assert "code-generation.mdc" in skill_files
    assert "python-backend.mdc" in skill_files
    assert "frontend-react.mdc" in skill_files
    assert "pr-review.mdc" in skill_files
    assert "debugging.mdc" in skill_files

    for rule_path in written:
        text = rule_path.read_text(encoding="utf-8")
        assert rule_path.parent == out
        assert text.startswith("---\n")
        assert "alwaysApply: false" in text
        assert "## When to use" in text
        assert "## Rules" in text
