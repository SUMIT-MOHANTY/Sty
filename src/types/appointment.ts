export interface AppointmentSlot {
  id: string;
  date: string;
  startTime: string;
  endTime: string;
  available: boolean;
  serviceId?: string;
  serviceName?: string;
}

export interface Appointment {
  id: string;
  slotId: string;
  date: string;
  startTime: string;
  endTime: string;
  serviceName: string;
  clientName: string;
  clientEmail: string;
  clientPhone: string;
  status: 'scheduled' | 'completed' | 'cancelled';
  notes?: string;
  createdAt: string;
}

export type AppointmentFormData = Omit<Appointment, 'id' | 'createdAt'>;

export interface AppointmentFilters {
  startDate?: string;
  endDate?: string;
  status?: string;
  serviceId?: string;
}
