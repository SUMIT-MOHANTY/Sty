import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { CheckCircle } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const RegisterSuccess = () => {
  const navigate = useNavigate();

  return (
    <Box
      sx={{
        maxWidth: 600,
        mx: 'auto',
        p: 4,
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}
    >
      <CheckCircle sx={{ fontSize: 80, color: 'success.main', mb: 2 }} />
      <Typography variant="h4" component="h1" gutterBottom>
        Registration Successful!
      </Typography>
      <Typography variant="body1" sx={{ mb: 3 }}>
        Your account has been created successfully. Please check your email to verify your account before logging in.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        onClick={() => navigate('/login')}
        sx={{ mt: 2 }}
      >
        Log In
      </Button>
    </Box>
  );
};

export default RegisterSuccess;
