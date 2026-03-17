import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import AppointmentList from '../../../components/appointments/AppointmentList';
import { useApi } from '../../../hooks/useApi';

// Mock the useApi hook
jest.mock('../../../hooks/useApi');

const mockAppointments = [
  {
    id: 'appt-1',
    user_id: 'user-1',
    appointment_date: '2023-10-15',
    appointment_time: '10:30',
    location_id: 'loc-1',
    status: 'scheduled',
    created_at: '2023-09-01T12:00:00Z',
    updated_at: '2023-09-01T12:00:00Z',
    location: {
      id: 'loc-1',
      name: 'Downtown Passport Office',
      address: '123 Main St',
      city: 'Anytown',
      state: 'NY',
      postal_code: '10001'
    }
  },
  {
    id: 'appt-2',
    user_id: 'user-1',
    appointment_date: '2023-09-10',
    appointment_time: '14:15',
    location_id: 'loc-2',
    status: 'completed',
    created_at: '2023-08-15T10:00:00Z',
    updated_at: '2023-09-10T15:00:00Z',
    location: {
      id: 'loc-2',
      name: 'Midtown Passport Center',
      address: '456 Fifth Ave',
      city: 'Anytown',
      state: 'NY',
      postal_code: '10022'
    }
  }
];

describe('AppointmentList', () => {
  beforeEach(() => {
    (useApi as jest.Mock).mockReturnValue({
      get: jest.fn().mockResolvedValue(mockAppointments)
    });
  });

  it('renders loading state initially', () => {
    render(<AppointmentList onSelectAppointment={() => {}} />);
    expect(screen.getByText('Loading appointments...')).toBeInTheDocument();
  });

  it('renders appointments after loading', async () => {
    render(<AppointmentList onSelectAppointment={() => {}} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading appointments...')).not.toBeInTheDocument();
    });

    expect(screen.getByText('Downtown Passport Office')).toBeInTheDocument();
    expect(screen.getByText('Midtown Passport Center')).toBeInTheDocument();
  });

  it('filters appointments by status', async () => {
    render(<AppointmentList onSelectAppointment={() => {}} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading appointments...')).not.toBeInTheDocument();
    });

    // Both appointments should be visible initially
    expect(screen.getByText('Downtown Passport Office')).toBeInTheDocument();
    expect(screen.getByText('Midtown Passport Center')).toBeInTheDocument();

    // Filter to show only completed appointments
    fireEvent.change(screen.getByLabelText('Filter by status:'), { target: { value: 'completed' } });

    // Now only the completed appointment should be visible
    expect(screen.queryByText('Downtown Passport Office')).not.toBeInTheDocument();
    expect(screen.getByText('Midtown Passport Center')).toBeInTheDocument();
  });

  it('calls onSelectAppointment when View Details button is clicked', async () => {
    const mockSelectFn = jest.fn();
    render(<AppointmentList onSelectAppointment={mockSelectFn} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading appointments...')).not.toBeInTheDocument();
    });

    const viewDetailsButtons = screen.getAllByText('View Details');
    fireEvent.click(viewDetailsButtons[0]);

    expect(mockSelectFn).toHaveBeenCalledWith(mockAppointments[0]);
  });
});
