import React, { useState } from 'react';
import { ApplicationHistoryResponse, StatusUpdate } from '../../types/status';
import StatusBadge from './StatusBadge';

interface StatusHistoryViewProps {
  historyData: ApplicationHistoryResponse | null;
  isLoading: boolean;
  error: Error | null;
}

const StatusHistoryView: React.FC<StatusHistoryViewProps> = ({ historyData, isLoading, error }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  if (isLoading) {
    return (
      <div className="p-6 flex justify-center" data-testid="loading">
        <div className="animate-pulse flex flex-col w-full">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-4"></div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-200 rounded mb-4"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
        <h3 className="text-lg font-medium text-red-800">Error loading history</h3>
        <p className="text-red-700">{error.message}</p>
      </div>
    );
  }

  if (!historyData || historyData.history.length === 0) {
    return (
      <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
        <p className="text-gray-700">No history available for this application.</p>
      </div>
    );
  }

  // Sort history by timestamp (newest first)
  const sortedHistory = [...historyData.history].sort(
    (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );

  // Paginate the history
  const totalPages = Math.ceil(sortedHistory.length / itemsPerPage);
  const paginatedHistory = sortedHistory.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-4 py-5 sm:px-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">Application Status History</h3>
        <p className="mt-1 max-w-2xl text-sm text-gray-500">
          Complete history of status changes for application #{historyData.application_id}
        </p>
      </div>

      <div className="border-t border-gray-200">
        <ul className="divide-y divide-gray-200">
          {paginatedHistory.map((update: StatusUpdate, index: number) => (
            <li key={index} className="p-4">
              <div className="flex flex-col sm:flex-row sm:justify-between">
                <div className="mb-2 sm:mb-0">
                  <div className="flex items-center">
                    <StatusBadge status={update.status} />
                    <span className="ml-2 text-sm font-medium text-gray-900">
                      Updated by {update.updated_by}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-gray-700">{update.message}</p>
                </div>
                <div className="text-sm text-gray-500">
                  {formatDate(update.timestamp)}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setCurrentPage(Math.max(currentPage - 1, 1))}
              disabled={currentPage === 1}
              className={`${
                currentPage === 1 ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'
              } relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md`}
            >
              Previous
            </button>
            <button
              onClick={() => setCurrentPage(Math.min(currentPage + 1, totalPages))}
              disabled={currentPage === totalPages}
              className={`${
                currentPage === totalPages ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'
              } ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md`}
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{(currentPage - 1) * itemsPerPage + 1}</span> to{' '}
                <span className="font-medium">
                  {Math.min(currentPage * itemsPerPage, sortedHistory.length)}
                </span>{' '}
                of <span className="font-medium">{sortedHistory.length}</span> results
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                {/* Previous page */}
                <button
                  onClick={() => setCurrentPage(Math.max(currentPage - 1, 1))}
                  disabled={currentPage === 1}
                  className={`${
                    currentPage === 1 ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-500 hover:bg-gray-50'
                  } relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium`}
                >
                  Previous
                </button>

                {/* Page numbers */}
                {[...Array(totalPages)].map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i + 1)}
                    className={`${
                      currentPage === i + 1
                        ? 'bg-indigo-50 border-indigo-500 text-indigo-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    } relative inline-flex items-center px-4 py-2 border text-sm font-medium`}
                  >
                    {i + 1}
                  </button>
                ))}

                {/* Next page */}
                <button
                  onClick={() => setCurrentPage(Math.min(currentPage + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className={`${
                    currentPage === totalPages ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-500 hover:bg-gray-50'
                  } relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium`}
                >
                  Next
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusHistoryView;
