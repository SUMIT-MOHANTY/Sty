const Application = require('../models/application.model');
const User = require('../models/user.model');
const { StatusCodes } = require('http-status-codes');
const { BadRequestError, NotFoundError } = require('../errors');
const applicationService = require('../services/application.service');

/**
 * Get all passport applications with optional filtering
 */
const getAllApplications = async (req, res) => {
  const { status, page = 1, limit = 10 } = req.query;
  const skip = (page - 1) * limit;

  const query = {};
  if (status) {
    query.status = status;
  }

  const applications = await Application.find(query)
    .sort({ createdAt: -1 })
    .skip(skip)
    .limit(parseInt(limit))
    .populate('userId', 'name email');

  const totalApplications = await Application.countDocuments(query);

  res.status(StatusCodes.OK).json({
    applications,
    totalPages: Math.ceil(totalApplications / limit),
    currentPage: parseInt(page),
    totalApplications
  });
};

/**
 * Get a single application by ID
 */
const getApplicationById = async (req, res) => {
  const { id: applicationId } = req.params;

  const application = await Application.findOne({ _id: applicationId })
    .populate('userId', 'name email phone');

  if (!application) {
    throw new NotFoundError(`No application with id: ${applicationId}`);
  }

  res.status(StatusCodes.OK).json({ application });
};

/**
 * Update application status
 */
const updateApplicationStatus = async (req, res) => {
  const { id: applicationId } = req.params;
  const { status, comments } = req.body;

  if (!status) {
    throw new BadRequestError('Status is required');
  }

  // Validate status values
  const validStatuses = ['pending', 'reviewing', 'approved', 'rejected'];
  if (!validStatuses.includes(status)) {
    throw new BadRequestError(`Status must be one of: ${validStatuses.join(', ')}`);
  }

  const application = await Application.findOne({ _id: applicationId });

  if (!application) {
    throw new NotFoundError(`No application with id: ${applicationId}`);
  }

  // Update application status
  application.status = status;
  if (comments) {
    application.adminComments = comments;
  }
  application.lastUpdatedBy = req.user.userId;
  application.statusHistory.push({
    status,
    changedBy: req.user.userId,
    comments: comments || undefined
  });

  await application.save();

  // Send notification to user about status change
  await applicationService.notifyStatusChange(application);

  res.status(StatusCodes.OK).json({
    message: 'Application status updated successfully',
    application
  });
};

/**
 * Get application statistics
 */
const getApplicationStatistics = async (req, res) => {
  const { startDate, endDate } = req.query;

  // Prepare date filters
  const dateFilter = {};
  if (startDate) {
    dateFilter.createdAt = { $gte: new Date(startDate) };
  }
  if (endDate) {
    if (!dateFilter.createdAt) dateFilter.createdAt = {};
    dateFilter.createdAt.$lte = new Date(endDate);
  }

  // Get counts by status
  const statusStats = await Application.aggregate([
    { $match: dateFilter },
    { $group: { _id: '$status', count: { $sum: 1 } } }
  ]);

  // Format status stats
  const statusCounts = statusStats.reduce((acc, curr) => {
    acc[curr._id] = curr.count;
    return acc;
  }, {});

  // Get daily application counts
  const dailyStats = await Application.aggregate([
    { $match: dateFilter },
    {
      $group: {
        _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
        count: { $sum: 1 }
      }
    },
    { $sort: { _id: 1 } }
  ]);

  // Get processing time averages
  const processingTimeStats = await Application.aggregate([
    { $match: { status: { $in: ['approved', 'rejected'] } } },
    {
      $project: {
        processingTime: {
          $divide: [
            { $subtract: ['$updatedAt', '$createdAt'] },
            1000 * 60 * 60 * 24 // convert ms to days
          ]
        }
      }
    },
    {
      $group: {
        _id: null,
        averageProcessingTime: { $avg: '$processingTime' }
      }
    }
  ]);

  const statistics = {
    total: await Application.countDocuments(dateFilter),
    statusCounts,
    dailyApplications: dailyStats,
    averageProcessingDays: processingTimeStats.length > 0
      ? processingTimeStats[0].averageProcessingTime.toFixed(2)
      : 0
  };

  res.status(StatusCodes.OK).json({ statistics });
};

module.exports = {
  getAllApplications,
  getApplicationById,
  updateApplicationStatus,
  getApplicationStatistics
};
