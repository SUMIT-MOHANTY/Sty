import { StatusType } from '../components/status/StatusIndicator';

export interface StatusInfo {
  id: string;
  title: string;
  status: StatusType;
  timestamp: string;
  description?: string;
  details?: Record<string, any>;
}
