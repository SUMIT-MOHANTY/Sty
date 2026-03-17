import { HistoryEntry } from '../types/historyTypes';
import { HistoryFilters } from '../components/history/HistoryFilter';

export const filterHistoryEntries = (entries: HistoryEntry[], filters: HistoryFilters): HistoryEntry[] => {
  return entries.filter(entry => {
    // Filter by search term
    if (filters.searchTerm && !entryMatchesSearchTerm(entry, filters.searchTerm)) {
      return false;
    }

    // Filter by date range
    if (filters.dateFrom && new Date(entry.timestamp) < new Date(filters.dateFrom)) {
      return false;
    }
    if (filters.dateTo) {
      const toDate = new Date(filters.dateTo);
      toDate.setHours(23, 59, 59, 999); // End of day
      if (new Date(entry.timestamp) > toDate) {
        return false;
      }
    }

    // Filter by status
    if (filters.status && filters.status.length > 0 && !filters.status.includes(entry.status)) {
      return false;
    }

    // Filter by category (assuming category is stored in metadata)
    if (filters.categories && filters.categories.length > 0 &&
        (!entry.metadata?.category || !filters.categories.includes(entry.metadata.category))) {
      return false;
    }

    return true;
  });
};

const entryMatchesSearchTerm = (entry: HistoryEntry, searchTerm: string): boolean => {
  const term = searchTerm.toLowerCase();

  // Check title and description
  if (entry.title.toLowerCase().includes(term) ||
      (entry.description && entry.description.toLowerCase().includes(term))) {
    return true;
  }

  // Check metadata values
  if (entry.metadata) {
    for (const value of Object.values(entry.metadata)) {
      if (String(value).toLowerCase().includes(term)) {
        return true;
      }
    }
  }

  return false;
};

export const groupHistoryEntriesByDate = (entries: HistoryEntry[]): Record<string, HistoryEntry[]> => {
  const groups: Record<string, HistoryEntry[]> = {};

  entries.forEach(entry => {
    const date = new Date(entry.timestamp);
    const dateString = date.toDateString();

    if (!groups[dateString]) {
      groups[dateString] = [];
    }

    groups[dateString].push(entry);
  });

  // Sort entries within each group by timestamp (newest first)
  Object.keys(groups).forEach(dateKey => {
    groups[dateKey].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  });

  return groups;
};
