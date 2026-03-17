import React from 'react';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { TextField, Button, Box, Typography, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/authService';

const RegisterSchema = Yup.object().shape({
  fullName: Yup.string().required('Full name is required'),
  email: Yup.string().email('Invalid email').required('Email is required'),
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .matches(/[a-zA-Z]/, 'Password must contain at least one letter')
    .matches(/[0-9]/, 'Password must contain at least one number')
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password'), null], 'Passwords must match')
    .required('Confirm password is required')
});

const RegisterForm = () => {
  const navigate = useNavigate();
  const [error, setError] = React.useState(null);

  return (
    <Box sx={{ maxWidth: 500, mx: 'auto', p: 2 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Create Account
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        Create an account to apply for a passport and track your application.
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Formik
        initialValues={{
          fullName: '',
          email: '',
          password: '',
          confirmPassword: ''
        }}
        validationSchema={RegisterSchema}
        onSubmit={async (values, { setSubmitting }) => {
          try {
            setError(null);
            await authService.register(values);
            navigate('/register-success');
          } catch (err) {
            setError(err.response?.data?.message || 'Failed to register. Please try again.');
          } finally {
            setSubmitting(false);
          }
        }}
      >
        {({ isSubmitting, errors, touched }) => (
          <Form>
            <Field
              as={TextField}
              fullWidth
              margin="normal"
              name="fullName"
              label="Full Name"
              error={touched.fullName && Boolean(errors.fullName)}
              helperText={touched.fullName && errors.fullName}
            />

            <Field
              as={TextField}
              fullWidth
              margin="normal"
              name="email"
              label="Email Address"
              type="email"
              error={touched.email && Boolean(errors.email)}
              helperText={touched.email && errors.email}
            />

            <Field
              as={TextField}
              fullWidth
              margin="normal"
              name="password"
              label="Password"
              type="password"
              error={touched.password && Boolean(errors.password)}
              helperText={touched.password && errors.password}
            />

            <Field
              as={TextField}
              fullWidth
              margin="normal"
              name="confirmPassword"
              label="Confirm Password"
              type="password"
              error={touched.confirmPassword && Boolean(errors.confirmPassword)}
              helperText={touched.confirmPassword && errors.confirmPassword}
            />

            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              sx={{ mt: 3, mb: 2 }}
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Registering...' : 'Register'}
            </Button>

            <Box sx={{ textAlign: 'center', mt: 1 }}>
              <Typography variant="body2">
                Already have an account?{' '}
                <Button
                  variant="text"
                  onClick={() => navigate('/login')}
                  sx={{ p: 0, minWidth: 'auto', verticalAlign: 'baseline' }}
                >
                  Log In
                </Button>
              </Typography>
            </Box>
          </Form>
        )}
      </Formik>
    </Box>
  );
};

export default RegisterForm;
