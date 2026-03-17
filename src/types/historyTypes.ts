import { StatusType } from '../components/status/StatusIndicator';

export interface HistoryEntry {
  id: string;
  title: string;
  status: StatusType;
  timestamp: string;
  description?: string;
  user?: string;
  metadata?: Record<string, any>;
  actions?: HistoryAction[];
}

export interface HistoryAction {
  label: string;
  handler: () => void;
  primary?: boolean;
  disabled?: boolean;
}
