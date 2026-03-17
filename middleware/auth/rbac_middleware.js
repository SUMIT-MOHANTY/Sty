/**
 * Role-Based Access Control (RBAC) Middleware
 * Checks if user has required roles to access a route
 */

/**
 * Middleware factory that creates a middleware function checking for specific roles
 * @param {string|string[]} requiredRoles - Role(s) required to access the route
 * @returns {Function} Express middleware function
 */
const checkRole = (requiredRoles) => {
  return (req, res, next) => {
    // Must be used after authenticateJWT middleware
    if (!req.user) {
      return res.status(401).json({ message: 'Unauthenticated' });
    }

    const userRoles = req.user.roles || [];

    // Convert single role to array for consistent handling
    const roles = Array.isArray(requiredRoles) ? requiredRoles : [requiredRoles];

    // Check if user has any of the required roles
    const hasRequiredRole = roles.some(role => userRoles.includes(role));

    if (!hasRequiredRole) {
      return res.status(403).json({ message: 'Insufficient permissions' });
    }

    next();
  };
};

module.exports = checkRole;
