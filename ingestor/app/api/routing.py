from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import logging
from app.core.registry import commands
from fastapi import Body
from typing import Any

log = logging.getLogger(__name__)


def _make_post_endpoint(func, args_model: Optional[type[BaseModel]]):
    if args_model is None:

        async def endpoint():
            try:
                return await func()
            except Exception as e:
                log.exception("Ошибка команды без аргументов")
                raise HTTPException(status_code=500, detail=str(e))

        return endpoint

    def make_async_endpoint(func, args_model):
        if hasattr(args_model, "model_rebuild"):
            args_model.model_rebuild()

        async def endpoint(args = Body(...)):
            try:
                kwargs = args.model_dump()
                return await func(**kwargs)
            except Exception as e:
                log.exception("Ошибка команды с аргументами")
                raise HTTPException(status_code=500, detail=str(e))

        endpoint.__annotations__ = {'args': args_model, 'return': Any}
        return endpoint

    return make_async_endpoint(func, args_model)


def setup_routes(router: APIRouter, *, prefix: str = "/scan") -> None:
    if not commands:
        log.info("commands пуст")

    for name, meta in commands.items():
        log.info(f"Регистрируем команду: {name} → {meta['func'].__name__}")
        endpoint = _make_post_endpoint(meta["func"], meta.get("args_model"))
        router.add_api_route(
            path=f"{prefix}/{name}",
            endpoint=endpoint,
            methods=["POST"],
            response_model=meta.get("response_model"),
            description=meta.get("description", ""),
            name=f"post_{name}",
            tags=meta.get("tags", ["scan"]),
        )