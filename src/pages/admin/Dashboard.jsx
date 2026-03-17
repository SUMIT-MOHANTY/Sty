import React, { useState, useEffect } from 'react';
import { Box, Typography, Grid, Paper, Container } from '@mui/material';
import ApplicationStatusChart from '../../components/admin/ApplicationStatusChart';
import RecentApplicationsTable from '../../components/admin/RecentApplicationsTable';
import StatisticCard from '../../components/admin/StatisticCard';
import { fetchDashboardStatistics } from '../../services/adminService';

const AdminDashboard = () => {
  const [statistics, setStatistics] = useState({
    totalApplications: 0,
    pendingReview: 0,
    approved: 0,
    rejected: 0,
    recentApplications: []
  });

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const data = await fetchDashboardStatistics();
        setStatistics(data);
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      }
    };

    loadDashboardData();
  }, []);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom component="h1">
        Admin Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Summary statistics */}
        <Grid item xs={12} md={3}>
          <StatisticCard
            title="Total Applications"
            value={statistics.totalApplications}
            icon="description"
            color="#3f51b5"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatisticCard
            title="Pending Review"
            value={statistics.pendingReview}
            icon="hourglass_empty"
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatisticCard
            title="Approved"
            value={statistics.approved}
            icon="check_circle"
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <StatisticCard
            title="Rejected"
            value={statistics.rejected}
            icon="cancel"
            color="#f44336"
          />
        </Grid>

        {/* Chart */}
        <Grid item xs={12} md={8}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              flexDirection: 'column',
              height: 340,
            }}
          >
            <ApplicationStatusChart statistics={statistics} />
          </Paper>
        </Grid>

        {/* Recent Applications */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom component="div">
              Recent Applications
            </Typography>
            <RecentApplicationsTable applications={statistics.recentApplications} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AdminDashboard;
