from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.db.enums import UserRole
from src.db.models import User, Project
from src.db.session import get_session
from src.security import get_current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")
    return current_user

async def get_project_or_404(project_id: int, session: AsyncSession = Depends(get_session)) -> Project:
    result = await session.execute(select(Project).where(Project.id == project_id).limit(1))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project

async def require_owner_of_project(project: Project = Depends(get_project_or_404),
                                   current_user: User = Depends(get_current_user)
                                   ) -> Project:
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project owner only")
    return project

async def require_view_access(project: Project = Depends(get_project_or_404),
                              current_user: User = Depends(get_current_user)) -> Project:
    if project.owner_id != current_user.id or current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return project
