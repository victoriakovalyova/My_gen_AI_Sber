from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.contract import Contract, ContractVersion

class ContractRepository:
    """Репозиторий для работы с договорами и их версиями в базе данных."""
    def __init__(self, db: AsyncSession):
        """Инициализация репозитория с асинхронной сессией базы данных."""
        self.db = db

    async def create_contract(self, contract_data: dict) -> Contract:
        """Создать новый договор и сохранить в базе."""
        contract = Contract(**contract_data)
        self.db.add(contract)
        await self.db.commit()
        await self.db.refresh(contract)
        return contract

    async def get_contract(self, contract_id: int) -> Optional[Contract]:
        """Получить договор по его идентификатору вместе со всеми версиями."""
        result = await self.db.execute(
            select(Contract).options(selectinload(Contract.versions)).where(Contract.id == contract_id)
        )
        return result.scalar_one_or_none()

    async def get_all_contracts(self) -> List[Contract]:
        """Получить список всех договоров с загруженными версиями."""
        result = await self.db.execute(select(Contract).options(selectinload(Contract.versions)))
        return result.scalars().all()

    async def update_contract(self, contract_id: int, update_data: dict) -> Optional[Contract]:
        """Обновить поля договора по ID."""
        contract = await self.get_contract(contract_id)
        if not contract:
            return None
        for key, value in update_data.items():
            setattr(contract, key, value)
        await self.db.commit()
        await self.db.refresh(contract)
        return contract

    async def delete_contract(self, contract_id: int) -> bool:
        """Удалить договор по ID."""
        contract = await self.get_contract(contract_id)
        if not contract:
            return False
        await self.db.delete(contract)
        await self.db.commit()
        return True

    # Для версий
    async def create_version(self, version_data: dict) -> ContractVersion:
        """Создать новую версию договора."""
        version = ContractVersion(**version_data)
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        return version

    async def get_versions_by_contract(self, contract_id: int) -> List[ContractVersion]:
        """Получить все версии договора по ID договора, отсортированные по номеру версии."""
        result = await self.db.execute(
            select(ContractVersion).where(ContractVersion.contract_id == contract_id).order_by(ContractVersion.version_number)
        )
        return result.scalars().all()