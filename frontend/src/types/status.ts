export type ApplicationStatus = 'submitted' | 'under_review' | 'approved' | 'rejected' | 'pending_documents';

export interface StatusUpdate {
  status: ApplicationStatus;
  timestamp: string;
  message: string;
  updated_by: string;
}

export interface ApplicationStatusResponse {
  application_id: string;
  current_status: ApplicationStatus;
  last_updated: string;
  estimated_completion_date: string | null;
}

export interface ApplicationHistoryResponse {
  application_id: string;
  history: StatusUpdate[];
}
