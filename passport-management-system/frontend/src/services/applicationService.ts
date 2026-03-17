import apiClient from '../utils/apiClient';

export interface Application {
  id: number;
  user_id: number;
  application_number: string;
  application_type: string;
  status: string;
  submitted_at: string;
  last_updated_at: string;
  notes: string | null;
}

export interface StatusUpdate {
  id: number;
  application_id: number;
  status: string;
  comment: string | null;
  created_at: string;
  created_by: number;
}

export interface ApplicationStatus {
  application: Application;
  current_status: string;
  status_history: StatusUpdate[];
}

export const applicationService = {
  async getApplications(): Promise<Application[]> {
    const response = await apiClient.get('/applications');
    return response.data;
  },

  async getApplicationById(id: number): Promise<Application> {
    const response = await apiClient.get(`/applications/${id}`);
    return response.data;
  },

  async getApplicationStatus(id: number): Promise<ApplicationStatus> {
    const response = await apiClient.get(`/applications/${id}/status`);
    return response.data;
  },

  async submitApplication(applicationData: {
    application_type: string;
    notes?: string;
  }): Promise<Application> {
    const response = await apiClient.post('/applications', applicationData);
    return response.data;
  }
};

export default applicationService;
