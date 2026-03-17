const request = require('supertest');
const mongoose = require('mongoose');
const { MongoMemoryServer } = require('mongodb-memory-server');
const jwt = require('jsonwebtoken');

const app = require('../../src/app');
const User = require('../../src/models/user.model');
const Application = require('../../src/models/application.model');
const config = require('../../src/config/config');

let mongoServer;

// Create test admin user and token
const createAdminUserAndToken = async () => {
  const adminUser = await User.create({
    name: 'Admin User',
    email: 'admin@test.com',
    password: 'password123',
    role: 'admin'
  });

  const token = jwt.sign(
    { userId: adminUser._id, email: adminUser.email, role: 'admin' },
    config.jwt.secret,
    { expiresIn: '1h' }
  );

  return { adminUser, token };
};

// Create test application
const createTestApplication = async (userId) => {
  return await Application.create({
    userId,
    applicationType: 'new',
    personalDetails: {
      firstName: 'Test',
      lastName: 'User',
      dateOfBirth: new Date('1990-01-01'),
      gender: 'male',
      placeOfBirth: 'Test City',
      nationality: 'Test Country'
    },
    contactDetails: {
      email: 'test@example.com',
      phone: '1234567890',
      address: {
        street: '123 Test St',
        city: 'Test City',
        state: 'Test State',
        postalCode: '12345',
        country: 'Test Country'
      }
    },
    documents: {
      idProof: {
        documentType: 'national-id',
        documentNumber: '123456789',
        documentImage: 'test-image-url.jpg'
      },
      photo: 'test-photo-url.jpg'
    },
    travelDetails: {
      purposeOfTravel: 'Tourism',
      countriesVisiting: ['Country1', 'Country2']
    },
    emergencyContact: {
      name: 'Emergency Contact',
      relationship: 'Relative',
      phone: '0987654321'
    },
    status: 'pending'
  });
};

describe('Admin API Routes', () => {
  beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();
    await mongoose.connect(mongoUri);
  });

  afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
  });

  beforeEach(async () => {
    await User.deleteMany({});
    await Application.deleteMany({});
  });

  describe('GET /api/admin/applications', () => {
    it('should return all applications when admin is authenticated', async () => {
      // Create admin and token
      const { adminUser, token } = await createAdminUserAndToken();

      // Create a regular user
      const regularUser = await User.create({
        name: 'Regular User',
        email: 'user@test.com',
        password: 'password123'
      });

      // Create test applications
      const application1 = await createTestApplication(regularUser._id);
      const application2 = await createTestApplication(regularUser._id);

      // Make request with admin token
      const response = await request(app)
        .get('/api/admin/applications')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(response.body.applications).toHaveLength(2);
      expect(response.body.totalApplications).toBe(2);
    });

    it('should return 401 when token is missing', async () => {
      await request(app)
        .get('/api/admin/applications')
        .expect(401);
    });

    it('should return 403 when non-admin user tries to access', async () => {
      // Create regular user
      const regularUser = await User.create({
        name: 'Regular User',
        email: 'user@test.com',
        password: 'password123',
        role: 'user'
      });

      // Create token for regular user
      const token = jwt.sign(
        { userId: regularUser._id, email: regularUser.email, role: 'user' },
        config.jwt.secret,
        { expiresIn: '1h' }
      );

      await request(app)
        .get('/api/admin/applications')
        .set('Authorization', `Bearer ${token}`)
        .expect(403);
    });
  });

  describe('GET /api/admin/applications/:id', () => {
    it('should return application details when admin is authenticated', async () => {
      const { adminUser, token } = await createAdminUserAndToken();
      const regularUser = await User.create({
        name: 'Regular User',
        email: 'user@test.com',
        password: 'password123'
      });

      const application = await createTestApplication(regularUser._id);

      const response = await request(app)
        .get(`/api/admin/applications/${application._id}`)
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(response.body.application._id.toString()).toBe(application._id.toString());
    });

    it('should return 404 when application does not exist', async () => {
      const { token } = await createAdminUserAndToken();
      const fakeId = new mongoose.Types.ObjectId();

      await request(app)
        .get(`/api/admin/applications/${fakeId}`)
        .set('Authorization', `Bearer ${token}`)
        .expect(404);
    });
  });

  describe('PATCH /api/admin/applications/:id/status', () => {
    it('should update application status when admin is authenticated', async () => {
      const { adminUser, token } = await createAdminUserAndToken();
      const regularUser = await User.create({
        name: 'Regular User',
        email: 'user@test.com',
        password: 'password123'
      });

      const application = await createTestApplication(regularUser._id);

      const response = await request(app)
        .patch(`/api/admin/applications/${application._id}/status`)
        .set('Authorization', `Bearer ${token}`)
        .send({ status: 'approved', comments: 'Application looks good' })
        .expect(200);

      expect(response.body.application.status).toBe('approved');
      expect(response.body.application.adminComments).toBe('Application looks good');

      // Check that history was updated
      const updatedApp = await Application.findById(application._id);
      expect(updatedApp.statusHistory).toHaveLength(1);
      expect(updatedApp.statusHistory[0].status).toBe('approved');
    });

    it('should return 400 for invalid status', async () => {
      const { token } = await createAdminUserAndToken();
      const regularUser = await User.create({
        name: 'Regular User',
        email: 'user@test.com',
        password: 'password123'
      });

      const application = await createTestApplication(regularUser._id);

      await request(app)
        .patch(`/api/admin/applications/${application._id}/status`)
        .set('Authorization', `Bearer ${token}`)
        .send({ status: 'invalid-status' })
        .expect(400);
    });
  });

  describe('GET /api/admin/applications/statistics', () => {
    it('should return application statistics', async () => {
      const { adminUser, token } = await createAdminUserAndToken();
      const regularUser = await User.create({
        name: 'Regular User',
        email: 'user@test.com',
        password: 'password123'
      });

      // Create applications with different statuses
      const app1 = await createTestApplication(regularUser._id);
      app1.status = 'pending';
      await app1.save();

      const app2 = await createTestApplication(regularUser._id);
      app2.status = 'reviewing';
      await app2.save();

      const app3 = await createTestApplication(regularUser._id);
      app3.status = 'approved';
      await app3.save();

      const response = await request(app)
        .get('/api/admin/applications/statistics')
        .set('Authorization', `Bearer ${token}`)
        .expect(200);

      expect(response.body.statistics.total).toBe(3);
      expect(response.body.statistics.statusCounts).toHaveProperty('pending');
      expect(response.body.statistics.statusCounts).toHaveProperty('reviewing');
      expect(response.body.statistics.statusCounts).toHaveProperty('approved');
    });
  });
});
