from __future__ import annotations
from typing import Optional, Callable, Any
from pydantic import BaseModel
import re

commands: dict[str, dict] = {}


def _ensure_command_name(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_\-]+", name):
        raise ValueError("Имя команды может содержать только буквы, цифры, _ и -")
    return name


def register_command(
    command_name: str,
    args_model: Optional[type[BaseModel]] = None,
    response_model: Optional[type[BaseModel]] = None,
    description: str = "",
):
    """Декоратор для регистрации команд с метаданными"""
    _ensure_command_name(command_name)
    if args_model is not None and not issubclass(args_model, BaseModel):
        raise TypeError("args_model должен наследовать BaseModel")
    if response_model is not None and not issubclass(response_model, BaseModel):
        raise TypeError("response_model должен наследовать BaseModel")
    if command_name in commands:
        raise ValueError(f"Команда '{command_name}' уже зарегистрирована")

    def decorator(func: Callable[..., Any]):
        commands[command_name] = {
            "func": func,
            "args_model": args_model,
            "response_model": response_model,
            "description": description,
        }
        return func

    return decorator


# from typing import Callable, Optional
# from pydantic import BaseModel

# commands: dict[str, dict] = {}

# def register_command(
#     command_name: str,
#     args_model: Optional[type[BaseModel]] = None,
#     response_model: Optional[type[BaseModel]] = None,
#     description: str = ""
# ):
#     """Декоратор для регистрации команд с метаданными"""
#     def decorator(func: Callable):
#         commands[command_name] = {
#             "func": func,
#             "args_model": args_model,
#             "response_model": response_model,
#             "description": description
#         }
#         return func
#     return decorator
