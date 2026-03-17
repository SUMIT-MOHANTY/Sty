const express = require('express');
const router = express.Router();
const adminController = require('../controllers/admin.controller');
const authMiddleware = require('../middlewares/auth.middleware');

/**
 * @swagger
 * /api/admin/applications:
 *   get:
 *     summary: Get all passport applications
 *     description: Retrieves all passport applications (admin access required)
 *     tags: [Admin]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *         description: Filter by application status
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *         description: Page number for pagination
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *         description: Number of items per page
 *     responses:
 *       200:
 *         description: List of passport applications
 *       401:
 *         description: Unauthorized
 *       403:
 *         description: Forbidden - Admin access required
 */
router.get('/applications',
  authMiddleware.authenticate,
  authMiddleware.isAdmin,
  adminController.getAllApplications
);

/**
 * @swagger
 * /api/admin/applications/{id}:
 *   get:
 *     summary: Get passport application details
 *     description: Retrieves detailed information about a specific passport application
 *     tags: [Admin]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Application ID
 *     responses:
 *       200:
 *         description: Application details
 *       401:
 *         description: Unauthorized
 *       403:
 *         description: Forbidden - Admin access required
 *       404:
 *         description: Application not found
 */
router.get('/applications/:id',
  authMiddleware.authenticate,
  authMiddleware.isAdmin,
  adminController.getApplicationById
);

/**
 * @swagger
 * /api/admin/applications/{id}/status:
 *   patch:
 *     summary: Update application status
 *     description: Update the status of a passport application
 *     tags: [Admin]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: Application ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - status
 *             properties:
 *               status:
 *                 type: string
 *                 enum: [pending, reviewing, approved, rejected]
 *               comments:
 *                 type: string
 *     responses:
 *       200:
 *         description: Status updated successfully
 *       400:
 *         description: Invalid status or request
 *       401:
 *         description: Unauthorized
 *       403:
 *         description: Forbidden - Admin access required
 *       404:
 *         description: Application not found
 */
router.patch('/applications/:id/status',
  authMiddleware.authenticate,
  authMiddleware.isAdmin,
  adminController.updateApplicationStatus
);

/**
 * @swagger
 * /api/admin/applications/statistics:
 *   get:
 *     summary: Get application statistics
 *     description: Retrieves statistics about passport applications
 *     tags: [Admin]
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: startDate
 *         schema:
 *           type: string
 *           format: date
 *         description: Start date for statistics (YYYY-MM-DD)
 *       - in: query
 *         name: endDate
 *         schema:
 *           type: string
 *           format: date
 *         description: End date for statistics (YYYY-MM-DD)
 *     responses:
 *       200:
 *         description: Application statistics
 *       401:
 *         description: Unauthorized
 *       403:
 *         description: Forbidden - Admin access required
 */
router.get('/applications/statistics',
  authMiddleware.authenticate,
  authMiddleware.isAdmin,
  adminController.getApplicationStatistics
);

module.exports = router;
