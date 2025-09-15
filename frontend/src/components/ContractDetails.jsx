import React from 'react';
import './ContractDetails.css';

// Функции для форматирования
const formatDate = (dateString) => {
  if (!dateString) return 'Дата не указана';
  const [year, month, day] = dateString.split('-');
  return `${day}.${month}.${year}`;
};

const formatSum = (amount) => {
  if (amount === null || amount === undefined) return 'Сумма не указана';
  return `${amount.toLocaleString('ru-RU')} ₽`;
};

const ContractDetails = ({ contract, restoring, onEditContract }) => {
  if (restoring) {
    return (
      <main className="main-content">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <span>Восстановление...</span>
        </div>
      </main>
    );
  }

  if (!contract) {
    return (
      <main className="main-content">
        <h2 className="section-title">
          <i className="fas fa-info-circle"></i> Выберите контракт для просмотра
        </h2>
        <div className="no-contract-selected">
          <i className="fas fa-folder-open"></i>
          <p>Для просмотра детальной информации выберите контракт из списка слева</p>
        </div>
      </main>
    );
  }

  // Функция для определения статуса
  const getStatusInfo = (contractData) => {
    if (contractData.readiness_description?.includes('заверш')) {
      return { status: 'completed', statusText: 'Завершен' };
    }
    return { status: 'active', statusText: 'Активный' };
  };

  const statusInfo = getStatusInfo(contract);
  const statusClass = `card-status status-${statusInfo.status}`;
  
  return (
    <main className="main-content">
      <h2 className="section-title">
        <i className="fas fa-info-circle"></i> Детальная информация о контракте
      </h2>
      
      <section className="contract-details">
        <div className="contract-header">
          <h2 className="contract-title">{contract.name || 'Без названия'}</h2>
          <div className="contract-header-actions">
            <span className={statusClass}>{statusInfo.statusText}</span>
            <button 
              className="edit-btn"
              onClick={() => onEditContract(contract)}
              title="Редактировать контракт"
            >
              <i className="fas fa-edit"></i> Редактировать
            </button>
          </div>
        </div>
        
        <div className="contract-info-flow">
          <div className="info-section">
            <h3 className="info-section-title">
              <i className="fas fa-key"></i> Ключевые параметры
            </h3>
            <div className="info-row">
              <div className="info-item info-important">
                <div className="info-label">
                  <div className="info-icon"><i className="fas fa-hashtag"></i></div> 
                  Номер контракта
                </div>
                <div className="info-value value-large">{contract.number || 'Не указан'}</div>
              </div>
              <div className="info-item info-highlight">
                <div className="info-label">
                  <i className="fas fa-ruble-sign"></i> Плановая сумма
                </div>
                <div className="info-value value-large">{formatSum(contract.planned_amount)}</div>
              </div>
              <div className="info-item info-highlight">
                <div className="info-label">
                  <i className="fas fa-ruble-sign"></i> Фактическая сумма
                </div>
                <div className="info-value value-large">{formatSum(contract.actual_amount)}</div>
              </div>
              <div className="info-item info-important">
                <div className="info-label">
                  <i className="fas fa-calendar-check"></i> Срок исполнения
                </div>
                <div className="info-value value-warning">{formatDate(contract.execution_deadline)}</div>
              </div>
            </div>
          </div>
          
          <div className="info-section">
            <h3 className="info-section-title">
              <i className="fas fa-list-alt"></i> Основная информация
            </h3>
            <div className="info-row">
              <div className="info-item">
                <div className="info-label">
                  <i className="fas fa-building"></i> Стороны контракта
                </div>
                <div className="info-value">{contract.parties || 'Не указаны'}</div>
              </div>
              <div className="info-item">
                <div className="info-label">
                  <i className="fas fa-file-contract"></i> Номер контракта
                </div>
                <div className="info-value">{contract.number || 'Не указан'}</div>
              </div>
              <div className="info-item">
                <div className="info-label">
                  <i className="fas fa-calendar-alt"></i> Дата контракта
                </div>
                <div className="info-value">{formatDate(contract.contract_date)}</div>
              </div>
            </div>
          </div>
          
          <div className="info-section">
            <h3 className="info-section-title">
              <i className="fas fa-align-left"></i> Описание готовности
            </h3>
            <div className="info-row">
              <div className="info-item info-highlight full-width">
                <div className="info-label">
                  <i className="fas fa-clipboard-check"></i> Описание
                </div>
                <div className="info-value">{contract.readiness_description || 'Описание отсутствует'}</div>
              </div>
            </div>
          </div>
          
          <div className="info-section">
            <h3 className="info-section-title">
              <i className="fas fa-database"></i> Системная информация
            </h3>
            <div className="info-row">
              <div className="info-item">
                <div className="info-label">
                  <i className="fas fa-fingerprint"></i> ID контракта
                </div>
                <div className="info-value">{contract.id}</div>
              </div>
              <div className="info-item">
                <div className="info-label">
                  <i className="fas fa-clock"></i> Дата создания
                </div>
                <div className="info-value">
                  {contract.created_at ? new Date(contract.created_at).toLocaleString('ru-RU') : 'Не указана'}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="analysis-section">
          <h3>
            <i className="fas fa-chart-line"></i> Анализ контракта
          </h3>
          
          <div className="analysis-grid">
            <div className="analysis-item">
              <h4>Финансовый анализ</h4>
              <p>
                {contract.actual_amount && contract.planned_amount ? 
                 `Фактическая сумма составляет ${Math.round((contract.actual_amount / contract.planned_amount) * 100)}% от плановой.` : 
                 'Данные для финансового анализа отсутствуют.'}
              </p>
            </div>
            
            <div className="analysis-item">
              <h4>Сроки исполнения</h4>
              <p>
                {contract.execution_deadline ? 
                 `Срок исполнения установлен до ${formatDate(contract.execution_deadline)}.` : 
                 'Срок исполнения не указан.'}
              </p>
            </div>
            
            <div className="analysis-item">
              <h4>Статус выполнения</h4>
              <p>
                {contract.readiness_description ? 
                 'По описанию готовности можно оценить текущий статус выполнения работ.' : 
                 'Информация о готовности отсутствует.'}
              </p>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
};

export default ContractDetails;