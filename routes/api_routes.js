/**
 * API routes with role-based protection
 */
const express = require('express');
const router = express.Router();
const authenticateJWT = require('../middleware/auth/jwt_middleware');
const checkRole = require('../middleware/auth/rbac_middleware');

// Example controller for demonstration
const demoController = {
  publicEndpoint: (req, res) => {
    res.json({ message: 'This is a public endpoint' });
  },

  protectedEndpoint: (req, res) => {
    res.json({
      message: 'This is a protected endpoint',
      user: req.user
    });
  },

  adminEndpoint: (req, res) => {
    res.json({
      message: 'This is an admin-only endpoint',
      user: req.user
    });
  },

  multiRoleEndpoint: (req, res) => {
    res.json({
      message: 'This endpoint is accessible to admins and editors',
      user: req.user
    });
  }
};

// Public route - no authentication
router.get('/public', demoController.publicEndpoint);

// Protected route - any authenticated user
router.get('/protected', authenticateJWT, demoController.protectedEndpoint);

// Admin only route
router.get('/admin', authenticateJWT, checkRole('admin'), demoController.adminEndpoint);

// Multi-role route - accessible to admins and editors
router.get('/content',
  authenticateJWT,
  checkRole(['admin', 'editor']),
  demoController.multiRoleEndpoint
);

module.exports = router;
