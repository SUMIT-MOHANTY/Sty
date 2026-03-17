import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Configure axios with authorization header
const getAuthHeader = () => {
  const token = localStorage.getItem('adminToken');
  return {
    headers: {
      Authorization: token ? `Bearer ${token}` : ''
    }
  };
};

// Dashboard statistics
export const fetchDashboardStatistics = async () => {
  try {
    const response = await axios.get(`${API_URL}/admin/dashboard`, getAuthHeader());
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
};

// Applications list
export const fetchApplications = async (params) => {
  try {
    const response = await axios.get(`${API_URL}/admin/applications`, {
      ...getAuthHeader(),
      params
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching applications:', error);
    throw error;
  }
};

// Application details
export const fetchApplicationById = async (id) => {
  try {
    const response = await axios.get(`${API_URL}/admin/applications/${id}`, getAuthHeader());
    return response.data;
  } catch (error) {
    console.error(`Error fetching application #${id}:`, error);
    throw error;
  }
};

// Update application status
export const updateApplicationStatus = async (id, action, comment) => {
  try {
    const response = await axios.patch(
      `${API_URL}/admin/applications/${id}/status`,
      { action, comment },
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error(`Error updating application #${id} status:`, error);
    throw error;
  }
};

// Admin login
export const adminLogin = async (credentials) => {
  try {
    const response = await axios.post(`${API_URL}/admin/login`, credentials);
    localStorage.setItem('adminToken', response.data.token);
    return response.data;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

// Admin logout
export const adminLogout = () => {
  localStorage.removeItem('adminToken');
};

// Check admin authentication
export const checkAuthStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/admin/auth-check`, getAuthHeader());
    return response.data;
  } catch (error) {
    console.error('Auth check failed:', error);
    localStorage.removeItem('adminToken');
    throw error;
  }
};
