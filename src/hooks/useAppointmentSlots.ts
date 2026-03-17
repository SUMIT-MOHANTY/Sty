import { useState, useEffect, useCallback } from 'react';
import { AppointmentSlot } from '../types/appointment';
import { appointmentService } from '../services/appointmentService';

export const useAppointmentSlots = () => {
  const [slots, setSlots] = useState<AppointmentSlot[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSlots = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await appointmentService.getSlots();
      setSlots(data);
    } catch (err) {
      setError('Failed to load appointment slots');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSlots();
  }, [fetchSlots]);

  const createSlot = async (slot: Omit<AppointmentSlot, 'id'>) => {
    try {
      const newSlot = await appointmentService.createSlot(slot);
      setSlots(prev => [...prev, newSlot]);
      return true;
    } catch (err) {
      setError('Failed to create appointment slot');
      console.error(err);
      return false;
    }
  };

  const updateSlot = async (id: string, slotData: Partial<AppointmentSlot>) => {
    try {
      const updatedSlot = await appointmentService.updateSlot(id, slotData);
      setSlots(prev =>
        prev.map(slot => slot.id === id ? updatedSlot : slot)
      );
      return true;
    } catch (err) {
      setError('Failed to update appointment slot');
      console.error(err);
      return false;
    }
  };

  const deleteSlot = async (id: string) => {
    try {
      await appointmentService.deleteSlot(id);
      setSlots(prev => prev.filter(slot => slot.id !== id));
      return true;
    } catch (err) {
      setError('Failed to delete appointment slot');
      console.error(err);
      return false;
    }
  };

  return {
    slots,
    isLoading,
    error,
    createSlot,
    updateSlot,
    deleteSlot,
    refreshSlots: fetchSlots,
  };
};
