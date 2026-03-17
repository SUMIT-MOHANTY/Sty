import React, { useState } from 'react';
import { useAdminApplications } from '../hooks/useAdminApplications';
import { ApplicationStatus, IApplicationStatusUpdate } from '../types';

export const AdminApplications: React.FC = () => {
  const [selectedStatus, setSelectedStatus] = useState<ApplicationStatus | undefined>(undefined);
  const [statusUpdateFormVisible, setStatusUpdateFormVisible] = useState<string | null>(null);
  const [statusUpdate, setStatusUpdate] = useState<IApplicationStatusUpdate>({
    status: 'under_review',
    adminNotes: '',
  });

  const {
    applications,
    loading,
    error,
    updateApplicationStatus,
    nextPage,
    prevPage,
    currentPage,
    totalPages,
    fetchApplications
  } = useAdminApplications(selectedStatus);

  const handleStatusFilter = (status?: ApplicationStatus) => {
    setSelectedStatus(status);
    fetchApplications(status);
  };

  const handleStatusUpdateSubmit = async (applicationId: string) => {
    try {
      await updateApplicationStatus(applicationId, statusUpdate);
      setStatusUpdateFormVisible(null);
      // Reset form
      setStatusUpdate({
        status: 'under_review',
        adminNotes: '',
      });
    } catch (err) {
      console.error("Failed to update status:", err);
    }
  };

  if (loading && applications.length === 0) {
    return <div className="loading">Loading applications...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="admin-applications">
      <h2>Passport Applications</h2>

      <div className="filter-controls">
        <label>Filter by status:</label>
        <select
          value={selectedStatus || ''}
          onChange={(e) => handleStatusFilter(e.target.value as ApplicationStatus || undefined)}
        >
          <option value="">All Statuses</option>
          <option value="submitted">Submitted</option>
          <option value="under_review">Under Review</option>
          <option value="additional_info_required">Additional Info Required</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="pending_appointment">Pending Appointment</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <div className="applications-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Applicant</th>
              <th>Submitted</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {applications.map(application => (
              <React.Fragment key={application.id}>
                <tr>
                  <td>{application.id}</td>
                  <td>
                    {application.applicantName}<br />
                    <small>{application.applicantEmail}</small>
                  </td>
                  <td>{new Date(application.submittedAt).toLocaleDateString()}</td>
                  <td>
                    <span className={`status-badge ${application.status}`}>
                      {application.status.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td>
                    <button
                      className="view-btn"
                      onClick={() => window.location.href = `/admin/applications/${application.id}`}
                    >
                      View
                    </button>
                    <button
                      className="update-btn"
                      onClick={() => setStatusUpdateFormVisible(application.id)}
                    >
                      Update Status
                    </button>
                  </td>
                </tr>
                {statusUpdateFormVisible === application.id && (
                  <tr className="status-update-form">
                    <td colSpan={5}>
                      <h4>Update Application Status</h4>
                      <div className="form-group">
                        <label>Status:</label>
                        <select
                          value={statusUpdate.status}
                          onChange={(e) => setStatusUpdate({
                            ...statusUpdate,
                            status: e.target.value as ApplicationStatus
                          })}
                        >
                          <option value="under_review">Under Review</option>
                          <option value="additional_info_required">Additional Info Required</option>
                          <option value="approved">Approved</option>
                          <option value="rejected">Rejected</option>
                          <option value="completed">Completed</option>
                        </select>
                      </div>

                      <div className="form-group">
                        <label>Admin Notes:</label>
                        <textarea
                          value={statusUpdate.adminNotes || ''}
                          onChange={(e) => setStatusUpdate({
                            ...statusUpdate,
                            adminNotes: e.target.value
                          })}
                        />
                      </div>

                      {statusUpdate.status === 'rejected' && (
                        <div className="form-group">
                          <label>Rejection Reason:</label>
                          <textarea
                            value={statusUpdate.rejectionReason || ''}
                            onChange={(e) => setStatusUpdate({
                              ...statusUpdate,
                              rejectionReason: e.target.value
                            })}
                            required
                          />
                        </div>
                      )}

                      <div className="form-actions">
                        <button
                          className="cancel-btn"
                          onClick={() => setStatusUpdateFormVisible(null)}
                        >
                          Cancel
                        </button>
                        <button
                          className="save-btn"
                          onClick={() => handleStatusUpdateSubmit(application.id)}
                        >
                          Save
                        </button>
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
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
