import { Appointment, AppointmentSlot, AppointmentFilters } from '../types/appointment';

// API service for appointment management
export const appointmentService = {
  // Get all appointment slots
  async getSlots(): Promise<AppointmentSlot[]> {
    try {
      const response = await fetch('/api/admin/slots');
      if (!response.ok) throw new Error('Failed to fetch slots');
      return await response.json();
    } catch (error) {
      console.error('Error fetching appointment slots:', error);
      throw error;
    }
  },

  // Create a new appointment slot
  async createSlot(slot: Omit<AppointmentSlot, 'id'>): Promise<AppointmentSlot> {
    try {
      const response = await fetch('/api/admin/slots', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(slot),
      });
      if (!response.ok) throw new Error('Failed to create slot');
      return await response.json();
    } catch (error) {
      console.error('Error creating appointment slot:', error);
      throw error;
    }
  },

  // Update an existing appointment slot
  async updateSlot(id: string, slot: Partial<AppointmentSlot>): Promise<AppointmentSlot> {
    try {
      const response = await fetch(`/api/admin/slots/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(slot),
      });
      if (!response.ok) throw new Error('Failed to update slot');
      return await response.json();
    } catch (error) {
      console.error('Error updating appointment slot:', error);
      throw error;
    }
  },

  // Delete an appointment slot
  async deleteSlot(id: string): Promise<void> {
    try {
      const response = await fetch(`/api/admin/slots/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete slot');
    } catch (error) {
      console.error('Error deleting appointment slot:', error);
      throw error;
    }
  },

  // Get all appointments with optional filters
  async getAppointments(filters?: AppointmentFilters): Promise<Appointment[]> {
    try {
      let url = '/api/admin/appointments';
      if (filters) {
        const params = new URLSearchParams();
        if (filters.startDate) params.append('startDate', filters.startDate);
        if (filters.endDate) params.append('endDate', filters.endDate);
        if (filters.status) params.append('status', filters.status);
        if (filters.serviceId) params.append('serviceId', filters.serviceId);
        url += `?${params.toString()}`;
      }

      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch appointments');
      return await response.json();
    } catch (error) {
      console.error('Error fetching appointments:', error);
      throw error;
    }
  },

  // Update appointment status
  async updateAppointmentStatus(id: string, status: 'scheduled' | 'completed' | 'cancelled'): Promise<Appointment> {
    try {
      const response = await fetch(`/api/admin/appointments/${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      if (!response.ok) throw new Error('Failed to update appointment status');
      return await response.json();
    } catch (error) {
      console.error('Error updating appointment status:', error);
      throw error;
    }
  },
};
