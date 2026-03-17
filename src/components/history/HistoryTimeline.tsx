import React from 'react';
import { HistoryEntry } from '../../types/historyTypes';
import StatusIndicator from '../status/StatusIndicator';
import '../../styles/HistoryTimeline.css';

interface HistoryTimelineProps {
  entries: HistoryEntry[];
  title?: string;
  maxItems?: number;
  onEntryClick?: (entry: HistoryEntry) => void;
}

const HistoryTimeline: React.FC<HistoryTimelineProps> = ({
  entries,
  title = 'Activity History',
  maxItems,
  onEntryClick,
}) => {
  const displayEntries = maxItems ? entries.slice(0, maxItems) : entries;

  const formatTimeAgo = (timestamp: string): string => {
    const now = new Date();
    const date = new Date(timestamp);
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}d ago`;
    if (diffHours > 0) return `${diffHours}h ago`;
    if (diffMins > 0) return `${diffMins}m ago`;
    return 'Just now';
  };

  return (
    <div className="history-timeline">
      <h2 className="history-timeline-title">{title}</h2>

      <div className="timeline">
        {displayEntries.length === 0 ? (
          <div className="no-history">No history entries available</div>
        ) : (
          displayEntries.map((entry) => (
            <div
              key={entry.id}
              className={`timeline-item ${entry.status}`}
              onClick={() => onEntryClick && onEntryClick(entry)}
            >
              <div className="timeline-connector"></div>
              <div className="timeline-content">
                <div className="timeline-header">
                  <StatusIndicator status={entry.status} />
                  <h4 className="timeline-title">{entry.title}</h4>
                  <span className="timeline-time" title={new Date(entry.timestamp).toLocaleString()}>
                    {formatTimeAgo(entry.timestamp)}
                  </span>
                </div>
                {entry.description && (
                  <div className="timeline-description">{entry.description}</div>
                )}
                {entry.metadata && (
                  <div className="timeline-metadata">
                    {Object.entries(entry.metadata).map(([key, value]) => (
                      <span key={key} className="metadata-item">
                        {key}: {String(value)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {entries.length > (maxItems || 0) && (
          <div className="timeline-more">
            + {entries.length - (maxItems || 0)} more entries...
          </div>
        )}
      </div>
    </div>
  );
};

export default HistoryTimeline;
