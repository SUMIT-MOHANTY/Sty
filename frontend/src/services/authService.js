import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class AuthService {
  async register(userData) {
    const response = await axios.post(`${API_URL}/auth/register`, {
      full_name: userData.fullName,
      email: userData.email,
      password: userData.password
    });
    return response.data;
  }

  async login(email, password) {
    const response = await axios.post(`${API_URL}/auth/login`, {
      email,
      password
    });
    if (response.data.access_token) {
      localStorage.setItem('user', JSON.stringify(response.data));
    }
    return response.data;
  }

  logout() {
    localStorage.removeItem('user');
  }

  getCurrentUser() {
    return JSON.parse(localStorage.getItem('user'));
  }

  isAuthenticated() {
    const user = this.getCurrentUser();
    return !!user && !!user.access_token;
  }
}

export default new AuthService();
