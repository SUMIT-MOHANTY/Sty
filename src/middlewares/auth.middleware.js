const jwt = require('jsonwebtoken');
const { StatusCodes } = require('http-status-codes');
const { UnauthorizedError, ForbiddenError } = require('../errors');
const User = require('../models/user.model');
const config = require('../config/config');

/**
 * Authenticate user from JWT token
 */
const authenticate = async (req, res, next) => {
  // Check header
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    throw new UnauthorizedError('Authentication invalid');
  }

  const token = authHeader.split(' ')[1];

  try {
    const payload = jwt.verify(token, config.jwt.secret);

    // Attach user to request object
    req.user = {
      userId: payload.userId,
      email: payload.email,
      role: payload.role
    };

    next();
  } catch (error) {
    throw new UnauthorizedError('Authentication invalid');
  }
};

/**
 * Check if user has admin role
 */
const isAdmin = async (req, res, next) => {
  if (!req.user) {
    throw new UnauthorizedError('Authentication required');
  }

  try {
    // Get fresh user data from database to ensure role is current
    const user = await User.findById(req.user.userId);

    if (!user) {
      throw new UnauthorizedError('User not found');
    }

    if (user.role !== 'admin' && user.role !== 'superadmin') {
      throw new ForbiddenError('Admin access required');
    }

    // Add full user role to request for more granular permissions
    req.user.role = user.role;

    next();
  } catch (error) {
    if (error instanceof ForbiddenError || error instanceof UnauthorizedError) {
      throw error;
    }
    throw new UnauthorizedError('Authentication failed');
  }
};

/**
 * Check if user is a super admin
 */
const isSuperAdmin = async (req, res, next) => {
  if (!req.user) {
    throw new UnauthorizedError('Authentication required');
  }

  try {
    const user = await User.findById(req.user.userId);

    if (!user) {
      throw new UnauthorizedError('User not found');
    }

    if (user.role !== 'superadmin') {
      throw new ForbiddenError('Super admin access required');
    }

    next();
  } catch (error) {
    if (error instanceof ForbiddenError || error instanceof UnauthorizedError) {
      throw error;
    }
    throw new UnauthorizedError('Authentication failed');
  }
};

module.exports = {
  authenticate,
  isAdmin,
  isSuperAdmin
};
