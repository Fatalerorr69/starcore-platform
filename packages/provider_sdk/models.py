"""
Provider Models
"""

from pydantic import BaseModel


class Resource(BaseModel):
    id: str
    name: str
    type: str
    status: str
