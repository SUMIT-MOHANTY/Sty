import React from 'react';
import StatusCard from './StatusCard';
import { StatusInfo } from '../../types/statusTypes';
import '../../styles/StatusOverview.css';

interface StatusOverviewProps {
  statuses: StatusInfo[];
  title?: string;
  showTimestamp?: boolean;
  onStatusClick?: (status: StatusInfo) => void;
}

const StatusOverview: React.FC<StatusOverviewProps> = ({
  statuses,
  title = 'System Status',
  showTimestamp = true,
  onStatusClick,
}) => {
  return (
    <div className="status-overview">
      <h2 className="status-overview-title">{title}</h2>

      <div className="status-summary">
        <span>Total: {statuses.length}</span>
        <span>Success: {statuses.filter(s => s.status === 'success').length}</span>
        <span>Warning: {statuses.filter(s => s.status === 'warning').length}</span>
        <span>Error: {statuses.filter(s => s.status === 'error').length}</span>
        <span>Pending: {statuses.filter(s => s.status === 'pending').length}</span>
      </div>

      <div className="status-cards">
        {statuses.map((statusInfo) => (
          <StatusCard
            key={statusInfo.id}
            title={statusInfo.title}
            status={statusInfo.status}
            description={statusInfo.description}
            timestamp={showTimestamp ? statusInfo.timestamp : undefined}
            details={statusInfo.details}
            onAction={onStatusClick ? () => onStatusClick(statusInfo) : undefined}
          />
        ))}
      </div>
    </div>
  );
};

export default StatusOverview;
