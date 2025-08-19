import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Configure axios to include credentials (cookies)
axios.defaults.withCredentials = true;

// API service class
class JournalAPI {
  // Authentication methods
  async login(password) {
    try {
      const response = await axios.post(`${API}/login`, { password });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout() {
    try {
      const response = await axios.post(`${API}/logout`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Entry management methods
  async getEntries(search = '', category = 'all') {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (category && category !== 'all') params.append('category', category);
      params.append('grouped', 'true');

      const response = await axios.get(`${API}/entries?${params.toString()}`);
      return response.data.grouped || {};
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async createEntry(entryData) {
    try {
      const response = await axios.post(`${API}/entries`, entryData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateEntry(entryId, entryData) {
    try {
      const response = await axios.put(`${API}/entries/${entryId}`, entryData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async deleteEntry(entryId) {
    try {
      const response = await axios.delete(`${API}/entries/${entryId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Category management methods
  async getCategories() {
    try {
      const response = await axios.get(`${API}/categories`);
      return response.data.categories || [];
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handling
  handleError(error) {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 401) {
        // Unauthorized - redirect to login
        localStorage.removeItem('userRole');
        window.location.href = '/';
        return new Error('Session expired. Please login again.');
      } else if (status === 403) {
        return new Error('Access denied. Insufficient permissions.');
      } else if (status === 404) {
        return new Error('Resource not found.');
      } else if (data && data.detail) {
        return new Error(data.detail);
      }
      
      return new Error(`Server error: ${status}`);
    } else if (error.request) {
      // Network error
      return new Error('Network error. Please check your connection.');
    } else {
      // Other error
      return new Error(error.message || 'An unexpected error occurred.');
    }
  }

  // Utility methods
  async searchEntries(query, isSharedOnly = false) {
    try {
      const params = new URLSearchParams();
      if (query) params.append('search', query);
      params.append('grouped', 'true');

      const response = await axios.get(`${API}/entries?${params.toString()}`);
      return response.data.grouped || {};
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Get flat entries list (for stats)
  async getEntriesList(search = '', category = 'all') {
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (category && category !== 'all') params.append('category', category);
      params.append('grouped', 'false');

      const response = await axios.get(`${API}/entries?${params.toString()}`);
      return response.data.entries || [];
    } catch (error) {
      throw this.handleError(error);
    }
  }
}

// Export singleton instance
export const journalAPI = new JournalAPI();
export default journalAPI;