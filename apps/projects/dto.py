from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectDTO(BaseModel):
    name: str = Field(..., min_length=3, max_length=250)
    description: str | None = Field(None, min_length=5, max_length=1000)

class ProjectCreateDTO(ProjectDTO):
    pass

class ProjectUpdateDTO(BaseModel):
    name: str = Optional[str]
    description: Optional[str]

class ProjectOutDTO(ProjectDTO):
    id: int
    owner_id: int
    created_at: datetime