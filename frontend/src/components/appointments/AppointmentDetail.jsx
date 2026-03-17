import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { fetchAppointmentById } from '../../store/appointmentSlice';
import { sanitizeAppointmentData } from '../../utils/security/sanitizer';
import { hasAppointmentAccess } from '../../utils/security/authChecks';

const AppointmentDetail = () => {
  const { appointmentId } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { currentAppointment, loading, error } = useSelector(state => state.appointments);
  const user = useSelector(state => state.auth.user);
  const [hasAccess, setHasAccess] = useState(false);

  // Validate appointment ID is a number to prevent injection
  useEffect(() => {
    if (!/^\d+$/.test(appointmentId)) {
      navigate('/not-found');
      return;
    }

    dispatch(fetchAppointmentById(appointmentId));
  }, [appointmentId, dispatch, navigate]);

  // Check access rights after appointment is loaded
  useEffect(() => {
    if (currentAppointment) {
      const accessGranted = hasAppointmentAccess(currentAppointment, user);
      setHasAccess(accessGranted);

      // If no access, redirect to forbidden page
      if (!accessGranted) {
        navigate('/forbidden');
      }
    }
  }, [currentAppointment, user, navigate]);

  if (loading) return <div className="loading">Loading appointment details...</div>;

  if (error) {
    // Generic error to prevent information leakage
    return <div className="error-message">Unable to load appointment details. Please try again later.</div>;
  }

  if (!currentAppointment || !hasAccess) {
    return null; // Will redirect in useEffect
  }

  // Sanitize data before displaying
  const safeAppointment = sanitizeAppointmentData(currentAppointment);

  return (
    <div className="appointment-detail">
      <h2>Appointment Details</h2>
      <div className="detail-container">
        <div className="detail-row">
          <span className="label">Title:</span>
          <span className="value">{safeAppointment.title}</span>
        </div>
        <div className="detail-row">
          <span className="label">Date:</span>
          <span className="value">{safeAppointment.date}</span>
        </div>
        <div className="detail-row">
          <span className="label">Time:</span>
          <span className="value">{safeAppointment.time}</span>
        </div>
        <div className="detail-row">
          <span className="label">Patient:</span>
          <span className="value">{safeAppointment.patientName}</span>
        </div>
        <div className="detail-row">
          <span className="label">Doctor:</span>
          <span className="value">{safeAppointment.doctorName}</span>
        </div>
        <div className="detail-row">
          <span className="label">Notes:</span>
          <div className="value notes">{safeAppointment.notes}</div>
        </div>
      </div>
    </div>
  );
};

export default AppointmentDetail;
