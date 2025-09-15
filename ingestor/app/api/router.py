from fastapi import APIRouter
from app.core.commands import clear_tags
from app.api.routing import setup_routes

router = APIRouter()
setup_routes(router)