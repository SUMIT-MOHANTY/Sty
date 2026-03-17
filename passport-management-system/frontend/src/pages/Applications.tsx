import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import applicationService, { Application } from '../services/applicationService';
import Card from '../components/Card';
import Button from '../components/Button';
import ApplicationTable from '../components/ApplicationTable';

const Applications: React.FC = () => {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        const data = await applicationService.getApplications();
        setApplications(data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load applications');
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="text-center py-10">
          <div className="text-red-500 text-lg">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 text-primary hover:text-primary-dark"
          >
            Try again
          </button>
        </div>
      );
    }

    if (applications.length === 0) {
      return (
        <div className="text-center py-10">
          <h3 className="text-lg font-medium mb-2">No applications found</h3>
          <p className="text-gray-500 mb-6">Start your passport application process now.</p>
          <Link to="/applications/new">
            <Button>New Application</Button>
          </Link>
        </div>
      );
    }

    return <ApplicationTable applications={applications} />;
  };

  return (
    <div className="container mx-auto p-4">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">My Applications</h1>
        <Link to="/applications/new">
          <Button>New Application</Button>
        </Link>
      </div>

      <Card>{renderContent()}</Card>
    </div>
  );
};

export default Applications;
