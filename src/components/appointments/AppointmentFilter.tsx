import React, { useState } from 'react';
import { Button } from '../Button';

interface AppointmentFilterProps {
  onFilter: (filters: any) => void;
}

export const AppointmentFilter: React.FC<AppointmentFilterProps> = ({ onFilter }) => {
  const [filters, setFilters] = useState({
    date: '',
    status: 'all'
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilter(filters);
  };

  const handleReset = () => {
    setFilters({
      date: '',
      status: 'all'
    });
    onFilter({
      date: '',
      status: 'all'
    });
  };

  return (
    <div className="p-4">
      <h3 className="text-lg font-medium mb-4">Filter Appointments</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input
              type="date"
              name="date"
              value={filters.date}
              onChange={handleChange}
              className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              name="status"
              value={filters.status}
              onChange={handleChange}
              className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
            >
              <option value="all">All Statuses</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <div className="flex items-end space-x-2">
            <Button type="submit" variant="primary">Apply Filters</Button>
            <Button type="button" variant="secondary" onClick={handleReset}>Reset</Button>
          </div>
        </div>
      </form>
    </div>
  );
};
