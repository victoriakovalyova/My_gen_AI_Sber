import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash

log = logging.getLogger(__name__)

class UserService:
    """Сервис для управления пользователями."""
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user(self, user_in: UserCreate) -> dict:
        """
        Создает нового пользователя.
        Хеширует пароль из входящих данных и сохраняет пользователя через репозиторий.
        """
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.dict(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        return await self.repo.create(user_data)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> dict:
        """
        Обновляет информацию существующего пользователя.
        Если в обновлении есть пароль, он будет захеширован перед сохранением.
        """
        user = await self.repo.get(user_id)
        if not user:
            raise ValueError("Пользователь не найден.")
        if user_in.password:
            user_in.password = get_password_hash(user_in.password)
        return await self.repo.update(user, user_in)