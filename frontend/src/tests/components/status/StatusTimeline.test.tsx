import React from 'react';
import { render, screen } from '@testing-library/react';
import StatusTimeline from '../../../components/status/StatusTimeline';
import '@testing-library/jest-dom';

describe('StatusTimeline Component', () => {
  it('renders all status steps', () => {
    render(<StatusTimeline currentStatus="submitted" />);
    expect(screen.getByText('Submitted')).toBeInTheDocument();
    expect(screen.getByText('Under Review')).toBeInTheDocument();
    expect(screen.getByText('Documents Required')).toBeInTheDocument();
    expect(screen.getByText('Approved')).toBeInTheDocument();
  });

  it('highlights current status correctly for submitted', () => {
    const { container } = render(<StatusTimeline currentStatus="submitted" />);
    const currentStatusCircle = container.querySelector('.bg-blue-500');
    expect(currentStatusCircle).toBeInTheDocument();
  });

  it('highlights current status correctly for under_review', () => {
    const { container } = render(<StatusTimeline currentStatus="under_review" />);
    // First status should be completed (green) and second should be current (blue)
    const completedCircles = container.querySelectorAll('.bg-green-500');
    const currentCircle = container.querySelector('.bg-blue-500');
    expect(completedCircles.length).toBe(1);
    expect(currentCircle).toBeInTheDocument();
  });

  it('shows rejected status when applicable', () => {
    const { container } = render(<StatusTimeline currentStatus="rejected" />);
    expect(screen.getByText('Rejected')).toBeInTheDocument();
    const rejectionCircle = container.querySelector('.bg-red-500');
    expect(rejectionCircle).toBeInTheDocument();
  });
});
