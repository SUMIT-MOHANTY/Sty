import React from 'react';
import { HistoryEntry } from '../../types/historyTypes';
import StatusIndicator from '../status/StatusIndicator';
import '../../styles/HistoryDetail.css';

interface HistoryDetailProps {
  entry: HistoryEntry;
  onClose?: () => void;
}

const HistoryDetail: React.FC<HistoryDetailProps> = ({
  entry,
  onClose,
}) => {
  return (
    <div className="history-detail">
      <div className="detail-header">
        <h2>{entry.title}</h2>
        {onClose && (
          <button className="close-button" onClick={onClose}></button>
        )}
      </div>

      <div className="detail-meta">
        <StatusIndicator status={entry.status} label={entry.status} />
        <div className="detail-timestamp">
          <span className="timestamp-label">When:</span>
          <time dateTime={new Date(entry.timestamp).toISOString()}>
            {new Date(entry.timestamp).toLocaleString()}
          </time>
        </div>
        {entry.user && (
          <div className="detail-user">
            <span className="user-label">By:</span>
            <span>{entry.user}</span>
          </div>
        )}
      </div>

      {entry.description && (
        <div className="detail-description">
          <h3>Description</h3>
          <p>{entry.description}</p>
        </div>
      )}

      {entry.metadata && Object.keys(entry.metadata).length > 0 && (
        <div className="detail-metadata">
          <h3>Additional Information</h3>
          <div className="metadata-table">
            {Object.entries(entry.metadata).map(([key, value]) => (
              <div key={key} className="metadata-row">
                <div className="metadata-key">{key}</div>
                <div className="metadata-value">
                  {typeof value === 'object'
                    ? JSON.stringify(value, null, 2)
                    : String(value)
                  }
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {entry.actions && entry.actions.length > 0 && (
        <div className="detail-actions">
          <h3>Actions</h3>
          <div className="action-buttons">
            {entry.actions.map((action) => (
              <button
                key={action.label}
                className={`action-button ${action.primary ? 'primary' : 'secondary'}`}
                onClick={action.handler}
                disabled={action.disabled}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryDetail;
