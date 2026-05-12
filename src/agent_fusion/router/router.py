from __future__ import annotations

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
        matched = self._match_rules(task)
        if task.pin_agent:
            skill = matched.skill if matched is not None and matched.skill is not None else self._default_skill
            return RouteDecision(
                agent=task.pin_agent,
                skill=skill,
                confidence=1.0,
                reason="explicit pin",
                fallback_used=matched is None,
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
        return self._fallback_decision()

    def _validate_pins(self, task: Task) -> None:
        if task.pin_skill is not None and task.pin_skill not in self._skills:
            raise RoutingError(f"pin_skill {task.pin_skill!r}: unknown skill")
        if task.pin_agent is not None and not self._agent_registry.is_available(task.pin_agent):
            raise RoutingError(f"pin_agent {task.pin_agent!r}: unavailable agent")

    def _match_rules(self, task: Task) -> RoutingRule | None:
        for rule in self._rules:
            if rule.matches(task):
                return rule
        return None

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
