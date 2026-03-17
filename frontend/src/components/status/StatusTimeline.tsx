import React from 'react';
import { ApplicationStatus } from '../../types/status';

interface StatusTimelineProps {
  currentStatus: ApplicationStatus;
}

const StatusTimeline: React.FC<StatusTimelineProps> = ({ currentStatus }) => {
  // Define all statuses in order
  const statuses: { status: ApplicationStatus; label: string }[] = [
    { status: 'submitted', label: 'Submitted' },
    { status: 'under_review', label: 'Under Review' },
    { status: 'pending_documents', label: 'Documents Required' },
    { status: 'approved', label: 'Approved' },
  ];

  // Helper function to determine if a status is active or completed
  const getStatusState = (status: ApplicationStatus) => {
    const statusOrder = {
      submitted: 0,
      under_review: 1,
      pending_documents: 2,
      approved: 3,
      rejected: -1, // Special case
    };

    // If current status is rejected, only "submitted" is completed
    if (currentStatus === 'rejected') {
      if (status === 'submitted') return 'completed';
      if (status === 'rejected') return 'current';
      return 'upcoming';
    }

    // Normal flow
    if (statusOrder[currentStatus] === statusOrder[status]) return 'current';
    if (statusOrder[currentStatus] > statusOrder[status]) return 'completed';
    return 'upcoming';
  };

  return (
    <div className="py-6">
      <div className="flex items-center w-full">
        {statuses.map((statusItem, index) => (
          <React.Fragment key={statusItem.status}>
            {/* Status circle */}
            <div className="relative">
              <div
                className={`
                  w-6 h-6 rounded-full border-2 flex items-center justify-center
                  ${getStatusState(statusItem.status) === 'completed'
                    ? 'bg-green-500 border-green-500'
                    : getStatusState(statusItem.status) === 'current'
                    ? 'bg-blue-500 border-blue-500'
                    : 'bg-white border-gray-300'}
                `}
              >
                {getStatusState(statusItem.status) === 'completed' && (
                  <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className="mt-2 absolute -left-1/2 transform translate-x-1/2 text-xs font-medium text-center w-20">
                {statusItem.label}
              </div>
            </div>

            {/* Line connecting circles */}
            {index < statuses.length - 1 && (
              <div
                className={`flex-1 h-0.5 ${
                  getStatusState(statuses[index + 1].status) === 'completed' ||
                  (getStatusState(statusItem.status) === 'completed' && getStatusState(statuses[index + 1].status) === 'current')
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                }`}
              />
            )}
          </React.Fragment>
        ))}

        {/* Special case for rejection status */}
        {currentStatus === 'rejected' && (
          <div className="relative ml-4">
            <div className="w-6 h-6 rounded-full bg-red-500 border-2 border-red-500 flex items-center justify-center">
              <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <div className="mt-2 absolute -left-1/2 transform translate-x-1/2 text-xs font-medium text-center w-20">
              Rejected
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatusTimeline;
