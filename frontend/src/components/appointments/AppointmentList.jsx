import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchAppointments } from '../../store/appointmentSlice';
import { sanitizeAppointmentData } from '../../utils/security/sanitizer';
import { hasAppointmentAccess } from '../../utils/security/authChecks';
import { addCsrfHeader } from '../../utils/security/csrfProtection';

const AppointmentList = () => {
  const dispatch = useDispatch();
  const { appointments, loading, error } = useSelector(state => state.appointments);
  const user = useSelector(state => state.auth.user);

  useEffect(() => {
    // Only fetch if user is authenticated
    if (user && user.id) {
      dispatch(fetchAppointments());
    }
  }, [dispatch, user]);

  // Filter appointments based on user role and permissions
  const filteredAppointments = appointments.filter(appt =>
    hasAppointmentAccess(appt, user)
  ).map(appt => sanitizeAppointmentData(appt));

  if (!user) {
    return <div className="error-message">Please log in to view appointments</div>;
  }

  if (loading) return <div className="loading">Loading appointments...</div>;

  if (error) {
    // Generic error message to prevent data leakage
    return <div className="error-message">Unable to load appointments. Please try again later.</div>;
  }

  return (
    <div className="appointment-list">
      <h2>Your Appointments</h2>
      {filteredAppointments.length === 0 ? (
        <p>No appointments found.</p>
      ) : (
        <ul>
          {filteredAppointments.map(appointment => (
            <li key={appointment.id} className="appointment-item">
              <div className="appointment-title">{appointment.title}</div>
              <div className="appointment-details">
                <span>Date: {appointment.date}</span>
                <span>Time: {appointment.time}</span>
                <span>Patient: {appointment.patientName}</span>
                <span>Doctor: {appointment.doctorName}</span>
              </div>
              {/* Only show edit/delete buttons if user has permission */}
              {user.role === 'admin' || appointment.doctorId === user.id ? (
                <div className="appointment-actions">
                  <button onClick={() => /* handle with CSRF protection */ {}}>Edit</button>
                  <button onClick={() => /* handle with CSRF protection */ {}}>Delete</button>
                </div>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AppointmentList;
