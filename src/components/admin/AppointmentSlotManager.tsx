import React, { useState } from 'react';
import { AppointmentSlot } from '../../types/appointment';
import { useAppointmentSlots } from '../../hooks/useAppointmentSlots';

interface SlotFormData {
  date: string;
  startTime: string;
  endTime: string;
  serviceId?: string;
}

const AppointmentSlotManager: React.FC = () => {
  const { slots, isLoading, error, createSlot, updateSlot, deleteSlot } = useAppointmentSlots();
  const [formData, setFormData] = useState<SlotFormData>({
    date: '',
    startTime: '',
    endTime: '',
  });
  const [editingId, setEditingId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const slotData: Omit<AppointmentSlot, 'id'> = {
      ...formData,
      available: true,
    };

    if (editingId) {
      await updateSlot(editingId, slotData);
    } else {
      await createSlot(slotData);
    }

    // Reset form
    setFormData({ date: '', startTime: '', endTime: '', serviceId: '' });
    setEditingId(null);
    setShowForm(false);
  };

  const handleEdit = (slot: AppointmentSlot) => {
    setFormData({
      date: slot.date,
      startTime: slot.startTime,
      endTime: slot.endTime,
      serviceId: slot.serviceId,
    });
    setEditingId(slot.id);
    setShowForm(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this slot?')) {
      await deleteSlot(id);
    }
  };

  const handleCancel = () => {
    setFormData({ date: '', startTime: '', endTime: '', serviceId: '' });
    setEditingId(null);
    setShowForm(false);
  };

  // Group slots by date for better organization
  const slotsByDate = slots.reduce((acc, slot) => {
    if (!acc[slot.date]) acc[slot.date] = [];
    acc[slot.date].push(slot);
    return acc;
  }, {} as Record<string, AppointmentSlot[]>);

  if (isLoading) return <div className="loading">Loading slots...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="appointment-slot-manager">
      <div className="action-bar">
        <h2>Appointment Slots</h2>
        {!showForm && (
          <button
            className="btn btn-primary"
            onClick={() => setShowForm(true)}
          >
            Create New Slot
          </button>
        )}
      </div>

      {showForm && (
        <div className="slot-form-container">
          <h3>{editingId ? 'Edit Appointment Slot' : 'Create Appointment Slot'}</h3>
          <form onSubmit={handleSubmit} className="slot-form">
            <div className="form-group">
              <label htmlFor="date">Date</label>
              <input
                id="date"
                type="date"
                name="date"
                value={formData.date}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="startTime">Start Time</label>
              <input
                id="startTime"
                type="time"
                name="startTime"
                value={formData.startTime}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="endTime">End Time</label>
              <input
                id="endTime"
                type="time"
                name="endTime"
                value={formData.endTime}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="serviceId">Service (Optional)</label>
              <select
                id="serviceId"
                name="serviceId"
                value={formData.serviceId || ''}
                onChange={handleInputChange}
              >
                <option value="">Any Service</option>
                {/* This would be populated from a service API */}
                <option value="1">Haircut</option>
                <option value="2">Massage</option>
                <option value="3">Consultation</option>
              </select>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn btn-primary">
                {editingId ? 'Update Slot' : 'Create Slot'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={handleCancel}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="slots-container">
        {Object.keys(slotsByDate).length === 0 ? (
          <p className="no-slots">No appointment slots available.</p>
        ) : (
          Object.entries(slotsByDate).map(([date, dateSlots]) => (
            <div key={date} className="date-group">
              <h3 className="date-header">{new Date(date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</h3>
              <div className="slots-grid">
                {dateSlots.map(slot => (
                  <div key={slot.id} className={`slot-card ${!slot.available ? 'booked' : ''}`}>
                    <div className="slot-time">
                      {slot.startTime} - {slot.endTime}
                    </div>
                    {slot.serviceName && (
                      <div className="slot-service">{slot.serviceName}</div>
                    )}
                    <div className="slot-status">
                      Status: {slot.available ? 'Available' : 'Booked'}
                    </div>
                    <div className="slot-actions">
                      <button
                        className="btn btn-small"
                        onClick={() => handleEdit(slot)}
                        disabled={!slot.available}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-small btn-danger"
                        onClick={() => handleDelete(slot.id)}
                        disabled={!slot.available}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AppointmentSlotManager;
