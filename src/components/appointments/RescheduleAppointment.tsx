import React, { useState, useEffect } from 'react';
import { useApi } from '../../hooks/useApi';
import { Appointment } from '../../types/appointment';
import { Card } from '../Card';
import { Button } from '../Button';
import TimeSlotPicker from '../TimeSlotPicker';

interface TimeSlot {
  date: string;
  time: string;
  available: boolean;
}

interface RescheduleAppointmentProps {
  appointment: Appointment;
  onSuccess: (updatedAppointment: Appointment) => void;
  onCancel: () => void;
}

const RescheduleAppointment: React.FC<RescheduleAppointmentProps> = ({
  appointment,
  onSuccess,
  onCancel
}) => {
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const { get, put } = useApi();

  useEffect(() => {
    const fetchAvailableSlots = async () => {
      setIsLoading(true);
      try {
        // Use the location from the current appointment
        const response = await get(`/api/appointments/available-slots?location_id=${appointment.location_id}`);
        setAvailableSlots(response);
        setError(null);
      } catch (err) {
        setError('Failed to load available time slots. Please try again.');
        console.error('Error fetching time slots:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAvailableSlots();
  }, [appointment.location_id, get]);

  const handleReschedule = async () => {
    if (!selectedDate || !selectedTime) {
      setError('Please select a new date and time for your appointment.');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await put(`/api/appointments/${appointment.id}/reschedule`, {
        appointment_date: selectedDate,
        appointment_time: selectedTime
      });

      onSuccess(response);
    } catch (err) {
      setError('Failed to reschedule appointment. Please try again.');
      console.error('Error rescheduling appointment:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTimeSlotSelect = (date: string, time: string) => {
    setSelectedDate(date);
    setSelectedTime(time);
    setError(null); // Clear any previous errors
  };

  const formatDate = (dateStr: string): string => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <Card className="reschedule-appointment p-6">
      <h2 className="text-2xl font-bold mb-4">Reschedule Appointment</h2>

      <div className="current-appointment mb-6 p-3 bg-gray-50 rounded-md">
        <h3 className="text-lg font-medium mb-2">Current Appointment</h3>
        <p className="text-gray-700">
          Date: {formatDate(appointment.appointment_date)}
        </p>
        <p className="text-gray-700">
          Time: {appointment.appointment_time}
        </p>
        <p className="text-gray-700">
          Location: {appointment.location.name}
        </p>
      </div>

      <div className="new-appointment mb-6">
        <h3 className="text-lg font-medium mb-2">Select New Date & Time</h3>

        {isLoading ? (
          <div className="text-center py-4">Loading available time slots...</div>
        ) : (
          <TimeSlotPicker
            availableSlots={availableSlots}
            onSelectTimeSlot={handleTimeSlotSelect}
            selectedDate={selectedDate}
            selectedTime={selectedTime}
          />
        )}
      </div>

      {error && (
        <div className="error-message text-red-600 bg-red-100 p-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-3 mt-6">
        <Button
          variant="secondary"
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1"
        >
          Cancel
        </Button>

        <Button
          variant="primary"
          onClick={handleReschedule}
          disabled={isSubmitting || !selectedDate || !selectedTime}
          className="flex-1"
        >
          {isSubmitting ? 'Submitting...' : 'Confirm Reschedule'}
        </Button>
      </div>
    </Card>
  );
};

export default RescheduleAppointment;
