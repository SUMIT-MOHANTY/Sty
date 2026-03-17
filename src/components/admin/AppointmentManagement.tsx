import "./AppointmentManagement.css";
import React, { useState } from 'react';
import AppointmentSlotManager from './AppointmentSlotManager';
import AppointmentList from './AppointmentList';

const AppointmentManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'slots' | 'appointments'>('appointments');

  return (
    <div className="appointment-management">
      <div className="admin-header">
        <h1>Appointment Management</h1>
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'appointments' ? 'active' : ''}`}
            onClick={() => setActiveTab('appointments')}
          >
            View Appointments
          </button>
          <button
            className={`tab ${activeTab === 'slots' ? 'active' : ''}`}
            onClick={() => setActiveTab('slots')}
          >
            Manage Slots
          </button>
        </div>
      </div>

      <div className="admin-content">
        {activeTab === 'appointments' && <AppointmentList />}
        {activeTab === 'slots' && <AppointmentSlotManager />}
      </div>
    </div>
  );
};

export default AppointmentManagement;
