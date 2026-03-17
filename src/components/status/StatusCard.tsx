import React from 'react';
import StatusIndicator, { StatusType } from './StatusIndicator';
import '../../styles/StatusCard.css';

interface StatusCardProps {
  title: string;
  status: StatusType;
  description?: string;
  timestamp?: string;
  details?: Record<string, any>;
  onAction?: () => void;
  actionLabel?: string;
}

const StatusCard: React.FC<StatusCardProps> = ({
  title,
  status,
  description,
  timestamp,
  details,
  onAction,
  actionLabel = 'View Details',
}) => {
  return (
    <div className={`status-card status-${status}`}>
      <div className="status-card-header">
        <h3 className="status-card-title">{title}</h3>
        <StatusIndicator status={status} />
      </div>

      {description && (
        <div className="status-card-description">{description}</div>
      )}

      {timestamp && (
        <div className="status-card-timestamp">
          <time dateTime={new Date(timestamp).toISOString()}>
            {new Date(timestamp).toLocaleString()}
          </time>
        </div>
      )}

      {details && Object.keys(details).length > 0 && (
        <div className="status-card-details">
          {Object.entries(details).map(([key, value]) => (
            <div key={key} className="status-detail-row">
              <span className="detail-key">{key}:</span>
              <span className="detail-value">{String(value)}</span>
            </div>
          ))}
        </div>
      )}

      {onAction && (
        <button className="status-card-action" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
};

export default StatusCard;
