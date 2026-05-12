from __future__ import annotations

from typing import Protocol


class AgentRegistry(Protocol):
    def is_available(self, name: str) -> bool:
        ...


class StaticAgentRegistry:
    def __init__(self, agents: frozenset[str] | set[str] | tuple[str, ...]) -> None:
        self._agents = frozenset(agents)

    def is_available(self, name: str) -> bool:
        return name in self._agents
