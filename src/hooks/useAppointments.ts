import { useState, useEffect, useCallback } from 'react';
import { Appointment, AppointmentFilters } from '../types/appointment';
import { appointmentService } from '../services/appointmentService';

export const useAppointments = (initialFilters?: AppointmentFilters) => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [filters, setFilters] = useState<AppointmentFilters>(initialFilters || {});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAppointments = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await appointmentService.getAppointments(filters);
      setAppointments(data);
    } catch (err) {
      setError('Failed to load appointments');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchAppointments();
  }, [fetchAppointments]);

  const updateAppointmentStatus = async (id: string, status: 'scheduled' | 'completed' | 'cancelled') => {
    try {
      await appointmentService.updateAppointmentStatus(id, status);
      // Update local state with the new status
      setAppointments(prev =>
        prev.map(apt => apt.id === id ? { ...apt, status } : apt)
      );
      return true;
    } catch (err) {
      setError('Failed to update appointment status');
      console.error(err);
      return false;
    }
  };

  return {
    appointments,
    isLoading,
    error,
    setFilters,
    updateAppointmentStatus,
    refreshAppointments: fetchAppointments,
  };
};
