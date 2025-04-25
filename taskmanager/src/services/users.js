import api from './api';

export const userService = {
  async getUsers(filters = {}) {
    const response = await api.get('/users', { params: filters });
    return response.data;
  },

  async getUserById(id) {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  async createUser(userData) {
    const response = await api.post('/users', userData);
    return response.data;
  },

  async updateUser(id, userData) {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  }
};

export default userService; 