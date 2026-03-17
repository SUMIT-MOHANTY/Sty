import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { format } from 'date-fns';
import applicationService, { Application, ApplicationStatus } from '../services/applicationService';
import StatusTimeline from '../components/StatusTimeline';
import Card from '../components/Card';
import Button from '../components/Button';
import DocumentUpload from '../components/DocumentUpload';

const ApplicationDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [applicationStatus, setApplicationStatus] = useState<ApplicationStatus | null>(null);
  const [activeTab, setActiveTab] = useState<'details' | 'documents' | 'status'>('details');

  useEffect(() => {
    const fetchApplicationStatus = async () => {
      try {
        setLoading(true);
        const data = await applicationService.getApplicationStatus(Number(id));
        setApplicationStatus(data);
        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load application status');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchApplicationStatus();
    }
  }, [id]);

  const formatStatus = (status: string): string => {
    return status
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'submitted': return 'text-blue-600 bg-blue-100';
      case 'document_verification': return 'text-purple-600 bg-purple-100';
      case 'background_check': return 'text-yellow-600 bg-yellow-100';
      case 'processing': return 'text-orange-600 bg-orange-100';
      case 'ready_for_pickup': return 'text-indigo-600 bg-indigo-100';
      case 'completed': return 'text-green-600 bg-green-100';
      case 'rejected': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

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
        <Link to="/applications" className="mt-4 text-primary hover:text-primary-dark">
          Back to Applications
        </Link>
      </div>
    );
  }

  if (!applicationStatus) {
    return (
      <div className="text-center py-10">
        <div className="text-lg">Application not found</div>
        <Link to="/applications" className="mt-4 text-primary hover:text-primary-dark">
          Back to Applications
        </Link>
      </div>
    );
  }

  const { application, status_history } = applicationStatus;

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Application Details</h1>
        <Link to="/applications">
          <Button variant="secondary">Back to Applications</Button>
        </Link>
      </div>

      <Card className="mb-6">
        <div className="flex flex-wrap md:flex-nowrap justify-between">
          <div>
            <h2 className="text-xl font-semibold">{application.application_type} Passport</h2>
            <p className="text-gray-500">Application #{application.application_number}</p>
            <p className="text-gray-500">
              Submitted on {format(new Date(application.submitted_at), 'MMMM d, yyyy')}
            </p>
          </div>
          <div className="mt-4 md:mt-0">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(application.status)}`}>
              {formatStatus(application.status)}
            </span>
          </div>
        </div>
      </Card>

      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('details')}
              className={`py-4 px-1 border-b-2 font-medium ${
                activeTab === 'details'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Details
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`py-4 px-1 border-b-2 font-medium ${
                activeTab === 'documents'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Documents
            </button>
            <button
              onClick={() => setActiveTab('status')}
              className={`py-4 px-1 border-b-2 font-medium ${
                activeTab === 'status'
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Status Timeline
            </button>
          </nav>
        </div>
      </div>

      {activeTab === 'details' && (
        <Card>
          <h3 className="text-lg font-medium mb-4">Application Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-500">Application Type</p>
              <p>{application.application_type}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Current Status</p>
              <p>{formatStatus(application.status)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Submitted Date</p>
              <p>{format(new Date(application.submitted_at), 'MMMM d, yyyy')}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Last Updated</p>
              <p>{format(new Date(application.last_updated_at), 'MMMM d, yyyy')}</p>
            </div>
            {application.notes && (
              <div className="col-span-2">
                <p className="text-sm text-gray-500">Notes</p>
                <p>{application.notes}</p>
              </div>
            )}
          </div>
        </Card>
      )}

      {activeTab === 'documents' && (
        <Card>
          <h3 className="text-lg font-medium mb-4">Documents</h3>
          <DocumentUpload applicationId={application.id} />
        </Card>
      )}

      {activeTab === 'status' && (
        <Card>
          <StatusTimeline
            statusHistory={status_history}
            currentStatus={application.status}
          />
        </Card>
      )}
    </div>
  );
};

export default ApplicationDetail;
