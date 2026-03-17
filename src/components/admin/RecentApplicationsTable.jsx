import React from 'react';
import {
  Table, TableBody, TableCell, TableHead, TableRow, Chip,
  Box, Typography, Button
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const statusColors = {
  'submitted': '#3498db',
  'in_review': '#f39c12',
  'pending_documents': '#e74c3c',
  'approved': '#2ecc71',
  'rejected': '#e74c3c'
};

const RecentApplicationsTable = ({ applications }) => {
  const navigate = useNavigate();

  if (!applications || applications.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No recent applications
        </Typography>
      </Box>
    );
  }

  const viewApplication = (id) => {
    navigate(`/admin/applications/${id}`);
  };

  return (
    <Table size="small">
      <TableHead>
        <TableRow>
          <TableCell>Application ID</TableCell>
          <TableCell>Name</TableCell>
          <TableCell>Submission Date</TableCell>
          <TableCell>Status</TableCell>
          <TableCell align="right">Action</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {applications.map((app) => (
          <TableRow key={app.id} hover>
            <TableCell>{app.id}</TableCell>
            <TableCell>{app.applicantName}</TableCell>
            <TableCell>{new Date(app.submissionDate).toLocaleDateString()}</TableCell>
            <TableCell>
              <Chip
                label={app.status.replace('_', ' ').toUpperCase()}
                size="small"
                sx={{
                  bgcolor: statusColors[app.status] || '#999',
                  color: 'white'
                }}
              />
            </TableCell>
            <TableCell align="right">
              <Button
                size="small"
                variant="outlined"
                onClick={() => viewApplication(app.id)}
              >
                View
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};

export default RecentApplicationsTable;
