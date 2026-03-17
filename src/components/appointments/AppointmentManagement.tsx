import React, { useState } from 'react';
import AppointmentList from './AppointmentList';
import AppointmentDetails from './AppointmentDetails';
import RescheduleAppointment from './RescheduleAppointment';
import CancelAppointmentModal from './CancelAppointmentModal';
import AppointmentReminders from './AppointmentReminders';
import PrintableConfirmation from './PrintableConfirmation';
import { Appointment } from '../../types/appointment';

enum ViewState {
  LIST,
  DETAILS,
  RESCHEDULE,
  REMINDERS,
  PRINT
}

const AppointmentManagement: React.FC = () => {
  const [viewState, setViewState] = useState<ViewState>(ViewState.LIST);
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [isCancelModalOpen, setIsCancelModalOpen] = useState<boolean>(false);

  const handleAppointmentSelect = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setViewState(ViewState.DETAILS);
  };

  const handleRescheduleClick = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setViewState(ViewState.RESCHEDULE);
  };

  const handleCancelClick = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setIsCancelModalOpen(true);
  };

  const handleRemindersClick = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setViewState(ViewState.REMINDERS);
  };

  const handlePrintClick = (appointment: Appointment) => {
    setSelectedAppointment(appointment);
    setViewState(ViewState.PRINT);
  };

  const handleRescheduleSuccess = (updatedAppointment: Appointment) => {
    setSelectedAppointment(updatedAppointment);
    setViewState(ViewState.DETAILS);
  };

  const handleCancelSuccess = () => {
    setIsCancelModalOpen(false);
    setViewState(ViewState.LIST); // Go back to list after cancellation
    setSelectedAppointment(null);
  };

  const renderContent = () => {
    switch (viewState) {
      case ViewState.LIST:
        return (
          <AppointmentList onSelectAppointment={handleAppointmentSelect} />
        );
      case ViewState.DETAILS:
        return selectedAppointment ? (
          <AppointmentDetails
            appointmentId={selectedAppointment.id}
            onClose={() => setViewState(ViewState.LIST)}
            onReschedule={handleRescheduleClick}
            onCancel={handleCancelClick}
            onPrint={handlePrintClick}
          />
        ) : null;
      case ViewState.RESCHEDULE:
        return selectedAppointment ? (
          <RescheduleAppointment
            appointment={selectedAppointment}
            onSuccess={handleRescheduleSuccess}
            onCancel={() => setViewState(ViewState.DETAILS)}
          />
        ) : null;
      case ViewState.REMINDERS:
        return selectedAppointment ? (
          <AppointmentReminders
            appointmentId={selectedAppointment.id}
            onClose={() => setViewState(ViewState.DETAILS)}
          />
        ) : null;
      case ViewState.PRINT:
        return selectedAppointment ? (
          <PrintableConfirmation
            appointment={selectedAppointment}
            onClose={() => setViewState(ViewState.DETAILS)}
          />
        ) : null;
      default:
        return null;
    }
  };

  return (
    <div className="appointment-management">
      {renderContent()}

      {selectedAppointment && (
        <CancelAppointmentModal
          appointment={selectedAppointment}
          isOpen={isCancelModalOpen}
          onClose={() => setIsCancelModalOpen(false)}
          onSuccess={handleCancelSuccess}
        />
      )}
    </div>
  );
};

export default AppointmentManagement;
