import { defineStore } from 'pinia';
import authService from '../services/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: authService.getCurrentUser(),
    isAuthenticated: authService.isAuthenticated(),
    loading: false,
    error: null
  }),

  actions: {
    async login(email, password) {
      this.loading = true;
      this.error = null;
      
      try {
        const data = await authService.login(email, password);
        this.user = data.user;
        this.isAuthenticated = true;
        return data;
      } catch (error) {
        this.error = error.response?.data?.error || 'Login failed';
        throw error;
      } finally {
        this.loading = false;
      }
    },

    async refreshToken() {
      try {
        const data = await authService.refreshToken();
        return data;
      } catch (error) {
        this.logout();
        throw error;
      }
    },

    logout() {
      authService.logout();
      this.user = null;
      this.isAuthenticated = false;
    }
  }
}); 