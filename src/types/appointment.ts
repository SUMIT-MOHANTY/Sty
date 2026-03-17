export interface Location {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  instructions?: string;
}

export interface ApplicationSummary {
  id: string;
  type: string;
  status: string;
}

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
  userId: string;
  slotId?: string;
  date: string;
  time?: string;
  startTime?: string;
  endTime?: string;
  duration?: number; // in minutes
  serviceName?: string;
  clientName?: string;
  clientEmail?: string;
  clientPhone?: string;
  location?: Location;
  status: 'scheduled' | 'completed' | 'cancelled' | 'pending';
  purpose?: string;
  notes?: string;
  createdAt: string;
  updatedAt?: string;
  application?: ApplicationSummary;
}

export type AppointmentFormData = Omit<Appointment, 'id' | 'createdAt'>;

export interface AppointmentFilters {
  startDate?: string;
  endDate?: string;
  status?: string;
  serviceId?: string;
}
