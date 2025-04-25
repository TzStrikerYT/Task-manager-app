<script setup>
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const user = computed(() => authStore.user);

const isMobileMenuOpen = ref(false);

// Define las rutas de navegación principales
const navItems = [
  { name: 'Inicio', path: '/dashboard', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: 'Tareas', path: '/tasks', icon: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01' },
  { name: 'Usuarios', path: '/users', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
];

// Verifica si la ruta actual coincide con la ruta del elemento de navegación
function isActive(path) {
  return route.path === path || route.path.startsWith(`${path}/`);
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

function handleLogout() {
  authStore.logout();
  router.push('/login');
}

function navigateTo(path) {
  router.push(path);
  isMobileMenuOpen.value = false; // Cierra el menú móvil al navegar
}
</script>

<template>
  <!-- Sidebar para pantallas medianas y grandes -->
  <aside class="hidden md:flex flex-col fixed h-screen w-64 bg-gray-800 border-r border-gray-700">
    <!-- Logo y título -->
    <div class="h-16 flex items-center px-6 border-b border-gray-700">
      <h1 class="text-xl font-bold text-indigo-400">Stasker</h1>
    </div>
    
    <!-- Perfil de usuario -->
    <div class="p-4 border-b border-gray-700">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold">
          {{ user?.name?.charAt(0) || '?' }}
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-200 truncate">{{ user?.name || 'Usuario' }}</p>
          <p class="text-xs text-gray-500 truncate">{{ user?.role || 'Rol' }}</p>
        </div>
      </div>
    </div>
    
    <!-- Navegación -->
    <nav class="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
      <a 
        v-for="item in navItems" 
        :key="item.path"
        @click="navigateTo(item.path)"
        :class="[
          'flex items-center px-4 py-3 text-sm rounded-md cursor-pointer transition-colors duration-200',
          isActive(item.path) 
            ? 'bg-gray-700 text-indigo-400' 
            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
        ]"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
        </svg>
        {{ item.name }}
      </a>
    </nav>
    
    <!-- Footer con botón de logout -->
    <div class="p-4 border-t border-gray-700">
      <button 
        @click="handleLogout" 
        class="w-full flex items-center px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 hover:text-white rounded-md transition-colors duration-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        Cerrar Sesión
      </button>
    </div>
  </aside>
  
  <!-- Header para móviles con menú desplegable -->
  <div class="md:hidden bg-gray-800 border-b border-gray-700 fixed top-0 left-0 right-0 z-10">
    <div class="flex items-center justify-between h-16 px-4">
      <h1 class="text-xl font-bold text-indigo-400">Stasker</h1>
      
      <!-- Botón de hamburguesa -->
      <button 
        @click="toggleMobileMenu"
        class="text-gray-300 hover:text-white focus:outline-none"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
    
    <!-- Menú móvil desplegable -->
    <div v-if="isMobileMenuOpen" class="bg-gray-800 shadow-lg pb-3">
      <!-- Perfil de usuario -->
      <div class="p-4 border-b border-gray-700">
        <div class="flex items-center space-x-3">
          <div class="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold">
            {{ user?.name?.charAt(0) || '?' }}
          </div>
          <div>
            <p class="text-sm font-medium text-gray-200">{{ user?.name || 'Usuario' }}</p>
            <p class="text-xs text-gray-500">{{ user?.role || 'Rol' }}</p>
          </div>
        </div>
      </div>
      
      <!-- Navegación móvil -->
      <nav class="px-2 pt-2 pb-4 space-y-1">
        <a 
          v-for="item in navItems" 
          :key="item.path"
          @click="navigateTo(item.path)"
          :class="[
            'flex items-center px-4 py-3 text-sm rounded-md cursor-pointer transition-colors duration-200',
            isActive(item.path) 
              ? 'bg-gray-700 text-indigo-400' 
              : 'text-gray-300 hover:bg-gray-700 hover:text-white'
          ]"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="item.icon" />
          </svg>
          {{ item.name }}
        </a>
        
        <!-- Botón de logout en menú móvil -->
        <a 
          @click="handleLogout" 
          class="flex items-center px-4 py-3 text-sm text-gray-300 hover:bg-gray-700 hover:text-white rounded-md cursor-pointer transition-colors duration-200"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          Cerrar Sesión
        </a>
      </nav>
    </div>
  </div>
  
  <!-- Espaciador para móviles (para que el contenido no quede debajo del header) -->
  <div class="h-16 md:hidden"></div>
</template> 