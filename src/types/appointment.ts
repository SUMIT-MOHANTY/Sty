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

export interface Appointment {
  id: string;
  userId: string;
  date: string;
  time: string;
  duration: number; // in minutes
  location: Location;
  status: 'scheduled' | 'completed' | 'cancelled' | 'pending';
  purpose: string;
  notes?: string;
  createdAt: string;
  updatedAt: string;
  application?: ApplicationSummary;
}
