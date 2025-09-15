from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User

class UserRepository:
    """Репозиторий для работы с моделью пользователя в базе данных."""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = User

    async def get_by_username(self, username: str) -> User | None:
        """
        Получает пользователя по имени пользователя.
        Выполняет асинхронный SELECT запрос по фильтру username.
        """
        query = select(self.model).where(self.model.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()