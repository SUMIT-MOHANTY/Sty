import React, { useState } from 'react';
import { useAppointments } from '../../hooks/useAppointments';
import { AppointmentFilters } from '../../types/appointment';

const AppointmentList: React.FC = () => {
  const [filters, setFilters] = useState<AppointmentFilters>({
    startDate: new Date().toISOString().split('T')[0], // Today
    status: '',
  });

  const {
    appointments,
    isLoading,
    error,
    setFilters: applyFilters,
    updateAppointmentStatus
  } = useAppointments(filters);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const handleApplyFilters = (e: React.FormEvent) => {
    e.preventDefault();
    applyFilters(filters);
  };

  const handleStatusChange = async (id: string, status: 'scheduled' | 'completed' | 'cancelled') => {
    await updateAppointmentStatus(id, status);
  };

  // Group appointments by date for better organization
  const appointmentsByDate = appointments.reduce((acc, appointment) => {
    if (!acc[appointment.date]) acc[appointment.date] = [];
    acc[appointment.date].push(appointment);
    return acc;
  }, {} as Record<string, typeof appointments>);

  if (isLoading) return <div className="loading">Loading appointments...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="appointment-list">
      <div className="filters-section">
        <h3>Filter Appointments</h3>
        <form onSubmit={handleApplyFilters} className="filters-form">
          <div className="form-group">
            <label htmlFor="startDate">Start Date</label>
            <input
              id="startDate"
              type="date"
              name="startDate"
              value={filters.startDate || ''}
              onChange={handleFilterChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="endDate">End Date (Optional)</label>
            <input
              id="endDate"
              type="date"
              name="endDate"
              value={filters.endDate || ''}
              onChange={handleFilterChange}
            />
          </div>

          <div className="form-group">
            <label htmlFor="status">Status</label>
            <select
              id="status"
              name="status"
              value={filters.status || ''}
              onChange={handleFilterChange}
            >
              <option value="">All Statuses</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="serviceId">Service (Optional)</label>
            <select
              id="serviceId"
              name="serviceId"
              value={filters.serviceId || ''}
              onChange={handleFilterChange}
            >
              <option value="">All Services</option>
              {/* This would be populated from a service API */}
              <option value="1">Haircut</option>
              <option value="2">Massage</option>
              <option value="3">Consultation</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary">Apply Filters</button>
        </form>
      </div>

      <div className="appointments-container">
        <h2>Appointments</h2>

        {Object.keys(appointmentsByDate).length === 0 ? (
          <p className="no-appointments">No appointments found matching your criteria.</p>
        ) : (
          Object.entries(appointmentsByDate).map(([date, dateAppointments]) => (
            <div key={date} className="date-group">
              <h3 className="date-header">
                {new Date(date).toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </h3>

              <div className="appointments-grid">
                {dateAppointments.map(appointment => (
                  <div
                    key={appointment.id}
                    className={`appointment-card status-${appointment.status}`}
                  >
                    <div className="appointment-time">
                      {appointment.startTime} - {appointment.endTime}
                    </div>

                    <div className="appointment-service">
                      <strong>Service:</strong> {appointment.serviceName}
                    </div>

                    <div className="client-info">
                      <div><strong>Client:</strong> {appointment.clientName}</div>
                      <div><strong>Email:</strong> {appointment.clientEmail}</div>
                      <div><strong>Phone:</strong> {appointment.clientPhone}</div>
                    </div>

                    {appointment.notes && (
                      <div className="appointment-notes">
                        <strong>Notes:</strong> {appointment.notes}
                      </div>
                    )}

                    <div className="appointment-status">
                      <span className={`status-badge status-${appointment.status}`}>
                        {appointment.status}
                      </span>
                    </div>

                    <div className="appointment-actions">
                      <select
                        value={appointment.status}
                        onChange={(e) => handleStatusChange(
                          appointment.id,
                          e.target.value as 'scheduled' | 'completed' | 'cancelled'
                        )}
                      >
                        <option value="scheduled">Scheduled</option>
                        <option value="completed">Completed</option>
                        <option value="cancelled">Cancelled</option>
                      </select>
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

export default AppointmentList;
