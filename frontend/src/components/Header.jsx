import React from 'react';
import './Header.css'
const Header = ({ toggleFilters, filtersVisible }) => {
  return (
    <header className="header">
      <div className="search-container">
        <input 
          type="text" 
          className="search-input" 
          placeholder="Введите номер контракта, название или организацию..." 
        />
        <button className="search-btn">
          <i className="fas fa-search"></i> Найти
        </button>
        <button 
          className="toggle-filters" 
          id="toggleFilters"
          onClick={toggleFilters}
        >
          <i className={filtersVisible ? "fas fa-times" : "fas fa-filter"}></i> 
          {filtersVisible ? "Скрыть фильтры" : "Фильтры"}
        </button>
      </div>
    </header>
  );
};

export default Header;