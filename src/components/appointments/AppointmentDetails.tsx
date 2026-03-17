import React from 'react';
import { Appointment } from '../../types/appointment';
import { formatDate } from '../../utils/date';

interface AppointmentDetailsProps {
  appointment: Appointment;
}

export const AppointmentDetails: React.FC<AppointmentDetailsProps> = ({ appointment }) => {
  return (
    <div className="space-y-4">
      <div className="border-b pb-4">
        <h3 className="text-lg font-medium">Appointment Information</h3>
        <div className="grid grid-cols-2 gap-4 mt-2">
          <div>
            <p className="text-sm font-medium text-gray-500">Reference Number</p>
            <p>{appointment.id}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Status</p>
            <p className="capitalize">{appointment.status}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Date</p>
            <p>{formatDate(appointment.date)}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Time</p>
            <p>{appointment.time}</p>
          </div>
        </div>
      </div>

      <div className="border-b pb-4">
        <h3 className="text-lg font-medium">Location</h3>
        <div className="mt-2">
          <p className="font-medium">{appointment.location.name}</p>
          <p>{appointment.location.address}</p>
          <p>{appointment.location.city}, {appointment.location.state} {appointment.location.zipCode}</p>
          {appointment.location.instructions && (
            <div className="mt-2">
              <p className="text-sm font-medium text-gray-500">Special Instructions</p>
              <p className="text-sm">{appointment.location.instructions}</p>
            </div>
          )}
        </div>
      </div>

      {appointment.application && (
        <div>
          <h3 className="text-lg font-medium">Related Application</h3>
          <div className="mt-2">
            <p><span className="font-medium">Application ID:</span> {appointment.application.id}</p>
            <p><span className="font-medium">Type:</span> {appointment.application.type}</p>
            <p><span className="font-medium">Status:</span> {appointment.application.status}</p>
          </div>
        </div>
      )}
    </div>
  );
};
