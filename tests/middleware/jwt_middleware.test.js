/**
 * Tests for JWT authentication middleware
 */
const jwt = require('jsonwebtoken');
const mongoose = require('mongoose');
const { User } = require('../../models');
const authenticateJWT = require('../../middleware/auth/jwt_middleware');
const config = require('../../config');

// Mock dependencies
jest.mock('../../models', () => ({
  User: {
    findById: jest.fn()
  }
}));

describe('JWT Authentication Middleware', () => {
  let req, res, next;

  beforeEach(() => {
    req = {
      headers: {}
    };
    res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    next = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should return 401 if no authorization header is present', async () => {
    await authenticateJWT(req, res, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: 'Authorization header missing' });
    expect(next).not.toHaveBeenCalled();
  });

  test('should return 401 if token is missing', async () => {
    req.headers.authorization = 'Bearer ';

    await authenticateJWT(req, res, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: 'Token missing' });
    expect(next).not.toHaveBeenCalled();
  });

  test('should attach user to request and call next if token is valid', async () => {
    const userId = new mongoose.Types.ObjectId().toString();
    const user = {
      _id: userId,
      email: 'test@example.com',
      roles: ['user']
    };

    const token = jwt.sign({ userId }, config.jwt.secret);
    req.headers.authorization = `Bearer ${token}`;

    User.findById.mockResolvedValue(user);

    await authenticateJWT(req, res, next);

    expect(User.findById).toHaveBeenCalledWith(userId);
    expect(req.user).toEqual({
      id: user._id,
      email: user.email,
      roles: user.roles
    });
    expect(next).toHaveBeenCalled();
    expect(res.status).not.toHaveBeenCalled();
  });
});
