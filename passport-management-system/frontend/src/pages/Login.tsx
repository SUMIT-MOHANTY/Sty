import React from 'react';
import { Link } from 'react-router-dom';
import LoginForm from '../components/LoginForm';
import Card from '../components/Card';

const Login: React.FC = () => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md px-4">
        <h1 className="text-3xl font-bold text-center mb-6 text-blue-800">
          Passport Management System
        </h1>

        <Card>
          <h2 className="text-2xl font-semibold mb-6 text-center">Login</h2>
          <LoginForm />

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-blue-600 hover:underline">
                Register here
              </Link>
            </p>
            <p className="text-sm text-gray-600 mt-2">
              <Link to="/forgot-password" className="text-blue-600 hover:underline">
                Forgot password?
              </Link>
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Login;
