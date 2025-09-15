from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db, get_current_user
from app.schemas.contract import (ContractCreate, ContractRead, ContractUpdate, ContractVersionCreate, ContractVersionRead)
from app.repositories.contract_repository import ContractRepository
from app.services.contract_service import ContractService

router = APIRouter()

@router.post("/", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_in: ContractCreate,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """Создать новый договор."""
    repo = ContractRepository(db)
    contract = await repo.create_contract(contract_in.model_dump())
    return contract

@router.get("/{contract_id}", response_model=ContractRead)
async def read_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """Получить договор по ID."""
    repo = ContractRepository(db)
    contract = await repo.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.get("/", response_model=List[ContractRead])
async def read_contracts(
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """Получить список всех договоров с их версиями."""
    repo = ContractRepository(db)
    return await repo.get_all_contracts()

@router.patch("/{contract_id}", response_model=ContractRead)
async def update_contract(
    contract_id: int,
    update_in: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """Обновить существующий договор по ID."""
    repo = ContractRepository(db)
    contract = await repo.update_contract(contract_id, update_in.model_dump(exclude_unset=True))
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.post("/{contract_id}/versions", response_model=ContractVersionRead, status_code=status.HTTP_201_CREATED)
async def create_version(
    contract_id: int,
    version_in: ContractVersionCreate,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """Создать новую версию договора по ID договора."""
    repo = ContractRepository(db)
    service = ContractService(repo)
    version_data = await service.create_new_version(contract_id, version_in)
    if not version_data:
        raise HTTPException(status_code=404, detail="Contract not found")
    return version_data

@router.get("/{contract_id}/versions", response_model=List[ContractVersionRead])
async def read_versions(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user = Depends(get_current_user)
):
    """Получить список всех версий указанного договора."""
    repo = ContractRepository(db)
    versions = await repo.get_versions_by_contract(contract_id)
    if not versions:
        raise HTTPException(status_code=404, detail="No versions found")
    return versions