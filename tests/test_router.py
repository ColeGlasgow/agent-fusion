from dataclasses import replace
from pathlib import Path

import pytest

from agent_fusion.router import Router, RoutingError, StaticAgentRegistry, Task
from agent_fusion.skills import Skill, load_skills_dir

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
CONFIG_RULES = REPO_ROOT / "config" / "routing_rules.yaml"


def _skills():
    return load_skills_dir(SKILLS_DIR)


def _registry(*agents: str) -> StaticAgentRegistry:
    return StaticAgentRegistry(frozenset(agents))


def _router(rules=CONFIG_RULES, skills=None, agents=("claude-opus", "claude-sonnet", "codex-medium")) -> Router:
    return Router(
        skills=skills or _skills(),
        agent_registry=_registry(*agents),
        rules=rules,
        default_skill="code-generation",
        default_agent="codex-medium",
    )


def _rules_file(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "routing_rules.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def _add_skill_with_paths(skills: dict[str, Skill], name: str, paths: tuple[str, ...]) -> None:
    skills[name] = replace(
        skills["code-generation"],
        name=name,
        paths=paths,
        preferred_models=("codex-medium",),
    )


def test_empty_description_raises_before_stage_1():
    with pytest.raises(RoutingError, match="Task.description"):
        Task(description="", pin_skill="missing")


def test_unknown_pin_skill_raises_and_names_skill():
    router = _router()

    with pytest.raises(RoutingError, match="pin_skill 'missing-skill'"):
        router.route(Task(description="review this", pin_skill="missing-skill"))


def test_unavailable_pin_agent_raises():
    router = _router(agents=("claude-opus",))

    with pytest.raises(RoutingError, match="pin_agent 'codex-medium'.*unavailable"):
        router.route(Task(description="review this", pin_agent="codex-medium"))


def test_missing_rules_file_warns_and_falls_back(tmp_path):
    missing = tmp_path / "missing.yaml"
    with pytest.warns(RuntimeWarning, match="rules file missing"):
        router = _router(rules=missing, agents=("codex-medium",))

    decision = router.route(Task(description="anything"))

    assert decision.skill == "code-generation"
    assert decision.agent == "codex-medium"
    assert decision.fallback_used is True


def test_yaml_syntax_error_fails_at_router_construction(tmp_path):
    bad = _rules_file(tmp_path, "rules: [\n")

    with pytest.raises(RoutingError, match="routing_rules.yaml.*failed to parse"):
        _router(rules=bad)


def test_two_matching_rules_use_first_match(tmp_path):
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: first
    when:
      always: true
    then:
      skill: debugging
  - name: second
    when:
      always: true
    then:
      skill: pr-review
""",
    )
    router = _router(rules=rules)

    decision = router.route(Task(description="review broken code"))

    assert decision.skill == "debugging"
    assert decision.reason == "matched rule: first"


def test_skill_with_empty_preferred_models_uses_default_agent(tmp_path):
    skills = _skills()
    skills["empty"] = replace(skills["code-generation"], name="empty", preferred_models=())
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: empty-skill
    when:
      always: true
    then:
      skill: empty
""",
    )
    router = Router(
        skills=skills,
        agent_registry=_registry("claude-opus"),
        rules=rules,
        default_skill="empty",
        default_agent="codex-medium",
    )

    decision = router.route(Task(description="write code"))

    assert decision.skill == "empty"
    assert decision.agent == "codex-medium"


def test_pin_agent_and_pin_skill_return_both_at_confidence_1():
    router = _router()

    decision = router.route(
        Task(description="anything", pin_agent="codex-medium", pin_skill="debugging")
    )

    assert decision.agent == "codex-medium"
    assert decision.skill == "debugging"
    assert decision.confidence == 1.0
    assert decision.reason == "explicit pin"
    assert decision.fallback_used is False


def test_pin_skill_only_resolves_agent_via_preferred_models():
    router = _router(agents=("claude-sonnet", "codex-medium"))

    decision = router.route(Task(description="anything", pin_skill="pr-review"))

    assert decision.skill == "pr-review"
    assert decision.agent == "claude-sonnet"
    assert decision.reason == "explicit pin"


def test_pin_agent_only_still_applies_stage_2_for_skill():
    router = _router()

    decision = router.route(Task(description="please review this", pin_agent="codex-medium"))

    assert decision.agent == "codex-medium"
    assert decision.skill == "pr-review"
    assert decision.reason == "explicit pin"


def test_description_matches_regex_matches(tmp_path):
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: review-rule
    when:
      description_matches: "(?i)review"
    then:
      skill: pr-review
""",
    )
    router = _router(rules=rules)

    decision = router.route(Task(description="please review this"))

    assert decision.skill == "pr-review"
    assert decision.reason == "matched rule: review-rule"


def test_always_true_matches_anything(tmp_path):
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: catch-all
    when:
      always: true
    then:
      skill: code-generation
""",
    )
    router = _router(rules=rules)

    decision = router.route(Task(description="unclassified work"))

    assert decision.skill == "code-generation"
    assert decision.reason == "matched rule: catch-all"


def test_attachment_paths_select_skill_before_catch_all(tmp_path):
    skills = _skills()
    _add_skill_with_paths(skills, "python-auto", ("**/*.py",))
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: catch-all
    when:
      always: true
    then:
      skill: code-generation
""",
    )
    router = _router(rules=rules, skills=skills)

    decision = router.route(Task(description="change this file", attachments=("src/foo.py",)))

    assert decision.skill == "python-auto"
    assert decision.confidence == 0.9
    assert decision.reason == "task attachments matched skill paths: **/*.py"


def test_explicit_rule_wins_over_attachment_path(tmp_path):
    skills = _skills()
    _add_skill_with_paths(skills, "python-auto", ("**/*.py",))
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: review-rule
    when:
      description_matches: "(?i)review"
    then:
      skill: pr-review
  - name: catch-all
    when:
      always: true
    then:
      skill: code-generation
""",
    )
    router = _router(rules=rules, skills=skills)

    decision = router.route(Task(description="review this", attachments=("src/foo.py",)))

    assert decision.skill == "pr-review"
    assert decision.confidence == 1.0
    assert decision.reason == "matched rule: review-rule"


def test_attachment_paths_do_not_fire_without_attachments(tmp_path):
    skills = _skills()
    _add_skill_with_paths(skills, "python-auto", ("**/*.py",))
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: catch-all
    when:
      always: true
    then:
      skill: code-generation
""",
    )
    router = _router(rules=rules, skills=skills)

    decision = router.route(Task(description="change this file"))

    assert decision.skill == "code-generation"
    assert decision.confidence == 1.0
    assert decision.reason == "matched rule: catch-all"


def test_more_specific_attachment_path_wins(tmp_path):
    skills = _skills()
    _add_skill_with_paths(skills, "python-general", ("**/*.py",))
    _add_skill_with_paths(skills, "python-tests", ("tests/**/*.py",))
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: catch-all
    when:
      always: true
    then:
      skill: code-generation
""",
    )
    router = _router(rules=rules, skills=skills)

    decision = router.route(Task(description="change this file", attachments=("tests/foo.py",)))

    assert decision.skill == "python-tests"
    assert decision.reason == "task attachments matched skill paths: tests/**/*.py"


def test_attachment_path_reason_cites_matching_glob_verbatim(tmp_path):
    skills = _skills()
    _add_skill_with_paths(skills, "python-auto", ("src/**/*.py",))
    rules = _rules_file(
        tmp_path,
        """
rules:
  - name: catch-all
    when:
      always: true
    then:
      skill: code-generation
""",
    )
    router = _router(rules=rules, skills=skills)

    decision = router.route(Task(description="change this file", attachments=("src/foo.py",)))

    assert decision.reason == "task attachments matched skill paths: src/**/*.py"


@pytest.mark.parametrize(
    ("rules_text", "message"),
    [
        (
            """
rules:
  - name: bad
    extra: nope
    when:
      always: true
    then:
      skill: code-generation
""",
            "rule\\[0\\].*unknown keys",
        ),
        (
            """
rules:
  - name: bad-regex
    when:
      description_matches: "["
    then:
      skill: code-generation
""",
            "bad-regex.*regex failed to compile",
        ),
        (
            """
rules:
  - name: no-target
    when:
      always: true
    then: {}
""",
            "no-target.*must include skill or agent",
        ),
    ],
)
def test_invalid_rules_are_rejected(tmp_path, rules_text, message):
    rules = _rules_file(tmp_path, rules_text)

    with pytest.raises(RoutingError, match=message):
        _router(rules=rules)
