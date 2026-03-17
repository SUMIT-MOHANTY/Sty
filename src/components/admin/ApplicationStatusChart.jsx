import React from 'react';
import { Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const ApplicationStatusChart = ({ statistics }) => {
  const data = [
    { name: 'Pending Review', value: statistics.pendingReview, color: '#ff9800' },
    { name: 'Approved', value: statistics.approved, color: '#4caf50' },
    { name: 'Rejected', value: statistics.rejected, color: '#f44336' },
  ];

  return (
    <>
      <Typography variant="h6" gutterBottom component="div">
        Application Status Distribution
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={true}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => [`${value} applications`, 'Count']} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </>
  );
};

export default ApplicationStatusChart;
