import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import FormInput from './FormInput';
import Button from './Button';

const LoginForm: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [formErrors, setFormErrors] = useState({
    email: '',
    password: '',
  });

  const { login, isLoading, error } = useAuth();

  const validateForm = (): boolean => {
    let isValid = true;
    const errors = {
      email: '',
      password: '',
    };

    // Email validation
    if (!formData.email) {
      errors.email = 'Email is required';
      isValid = false;
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
      isValid = false;
    }

    // Password validation
    if (!formData.password) {
      errors.password = 'Password is required';
      isValid = false;
    }

    setFormErrors(errors);
    return isValid;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      await login(formData.email, formData.password);
    } catch (err) {
      // Error is handled by the AuthContext
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 text-red-700 p-3 rounded-md text-sm">
          {error}
        </div>
      )}

      <FormInput
        label="Email"
        name="email"
        type="email"
        value={formData.email}
        onChange={handleChange}
        error={formErrors.email}
        placeholder="your.email@example.com"
        required
      />

      <FormInput
        label="Password"
        name="password"
        type="password"
        value={formData.password}
        onChange={handleChange}
        error={formErrors.password}
        required
      />

      <div className="pt-2">
        <Button
          type="submit"
          isLoading={isLoading}
          fullWidth
        >
          Login
        </Button>
      </div>
    </form>
  );
};

export default LoginForm;
