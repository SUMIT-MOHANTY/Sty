import React from 'react';
import '../../styles/StatusIndicator.css';

export type StatusType = 'success' | 'error' | 'warning' | 'info' | 'pending';

interface StatusIndicatorProps {
  status: StatusType;
  label?: string;
  className?: string;
  animated?: boolean;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  status,
  label,
  className = '',
  animated = false,
}) => {
  return (
    <div className={`status-indicator ${status} ${className} ${animated ? 'animated' : ''}`}>
      <span className="status-dot"></span>
      {label && <span className="status-label">{label}</span>}
    </div>
  );
};

export default StatusIndicator;
