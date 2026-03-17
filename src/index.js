const app = require('./app');
const mongoose = require('mongoose');
const config = require('./config/config');

// Handle uncaught exceptions
process.on('uncaughtException', (err) => {
  console.log('UNCAUGHT EXCEPTION!  Shutting down...');
  console.log(err.name, err.message);
  process.exit(1);
});

// Connect to MongoDB
mongoose
  .connect(config.mongodb.url, config.mongodb.options)
  .then(() => {
    console.log('Connected to MongoDB');

    // Start server
    const server = app.listen(config.port, () => {
      console.log(`Server running on port ${config.port}...`);
    });

    // Handle unhandled rejections
    process.on('unhandledRejection', (err) => {
      console.log('UNHANDLED REJECTION!  Shutting down...');
      console.log(err.name, err.message);
      server.close(() => {
        process.exit(1);
      });
    });

    // Handle SIGTERM
    process.on('SIGTERM', () => {
      console.log(' SIGTERM RECEIVED. Shutting down gracefully');
      server.close(() => {
        console.log(' Process terminated!');
      });
    });
  })
  .catch((err) => {
    console.error('MongoDB connection error:', err);
    process.exit(1);
  });
