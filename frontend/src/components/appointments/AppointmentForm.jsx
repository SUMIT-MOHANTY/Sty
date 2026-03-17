import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchAppointmentById, createAppointment, updateAppointment } from '../../store/appointmentSlice';
import { getCsrfToken } from '../../utils/security/csrfProtection';
import { hasAppointmentAccess } from '../../utils/security/authChecks';

const AppointmentForm = () => {
  const { appointmentId } = useParams();
  const isEditing = Boolean(appointmentId);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { currentAppointment, loading, error } = useSelector(state => state.appointments);
  const user = useSelector(state => state.auth.user);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    date: '',
    time: '',
    patientId: '',
    patientName: '',
    doctorId: '',
    doctorName: '',
    notes: '',
  });

  // Validation state
  const [errors, setErrors] = useState({});

  // Load appointment data if editing
  useEffect(() => {
    if (isEditing) {
      // Validate ID format to prevent injection
      if (!/^\d+$/.test(appointmentId)) {
        navigate('/not-found');
        return;
      }

      dispatch(fetchAppointmentById(appointmentId));
    }
  }, [isEditing, appointmentId, dispatch, navigate]);

  // Populate form with appointment data when loaded
  useEffect(() => {
    if (isEditing && currentAppointment) {
      // Check access before showing form
      if (!hasAppointmentAccess(currentAppointment, user)) {
        navigate('/forbidden');
        return;
      }

      setFormData({
        title: currentAppointment.title || '',
        date: currentAppointment.date || '',
        time: currentAppointment.time || '',
        patientId: currentAppointment.patientId || '',
        patientName: currentAppointment.patientName || '',
        doctorId: currentAppointment.doctorId || '',
        doctorName: currentAppointment.doctorName || '',
        notes: currentAppointment.notes || '',
      });
    }
  }, [isEditing, currentAppointment, user, navigate]);

  // Input validation function
  const validateForm = () => {
    const newErrors = {};

    // Required fields
    if (!formData.title.trim()) newErrors.title = 'Title is required';
    if (!formData.date) newErrors.date = 'Date is required';
    if (!formData.time) newErrors.time = 'Time is required';
    if (!formData.patientId) newErrors.patientId = 'Patient is required';
    if (!formData.doctorId) newErrors.doctorId = 'Doctor is required';

    // Date validation
    const selectedDate = new Date(formData.date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (selectedDate < today) {
      newErrors.date = 'Appointment date cannot be in the past';
    }

    // Title length check
    if (formData.title.length > 100) {
      newErrors.title = 'Title cannot exceed 100 characters';
    }

    // Notes length check
    if (formData.notes.length > 1000) {
      newErrors.notes = 'Notes cannot exceed 1000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    // Maximum input lengths to prevent buffer overflows
    const maxLengths = {
      title: 100,
      notes: 1000,
      patientName: 100,
      doctorName: 100
    };

    // Truncate input if it exceeds max length
    const truncatedValue = maxLengths[name] && value.length > maxLengths[name]
      ? value.slice(0, maxLengths[name])
      : value;

    setFormData(prev => ({ ...prev, [name]: truncatedValue }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    // Add CSRF token
    const csrfToken = getCsrfToken();

    try {
      if (isEditing) {
        await dispatch(updateAppointment({
          id: appointmentId,
          ...formData,
          _csrf: csrfToken
        }));
      } else {
        await dispatch(createAppointment({
          ...formData,
          _csrf: csrfToken
        }));
      }

      // Redirect on success
      navigate('/appointments');
    } catch (err) {
      // Error already handled by redux
    }
  };

  // Check if user is authenticated
  if (!user) {
    return <div className="error-message">Please log in to manage appointments</div>;
  }

  // Check if user has permission to create appointments
  if (!isEditing && user.role !== 'admin' && user.role !== 'doctor' && user.role !== 'staff') {
    return <div className="error-message">You don't have permission to create appointments</div>;
  }

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="appointment-form">
      <h2>{isEditing ? 'Edit Appointment' : 'Create New Appointment'}</h2>
      {error && <div className="error-message">An error occurred. Please try again later.</div>}

      <form onSubmit={handleSubmit} noValidate>
        <input type="hidden" name="_csrf" value={getCsrfToken()} />

        <div className="form-group">
          <label htmlFor="title">Title *</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            maxLength={100}
            className={errors.title ? 'error' : ''}
          />
          {errors.title && <div className="error-text">{errors.title}</div>}
        </div>

        {/* Date and time fields */}
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="date">Date *</label>
            <input
              type="date"
              id="date"
              name="date"
              value={formData.date}
              onChange={handleChange}
              className={errors.date ? 'error' : ''}
            />
            {errors.date && <div className="error-text">{errors.date}</div>}
          </div>

          <div className="form-group">
            <label htmlFor="time">Time *</label>
            <input
              type="time"
              id="time"
              name="time"
              value={formData.time}
              onChange={handleChange}
              className={errors.time ? 'error' : ''}
            />
            {errors.time && <div className="error-text">{errors.time}</div>}
          </div>
        </div>

        {/* Patient and doctor selection fields would go here */}
        {/* For brevity, simplified to just IDs */}

        <div className="form-group">
          <label htmlFor="notes">Notes</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            maxLength={1000}
            className={errors.notes ? 'error' : ''}
          />
          {errors.notes && <div className="error-text">{errors.notes}</div>}
        </div>

        <div className="form-actions">
          <button type="button" onClick={() => navigate('/appointments')}>
            Cancel
          </button>
          <button type="submit" className="primary">
            {isEditing ? 'Update Appointment' : 'Create Appointment'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AppointmentForm;
