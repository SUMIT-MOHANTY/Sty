import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Paper, TableContainer, Table, TableHead,
  TableRow, TableCell, TableBody, TablePagination, Button,
  TextField, MenuItem, Select, InputLabel, FormControl,
  Chip, IconButton, Tooltip
} from '@mui/material';
import { Search, FilterList, Visibility, Edit } from '@mui/icons-material';
import { fetchApplications } from '../../services/adminService';
import { useNavigate } from 'react-router-dom';

const statusColors = {
  'submitted': '#3498db',
  'in_review': '#f39c12',
  'pending_documents': '#e74c3c',
  'approved': '#2ecc71',
  'rejected': '#e74c3c'
};

const ApplicationsList = () => {
  const navigate = useNavigate();
  const [applications, setApplications] = useState([]);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalCount, setTotalCount] = useState(0);
  const [filters, setFilters] = useState({
    status: '',
    search: '',
    dateFrom: '',
    dateTo: ''
  });

  useEffect(() => {
    const loadApplications = async () => {
      try {
        const result = await fetchApplications({
          page: page + 1,
          limit: rowsPerPage,
          ...filters
        });

        setApplications(result.applications);
        setTotalCount(result.totalCount);
      } catch (error) {
        console.error("Failed to load applications:", error);
      }
    };

    loadApplications();
  }, [page, rowsPerPage, filters]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
    setPage(0);
  };

  const viewApplication = (id) => {
    navigate(`/admin/applications/${id}`);
  };

  const editApplication = (id) => {
    navigate(`/admin/applications/${id}/edit`);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom component="h1">
        Passport Applications
      </Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 2 }}>
          <TextField
            label="Search by Name or ID"
            name="search"
            value={filters.search}
            onChange={handleFilterChange}
            size="small"
            sx={{ minWidth: 200 }}
            InputProps={{
              endAdornment: <Search />
            }}
          />

          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status</InputLabel>
            <Select
              name="status"
              value={filters.status}
              label="Status"
              onChange={handleFilterChange}
            >
              <MenuItem value="">All</MenuItem>
              <MenuItem value="submitted">Submitted</MenuItem>
              <MenuItem value="in_review">In Review</MenuItem>
              <MenuItem value="pending_documents">Pending Documents</MenuItem>
              <MenuItem value="approved">Approved</MenuItem>
              <MenuItem value="rejected">Rejected</MenuItem>
            </Select>
          </FormControl>

          <TextField
            label="From Date"
            type="date"
            name="dateFrom"
            value={filters.dateFrom}
            onChange={handleFilterChange}
            size="small"
            InputLabelProps={{ shrink: true }}
          />

          <TextField
            label="To Date"
            type="date"
            name="dateTo"
            value={filters.dateTo}
            onChange={handleFilterChange}
            size="small"
            InputLabelProps={{ shrink: true }}
          />
        </Box>
      </Paper>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Application ID</TableCell>
                <TableCell>Applicant Name</TableCell>
                <TableCell>Submission Date</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Actions</TableCell>
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
                      sx={{
                        bgcolor: statusColors[app.status] || '#999',
                        color: 'white'
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Tooltip title="View Details">
                        <IconButton onClick={() => viewApplication(app.id)}>
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Application">
                        <IconButton onClick={() => editApplication(app.id)}>
                          <Edit />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))}
              {applications.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    No applications found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={totalCount}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[10, 25, 50, 100]}
        />
      </Paper>
    </Box>
  );
};

export default ApplicationsList;
