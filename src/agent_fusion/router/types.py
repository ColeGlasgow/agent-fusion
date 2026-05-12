from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


class RoutingError(ValueError):
    """Raised when routing input or configuration is invalid."""


@dataclass(frozen=True)
class Task:
    description: str
    attachments: tuple = ()
    pin_agent: str | None = None
    pin_skill: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.description, str) or not self.description.strip():
            raise RoutingError("Task.description: description must be non-empty")


@dataclass(frozen=True)
class RouteDecision:
    agent: str
    skill: str | None
    confidence: float
    reason: str
    fallback_used: bool
