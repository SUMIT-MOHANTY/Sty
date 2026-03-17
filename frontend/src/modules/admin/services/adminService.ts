import { api } from '../../../services/api';
import {
  IApplication,
  IAdminUser,
  ISystemSettings,
  IApplicationStatusUpdate,
  IUserPermissionUpdate
} from '../types';

export const adminService = {
  // Applications
  getApplications: async (skip = 0, limit = 100, status?: string): Promise<IApplication[]> => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    if (status) {
      params.append('status', status);
    }

    const response = await api.get(`/admin/applications?${params.toString()}`);
    return response.data;
  },

  updateApplicationStatus: async (
    applicationId: string,
    statusUpdate: IApplicationStatusUpdate
  ): Promise<IApplication> => {
    const response = await api.patch(`/admin/applications/${applicationId}`, statusUpdate);
    return response.data;
  },

  // Users
  getUsers: async (skip = 0, limit = 100): Promise<IAdminUser[]> => {
    const params = new URLSearchParams();
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());

    const response = await api.get(`/admin/users?${params.toString()}`);
    return response.data;
  },

  updateUserPermissions: async (
    userId: string,
    permissionUpdate: IUserPermissionUpdate
  ): Promise<IAdminUser> => {
    const response = await api.patch(`/admin/users/${userId}`, permissionUpdate);
    return response.data;
  },

  // System Settings
  getSystemSettings: async (): Promise<ISystemSettings> => {
    const response = await api.get('/admin/settings');
    return response.data;
  },

  updateSystemSettings: async (settings: ISystemSettings): Promise<ISystemSettings> => {
    const response = await api.put('/admin/settings', settings);
    return response.data;
  }
};
