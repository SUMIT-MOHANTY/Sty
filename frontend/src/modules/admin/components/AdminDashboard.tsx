import React, { useState } from 'react';
import { AdminApplications } from './AdminApplications';
import { AdminUsers } from './AdminUsers';
import { AdminSettings } from './AdminSettings';

type DashboardTab = 'applications' | 'users' | 'settings';

export const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<DashboardTab>('applications');

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>

        <div className="admin-nav">
          <button
            className={`admin-nav-item ${activeTab === 'applications' ? 'active' : ''}`}
            onClick={() => setActiveTab('applications')}
          >
            Applications
          </button>
          <button
            className={`admin-nav-item ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
          >
            Users
          </button>
          <button
            className={`admin-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            System Settings
          </button>
        </div>
      </div>

      <div className="admin-content">
        {activeTab === 'applications' && <AdminApplications />}
        {activeTab === 'users' && <AdminUsers />}
        {activeTab === 'settings' && <AdminSettings />}
      </div>
    </div>
  );
};
