import React, { useState, useEffect } from 'react';
import './ContractModal.css';

const ContractModal = ({ isOpen, onClose, contract = null, onSave }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    number: '',
    name: '',
    contract_date: '',
    parties: '',
    execution_deadline: '',
    planned_amount: '',
    actual_amount: '',
    readiness_description: ''
  });
  const [attachedFiles, setAttachedFiles] = useState([]);

  useEffect(() => {
    if (contract) {
      setFormData({
        number: contract.number || '',
        name: contract.name || '',
        contract_date: contract.contract_date || '',
        parties: contract.parties || '',
        execution_deadline: contract.execution_deadline || '',
        planned_amount: contract.planned_amount || '',
        actual_amount: contract.actual_amount || '',
        readiness_description: contract.readiness_description || ''
      });
    } else {
      setFormData({
        number: '',
        name: '',
        contract_date: '',
        parties: '',
        execution_deadline: '',
        planned_amount: '',
        actual_amount: '',
        readiness_description: ''
      });
    }
    setAttachedFiles([]);
  }, [contract, isOpen]);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    setAttachedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (!formData.number || !formData.name || !formData.contract_date) {
        alert('Заполните обязательные поля: номер, название и дата контракта');
        setIsSubmitting(false);
        return;
      }

      // Собираем только заполненные поля
      const payload = {};
      if (formData.number) payload.number = formData.number;
      if (formData.name) payload.name = formData.name;
      if (formData.contract_date) payload.contract_date = formData.contract_date;
      if (formData.parties) payload.parties = formData.parties || null;
      if (formData.execution_deadline) payload.execution_deadline = formData.execution_deadline || null;
      if (formData.planned_amount) payload.planned_amount = parseFloat(formData.planned_amount);
      if (formData.actual_amount) payload.actual_amount = parseFloat(formData.actual_amount);
      if (formData.readiness_description) payload.readiness_description = formData.readiness_description || null;

      // Отправка на сервер
      const url = contract
        ? `http://localhost/api/v1/contracts/${contract.id}`
        : 'http://localhost/api/v1/contracts/';
      const method = contract ? 'PATCH' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка при сохранении контракта');
      }

      const savedContract = await response.json();
      onSave(savedContract);
      onClose();
    } catch (error) {
      console.error(error);
      alert(error.message || 'Произошла ошибка при сохранении контракта');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content contract-modal">
        <div className="modal-header">
          <h2>{contract ? 'Редактирование контракта' : 'Создание нового контракта'}</h2>
          <button className="close-modal" onClick={onClose}><i className="fas fa-times"></i></button>
        </div>

        <form onSubmit={handleSubmit} className="contract-form">
          <div className="form-section">
            <h3>Основная информация</h3>
            <div className="form-row">
              <div className="form-group required">
                <label>Номер контракта</label>
                <input
                  type="text"
                  value={formData.number}
                  onChange={(e) => handleInputChange('number', e.target.value)}
                  placeholder="Введите номер контракта"
                  required
                />
              </div>

              <div className="form-group required">
                <label>Название контракта</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Введите название контракта"
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group required">
                <label>Дата заключения</label>
                <input
                  type="date"
                  value={formData.contract_date}
                  onChange={(e) => handleInputChange('contract_date', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>Срок исполнения</label>
                <input
                  type="date"
                  value={formData.execution_deadline}
                  onChange={(e) => handleInputChange('execution_deadline', e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Стороны контракта</label>
              <input
                type="text"
                value={formData.parties}
                onChange={(e) => handleInputChange('parties', e.target.value)}
                placeholder="Укажите стороны контракта"
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Финансовая информация</h3>
            <div className="form-row">
              <div className="form-group">
                <label>Плановая сумма (₽)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.planned_amount}
                  onChange={(e) => handleInputChange('planned_amount', e.target.value)}
                  placeholder="0.00"
                />
              </div>

              <div className="form-group">
                <label>Фактическая сумма (₽)</label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.actual_amount}
                  onChange={(e) => handleInputChange('actual_amount', e.target.value)}
                  placeholder="0.00"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Описание и статус</h3>
            <div className="form-group">
              <label>Описание готовности</label>
              <textarea
                rows="4"
                value={formData.readiness_description}
                onChange={(e) => handleInputChange('readiness_description', e.target.value)}
                placeholder="Опишите текущий статус выполнения контракта..."
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Прикрепленные файлы (опционально)</h3>
            <label htmlFor="contract-files" className="file-drop-zone">
              <i className="fas fa-paperclip"></i>
              Перетащите файлы сюда или нажмите для выбора
              <input
                id="contract-files"
                type="file"
                multiple
                onChange={handleFileChange}
                className="file-input"
              />
            </label>

            {attachedFiles.length > 0 && (
              <div className="attached-files">
                {attachedFiles.map((file, index) => (
                  <div key={index} className="file-item">
                    <span>{file.name} ({(file.size / 1024).toFixed(1)} KB)</span>
                    <button type="button" onClick={() => removeFile(index)}>×</button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="form-actions">
            <button type="button" onClick={onClose} className="btn-secondary">Отмена</button>
            <button type="submit" disabled={isSubmitting} className="btn-primary">
              {isSubmitting ? <>Сохранение... <i className="fas fa-spinner fa-spin"></i></> : (contract ? 'Сохранить изменения' : 'Создать контракт')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ContractModal;
