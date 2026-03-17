/**
 * Audit logging for appointment-related actions
 */
const fs = require('fs');
const path = require('path');

// Log directory should be configurable through environment variables
const LOG_DIR = process.env.LOG_DIR || path.join(__dirname, '..', 'logs');

// Ensure log directory exists
if (!fs.existsSync(LOG_DIR)) {
  fs.mkdirSync(LOG_DIR, { recursive: true });
}

const LOG_FILE = path.join(LOG_DIR, 'appointment_audit.log');

const logAppointmentAction = (action, userId, appointmentData) => {
  const timestamp = new Date().toISOString();
  const appointmentId = appointmentData.id || 'new';

  // Redact sensitive information from logs
  const safeData = { ...appointmentData };

  // Remove any potentially sensitive fields
  if (safeData.notes) {
    safeData.notes = '[REDACTED]';
  }

  const logEntry = {
    timestamp,
    action,
    appointmentId,
    userId,
    changes: safeData
  };

  const logLine = JSON.stringify(logEntry) + '\n';

  // Asynchronously write to log file
  fs.appendFile(LOG_FILE, logLine, (err) => {
    if (err) {
      console.error('Error writing to audit log:', err);
    }
  });

  // If we have a centralized logging system, we'd also send it there
  // centralLogger.log('appointment_audit', logEntry);
};

module.exports = {
  logAppointmentAction
};
