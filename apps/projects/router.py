from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.projects.dto import ProjectDTO, ProjectReadDTO
from apps.projects.repository import ProjectRepository
from src.db.session import get_session

router = APIRouter(prefix="/projects", tags=["projects"])

def get_project_repo(
    session: Annotated[AsyncSession, Depends(get_session)]
) -> ProjectRepository:
    return ProjectRepository(session)

@router.get("/list", response_model=list[ProjectReadDTO])
async def list_projects(
    repo: Annotated[ProjectRepository, Depends(get_project_repo)],
    limit: int = 10,
):
    return await repo.get_all(limit)


@router.post("/create")
async def create_project(body: ProjectDTO, repo: Annotated[ProjectRepository, Depends(get_project_repo)]):
    return await repo.create(**body.model_dump())


@router.get("/{id_}", response_model=ProjectReadDTO)
async def get_project(
    id_: int,
    repo: Annotated[ProjectRepository, Depends(get_project_repo)]
):
    return await repo.get_one(id_)
