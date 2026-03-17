import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import StatusHistoryView from '../../../components/status/StatusHistoryView';
import '@testing-library/jest-dom';

describe('StatusHistoryView Component', () => {
  const mockHistoryData = {
    application_id: '123',
    history: [
      {
        status: 'submitted' as const,
        timestamp: '2023-05-15T10:30:00Z',
        message: 'Application submitted successfully',
        updated_by: 'System',
      },
      {
        status: 'under_review' as const,
        timestamp: '2023-05-16T14:22:00Z',
        message: 'Application is now under review',
        updated_by: 'Admin User',
      },
      {
        status: 'pending_documents' as const,
        timestamp: '2023-05-17T09:45:00Z',
        message: 'Additional documents required',
        updated_by: 'John Smith',
      },
      {
        status: 'under_review' as const,
        timestamp: '2023-05-18T11:15:00Z',
        message: 'Documents received, review resumed',
        updated_by: 'Admin User',
      },
      {
        status: 'approved' as const,
        timestamp: '2023-05-19T16:30:00Z',
        message: 'Application approved',
        updated_by: 'Jane Doe',
      },
    ],
  };

  it('renders loading state correctly', () => {
    render(<StatusHistoryView historyData={null} isLoading={true} error={null} />);
    expect(screen.getByTestId('loading')).toBeInTheDocument();
  });

  it('renders error state correctly', () => {
    render(
      <StatusHistoryView
        historyData={null}
        isLoading={false}
        error={new Error('Failed to load history')}
      />
    );
    expect(screen.getByText('Error loading history')).toBeInTheDocument();
    expect(screen.getByText('Failed to load history')).toBeInTheDocument();
  });

  it('renders empty state when no history', () => {
    render(
      <StatusHistoryView
        historyData={{ application_id: '123', history: [] }}
        isLoading={false}
        error={null}
      />
    );
    expect(screen.getByText('No history available for this application.')).toBeInTheDocument();
  });

  it('renders history items correctly', () => {
    render(
      <StatusHistoryView
        historyData={mockHistoryData}
        isLoading={false}
        error={null}
      />
    );

    expect(screen.getByText('Application Status History')).toBeInTheDocument();
    expect(screen.getByText('Application submitted successfully')).toBeInTheDocument();
    expect(screen.getByText('Application approved')).toBeInTheDocument();
    expect(screen.getByText('Updated by System')).toBeInTheDocument();
    expect(screen.getByText('Updated by Jane Doe')).toBeInTheDocument();
  });

  it('handles pagination correctly when there are more items than per page', () => {
    render(
      <StatusHistoryView
        historyData={mockHistoryData}
        isLoading={false}
        error={null}
      />
    );

    // First page should show first 5 items
    expect(screen.getByText('Application Status History')).toBeInTheDocument();

    // Check pagination
    const paginationButtons = screen.getAllByRole('button', { name: /[1-5]/ });
    expect(paginationButtons.length).toBeGreaterThanOrEqual(1);
  });
});
