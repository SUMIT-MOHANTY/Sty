export interface PersonalDetails {
  first_name: string;
  last_name: string;
  date_of_birth: string;
  place_of_birth: string;
  gender: string;
  nationality: string;
}

export interface ContactDetails {
  street: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone: string;
  email: string;
}

export interface ApplicationCreate {
  personal_details: PersonalDetails;
  contact_details: ContactDetails;
  passport_details?: Record<string, any>;
  additional_info?: Record<string, any>;
}

export interface Application extends ApplicationCreate {
  id: string;
  application_number: string;
  user_id: string;
  status: 'draft' | 'submitted' | 'under_review' | 'approved' | 'rejected' | 'completed';
  submitted_at?: string;
  created_at: string;
  updated_at: string;
}
