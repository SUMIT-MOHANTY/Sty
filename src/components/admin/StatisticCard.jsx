import React from 'react';
import { Paper, Typography, Box, Icon } from '@mui/material';

const StatisticCard = ({ title, value, icon, color }) => {
  return (
    <Paper
      sx={{
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        height: 140,
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: -10,
          right: -10,
          width: 80,
          height: 80,
          borderRadius: '50%',
          backgroundColor: color,
          opacity: 0.2,
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center'
        }}
      >
        <Icon sx={{ fontSize: 40, color: 'white', opacity: 0.8 }}>{icon}</Icon>
      </Box>
      <Typography component="h2" variant="h6" color="text.secondary" gutterBottom>
        {title}
      </Typography>
      <Typography component="p" variant="h3">
        {value}
      </Typography>
    </Paper>
  );
};

export default StatisticCard;
