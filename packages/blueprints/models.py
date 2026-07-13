"""
Blueprint Models
"""

from pydantic import BaseModel, Field


class ResourceSpec(BaseModel):
    name: str
    provider: str
    kind: str
    config: dict = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list)


class Blueprint(BaseModel):
    name: str
    version: str = "1.0"
    resources: list[ResourceSpec] = Field(default_factory=list)
