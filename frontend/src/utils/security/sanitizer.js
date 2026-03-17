/**
 * Security utilities to prevent XSS and injection attacks
 */
export const sanitizeInput = (input) => {
  if (!input) return '';

  // Basic HTML entity encoding to prevent XSS
  return String(input)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
};

export const sanitizeAppointmentData = (appointment) => {
  if (!appointment) return {};

  return {
    ...appointment,
    title: sanitizeInput(appointment.title),
    patientName: sanitizeInput(appointment.patientName),
    doctorName: sanitizeInput(appointment.doctorName),
    notes: sanitizeInput(appointment.notes),
    // Keep date and time as is since they're typically not vulnerable to XSS
  };
};
