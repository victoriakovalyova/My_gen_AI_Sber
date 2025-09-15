import React, { useState } from 'react';
import './TabsContainer.css';

const TabsContainer = ({ tabs, onCloseTab, onSelectTab }) => {
  const [showAllTabs, setShowAllTabs] = useState(false);
  
  if (tabs.length === 0) {
    return null;
  }

  const maxVisibleTabs = 4;
  const visibleTabs = tabs.slice(-maxVisibleTabs);
  const hiddenTabsCount = tabs.length - visibleTabs.length;

  return (
    <div className="tabs-container" id="tabsContainer">
      {hiddenTabsCount > 0 && (
        <div 
          className="tab-more-indicator"
          onClick={() => setShowAllTabs(true)}
          title={`Показать все вкладки (${tabs.length})`}
        >
          <i className="fas fa-ellipsis-h"></i>
          <span className="more-count">+{hiddenTabsCount}</span>
        </div>
      )}
      
      {visibleTabs.map(tab => (
        <div 
          key={tab.id} 
          className={`tab ${tab.active ? 'active' : ''}`}
          onClick={() => onSelectTab(tab.id)}
        >
          <i className="fas fa-file-contract"></i>
          <span className="tab-title">{tab.title}</span>
          <span 
            className="tab-close" 
            onClick={(e) => {
              e.stopPropagation();
              onCloseTab(tab.id);
            }}
          >
            <i className="fas fa-times"></i>
          </span>
        </div>
      ))}
      
      {showAllTabs && (
        <div className="all-tabs-overlay">
          <div className="all-tabs-header">
            <h3>Все открытые вкладки ({tabs.length})</h3>
            <button 
              className="close-overlay"
              onClick={() => setShowAllTabs(false)}
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
          <div className="all-tabs-list">
            {tabs.map(tab => (
              <div 
                key={tab.id} 
                className={`all-tab-item ${tab.active ? 'active' : ''}`}
                onClick={() => {
                  onSelectTab(tab.id);
                  setShowAllTabs(false);
                }}
              >
                <i className="fas fa-file-contract"></i>
                <span className="all-tab-title">{tab.title}</span>
                <span 
                  className="all-tab-close" 
                  onClick={(e) => {
                    e.stopPropagation();
                    onCloseTab(tab.id);
                  }}
                >
                  <i className="fas fa-times"></i>
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TabsContainer;