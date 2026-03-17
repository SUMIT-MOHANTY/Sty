/**
 * JWT Authentication Middleware
 * Validates JWT tokens and attaches user data to request
 */
const jwt = require('jsonwebtoken');
const config = require('../../config');
const { User } = require('../../models');

/**
 * Middleware to authenticate JWT tokens
 * @param {Object} req - Express request object
 * @param {Object} res - Express response object
 * @param {Function} next - Express next function
 */
const authenticateJWT = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
      return res.status(401).json({ message: 'Authorization header missing' });
    }

    const token = authHeader.split(' ')[1];

    if (!token) {
      return res.status(401).json({ message: 'Token missing' });
    }

    const decoded = jwt.verify(token, config.jwt.secret);

    // Get user from database to ensure they still exist and have proper roles
    const user = await User.findById(decoded.userId);

    if (!user) {
      return res.status(401).json({ message: 'User not found' });
    }

    // Attach user data to request for use in controllers
    req.user = {
      id: user._id,
      email: user.email,
      roles: user.roles
    };

    next();
  } catch (error) {
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ message: 'Token expired' });
    }

    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ message: 'Invalid token' });
    }

    return res.status(500).json({ message: 'Internal server error' });
  }
};

module.exports = authenticateJWT;
