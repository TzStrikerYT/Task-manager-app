<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');

async function handleLogin() {
  loading.value = true;
  error.value = '';
  
  try {
    await authStore.login(email.value, password.value);
    router.push('/dashboard');
  } catch (err) {
    error.value = err.response?.data?.error || 'Login failed. Please check your credentials.';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="flex justify-center items-center min-h-screen bg-gray-900 px-4">
    <div class="w-full max-w-md p-8 rounded-lg bg-gray-800 shadow-2xl border border-gray-700">
      <h1 class="text-2xl font-bold text-center text-indigo-400 mb-1">Task Manager</h1>
      <h2 class="text-xl text-center text-gray-400 mb-8">Login</h2>
      
      <div v-if="error" class="mb-6 p-4 rounded bg-red-900/50 border border-red-700 text-red-200 text-sm">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-300 mb-2">Email</label>
          <input 
            id="email"
            type="email" 
            v-model="email" 
            required 
            placeholder="Enter your email"
            class="w-full px-4 py-3 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        
        <div>
          <label for="password" class="block text-sm font-medium text-gray-300 mb-2">Password</label>
          <input 
            id="password"
            type="password" 
            v-model="password" 
            required 
            placeholder="Enter your password"
            class="w-full px-4 py-3 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>
        
        <button 
          type="submit" 
          :disabled="loading"
          class="w-full py-3 px-4 rounded-md font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 focus:ring-offset-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          <span v-if="loading" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Logging in...
          </span>
          <span v-else>Login</span>
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Todos los estilos son manejados con clases de Tailwind */
</style> 