import React, { useState, useEffect } from 'react';
import { useApi } from '../../hooks/useApi';
import { AppointmentList } from '../../components/appointments/AppointmentList';
import { AppointmentFilter } from '../../components/appointments/AppointmentFilter';
import { Button } from '../../components/Button';
import { Modal } from '../../components/Modal';
import { AppointmentDetails } from '../../components/appointments/AppointmentDetails';
import { Appointment } from '../../types/appointment';
import { Card } from '../../components/Card';

export const ManageAppointmentsPage: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [filteredAppointments, setFilteredAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const api = useApi();

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/appointments');
        setAppointments(response.data);
        setFilteredAppointments(response.data);
        setIsLoading(false);
      } catch (err) {
        setError('Failed to fetch appointments');
        setIsLoading(false);
      }
    };

    fetchAppointments();
  }, [api]);

  const handleFilter = (filters: any) => {
    let filtered = [...appointments];

    if (filters.date) {
      filtered = filtered.filter(app =>
        new Date(app.date).toDateString() === new Date(filters.date).toDateString()
      );
    }

    if (filters.status && filters.status !== 'all') {
      filtered = filtered.filter(app => app.status === filters.status);
    }

    setFilteredAppointments(filtered);
  };

  const handleViewDetails = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setShowDetailsModal(true);
  };

  const handleCloseModal = () => {
    setShowDetailsModal(false);
    setSelectedAppointment(null);
  };

  const handleCancelAppointment = async (id: string) => {
    try {
      await api.put(`/appointments/${id}/cancel`);
      // Update local state
      const updatedAppointments = appointments.map(app =>
        app.id === id ? { ...app, status: 'cancelled' } : app
      );
      setAppointments(updatedAppointments);
      setFilteredAppointments(updatedAppointments);
      setShowDetailsModal(false);
    } catch (err) {
      setError('Failed to cancel appointment');
    }
  };

  const handleReschedule = (id: string) => {
    // Navigate to reschedule page
    window.location.href = `/appointments/reschedule/${id}`;
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Manage Appointments</h1>

      <Card className="mb-6">
        <AppointmentFilter onFilter={handleFilter} />
      </Card>

      {isLoading ? (
        <p>Loading appointments...</p>
      ) : error ? (
        <p className="text-red-500">{error}</p>
      ) : (
        <AppointmentList
          appointments={filteredAppointments}
          onViewDetails={handleViewDetails}
        />
      )}

      {showDetailsModal && selectedAppointment && (
        <Modal title="Appointment Details" onClose={handleCloseModal}>
          <AppointmentDetails appointment={selectedAppointment} />
          <div className="flex justify-end mt-4 space-x-2">
            {selectedAppointment.status !== 'cancelled' && (
              <>
                <Button
                  variant="secondary"
                  onClick={() => handleReschedule(selectedAppointment.id)}
                >
                  Reschedule
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleCancelAppointment(selectedAppointment.id)}
                >
                  Cancel Appointment
                </Button>
              </>
            )}
            <Button variant="primary" onClick={handleCloseModal}>Close</Button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default ManageAppointmentsPage;
