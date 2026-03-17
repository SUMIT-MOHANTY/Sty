import React from 'react';
import { format } from 'date-fns';

interface StatusUpdate {
  id: number;
  status: string;
  comment: string;
  created_at: string;
  created_by: number;
}

interface StatusTimelineProps {
  statusHistory: StatusUpdate[];
  currentStatus: string;
}

const StatusTimeline: React.FC<StatusTimelineProps> = ({ statusHistory, currentStatus }) => {
  const formatStatus = (status: string): string => {
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'submitted':
        return 'bg-blue-500';
      case 'document_verification':
        return 'bg-purple-500';
      case 'background_check':
        return 'bg-yellow-500';
      case 'processing':
        return 'bg-orange-500';
      case 'ready_for_pickup':
        return 'bg-indigo-500';
      case 'completed':
        return 'bg-green-500';
      case 'rejected':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="mt-4">
      <h2 className="text-xl font-bold mb-4">Application Status</h2>
      <div className="relative">
        <div className="absolute left-5 top-0 bottom-0 w-1 bg-gray-200"></div>
        <div className="space-y-6">
          {statusHistory.map((update, index) => (
            <div key={update.id} className="flex items-start">
              <div className={`relative z-10 mr-4 h-10 w-10 flex-shrink-0 flex items-center justify-center rounded-full ${getStatusColor(update.status)}`}>
                <svg className="h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="flex-grow bg-white p-4 rounded-lg shadow">
                <div className="flex justify-between">
                  <h3 className="font-medium text-lg">{formatStatus(update.status)}</h3>
                  <p className="text-sm text-gray-500">
                    {format(new Date(update.created_at), 'MMM d, yyyy h:mm a')}
                  </p>
                </div>
                {update.comment && <p className="text-gray-600 mt-1">{update.comment}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default StatusTimeline;
