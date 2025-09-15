import React from 'react';
import './ContractCard.css';

// Функция для форматирования даты из YYYY-MM-DD в DD.MM.YYYY
const formatDate = (dateString) => {
  if (!dateString) return 'Дата не указана';
  const [year, month, day] = dateString.split('-');
  return `${day}.${month}.${year}`;
};

// Функция для форматирования суммы
const formatSum = (amount) => {
  if (amount === null || amount === undefined) return 'Сумма не указана';
  return `${amount.toLocaleString('ru-RU')} ₽`;
};

const ContractCard = ({ contract, onClick, isActive }) => {
  // Определяем статус на основе данных (заглушка - нужно адаптировать под вашу логику)
  const getStatusInfo = (contractData) => {
    // Пример логики определения статуса
    if (contractData.readiness_description?.includes('заверш')) {
      return { status: 'completed', statusText: 'Завершен' };
    }
    return { status: 'active', statusText: 'Активный' };
  };

  const statusInfo = contract ? getStatusInfo(contract) : { status: '', statusText: '' };
  const statusClass = `card-status status-${statusInfo.status}`;
  
  if (!contract) {
    return (
      <div className="contract-card">
        <div className="card-header">
          <div className="card-title">Контракт не загружен</div>
        </div>
      </div>
    );
  }
  
  return (
    <div 
      className={`contract-card ${isActive ? 'expanded' : ''}`}
      onClick={onClick}
    >
      <div className="card-header">
        <div className="card-title">{contract.name || 'Без названия'}</div>
        <div className="card-date">{formatDate(contract.contract_date)}</div>
      </div>
      <div className="card-sum">{formatSum(contract.planned_amount)}</div>
      <div className="card-info">
        {contract.readiness_description || 'Описание отсутствует'}
        <div className="card-customer">{contract.parties || 'Заказчик не указан'}</div>
        <span className={statusClass}>{statusInfo.statusText}</span>
      </div>
    </div>
  );
};

export default ContractCard;