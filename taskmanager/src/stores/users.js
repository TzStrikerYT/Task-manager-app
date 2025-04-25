import { defineStore } from 'pinia';
import userService from '../services/users';

export const useUserStore = defineStore('users', {
  state: () => ({
    users: [],
    currentUser: null,
    loading: false,
    error: null
  }),

  actions: {
    async fetchUsers(filters = {}) {
      this.loading = true;
      this.error = null;
      
      try {
        const users = await userService.getUsers(filters);
        this.users = users;
        return users;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to fetch users';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async fetchUserById(id) {
      this.loading = true;
      this.error = null;
      
      try {
        const user = await userService.getUserById(id);
        this.currentUser = user;
        return user;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to fetch user';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async createUser(userData) {
      this.loading = true;
      this.error = null;
      
      try {
        const newUser = await userService.createUser(userData);
        this.users.push(newUser);
        return newUser;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to create user';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async updateUser(id, userData) {
      this.loading = true;
      this.error = null;
      
      try {
        const updatedUser = await userService.updateUser(id, userData);
        
        // Update in the users array
        const index = this.users.findIndex(user => user.id === id);
        if (index !== -1) {
          this.users[index] = updatedUser;
        }
        
        // Update current user if it's the same
        if (this.currentUser && this.currentUser.id === id) {
          this.currentUser = updatedUser;
        }
        
        return updatedUser;
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to update user';
        throw error;
      } finally {
        this.loading = false;
      }
    }
  }
}); 