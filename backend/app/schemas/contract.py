from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class ContractBase(BaseModel):
    """
    Базовая схема договора с опциональными полями.
    """
    number: Optional[str] = Field(
        None,
        description="Номер договора"
    )
    name: Optional[str] = Field(
        None, min_length=1, max_length=255,
        description="Название объекта по договору"
    )
    contract_date: Optional[date] = Field(
        None,
        description="Дата заключения договора"
    )
    parties: Optional[str] = Field(
        None, min_length=1,
        description="Участники или стороны договора"
    )
    execution_deadline: Optional[date] = Field(
        None,
        description="Срок исполнения договора"
    )
    planned_amount: Optional[Decimal] = Field(
        None, ge=0,
        description="Планируемая сумма договора"
    )
    actual_amount: Optional[Decimal] = Field(
        None, ge=0,
        description="Фактическая сумма договора"
    )
    readiness_description: Optional[str] = Field(
        None,
        description="Техническое описание стадии готовности"
    )


    @field_validator('planned_amount')
    @classmethod
    def validate_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Planned amount must be non-negative')
        return v

class ContractCreate(ContractBase):
    """
    Схема для создания договора (все поля опциональны).
    """
    pass

class ContractUpdate(ContractBase):
    """
    Схема для обновления договора.
    Все поля опциональны, актуальная сумма должна быть неотрицательной.
    """
    actual_amount: Optional[Decimal] = Field(None, ge=0)  # Валидация >= 0

    @field_validator('actual_amount')
    @classmethod
    def validate_actual_amount(cls, v):
        if v is not None and v < 0:
            raise ValueError('Actual amount must be non-negative')
        return v

class ContractRead(ContractBase):
    """
    Схема для чтения данных договора с идентификатором, датой создания и версиями.
    """
    id: int
    actual_amount: Optional[Decimal] = None
    created_at: Optional[datetime] = None
    versions: List['ContractVersionRead'] = []

    class Config:
        from_attributes = True

class ContractVersionBase(BaseModel):
    """
    Базовая схема версии договора.
    """
    version_number: int = Field(
        ..., gt=0, 
        description="Номер версии договора, обязательно"
    )
    changes_description: Optional[str] = Field(
        None, 
        description="Описание изменений в версии"
    )
    ai_summary: Optional[str] = Field(
        None, 
        description="ИИ-сгенерированное краткое резюме изменений"
    )


class ContractVersionCreate(ContractVersionBase):
    """
    Схема для создания версии договора.
    """
    pass

class ContractVersionRead(ContractVersionBase):
    """
    Схема для чтения версии договора с ID, ссылкой на договор и датой создания.
    """
    id: int
    contract_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
