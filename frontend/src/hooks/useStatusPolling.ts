import { useState, useEffect, useCallback, useRef } from 'react';
import { ApplicationStatusResponse, ApplicationHistoryResponse } from '../types/status';

interface UseStatusPollingOptions {
  pollingInterval?: number; // in milliseconds
  initialFetch?: boolean;
}

/**
 * Custom hook for polling application status data at regular intervals
 * @param applicationId - The ID of the application to poll
 * @param options - Configuration options for polling
 */
export const useStatusPolling = (
  applicationId: string | null,
  options: UseStatusPollingOptions = {}
) => {
  const { pollingInterval = 30000, initialFetch = true } = options;

  const [status, setStatus] = useState<ApplicationStatusResponse | null>(null);
  const [history, setHistory] = useState<ApplicationHistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(initialFetch);
  const [error, setError] = useState<Error | null>(null);

  // Use a ref to store the latest applicationId to avoid dependency issues
  const applicationIdRef = useRef(applicationId);

  // Update the ref when applicationId changes
  useEffect(() => {
    applicationIdRef.current = applicationId;
  }, [applicationId]);

  // Fetch status data
  const fetchStatus = useCallback(async () => {
    // Skip if no application ID is provided
    if (!applicationIdRef.current) {
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);

      // Fetch current status
      const statusResponse = await fetch(`/api/applications/${applicationIdRef.current}`);
      if (!statusResponse.ok) {
        throw new Error(`Status fetch failed: ${statusResponse.statusText}`);
      }
      const statusData = await statusResponse.json();
      setStatus(statusData);

      // Fetch history
      const historyResponse = await fetch(`/api/applications/${applicationIdRef.current}/history`);
      if (!historyResponse.ok) {
        throw new Error(`History fetch failed: ${historyResponse.statusText}`);
      }
      const historyData = await historyResponse.json();
      setHistory(historyData);

    } catch (err) {
      setError(err instanceof Error ? err : new Error('An unknown error occurred'));
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Set up polling
  useEffect(() => {
    // Initial fetch if requested
    if (initialFetch) {
      fetchStatus();
    }

    // Set up polling interval
    const intervalId = setInterval(fetchStatus, pollingInterval);

    // Clean up on unmount or when dependencies change
    return () => {
      clearInterval(intervalId);
    };
  }, [fetchStatus, pollingInterval, initialFetch]);

  // Function to manually trigger a refresh
  const refreshStatus = useCallback(() => {
    fetchStatus();
  }, [fetchStatus]);

  return {
    status,
    history,
    isLoading,
    error,
    refreshStatus,
  };
};

export default useStatusPolling;
