import time

from fastapi import FastAPI

from src.config import settings
from apps.projects.router import router as project_router
router = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

@router.get("/terrible-ping")
async def terrible_ping():
    time.sleep(5)  # I/O blocking operation for 10 seconds, the whole process will be blocked

    return {"pong": True}


@router.get("/good-ping")
async def good_ping():
    time.sleep(5)  # I/O blocking operation for 10 seconds, but in a separate thread for the whole `good_ping` route

    return {"pong": True}


@router.get("/perfect-ping")
async def perfect_ping():
    return {"pong": True}


router.include_router(project_router)