import React from 'react';
import { ApplicationStatus } from '../../types/status';
import {
  CheckCircleIcon,
  ClockIcon,
  DocumentSearchIcon,
  ExclamationCircleIcon,
  DocumentAddIcon
} from '@heroicons/react/solid';

interface StatusBadgeProps {
  status: ApplicationStatus;
  className?: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'submitted':
        return {
          label: 'Submitted',
          bgColor: 'bg-blue-100',
          textColor: 'text-blue-800',
          borderColor: 'border-blue-200',
          icon: <DocumentAddIcon className="w-4 h-4 mr-1" />
        };
      case 'under_review':
        return {
          label: 'Under Review',
          bgColor: 'bg-yellow-100',
          textColor: 'text-yellow-800',
          borderColor: 'border-yellow-200',
          icon: <DocumentSearchIcon className="w-4 h-4 mr-1" />
        };
      case 'approved':
        return {
          label: 'Approved',
          bgColor: 'bg-green-100',
          textColor: 'text-green-800',
          borderColor: 'border-green-200',
          icon: <CheckCircleIcon className="w-4 h-4 mr-1" />
        };
      case 'rejected':
        return {
          label: 'Rejected',
          bgColor: 'bg-red-100',
          textColor: 'text-red-800',
          borderColor: 'border-red-200',
          icon: <ExclamationCircleIcon className="w-4 h-4 mr-1" />
        };
      case 'pending_documents':
        return {
          label: 'Pending Documents',
          bgColor: 'bg-orange-100',
          textColor: 'text-orange-800',
          borderColor: 'border-orange-200',
          icon: <ClockIcon className="w-4 h-4 mr-1" />
        };
      default:
        return {
          label: 'Unknown',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
          borderColor: 'border-gray-200',
          icon: <ClockIcon className="w-4 h-4 mr-1" />
        };
    }
  };

  const config = getStatusConfig();

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
        ${config.bgColor} ${config.textColor} border ${config.borderColor} ${className}`}
    >
      {config.icon}
      {config.label}
    </span>
  );
};

export default StatusBadge;
