import { createBrowserRouter, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import VerifyEmail from './pages/VerifyEmail';
import Dashboard from './pages/Dashboard';
import ApplicationForm from './pages/ApplicationForm';
import Applications from './pages/Applications';
import ApplicationDetail from './pages/ApplicationDetail';
import AppointmentBooking from './pages/AppointmentBooking';
import AppointmentDetails from './pages/AppointmentDetails';
import NotFound from './pages/NotFound';
import { ProtectedRoute } from './components/ProtectedRoute';

const routes = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" replace />,
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/register',
    element: <Register />,
  },
  {
    path: '/verify-email',
    element: <VerifyEmail />,
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    ),
  },
  {
    path: '/applications/new',
    element: (
      <ProtectedRoute>
        <ApplicationForm />
      </ProtectedRoute>
    ),
  },
  {
    path: '/applications',
    element: (
      <ProtectedRoute>
        <Applications />
      </ProtectedRoute>
    ),
  },
  {
    path: '/applications/:id',
    element: (
      <ProtectedRoute>
        <ApplicationDetail />
      </ProtectedRoute>
    ),
  },
  {
    path: '/appointments/book',
    element: (
      <ProtectedRoute>
        <AppointmentBooking />
      </ProtectedRoute>
    ),
  },
  {
    path: '/appointments/:id',
    element: (
      <ProtectedRoute>
        <AppointmentDetails />
      </ProtectedRoute>
    ),
  },
  {
    path: '*',
    element: <NotFound />,
  },
]);

export default routes;
