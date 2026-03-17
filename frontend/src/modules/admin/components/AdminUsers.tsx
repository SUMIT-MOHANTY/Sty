import React, { useState } from 'react';
import { useAdminUsers } from '../hooks/useAdminUsers';
import { IUserPermissionUpdate } from '../types';

export const AdminUsers: React.FC = () => {
  const {
    users,
    loading,
    error,
    updateUserPermissions,
    nextPage,
    prevPage,
    currentPage,
    totalPages
  } = useAdminUsers();

  const [editingUserId, setEditingUserId] = useState<string | null>(null);
  const [userUpdate, setUserUpdate] = useState<IUserPermissionUpdate>({
    role: 'user',
    isActive: true
  });

  const handleEditUser = (userId: string, currentRole: string, currentActive: boolean) => {
    setEditingUserId(userId);
    setUserUpdate({
      role: currentRole,
      isActive: currentActive
    });
  };

  const handleCancelEdit = () => {
    setEditingUserId(null);
  };

  const handleSaveUserPermissions = async (userId: string) => {
    try {
      await updateUserPermissions(userId, userUpdate);
      setEditingUserId(null);
    } catch (err) {
      console.error("Failed to update user permissions:", err);
    }
  };

  if (loading && users.length === 0) {
    return <div className="loading">Loading users...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="admin-users">
      <h2>User Management</h2>

      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Role</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td>{`${user.firstName} ${user.lastName}`}</td>
                <td>{user.email}</td>
                <td>
                  {editingUserId === user.id ? (
                    <select
                      value={userUpdate.role}
                      onChange={(e) => setUserUpdate({
                        ...userUpdate,
                        role: e.target.value
                      })}
                    >
                      <option value="user">User</option>
                      <option value="admin">Admin</option>
                      <option value="support">Support</option>
                    </select>
                  ) : (
                    <span className={`role-badge ${user.role}`}>{user.role}</span>
                  )}
                </td>
                <td>
                  {editingUserId === user.id ? (
                    <select
                      value={userUpdate.isActive ? 'active' : 'inactive'}
                      onChange={(e) => setUserUpdate({
                        ...userUpdate,
                        isActive: e.target.value === 'active'
                      })}
                    >
                      <option value="active">Active</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  ) : (
                    <span className={`status-badge ${user.isActive ? 'active' : 'inactive'}`}>
                      {user.isActive ? 'Active' : 'Inactive'}
                    </span>
                  )}
                </td>
                <td>
                  {editingUserId === user.id ? (
                    <>
                      <button className="cancel-btn" onClick={handleCancelEdit}>Cancel</button>
                      <button className="save-btn" onClick={() => handleSaveUserPermissions(user.id)}>
                        Save
                      </button>
                    </>
                  ) : (
                    <button
                      className="edit-btn"
                      onClick={() => handleEditUser(user.id, user.role, user.isActive)}
                    >
                      Edit
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button onClick={prevPage} disabled={currentPage === 0}>Previous</button>
        <span>Page {currentPage + 1} of {totalPages}</span>
        <button onClick={nextPage} disabled={currentPage === totalPages - 1}>Next</button>
      </div>
    </div>
  );
};
