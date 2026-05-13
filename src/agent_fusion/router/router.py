from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any, Mapping, Sequence

from agent_fusion.router.agent_registry import AgentRegistry
from agent_fusion.router.rules import RoutingRule, load_rules
from agent_fusion.router.types import RouteDecision, RoutingError, Task


class Router:
    def __init__(
        self,
        skills: Mapping[str, Any],
        agent_registry: AgentRegistry,
        rules: Path | str | Sequence[RoutingRule],
        default_skill: str,
        default_agent: str,
    ) -> None:
        if default_skill not in skills:
            raise RoutingError(f"default_skill {default_skill!r}: unknown skill")
        self._skills = skills
        self._agent_registry = agent_registry
        self._rules = load_rules(Path(rules)) if isinstance(rules, (str, Path)) else tuple(rules)
        self._default_skill = default_skill
        self._default_agent = default_agent

    def route(self, task: Task) -> RouteDecision:
        self._validate_pins(task)
        if task.pin_agent and task.pin_skill:
            return RouteDecision(
                agent=task.pin_agent,
                skill=task.pin_skill,
                confidence=1.0,
                reason="explicit pin",
                fallback_used=False,
            )
        if task.pin_skill:
            return RouteDecision(
                agent=self._agent_for_skill(task.pin_skill),
                skill=task.pin_skill,
                confidence=1.0,
                reason="explicit pin",
                fallback_used=False,
            )
        matched = self._match_rules(task, include_always=False)
        path_match = None if matched is not None else self._match_skill_paths(task)
        catch_all = None if matched is not None or path_match is not None else self._match_rules(
            task, include_always=True
        )
        if task.pin_agent:
            skill = self._skill_from_match(matched, path_match, catch_all)
            return RouteDecision(
                agent=task.pin_agent,
                skill=skill,
                confidence=1.0,
                reason="explicit pin",
                fallback_used=matched is None and path_match is None and catch_all is None,
            )
        if matched is not None:
            skill = matched.skill
            agent = matched.agent if matched.agent is not None else self._agent_for_skill(skill)
            return RouteDecision(
                agent=agent,
                skill=skill,
                confidence=1.0,
                reason=f"matched rule: {matched.name}",
                fallback_used=False,
            )
        if path_match is not None:
            skill, glob = path_match
            return RouteDecision(
                agent=self._agent_for_skill(skill),
                skill=skill,
                confidence=0.9,
                reason=f"task attachments matched skill paths: {glob}",
                fallback_used=False,
            )
        if catch_all is not None:
            skill = catch_all.skill
            agent = catch_all.agent if catch_all.agent is not None else self._agent_for_skill(skill)
            return RouteDecision(
                agent=agent,
                skill=skill,
                confidence=1.0,
                reason=f"matched rule: {catch_all.name}",
                fallback_used=False,
            )
        return self._fallback_decision()

    def _validate_pins(self, task: Task) -> None:
        if task.pin_skill is not None and task.pin_skill not in self._skills:
            raise RoutingError(f"pin_skill {task.pin_skill!r}: unknown skill")
        if task.pin_agent is not None and not self._agent_registry.is_available(task.pin_agent):
            raise RoutingError(f"pin_agent {task.pin_agent!r}: unavailable agent")

    def _match_rules(self, task: Task, *, include_always: bool) -> RoutingRule | None:
        for rule in self._rules:
            if rule.always and not include_always:
                continue
            if rule.matches(task):
                return rule
        return None

    def _match_skill_paths(self, task: Task) -> tuple[str, str] | None:
        if not task.attachments:
            return None
        matches: list[tuple[int, str, str]] = []
        for skill_name, skill in self._skills.items():
            for glob in skill.paths:
                if any(self._path_matches(str(attachment), glob) for attachment in task.attachments):
                    matches.append((len(glob), skill_name, glob))
        if not matches:
            return None
        # Specificity is a rough heuristic: longer glob string wins, alphabetical by name as tiebreak.
        _specificity, skill_name, glob = sorted(matches, key=lambda item: (-item[0], item[1]))[0]
        return skill_name, glob

    def _path_matches(self, attachment: str, glob: str) -> bool:
        # Python's fnmatch does not natively support gitignore-style `**` recursive globs:
        # `fnmatch("foo.py", "**/*.py")` is False because the translated regex requires a `/`.
        # Re-run with `**/` stripped so a recursive glob also matches zero-directory paths.
        if fnmatch.fnmatch(attachment, glob):
            return True
        if "**/" in glob:
            return fnmatch.fnmatch(attachment, glob.replace("**/", ""))
        return False

    def _skill_from_match(
        self,
        rule: RoutingRule | None,
        path_match: tuple[str, str] | None,
        catch_all: RoutingRule | None,
    ) -> str | None:
        if rule is not None and rule.skill is not None:
            return rule.skill
        if path_match is not None:
            return path_match[0]
        if catch_all is not None and catch_all.skill is not None:
            return catch_all.skill
        return self._default_skill

    def _agent_for_skill(self, skill_name: str | None) -> str:
        if skill_name is None:
            return self._default_agent
        if skill_name not in self._skills:
            raise RoutingError(f"skill {skill_name!r}: unknown skill")
        for agent in self._skills[skill_name].preferred_models:
            if self._agent_registry.is_available(agent):
                return agent
        return self._default_agent

    def _fallback_decision(self) -> RouteDecision:
        return RouteDecision(
            agent=self._agent_for_skill(self._default_skill),
            skill=self._default_skill,
            confidence=1.0,
            reason=f"no rule match; defaulted to {self._default_skill} / {self._agent_for_skill(self._default_skill)}",
            fallback_used=True,
        )
