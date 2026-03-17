import React from 'react';
import { render, screen } from '@testing-library/react';
import StatusBadge from '../../../components/status/StatusBadge';
import '@testing-library/jest-dom';

describe('StatusBadge Component', () => {
  it('renders submitted status correctly', () => {
    render(<StatusBadge status="submitted" />);
    expect(screen.getByText('Submitted')).toBeInTheDocument();
  });

  it('renders under_review status correctly', () => {
    render(<StatusBadge status="under_review" />);
    expect(screen.getByText('Under Review')).toBeInTheDocument();
  });

  it('renders approved status correctly', () => {
    render(<StatusBadge status="approved" />);
    expect(screen.getByText('Approved')).toBeInTheDocument();
  });

  it('renders rejected status correctly', () => {
    render(<StatusBadge status="rejected" />);
    expect(screen.getByText('Rejected')).toBeInTheDocument();
  });

  it('renders pending_documents status correctly', () => {
    render(<StatusBadge status="pending_documents" />);
    expect(screen.getByText('Pending Documents')).toBeInTheDocument();
  });

  it('applies custom class names', () => {
    render(<StatusBadge status="approved" className="custom-class" />);
    const badge = screen.getByText('Approved').parentElement;
    expect(badge).toHaveClass('custom-class');
  });
});
