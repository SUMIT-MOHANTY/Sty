import React, { useState } from 'react';
import { StatusType } from '../status/StatusIndicator';
import '../../styles/HistoryFilter.css';

interface HistoryFilterProps {
  onFilterChange: (filters: HistoryFilters) => void;
  availableCategories?: string[];
  initialFilters?: Partial<HistoryFilters>;
}

export interface HistoryFilters {
  dateFrom: string | null;
  dateTo: string | null;
  status: StatusType[] | null;
  categories: string[] | null;
  searchTerm: string | null;
}

const HistoryFilter: React.FC<HistoryFilterProps> = ({
  onFilterChange,
  availableCategories = [],
  initialFilters = {},
}) => {
  const [filters, setFilters] = useState<HistoryFilters>({
    dateFrom: initialFilters.dateFrom || null,
    dateTo: initialFilters.dateTo || null,
    status: initialFilters.status || null,
    categories: initialFilters.categories || null,
    searchTerm: initialFilters.searchTerm || null,
  });

  const statusOptions: StatusType[] = ['success', 'error', 'warning', 'info', 'pending'];

  const handleChange = (filterName: keyof HistoryFilters, value: any) => {
    const newFilters = { ...filters, [filterName]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleStatusToggle = (status: StatusType) => {
    const currentStatuses = filters.status || [];
    const newStatuses = currentStatuses.includes(status)
      ? currentStatuses.filter(s => s !== status)
      : [...currentStatuses, status];

    handleChange('status', newStatuses.length ? newStatuses : null);
  };

  const handleCategoryToggle = (category: string) => {
    const currentCategories = filters.categories || [];
    const newCategories = currentCategories.includes(category)
      ? currentCategories.filter(c => c !== category)
      : [...currentCategories, category];

    handleChange('categories', newCategories.length ? newCategories : null);
  };

  const clearFilters = () => {
    const clearedFilters = {
      dateFrom: null,
      dateTo: null,
      status: null,
      categories: null,
      searchTerm: null,
    };
    setFilters(clearedFilters);
    onFilterChange(clearedFilters);
  };

  const hasActiveFilters = Object.values(filters).some(value =>
    value !== null && (Array.isArray(value) ? value.length > 0 : true)
  );

  return (
    <div className="history-filter">
      <div className="filter-header">
        <h3>Filter History</h3>
        {hasActiveFilters && (
          <button className="clear-filters" onClick={clearFilters}>
            Clear All
          </button>
        )}
      </div>

      <div className="filter-section">
        <label htmlFor="searchTerm">Search:</label>
        <input
          type="text"
          id="searchTerm"
          placeholder="Search by keyword..."
          value={filters.searchTerm || ''}
          onChange={(e) => handleChange('searchTerm', e.target.value || null)}
        />
      </div>

      <div className="filter-section">
        <h4>Date Range</h4>
        <div className="date-range">
          <div>
            <label htmlFor="dateFrom">From:</label>
            <input
              type="date"
              id="dateFrom"
              value={filters.dateFrom || ''}
              onChange={(e) => handleChange('dateFrom', e.target.value || null)}
            />
          </div>
          <div>
            <label htmlFor="dateTo">To:</label>
            <input
              type="date"
              id="dateTo"
              value={filters.dateTo || ''}
              onChange={(e) => handleChange('dateTo', e.target.value || null)}
            />
          </div>
        </div>
      </div>

      <div className="filter-section">
        <h4>Status</h4>
        <div className="status-filters">
          {statusOptions.map((status) => (
            <div
              key={status}
              className={`status-filter ${filters.status?.includes(status) ? 'active' : ''}`}
              onClick={() => handleStatusToggle(status)}
            >
              <span className={`status-dot ${status}`}></span>
              <span className="status-label">{status.charAt(0).toUpperCase() + status.slice(1)}</span>
            </div>
          ))}
        </div>
      </div>

      {availableCategories.length > 0 && (
        <div className="filter-section">
          <h4>Categories</h4>
          <div className="category-filters">
            {availableCategories.map((category) => (
              <div
                key={category}
                className={`category-filter ${filters.categories?.includes(category) ? 'active' : ''}`}
                onClick={() => handleCategoryToggle(category)}
              >
                {category}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryFilter;
