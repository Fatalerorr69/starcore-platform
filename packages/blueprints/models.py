"""
Blueprint Models
"""

from orchestrator.timeout import TimeoutStrategy
from pydantic import BaseModel, Field


class ResourceSpec(BaseModel):
    name: str
    provider: str
    kind: str
    config: dict = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)
    timeout_seconds: float | None = None
    timeout_strategy: TimeoutStrategy | None = None


class Blueprint(BaseModel):
    name: str
    version: str = "1.0"
    resources: list[ResourceSpec] = Field(default_factory=list)
