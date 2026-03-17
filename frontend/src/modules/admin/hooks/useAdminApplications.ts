import { useState, useEffect, useCallback } from 'react';
import { adminService } from '../services/adminService';
import { IApplication, ApplicationStatus, IApplicationStatusUpdate } from '../types';

export const useAdminApplications = (initialStatus?: ApplicationStatus) => {
  const [applications, setApplications] = useState<IApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const limit = 20;

  const fetchApplications = useCallback(async (status?: ApplicationStatus) => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminService.getApplications(currentPage * limit, limit, status);
      setApplications(data);

      // In a real implementation, we would get the total count from the API
      // For now, just set a placeholder value
      setTotalPages(Math.ceil(data.length / limit) + (data.length === limit ? 1 : 0));
    } catch (err) {
      setError('Failed to fetch applications');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [currentPage, limit]);

  useEffect(() => {
    fetchApplications(initialStatus);
  }, [fetchApplications, initialStatus]);

  const updateApplicationStatus = async (applicationId: string, statusUpdate: IApplicationStatusUpdate) => {
    try {
      setError(null);
      const updatedApplication = await adminService.updateApplicationStatus(applicationId, statusUpdate);

      // Update the application in the local state
      setApplications(prevApplications =>
        prevApplications.map(app =>
          app.id === applicationId ? updatedApplication : app
        )
      );

      return updatedApplication;
    } catch (err) {
      setError('Failed to update application status');
      console.error(err);
      throw err;
    }
  };

  const nextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1);
    }
  };

  return {
    applications,
    loading,
    error,
    currentPage,
    totalPages,
    fetchApplications,
    updateApplicationStatus,
    nextPage,
    prevPage
  };
};
