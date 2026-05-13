from __future__ import annotations

import re
import warnings
from dataclasses import dataclass
from pathlib import Path
from re import Pattern
from typing import Any

import yaml

from agent_fusion.router.types import RoutingError, Task

TOP_LEVEL_KEYS = {"rules"}
RULE_KEYS = {"name", "when", "then"}
WHEN_KEYS = {"description_matches", "always"}
THEN_KEYS = {"skill", "agent"}


@dataclass(frozen=True)
class RoutingRule:
    name: str
    description_pattern: Pattern[str] | None = None
    always: bool = False
    skill: str | None = None
    agent: str | None = None

    def matches(self, task: Task) -> bool:
        if self.always:
            return True
        if self.description_pattern is not None:
            return self.description_pattern.search(task.description) is not None
        return False


def load_rules(path: Path) -> tuple[RoutingRule, ...]:
    if not path.exists():
        warnings.warn(f"{path}: rules file missing; skipping rule-based routing", RuntimeWarning)  # noqa: B028
        return ()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RoutingError(f"{path}: rules YAML failed to parse: {exc}") from exc
    if not isinstance(data, dict):
        raise RoutingError(f"{path}: rules file must be a YAML mapping")
    _reject_unknown_keys(data, TOP_LEVEL_KEYS, path, "top-level")
    rules = data.get("rules")
    if not isinstance(rules, list):
        raise RoutingError(f"{path}: 'rules' must be a list")
    return tuple(_parse_rule(path, index, rule) for index, rule in enumerate(rules))


def _parse_rule(path: Path, index: int, data: Any) -> RoutingRule:
    label = f"rule[{index}]"
    if not isinstance(data, dict):
        raise RoutingError(f"{path}: {label} must be a mapping")
    _reject_unknown_keys(data, RULE_KEYS, path, label)
    name = data.get("name")
    if not isinstance(name, str) or not name:
        raise RoutingError(f"{path}: {label} name must be a non-empty string")
    when = data.get("when")
    if not isinstance(when, dict):
        raise RoutingError(f"{path}: rule {name!r} when must be a mapping")
    _reject_unknown_keys(when, WHEN_KEYS, path, f"rule {name!r} when")
    active_when = [key for key in WHEN_KEYS if key in when]
    if len(active_when) != 1:
        raise RoutingError(f"{path}: rule {name!r} when must contain exactly one condition")
    then = data.get("then")
    if not isinstance(then, dict):
        raise RoutingError(f"{path}: rule {name!r} then must be a mapping")
    _reject_unknown_keys(then, THEN_KEYS, path, f"rule {name!r} then")
    skill = then.get("skill")
    agent = then.get("agent")
    if skill is None and agent is None:
        raise RoutingError(f"{path}: rule {name!r} then must include skill or agent")
    if skill is not None and not isinstance(skill, str):
        raise RoutingError(f"{path}: rule {name!r} skill must be a string")
    if agent is not None and not isinstance(agent, str):
        raise RoutingError(f"{path}: rule {name!r} agent must be a string")
    if "always" in when:
        if when["always"] is not True:
            raise RoutingError(f"{path}: rule {name!r} always must be true")
        return RoutingRule(name=name, always=True, skill=skill, agent=agent)
    pattern_text = when["description_matches"]
    if not isinstance(pattern_text, str):
        raise RoutingError(f"{path}: rule {name!r} description_matches must be a string")
    try:
        pattern = re.compile(pattern_text)
    except re.error as exc:
        raise RoutingError(f"{path}: rule {name!r} description_matches regex failed to compile: {exc}") from exc
    return RoutingRule(name=name, description_pattern=pattern, skill=skill, agent=agent)


def _reject_unknown_keys(data: dict[str, Any], allowed: set[str], path: Path, label: str) -> None:
    unknown = data.keys() - allowed
    if unknown:
        raise RoutingError(f"{path}: {label} has unknown keys: {sorted(unknown)}")
