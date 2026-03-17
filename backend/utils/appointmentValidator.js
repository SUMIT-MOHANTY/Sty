/**
 * Validation utilities for appointment data
 */
const validateAppointment = (data) => {
  const errors = {};

  // Required fields
  if (!data.title || data.title.trim() === '') {
    errors.title = 'Title is required';
  }

  if (!data.date) {
    errors.date = 'Date is required';
  }

  if (!data.time) {
    errors.time = 'Time is required';
  }

  if (!data.patientId) {
    errors.patientId = 'Patient ID is required';
  }

  if (!data.doctorId) {
    errors.doctorId = 'Doctor ID is required';
  }

  // Format validations
  if (data.title && data.title.length > 100) {
    errors.title = 'Title cannot exceed 100 characters';
  }

  if (data.notes && data.notes.length > 1000) {
    errors.notes = 'Notes cannot exceed 1000 characters';
  }

  // Date validation
  if (data.date) {
    try {
      const appointmentDate = new Date(data.date);
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      if (appointmentDate < today) {
        errors.date = 'Appointment date cannot be in the past';
      }
    } catch (e) {
      errors.date = 'Invalid date format';
    }
  }

  // Time validation
  if (data.time && !/^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/.test(data.time)) {
    errors.time = 'Invalid time format';
  }

  // ID validations
  if (data.patientId && !/^\d+$/.test(data.patientId)) {
    errors.patientId = 'Invalid patient ID';
  }

  if (data.doctorId && !/^\d+$/.test(data.doctorId)) {
    errors.doctorId = 'Invalid doctor ID';
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
};

// Sanitize input before storing in database
const sanitizeAppointmentData = (data) => {
  const sanitized = { ...data };

  // Trim strings and limit lengths
  if (sanitized.title) {
    sanitized.title = sanitized.title.trim().substring(0, 100);
  }

  if (sanitized.notes) {
    sanitized.notes = sanitized.notes.trim().substring(0, 1000);
  }

  return sanitized;
};

module.exports = {
  validateAppointment,
  sanitizeAppointmentData
};
