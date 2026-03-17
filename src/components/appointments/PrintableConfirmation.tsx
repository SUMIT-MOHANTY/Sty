import React, { useRef } from 'react';
import { Appointment } from '../../types/appointment';
import { Button } from '../Button';

interface PrintableConfirmationProps {
  appointment: Appointment;
  onClose: () => void;
}

const PrintableConfirmation: React.FC<PrintableConfirmationProps> = ({
  appointment,
  onClose
}) => {
  const printRef = useRef<HTMLDivElement>(null);

  const handlePrint = () => {
    const printContent = printRef.current;
    if (!printContent) return;

    const originalContents = document.body.innerHTML;
    const printStyles = `
      <style>
        @media print {
          body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
          .print-header { text-align: center; margin-bottom: 20px; border-bottom: 1px solid #000; padding-bottom: 10px; }
          .print-section { margin-bottom: 15px; }
          .print-section h3 { margin-bottom: 5px; }
          .print-details p { margin: 3px 0; }
          .print-qr { text-align: center; margin: 20px 0; }
          .print-footer { text-align: center; margin-top: 30px; font-size: 0.9em; border-top: 1px solid #000; padding-top: 10px; }
          .no-print { display: none !important; }
        }
      </style>
    `;

    document.body.innerHTML = printStyles + printContent.outerHTML;
    window.print();
    document.body.innerHTML = originalContents;
  };

  const formatDate = (dateStr: string): string => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Generate a simple QR code representation (just for display purposes)
  const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=APPT-${appointment.id}`;

  return (
    <div className="printable-confirmation p-6">
      <div className="no-print flex justify-between mb-6">
        <h2 className="text-2xl font-bold">Appointment Confirmation</h2>
        <div className="flex gap-3">
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
          <Button variant="primary" onClick={handlePrint}>
            Print
          </Button>
        </div>
      </div>

      <div ref={printRef} className="print-content">
        <div className="print-header">
          <h1>Passport Appointment Confirmation</h1>
          <p>Appointment ID: {appointment.id}</p>
        </div>

        <div className="print-section">
          <h3 className="font-bold">Appointment Details</h3>
          <div className="print-details">
            <p><strong>Date:</strong> {formatDate(appointment.appointment_date)}</p>
            <p><strong>Time:</strong> {appointment.appointment_time}</p>
            <p><strong>Status:</strong> {appointment.status.charAt(0).toUpperCase() + appointment.status.slice(1)}</p>
          </div>
        </div>

        <div className="print-section">
          <h3 className="font-bold">Location</h3>
          <div className="print-details">
            <p>{appointment.location.name}</p>
            <p>{appointment.location.address}</p>
            <p>{appointment.location.city}, {appointment.location.state} {appointment.location.postal_code}</p>
          </div>
        </div>

        <div className="print-section">
          <h3 className="font-bold">Required Documents</h3>
          <div className="print-details">
            <ul>
              <li>Valid government-issued photo ID</li>
              <li>Proof of citizenship (birth certificate or naturalization certificate)</li>
              <li>Passport photo (2"x2")</li>
              <li>Completed application form</li>
              <li>Application fee payment receipt</li>
            </ul>
            <p className="mt-3 text-sm"><em>Please ensure you bring all required documents to your appointment.</em></p>
          </div>
        </div>

        <div className="print-qr">
          <img src={qrCodeUrl} alt="Appointment QR Code" width="150" height="150" />
          <p>Scan this QR code at the check-in desk</p>
        </div>

        <div className="print-footer">
          <p>For questions or changes, please call 1-800-555-0123</p>
          <p>This confirmation was printed on {new Date().toLocaleDateString()}</p>
        </div>
      </div>
    </div>
  );
};

export default PrintableConfirmation;
