import api from './api';

export const taskService = {
  async getTasks(filters = {}) {
    const response = await api.get('/tasks', { params: filters });
    return response.data;
  },

  async getTaskById(id) {
    const response = await api.get(`/tasks/${id}`);
    return response.data;
  },

  async createTask(taskData) {
    const response = await api.post('/tasks', taskData);
    return response.data;
  },

  async updateTask(id, taskData) {
    const response = await api.put(`/tasks/${id}`, taskData);
    return response.data;
  },

  async updateTaskStatus(id, status) {
    const response = await api.put(`/tasks/${id}/status`, { status });
    return response.data;
  },

  async updateTaskPriority(id, priority) {
    const response = await api.put(`/tasks/${id}/priority`, { priority });
    return response.data;
  },

  async assignUserToTask(taskId, userId) {
    const response = await api.post(`/tasks/${taskId}/assign/${userId}`);
    return response.data;
  },

  async unassignUserFromTask(taskId, userId) {
    const response = await api.delete(`/tasks/${taskId}/unassign/${userId}`);
    return response.data;
  }
};

export default taskService; 