import { defineStore } from 'pinia';
import taskService from '../services/tasks';

export const useTaskStore = defineStore('tasks', {
  state: () => ({
    tasks: [],
    currentTask: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchTasks(filters = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const tasks = await taskService.getTasks(filters);
        this.tasks = tasks;
        return tasks;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to fetch tasks';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchTaskById(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const task = await taskService.getTaskById(id);
        this.currentTask = task;
        return task;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to fetch task';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async createTask(taskData) {
      this.loading = true;
      this.error = null;
      
      try {
        const newTask = await taskService.createTask(taskData);
        this.tasks.push(newTask);
        return newTask;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to create task';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateTask(id, taskData) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedTask = await taskService.updateTask(id, taskData);
        
        // Update in the tasks array
        const index = this.tasks.findIndex(task => task.id === id);
        if (index !== -1) {
          this.tasks[index] = updatedTask;
        }
        
        // Update current task if it's the same
        if (this.currentTask && this.currentTask.id === id) {
          this.currentTask = updatedTask;
        }
        
        return updatedTask;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to update task';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateTaskStatus(id, status) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedTask = await taskService.updateTaskStatus(id, status);
        
        // Update in the tasks array
        const index = this.tasks.findIndex(task => task.id === id);
        if (index !== -1) {
          this.tasks[index] = updatedTask;
        }
        
        // Update current task if it's the same
        if (this.currentTask && this.currentTask.id === id) {
          this.currentTask = updatedTask;
        }
        
        return updatedTask;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to update task status';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateTaskPriority(id, priority) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedTask = await taskService.updateTaskPriority(id, priority);
        
        // Update in the tasks array
        const index = this.tasks.findIndex(task => task.id === id);
        if (index !== -1) {
          this.tasks[index] = updatedTask;
        }
        
        // Update current task if it's the same
        if (this.currentTask && this.currentTask.id === id) {
          this.currentTask = updatedTask;
        }
        
        return updatedTask;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to update task priority';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async assignUserToTask(taskId, userId) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedTask = await taskService.assignUserToTask(taskId, userId);
        
        // Update in the tasks array
        const index = this.tasks.findIndex(task => task.id === taskId);
        if (index !== -1) {
          this.tasks[index] = updatedTask;
        }
        
        // Update current task if it's the same
        if (this.currentTask && this.currentTask.id === taskId) {
          this.currentTask = updatedTask;
        }
        
        return updatedTask;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to assign user to task';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async unassignUserFromTask(taskId, userId) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedTask = await taskService.unassignUserFromTask(taskId, userId);
        
        // Update in the tasks array
        const index = this.tasks.findIndex(task => task.id === taskId);
        if (index !== -1) {
          this.tasks[index] = updatedTask;
        }
        
        // Update current task if it's the same
        if (this.currentTask && this.currentTask.id === taskId) {
          this.currentTask = updatedTask;
        }
        
        return updatedTask;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to unassign user from task';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
}); 