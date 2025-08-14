from sqlalchemy import select
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from apps.projects.dto import ProjectDTO
from src.db.base import BaseRepository
from src.db.models import Project


class ProjectRepository(BaseRepository[Project]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)
