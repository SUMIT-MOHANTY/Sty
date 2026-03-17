export interface IAdminUser {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  isActive: boolean;
  permissions?: string[];
  createdAt: string;
}

export type ApplicationStatus =
  | 'submitted'
  | 'under_review'
  | 'additional_info_required'
  | 'approved'
  | 'rejected'
  | 'pending_appointment'
  | 'completed';

export interface IApplication {
  id: string;
  userId: string;
  applicantName: string;
  applicantEmail: string;
  status: ApplicationStatus;
  submittedAt: string;
  updatedAt: string;
  documents: IDocument[];
  adminNotes?: string;
  rejectionReason?: string;
}

export interface IDocument {
  id: string;
  applicationId: string;
  type: string;
  fileName: string;
  fileUrl: string;
  uploadedAt: string;
}

export interface ISystemSettings {
  applicationFee: number;
  appointmentSlotsPerDay: number;
  maintenanceMode: boolean;
  notificationEmail: string;
  documentRetentionDays: number;
  allowedDocumentTypes: string[];
  customSettings?: Record<string, any>;
}

export interface IApplicationStatusUpdate {
  status: ApplicationStatus;
  adminNotes?: string;
  rejectionReason?: string;
}

export interface IUserPermissionUpdate {
  role: string;
  isActive?: boolean;
  permissions?: string[];
}
