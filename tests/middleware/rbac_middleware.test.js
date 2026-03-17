/**
 * Tests for role-based access control middleware
 */
const checkRole = require('../../middleware/auth/rbac_middleware');

describe('RBAC Middleware', () => {
  let req, res, next;

  beforeEach(() => {
    req = {};
    res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn()
    };
    next = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('should return 401 if user is not authenticated', () => {
    const middleware = checkRole('admin');
    middleware(req, res, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: 'Unauthenticated' });
    expect(next).not.toHaveBeenCalled();
  });

  test('should return 403 if user does not have required role', () => {
    req.user = {
      id: '123',
      email: 'user@example.com',
      roles: ['user']
    };

    const middleware = checkRole('admin');
    middleware(req, res, next);

    expect(res.status).toHaveBeenCalledWith(403);
    expect(res.json).toHaveBeenCalledWith({ message: 'Insufficient permissions' });
    expect(next).not.toHaveBeenCalled();
  });

  test('should call next if user has required role', () => {
    req.user = {
      id: '123',
      email: 'admin@example.com',
      roles: ['admin']
    };

    const middleware = checkRole('admin');
    middleware(req, res, next);

    expect(next).toHaveBeenCalled();
    expect(res.status).not.toHaveBeenCalled();
  });

  test('should call next if user has one of multiple required roles', () => {
    req.user = {
      id: '123',
      email: 'editor@example.com',
      roles: ['editor']
    };

    const middleware = checkRole(['admin', 'editor']);
    middleware(req, res, next);

    expect(next).toHaveBeenCalled();
    expect(res.status).not.toHaveBeenCalled();
  });
});
