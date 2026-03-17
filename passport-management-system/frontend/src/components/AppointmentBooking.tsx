import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useNavigate } from 'react-router-dom';
import { LocationSelector } from './LocationSelector';
import { DatePicker } from './DatePicker';
import { TimeSlotGrid } from './TimeSlotGrid';
import { Button } from './Button';
import { Modal } from './Modal';
import { useAuth } from '../hooks/useAuth';
import { useApi } from '../hooks/useApi';
import { useToast } from '../hooks/useToast';
import { appointmentService } from '../services/appointmentService';

// Validation schema
const schema = yup.object().shape({
  applicationId: yup.number().required('Application ID is required'),
  locationId: yup.number().required('Please select a location'),
  date: yup.date()
    .required('Please select a date')
    .min(new Date(), 'Date cannot be in the past'),
  timeSlotId: yup.number().required('Please select an available time slot'),
});

type AppointmentBookingProps = {
  applicationId: number;
  onSuccess?: () => void;
};

export const AppointmentBooking: React.FC<AppointmentBookingProps> = ({
  applicationId,
  onSuccess
}) => {
  const { user, csrfToken } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [isLoading, setIsLoading] = useState(false);
  const [locations, setLocations] = useState<any[]>([]);
  const [availableSlots, setAvailableSlots] = useState<any[]>([]);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<any>(null);
  const [bookingError, setBookingError] = useState<string | null>(null);
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);

  const { register, handleSubmit, watch, setValue, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      applicationId,
      locationId: undefined,
      date: undefined,
      timeSlotId: undefined,
    }
  });

  const selectedLocationId = watch('locationId');
  const selectedDate = watch('date');

  // Load locations when component mounts
  useEffect(() => {
    const loadLocations = async () => {
      try {
        const response = await appointmentService.getLocations();
        setLocations(response);
      } catch (error) {
        console.error('Error loading locations:', error);
        showToast('Error loading locations. Please try again.', 'error');
      }
    };

    loadLocations();

    // Anti-brute force timing
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, []);

  // Load available slots when location and date are selected
  useEffect(() => {
    if (selectedLocationId && selectedDate) {
      const fetchTimeSlots = async () => {
        setIsLoading(true);
        try {
          // Add random delay to prevent timing attacks (300-800ms)
          const randomDelay = Math.floor(Math.random() * 500) + 300;
          const newTimeoutId = setTimeout(async () => {
            const formattedDate = selectedDate.toISOString().split('T')[0];
            const slots = await appointmentService.getAvailableSlots(selectedLocationId, formattedDate);
            setAvailableSlots(slots);
            setIsLoading(false);
          }, randomDelay);

          setTimeoutId(newTimeoutId);
        } catch (error) {
          console.error('Error loading time slots:', error);
          showToast('Error loading available time slots. Please try again.', 'error');
          setIsLoading(false);
        }
      };

      fetchTimeSlots();
    } else {
      setAvailableSlots([]);
    }
  }, [selectedLocationId, selectedDate]);

  const onSubmit = async (data: any) => {
    setBookingError(null);

    // Find the selected time slot details
    const slot = availableSlots.find(slot => slot.id === data.timeSlotId);
    if (slot) {
      setSelectedSlot(slot);
      setShowConfirmModal(true);
    } else {
      showToast('Please select a valid time slot', 'error');
    }
  };

  const handleConfirmBooking = async () => {
    setIsLoading(true);
    try {
      const bookingData = {
        application_id: applicationId,
        time_slot_id: selectedSlot.id,
      };

      // Use the CSRF token in the request header
      const appointment = await appointmentService.bookAppointment(bookingData, csrfToken);

      setShowConfirmModal(false);
      showToast('Appointment booked successfully!', 'success');

      if (onSuccess) {
        onSuccess();
      } else {
        navigate(`/appointments/${appointment.id}`);
      }
    } catch (error: any) {
      console.error('Error booking appointment:', error);
      setBookingError(error.response?.data?.detail || 'Failed to book appointment. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTimeSlotSelect = (slotId: number) => {
    setValue('timeSlotId', slotId);
  };

  // Security enhancements
  if (!user) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-600">You must be logged in to book an appointment.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6" data-testid="appointment-booking">
      <h2 className="text-2xl font-semibold mb-6">Book an Appointment</h2>

      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Hidden application ID */}
        <input type="hidden" {...register('applicationId')} />

        {/* Location Selector */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Office Location
          </label>
          <LocationSelector
            locations={locations}
            value={selectedLocationId}
            onChange={(id) => setValue('locationId', id)}
            error={errors.locationId?.message}
          />
        </div>

        {/* Date Picker */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Date
          </label>
          <DatePicker
            value={selectedDate}
            onChange={(date) => setValue('date', date)}
            error={errors.date?.message}
            minDate={new Date()}
            maxDate={new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)} // 90 days ahead
          />
        </div>

        {/* Time Slot Grid */}
        {selectedLocationId && selectedDate && (
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Available Time Slot
            </label>
            {isLoading ? (
              <div className="flex justify-center p-6">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
              </div>
            ) : availableSlots.length > 0 ? (
              <TimeSlotGrid
                slots={availableSlots}
                onSelectSlot={handleTimeSlotSelect}
                selectedSlotId={watch('timeSlotId')}
                error={errors.timeSlotId?.message}
              />
            ) : (
              <div className="p-4 bg-gray-50 border border-gray-200 rounded-md">
                <p className="text-gray-600">No available time slots for the selected date and location.</p>
              </div>
            )}
          </div>
        )}

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button
            type="submit"
            disabled={isLoading || availableSlots.length === 0}
          >
            Continue to Book
          </Button>
        </div>
      </form>

      {/* Confirmation Modal */}
      {showConfirmModal && selectedSlot && (
        <Modal
          isOpen={true}
          onClose={() => setShowConfirmModal(false)}
          title="Confirm Appointment"
        >
          <div className="p-4">
            <p className="mb-4">Please confirm your appointment details:</p>

            <div className="mb-4 p-4 bg-gray-50 rounded-md">
              <div className="grid grid-cols-2 gap-2">
                <span className="text-gray-600">Location:</span>
                <span className="font-medium">{locations.find(l => l.id === selectedLocationId)?.name}</span>

                <span className="text-gray-600">Date:</span>
                <span className="font-medium">{selectedDate.toLocaleDateString()}</span>

                <span className="text-gray-600">Time:</span>
                <span className="font-medium">
                  {new Date(`2000-01-01T${selectedSlot.start_time}`).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} -
                  {new Date(`2000-01-01T${selectedSlot.end_time}`).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </span>
              </div>
            </div>

            {bookingError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-600 text-sm">{bookingError}</p>
              </div>
            )}

            <div className="flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowConfirmModal(false)}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                onClick={handleConfirmBooking}
                disabled={isLoading}
              >
                {isLoading ? 'Booking...' : 'Confirm Booking'}
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
