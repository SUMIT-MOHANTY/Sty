/**
 * Authentication routes
 */
const express = require('express');
const router = express.Router();
const authController = require('../controllers/auth_controller');
const authenticateJWT = require('../middleware/auth/jwt_middleware');

// Public routes
router.post('/register', authController.register);
router.post('/login', authController.login);

// Protected routes
router.get('/profile', authenticateJWT, authController.getProfile);

module.exports = router;
