/**
 * Authentication and authorization utilities
 */

export const hasAppointmentAccess = (appointment, user) => {
  if (!user || !appointment) return false;

  // Admin has access to all appointments
  if (user.role === 'admin') return true;

  // Doctors can see their own appointments
  if (user.role === 'doctor' && appointment.doctorId === user.id) return true;

  // Patients can see only their own appointments
  if (user.role === 'patient' && appointment.patientId === user.id) return true;

  // Staff might have limited access
  if (user.role === 'staff') {
    // Staff might be restricted to certain departments
    if (user.departments && user.departments.includes(appointment.departmentId)) {
      return true;
    }
  }

  return false;
};
