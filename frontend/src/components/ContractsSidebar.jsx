import React from 'react';
import ContractCard from './ContractCard';
import './ContractsSidebar.css';

const ContractsSidebar = ({ contracts, onContractClick, onContractEdit, activeContract }) => {
  return (
    <aside className="contracts-sidebar">
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"></link>

      <div className="sidebar-container"> 
        <div className="sidebar-header">
          <i className="fas fa-file-contract"></i> Контракты
        </div>
        <div className="cards-container">
          {contracts.map(contract => (
            <div key={contract.id} className="contract-item-wrapper">
              <ContractCard
                contract={contract}
                onClick={() => onContractClick(contract)}
                isActive={activeContract && activeContract.id === contract.id}
              />
              <button 
                className="edit-contract-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  onContractEdit(contract);
                }}
                title="Редактировать контракт"
              >
                <i className="fas fa-edit"></i>
              </button>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
};

export default ContractsSidebar;