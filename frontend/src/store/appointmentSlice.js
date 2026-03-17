import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { addCsrfHeader } from '../utils/security/csrfProtection';

// Async thunks with security headers
export const fetchAppointments = createAsyncThunk(
  'appointments/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/appointments', {
        headers: addCsrfHeader({
          'Content-Type': 'application/json'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch appointments');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      // Log error for monitoring but return generic message to user
      console.error('Appointment fetch error:', error);
      return rejectWithValue('Unable to load appointments');
    }
  }
);

export const fetchAppointmentById = createAsyncThunk(
  'appointments/fetchById',
  async (id, { rejectWithValue }) => {
    try {
      // Validate ID is numeric to prevent injection
      if (!/^\d+$/.test(id)) {
        throw new Error('Invalid appointment ID');
      }

      const response = await fetch(`/api/appointments/${id}`, {
        headers: addCsrfHeader({
          'Content-Type': 'application/json'
        })
      });

      if (!response.ok) {
        const status = response.status;
        if (status === 403) {
          throw new Error('Access denied');
        } else if (status === 404) {
          throw new Error('Appointment not found');
        }
        throw new Error('Failed to fetch appointment');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Appointment detail fetch error:', error);
      return rejectWithValue(error.message || 'Unable to load appointment');
    }
  }
);

export const createAppointment = createAsyncThunk(
  'appointments/create',
  async (appointmentData, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/appointments', {
        method: 'POST',
        headers: addCsrfHeader({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify(appointmentData)
      });

      if (!response.ok) {
        const status = response.status;
        if (status === 400) {
          // Handle validation errors
          const data = await response.json();
          throw new Error(data.message || 'Invalid appointment data');
        } else if (status === 403) {
          throw new Error('Permission denied');
        }
        throw new Error('Failed to create appointment');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Appointment creation error:', error);
      return rejectWithValue(error.message || 'Unable to create appointment');
    }
  }
);

export const updateAppointment = createAsyncThunk(
  'appointments/update',
  async ({ id, ...appointmentData }, { rejectWithValue }) => {
    try {
      // Validate ID is numeric to prevent injection
      if (!/^\d+$/.test(id)) {
        throw new Error('Invalid appointment ID');
      }

      const response = await fetch(`/api/appointments/${id}`, {
        method: 'PUT',
        headers: addCsrfHeader({
          'Content-Type': 'application/json'
        }),
        body: JSON.stringify(appointmentData)
      });

      if (!response.ok) {
        const status = response.status;
        if (status === 400) {
          const data = await response.json();
          throw new Error(data.message || 'Invalid appointment data');
        } else if (status === 403) {
          throw new Error('Permission denied');
        } else if (status === 404) {
          throw new Error('Appointment not found');
        }
        throw new Error('Failed to update appointment');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Appointment update error:', error);
      return rejectWithValue(error.message || 'Unable to update appointment');
    }
  }
);

export const deleteAppointment = createAsyncThunk(
  'appointments/delete',
  async (id, { rejectWithValue }) => {
    try {
      // Validate ID is numeric to prevent injection
      if (!/^\d+$/.test(id)) {
        throw new Error('Invalid appointment ID');
      }

      const response = await fetch(`/api/appointments/${id}`, {
        method: 'DELETE',
        headers: addCsrfHeader()
      });

      if (!response.ok) {
        const status = response.status;
        if (status === 403) {
          throw new Error('Permission denied');
        } else if (status === 404) {
          throw new Error('Appointment not found');
        }
        throw new Error('Failed to delete appointment');
      }

      return { id };
    } catch (error) {
      console.error('Appointment deletion error:', error);
      return rejectWithValue(error.message || 'Unable to delete appointment');
    }
  }
);

const appointmentSlice = createSlice({
  name: 'appointments',
  initialState: {
    appointments: [],
    currentAppointment: null,
    loading: false,
    error: null
  },
  reducers: {
    clearAppointmentErrors: (state) => {
      state.error = null;
    },
    clearCurrentAppointment: (state) => {
      state.currentAppointment = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch all appointments
      .addCase(fetchAppointments.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAppointments.fulfilled, (state, action) => {
        state.loading = false;
        state.appointments = action.payload;
      })
      .addCase(fetchAppointments.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch appointments';
      })

      // Fetch appointment by ID
      .addCase(fetchAppointmentById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAppointmentById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentAppointment = action.payload;
      })
      .addCase(fetchAppointmentById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch appointment';
      })

      // Create appointment
      .addCase(createAppointment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createAppointment.fulfilled, (state, action) => {
        state.loading = false;
        state.appointments.push(action.payload);
      })
      .addCase(createAppointment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to create appointment';
      })

      // Update appointment
      .addCase(updateAppointment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateAppointment.fulfilled, (state, action) => {
        state.loading = false;
        state.currentAppointment = action.payload;
        state.appointments = state.appointments.map(app =>
          app.id === action.payload.id ? action.payload : app
        );
      })
      .addCase(updateAppointment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update appointment';
      })

      // Delete appointment
      .addCase(deleteAppointment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteAppointment.fulfilled, (state, action) => {
        state.loading = false;
        state.appointments = state.appointments.filter(
          app => app.id !== action.payload.id
        );
      })
      .addCase(deleteAppointment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete appointment';
      });
  }
});

export const { clearAppointmentErrors, clearCurrentAppointment } = appointmentSlice.actions;
export default appointmentSlice.reducer;
