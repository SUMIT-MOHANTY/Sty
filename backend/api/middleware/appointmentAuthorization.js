/**
 * Middleware to check authorization for appointment-related actions
 */
const appointmentAuth = (req, res, next) => {
  // User must be authenticated
  if (!req.user) {
    return res.status(401).json({ message: 'Authentication required' });
  }

  const appointmentId = parseInt(req.params.id);
  const { user } = req;

  // For GET/POST routes without specific ID
  if (!appointmentId) {
    // For creation, check if user has permission to create appointments
    if (req.method === 'POST') {
      if (['admin', 'doctor', 'staff'].includes(user.role)) {
        return next();
      }
      return res.status(403).json({ message: 'Permission denied to create appointments' });
    }

    // For GET all, we filter in the controller
    return next();
  }

  // For specific appointment actions (GET, PUT, DELETE)
  // Load the appointment first
  req.db.getAppointment(appointmentId)
    .then(appointment => {
      if (!appointment) {
        return res.status(404).json({ message: 'Appointment not found' });
      }

      // Check authorization
      let authorized = false;

      // Admin has full access
      if (user.role === 'admin') {
        authorized = true;
      }
      // Doctors can see/edit their own appointments
      else if (user.role === 'doctor' && appointment.doctorId === user.id) {
        authorized = true;
      }
      // Patients can only see their own appointments
      else if (user.role === 'patient' && appointment.patientId === user.id) {
        // Patients can only view, not modify
        if (req.method === 'GET') {
          authorized = true;
        }
      }
      // Staff might have department-based restrictions
      else if (user.role === 'staff') {
        if (user.departments && user.departments.includes(appointment.departmentId)) {
          authorized = true;
        }
      }

      if (!authorized) {
        return res.status(403).json({ message: 'Permission denied' });
      }

      // Store appointment for use in the route handler
      req.appointment = appointment;
      next();
    })
    .catch(error => {
      console.error('Authorization error:', error);
      res.status(500).json({ message: 'Internal server error' });
    });
};

module.exports = appointmentAuth;
