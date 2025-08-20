
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.projects.dto import ProjectOutDTO, ProjectCreateDTO
from src.db.models import User, Project
from src.db.session import get_session
from src.security import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])



@router.post("/create", response_model=ProjectOutDTO)
async def create_project(
        body: ProjectCreateDTO,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user)):
    project = Project(
        name=body.name,
        description=body.description,
        owner_id=current_user.id,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project