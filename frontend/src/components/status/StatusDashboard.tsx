import React from 'react';
import StatusBadge from './StatusBadge';
import StatusTimeline from './StatusTimeline';
import useStatusPolling from '../../hooks/useStatusPolling';
import { Link } from 'react-router-dom';
import { ClockIcon, CalendarIcon, RefreshIcon } from '@heroicons/react/outline';

interface StatusDashboardProps {
  applicationId: string;
  pollingInterval?: number;
}

const StatusDashboard: React.FC<StatusDashboardProps> = ({ applicationId, pollingInterval = 60000 }) => {
  const { status, isLoading, error, refreshStatus } = useStatusPolling(applicationId, {
    pollingInterval,
    initialFetch: true,
  });

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Not available';

    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }).format(date);
  };

  if (isLoading) {
    return (
      <div className="animate-pulse bg-white shadow rounded-lg p-6">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="h-10 bg-gray-200 rounded mb-6"></div>
        <div className="h-20 bg-gray-200 rounded mb-6"></div>
        <div className="flex space-x-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-red-800">Error loading status</h3>
        <p className="text-red-700 mt-2">{error.message}</p>
        <button
          onClick={refreshStatus}
          className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700"
        >
          <RefreshIcon className="h-4 w-4 mr-2" />
          Retry
        </button>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-500">No status information available for this application.</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-5 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Application Status</h3>
      </div>

      <div className="px-6 py-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div className="flex items-center mb-4 md:mb-0">
            <StatusBadge status={status.current_status} className="text-sm" />
            <button
              onClick={refreshStatus}
              className="ml-3 inline-flex items-center text-sm text-gray-500 hover:text-gray-700"
            >
              <RefreshIcon className="h-4 w-4 mr-1" />
              Refresh
            </button>
          </div>

          <div className="flex flex-col text-sm text-gray-500">
            <div className="flex items-center mb-1">
              <ClockIcon className="h-4 w-4 mr-1" />
              <span>Last updated: {formatDate(status.last_updated)}</span>
            </div>

            {status.estimated_completion_date && (
              <div className="flex items-center">
                <CalendarIcon className="h-4 w-4 mr-1" />
                <span>Estimated completion: {formatDate(status.estimated_completion_date)}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="px-6 py-4">
        <StatusTimeline currentStatus={status.current_status} />
      </div>

      <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 text-right">
        <Link
          to={`/applications/${applicationId}/history`}
          className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          View complete history
          <svg className="ml-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
          </svg>
        </Link>
      </div>
    </div>
  );
};

export default StatusDashboard;
