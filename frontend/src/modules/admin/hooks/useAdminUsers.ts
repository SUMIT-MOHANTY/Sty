import { useState, useEffect, useCallback } from 'react';
import { adminService } from '../services/adminService';
import { IAdminUser, IUserPermissionUpdate } from '../types';

export const useAdminUsers = () => {
  const [users, setUsers] = useState<IAdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const limit = 20;

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminService.getUsers(currentPage * limit, limit);
      setUsers(data);

      // In a real implementation, we would get the total count from the API
      setTotalPages(Math.ceil(data.length / limit) + (data.length === limit ? 1 : 0));
    } catch (err) {
      setError('Failed to fetch users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [currentPage]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const updateUserPermissions = async (userId: string, permissionUpdate: IUserPermissionUpdate) => {
    try {
      setError(null);
      const updatedUser = await adminService.updateUserPermissions(userId, permissionUpdate);

      // Update the user in the local state
      setUsers(prevUsers =>
        prevUsers.map(user =>
          user.id === userId ? updatedUser : user
        )
      );

      return updatedUser;
    } catch (err) {
      setError('Failed to update user permissions');
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
    users,
    loading,
    error,
    currentPage,
    totalPages,
    fetchUsers,
    updateUserPermissions,
    nextPage,
    prevPage
  };
};
