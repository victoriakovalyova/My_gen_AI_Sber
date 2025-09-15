import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Header from './components/Header';
import FiltersPanel from './components/FiltersPanel';
import ContractsSidebar from './components/ContractsSidebar';
import ContractDetails from './components/ContractDetails';
import ContractModal from './components/ContractModal';
import TabsContainer from './components/TabsContainer';
import './App.css';

function App() {
  const [filtersVisible, setFiltersVisible] = useState(false);
  const [activeContract, setActiveContract] = useState(null);
  const [tabs, setTabs] = useState([]);
  const [contractsData, setContractsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    dateFrom: '',
    dateTo: '',
    amountFrom: '',
    amountTo: ''
  });
  const [isContractModalOpen, setIsContractModalOpen] = useState(false);
  const [editingContract, setEditingContract] = useState(null);

  // Показ/скрытие фильтров
  const toggleFilters = useCallback(() => setFiltersVisible(prev => !prev), []);

  // Открытие модального окна создания
  const openCreateModal = () => {
    setEditingContract(null);
    setIsContractModalOpen(true);
  };

  // Открытие модального окна редактирования
  const openEditModal = (contract) => {
    setEditingContract(contract);
    setIsContractModalOpen(true);
  };

  // Сохранение контракта
  const handleSaveContract = useCallback(async (contractData) => {
    try {
      let url = 'http://localhost/api/v1/contracts/';
      let method = 'POST';
      if (editingContract) {
        url = `http://localhost/api/v1/contracts/${editingContract.id}`;
        method = 'PATCH';
      }

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contractData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка при сохранении контракта');
      }

      const savedContract = await response.json();

      setContractsData(prev => {
        if (editingContract) {
          return prev.map(c => c.id === savedContract.id ? savedContract : c);
        }
        return [...prev, savedContract];
      });

      alert(editingContract ? 'Контракт успешно обновлен!' : 'Контракт успешно создан!');
    } catch (error) {
      console.error(error);
      alert(error.message || 'Произошла ошибка при сохранении контракта');
    }
  }, [editingContract]);

  // Загрузка контрактов с сервера
  useEffect(() => {
    const fetchContracts = async () => {
      try {
        const response = await fetch('http://localhost/api/v1/contracts/');
        if (!response.ok) throw new Error('Ошибка загрузки контрактов');
        const data = await response.json();
        setContractsData(data);
      } catch (error) {
        console.error(error);
        alert('Не удалось загрузить контракты с сервера.');
      } finally {
        setLoading(false);
      }
    };
    fetchContracts();
  }, []);

  // Фильтрация контрактов
  const filteredContracts = useMemo(() => {
    let result = [...contractsData];
    if (filters.dateFrom) {
      result = result.filter(c => new Date(c.contract_date) >= new Date(filters.dateFrom));
    }
    if (filters.dateTo) {
      result = result.filter(c => new Date(c.contract_date) <= new Date(filters.dateTo));
    }
    if (filters.amountFrom) {
      result = result.filter(c => c.planned_amount >= parseFloat(filters.amountFrom));
    }
    if (filters.amountTo) {
      result = result.filter(c => c.planned_amount <= parseFloat(filters.amountTo));
    }
    return result;
  }, [contractsData, filters]);

  const applyFilters = useCallback((newFilters) => setFilters(newFilters), []);
  const resetFilters = useCallback(() => setFilters({ dateFrom: '', dateTo: '', amountFrom: '', amountTo: '' }), []);

  // Вкладки
  const openContractTab = useCallback((contract) => {
    setActiveContract(contract);
    setTabs(prevTabs => {
      const newTabs = prevTabs.map(tab => ({ ...tab, active: false }));
      const existingTabIndex = newTabs.findIndex(tab => tab.contractId === contract.id);
      if (existingTabIndex !== -1) {
        newTabs[existingTabIndex].active = true;
      } else {
        newTabs.push({ id: Date.now(), title: contract.name, active: true, contractId: contract.id });
      }
      return newTabs;
    });
  }, []);

  const selectTab = useCallback((tabId) => {
    setTabs(prevTabs => {
      const updatedTabs = prevTabs.map(tab => ({ ...tab, active: tab.id === tabId }));
      const activeTab = updatedTabs.find(tab => tab.active);
      if (activeTab) {
        const correspondingContract = contractsData.find(c => c.id === activeTab.contractId);
        setActiveContract(correspondingContract);
      }
      return updatedTabs;
    });
  }, [contractsData]);

  const closeTab = useCallback((tabId) => {
    setTabs(prevTabs => {
      const newTabs = prevTabs.filter(tab => tab.id !== tabId);
      const closedTab = prevTabs.find(tab => tab.id === tabId);
      if (closedTab?.active) {
        if (newTabs.length > 0) {
          const lastTab = newTabs[newTabs.length - 1];
          lastTab.active = true;
          const correspondingContract = contractsData.find(c => c.id === lastTab.contractId);
          setActiveContract(correspondingContract);
        } else {
          setActiveContract(null);
        }
      }
      return newTabs;
    });
  }, [contractsData]);

  if (loading) return <div className="App"><div className="container">Загрузка...</div></div>;

  return (
    <div className="App">
      <div className="container">
        <Header toggleFilters={toggleFilters} filtersVisible={filtersVisible} />
        <FiltersPanel visible={filtersVisible} filters={filters} onApplyFilters={applyFilters} onResetFilters={resetFilters} />
        <TabsContainer tabs={tabs} onCloseTab={closeTab} onSelectTab={selectTab} />

        <div className="sidebar-area">
          <div className="sidebar-actions">
            <button className="import-btn" onClick={openCreateModal}>
              <i className="fas fa-plus"></i> Создать контракт
            </button>
          </div>

          <ContractsSidebar
            contracts={filteredContracts}
            onContractClick={openContractTab}
            onContractEdit={openEditModal}
            activeContract={activeContract}
          />
        </div>

        <ContractDetails contract={activeContract} onEditContract={openEditModal} />
      </div>

      <ContractModal
        isOpen={isContractModalOpen}
        onClose={() => setIsContractModalOpen(false)}
        contract={editingContract}
        onSave={handleSaveContract}
      />
    </div>
  );
}

export default App;
