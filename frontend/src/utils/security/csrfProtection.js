/**
 * CSRF protection utilities
 */

// Get CSRF token from cookie or meta tag
export const getCsrfToken = () => {
  // First try to get from meta tag
  const metaTag = document.querySelector('meta[name="csrf-token"]');
  if (metaTag) {
    return metaTag.getAttribute('content');
  }

  // Fallback to cookie
  const csrfCookie = document.cookie
    .split(';')
    .find(cookie => cookie.trim().startsWith('XSRF-TOKEN='));

  if (csrfCookie) {
    return csrfCookie.split('=')[1];
  }

  console.error('CSRF token not found');
  return '';
};

// Add CSRF token to request headers
export const addCsrfHeader = (headers = {}) => {
  return {
    ...headers,
    'X-CSRF-TOKEN': getCsrfToken(),
  };
};
