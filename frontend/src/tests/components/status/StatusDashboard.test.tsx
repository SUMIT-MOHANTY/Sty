import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import StatusDashboard from '../../../components/status/StatusDashboard';
import useStatusPolling from '../../../hooks/useStatusPolling';
import '@testing-library/jest-dom';

// Mock the hook
jest.mock('../../../hooks/useStatusPolling', () => ({
  __esModule: true,
  default: jest.fn(),
}));

describe('StatusDashboard Component', () => {
  // Helper to render within Router
  const renderWithRouter = (ui: React.ReactElement) => {
    return render(<BrowserRouter>{ui}</BrowserRouter>);
  };

  it('renders loading state correctly', () => {
    (useStatusPolling as jest.Mock).mockReturnValue({
      status: null,
      isLoading: true,
      error: null,
      refreshStatus: jest.fn(),
    });

    renderWithRouter(<StatusDashboard applicationId="123" />);

    // Check for loading indicators
    const loadingElements = document.querySelectorAll('.animate-pulse');
    expect(loadingElements.length).toBeGreaterThan(0);
  });

  it('renders error state correctly', () => {
    const mockRefresh = jest.fn();
    (useStatusPolling as jest.Mock).mockReturnValue({
      status: null,
      isLoading: false,
      error: new Error('Failed to load status'),
      refreshStatus: mockRefresh,
    });

    renderWithRouter(<StatusDashboard applicationId="123" />);

    expect(screen.getByText('Error loading status')).toBeInTheDocument();
    expect(screen.getByText('Failed to load status')).toBeInTheDocument();

    // Test refresh button
    fireEvent.click(screen.getByText('Retry'));
    expect(mockRefresh).toHaveBeenCalledTimes(1);
  });

  it('renders status information correctly', () => {
    (useStatusPolling as jest.Mock).mockReturnValue({
      status: {
        application_id: '123',
        current_status: 'under_review',
        last_updated: '2023-05-17T09:45:00Z',
        estimated_completion_date: '2023-06-01T00:00:00Z',
      },
      isLoading: false,
      error: null,
      refreshStatus: jest.fn(),
    });

    renderWithRouter(<StatusDashboard applicationId="123" />);

    expect(screen.getByText('Under Review')).toBeInTheDocument();
    expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
    expect(screen.getByText(/Estimated completion:/)).toBeInTheDocument();
    expect(screen.getByText('View complete history')).toBeInTheDocument();
  });

  it('handles refresh button click', () => {
    const mockRefresh = jest.fn();
    (useStatusPolling as jest.Mock).mockReturnValue({
      status: {
        application_id: '123',
        current_status: 'under_review',
        last_updated: '2023-05-17T09:45:00Z',
        estimated_completion_date: '2023-06-01T00:00:00Z',
      },
      isLoading: false,
      error: null,
      refreshStatus: mockRefresh,
    });

    renderWithRouter(<StatusDashboard applicationId="123" />);

    fireEvent.click(screen.getByText('Refresh'));
    expect(mockRefresh).toHaveBeenCalledTimes(1);
  });

  it('renders without estimated completion date', () => {
    (useStatusPolling as jest.Mock).mockReturnValue({
      status: {
        application_id: '123',
        current_status: 'submitted',
        last_updated: '2023-05-17T09:45:00Z',
        estimated_completion_date: null,
      },
      isLoading: false,
      error: null,
      refreshStatus: jest.fn(),
    });

    renderWithRouter(<StatusDashboard applicationId="123" />);

    expect(screen.getByText('Submitted')).toBeInTheDocument();
    expect(screen.queryByText(/Estimated completion:/)).not.toBeInTheDocument();
  });
});
