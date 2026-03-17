const nodemailer = require('nodemailer');
const User = require('../models/user.model');
const config = require('../config/config');

/**
 * Send email notification to user about application status change
 */
const sendStatusNotification = async (userEmail, applicationId, status) => {
  // In production, use a real email service like SendGrid, AWS SES, etc.
  // For development, use a test SMTP service or console log

  if (config.env === 'test') {
    console.log(`[TEST] Email notification to ${userEmail} about application ${applicationId} status change to ${status}`);
    return;
  }

  const transporter = nodemailer.createTransport({
    host: config.email.host,
    port: config.email.port,
    secure: config.email.secure,
    auth: {
      user: config.email.user,
      pass: config.email.password,
    },
  });

  const statusMessages = {
    pending: 'Your passport application has been received and is pending review.',
    reviewing: 'Your passport application is currently under review by our team.',
    approved: 'Congratulations! Your passport application has been approved.',
    rejected: 'Your passport application has been rejected. Please see the details for more information.'
  };

  const message = statusMessages[status] || 'Your passport application status has been updated.';

  const mailOptions = {
    from: config.email.from,
    to: userEmail,
    subject: `Passport Application Status Update - ${status.toUpperCase()}`,
    html: `
      <h2>Passport Application Status Update</h2>
      <p>Dear Applicant,</p>
      <p>${message}</p>
      <p>Application ID: ${applicationId}</p>
      <p>Status: ${status}</p>
      <p>You can check the details of your application by logging into your account.</p>
      <p>Thank you,</p>
      <p>Passport Service Team</p>
    `,
  };

  await transporter.sendMail(mailOptions);
};

/**
 * Notify user about status change
 */
const notifyStatusChange = async (application) => {
  try {
    const user = await User.findById(application.userId);
    if (!user || !user.email) {
      console.error('User email not found for notification', application.userId);
      return;
    }

    await sendStatusNotification(
      user.email,
      application._id,
      application.status
    );

    // If status is approved and we have phone number, could send SMS
    if (application.status === 'approved' && user.phone && config.sms.enabled) {
      // SMS notification code would go here
      console.log(`SMS notification would be sent to ${user.phone}`);
    }

  } catch (error) {
    console.error('Error sending notification:', error);
    // Don't throw - notifications shouldn't block the main flow
  }
};

module.exports = {
  notifyStatusChange,
  sendStatusNotification
};
