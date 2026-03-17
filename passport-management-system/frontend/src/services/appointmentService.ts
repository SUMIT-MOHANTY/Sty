import { apiClient } from '../utils/apiClient';
import { AxiosError } from 'axios';

export interface TimeSlot {
  id: number;
  location_id: number;
  start_time: string;
  end_time: string;
  date: string;
}

export interface AppointmentBookingData {
  application_id: number;
  time_slot_id: number;
}

export interface Appointment {
  id: number;
  user_id: number;
  application_id: number;
  location_id: number;
  time_slot_id: number;
  appointment_date: string;
  status: string;
  created_at: string;
  updated_at: string;
}

class AppointmentService {
  /**
   * Get all available locations for appointments
   */
  async getLocations() {
    try {
      const response = await apiClient.get('/locations');
      return response.data;
    } catch (error: any) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Get available time slots for a location and date
   * @param locationId - ID of the location
   * @param date - Date string in YYYY-MM-DD format
   */
  async getAvailableSlots(locationId: number, date: string): Promise<TimeSlot[]> {
    try {
      // Input validation
      if (!locationId || !date) {
        throw new Error('Location ID and date are required');
      }

      // Validate date format
      const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
      if (!dateRegex.test(date)) {
        throw new Error('Invalid date format. Use YYYY-MM-DD');
      }

      const response = await apiClient.get(`/appointments/available-slots?location_id=${locationId}&date=${date}`);
      return response.data;
    } catch (error: any) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Book an appointment
   * @param data - Appointment data
   * @param csrfToken - CSRF token for security
   */
  async bookAppointment(data: AppointmentBookingData, csrfToken: string): Promise<Appointment> {
    try {
      // Input validation
      if (!data.application_id || !data.time_slot_id) {
        throw new Error('Application ID and time slot ID are required');
      }

      const response = await apiClient.post('/appointments/', data, {
        headers: {
          'X-CSRF-Token': csrfToken
        }
      });

      return response.data;
    } catch (error: any) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Get appointment details
   * @param appointmentId - ID of the appointment
   */
  async getAppointment(appointmentId: number): Promise<Appointment> {
    try {
      if (!appointmentId) {
        throw new Error('Appointment ID is required');
      }

      const response = await apiClient.get(`/appointments/${appointmentId}`);
      return response.data;
    } catch (error: any) {
      this.handleError(error);
      throw error;
    }
  }

  /**
   * Handle API errors
   */
  private handleError(error: AxiosError) {
    // Log errors to monitoring service (would implement in production)
    console.error('Appointment service error:', error);

    // Rate limiting detection
    if (error.response?.status === 429) {
      console.error('Rate limit exceeded for appointment service');
    }

    // Network errors
    if (!error.response) {
      console.error('Network error when accessing appointment service');
    }
  }
}

export const appointmentService = new AppointmentService();
