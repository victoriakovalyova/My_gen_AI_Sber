from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, AsyncGenerator
from app.core.database import async_session
from app.core.security import verify_password
from app.repositories.user_repository import UserRepository
from app.models.user import User

security = HTTPBasic(auto_error=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения асинхронной сессии базы данных.
    Используется в эндпоинтах для работы с БД.
    """
    async with async_session() as session:
        yield session

async def get_current_user(
    credentials: Optional[HTTPBasicCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Зависимость для аутентификации пользователя через Basic Auth.
    Проверяет username и пароль, возвращает объект пользователя.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация",
            headers={"WWW-Authenticate": "Basic realm='Secure Area'"},
        )

    repo = UserRepository(db)
    user = await repo.get_by_username(credentials.username)
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic realm='Secure Area'"},
        )
    
    return user