from sqlalchemy import (Column, Integer, String, Date,
                        Numeric, Text, DateTime, ForeignKey, func)
from sqlalchemy.orm import relationship
from app.core.database import Base

class Contract(Base):
    """Модель договора."""
    __tablename__ = "contract"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=True, index=True)
    name = Column(String, nullable=True, index=True)
    contract_date = Column(Date, nullable=True)
    parties = Column(String, nullable=True)
    execution_deadline = Column(Date, nullable=True)
    planned_amount = Column(Numeric(15, 2), nullable=True)
    actual_amount = Column(Numeric(15, 2), nullable=True)
    readiness_description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=True)

    # Связь 1:N с версиями
    versions = relationship("ContractVersion", back_populates="contract", cascade="all, delete-orphan")

class ContractVersion(Base):
    """Модель версии договора."""
    __tablename__ = "contract_version"
    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contract.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    changes_description = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=True)

    # Обратная связь
    contract = relationship("Contract", back_populates="versions")