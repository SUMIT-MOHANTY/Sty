/**
 * Application configuration
 */
module.exports = {
  port: process.env.PORT || 3000,
  database: {
    url: process.env.MONGODB_URI || 'mongodb://localhost:27017/app',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true
    }
  },
  jwt: {
    secret: process.env.JWT_SECRET || 'your-secret-key-change-in-production',
    expiresIn: process.env.JWT_EXPIRES_IN || '1d'
  }
};
