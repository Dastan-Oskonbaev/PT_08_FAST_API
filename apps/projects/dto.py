from pydantic import BaseModel, Field


class ProjectDTO(BaseModel):
    name: str = Field(..., min_length=3, max_length=250)
    description: str | None = Field(None, min_length=5, max_length=1000)

class ProjectReadDTO(ProjectDTO):
    id: int


