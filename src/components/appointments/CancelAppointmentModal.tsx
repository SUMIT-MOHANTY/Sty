import React, { useState } from 'react';
import { useApi } from '../../hooks/useApi';
import { Appointment } from '../../types/appointment';
import { Modal } from '../Modal';
import { Button } from '../Button';

interface CancelAppointmentModalProps {
  appointment: Appointment;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const CancelAppointmentModal: React.FC<CancelAppointmentModalProps> = ({
  appointment,
  isOpen,
  onClose,
  onSuccess
}) => {
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const { post } = useApi();

  const handleCancel = async () => {
    setIsSubmitting(true);
    try {
      await post(`/api/appointments/${appointment.id}/cancel`, {});
      setError(null);
      onSuccess();
    } catch (err) {
      setError('Failed to cancel appointment. Please try again.');
      console.error('Error canceling appointment:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatDate = (dateStr: string): string => {
    return new Date(dateStr).toLocaleDateString();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Cancel Appointment">
      <div className="cancel-appointment-modal">
        <div className="mb-6">
          <p className="text-lg mb-4">Are you sure you want to cancel this appointment?</p>

          <div className="appointment-details bg-gray-50 p-4 rounded">
            <p><strong>Date:</strong> {formatDate(appointment.appointment_date)}</p>
            <p><strong>Time:</strong> {appointment.appointment_time}</p>
            <p><strong>Location:</strong> {appointment.location.name}</p>
          </div>

          <div className="mt-4 text-sm text-gray-600">
            <p className="mb-2">Please note:</p>
            <ul className="list-disc pl-5 space-y-1">
              <li>Cancellation cannot be undone</li>
              <li>You may need to wait before booking another appointment</li>
              <li>Cancellation may be subject to the passport office's policies</li>
            </ul>
          </div>
        </div>

        {error && (
          <div className="error-message text-red-600 bg-red-100 p-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="flex flex-col md:flex-row gap-3">
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={isSubmitting}
            className="flex-1"
          >
            Keep Appointment
          </Button>

          <Button
            variant="danger"
            onClick={handleCancel}
            disabled={isSubmitting}
            className="flex-1"
          >
            {isSubmitting ? 'Cancelling...' : 'Yes, Cancel Appointment'}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default CancelAppointmentModal;
