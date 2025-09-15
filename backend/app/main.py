from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.database import engine, Base
from app.middlewares.access_log import add_access_log_middleware
from app.exceptions.handlers import add_exception_handlers
from app.core.logging import setup_logging
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")
add_access_log_middleware(app)
add_exception_handlers(app)