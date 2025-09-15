import React, { useState } from 'react';
import './FiltersPanel.css'

const FiltersPanel = ({ visible, filters, onApplyFilters, onResetFilters }) => {
  const [localFilters, setLocalFilters] = useState(filters);
  
  if (!visible) return null;
  
  const handleFilterChange = (field, value) => {
    setLocalFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  const handleApply = () => {
    onApplyFilters(localFilters);
  };
  
  const handleReset = () => {
    const resetFilters = {
      dateFrom: '',
      dateTo: '',
      amountFrom: '',
      amountTo: ''
    };
    setLocalFilters(resetFilters);
    onResetFilters();
  };
  
  return (
    <div className="filters-panel active" id="filtersPanel">
      <div className="filter-group">
        <label className="filter-label">Дата заключения от</label>
        <input 
          type="date" 
          className="filter-input" 
          value={localFilters.dateFrom}
          onChange={(e) => handleFilterChange('dateFrom', e.target.value)}
        />
      </div>
      
      <div className="filter-group">
        <label className="filter-label">Дата заключения до</label>
        <input 
          type="date" 
          className="filter-input" 
          value={localFilters.dateTo}
          onChange={(e) => handleFilterChange('dateTo', e.target.value)}
        />
      </div>
      
      <div className="filter-group">
        <label className="filter-label">Сумма от</label>
        <input 
          type="number" 
          className="filter-input" 
          placeholder="₽"
          value={localFilters.amountFrom}
          onChange={(e) => handleFilterChange('amountFrom', e.target.value)}
        />
      </div>
      
      <div className="filter-group">
        <label className="filter-label">Сумма до</label>
        <input 
          type="number" 
          className="filter-input" 
          placeholder="₽"
          value={localFilters.amountTo}
          onChange={(e) => handleFilterChange('amountTo', e.target.value)}
        />
      </div>
      
      <div className="filter-actions">
        <button className="btn-apply" onClick={handleApply}>
          Применить
        </button>
        <button className="btn-reset" onClick={handleReset}>
          Сбросить
        </button>
      </div>
    </div>
  );
};

export default FiltersPanel;