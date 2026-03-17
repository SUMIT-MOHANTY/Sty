import React, { useState, useEffect } from 'react';
import { format } from 'date-fns';

const SlotForm = ({ slot, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    date: format(new Date(), 'yyyy-MM-dd'),
    time: '09:00',
    capacity: 1
  });

  useEffect(() => {
    if (slot) {
      setFormData({
        date: slot.date,
        time: slot.time,
        capacity: slot.capacity
      });
    }
  }, [slot]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div>
      <h3 className="text-lg font-medium mb-4">
        {slot ? 'Edit Appointment Slot' : 'Create New Appointment Slot'}
      </h3>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date
            </label>
            <input
              type="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              className="w-full border rounded p-2"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time
            </label>
            <select
              name="time"
              value={formData.time}
              onChange={handleChange}
              className="w-full border rounded p-2"
              required
            >
              {Array.from({ length: 18 }, (_, i) => {
                const hour = Math.floor(i / 2) + 9; // Start at 9:00
                const minute = i % 2 === 0 ? '00' : '30';
                const timeValue = `${hour.toString().padStart(2, '0')}:${minute}`;
                return (
                  <option key={i} value={timeValue}>
                    {timeValue}
                  </option>
                );
              })}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Capacity
            </label>
            <input
              type="number"
              name="capacity"
              value={formData.capacity}
              onChange={handleChange}
              min="1"
              max="50"
              className="w-full border rounded p-2"
              required
            />
          </div>
        </div>

        <div className="flex justify-end space-x-2">
          <button
            type="button"
            onClick={onCancel}
            className="border rounded px-4 py-2 hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="bg-blue-500 text-white rounded px-4 py-2 hover:bg-blue-600"
          >
            {slot ? 'Update Slot' : 'Create Slot'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SlotForm;
