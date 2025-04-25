<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from './components/Sidebar.vue';
import Toast from './components/Toast.vue';

const route = useRoute();

// Verificar si la ruta actual requiere mostrar el sidebar (no en la página de login)
const showSidebar = computed(() => route.path !== '/login');
</script>

<template>
  <div class="min-h-screen bg-gray-900 text-gray-100">
    <!-- Solo mostrar el sidebar en las páginas que no son de login -->
    <Sidebar v-if="showSidebar" />
    
    <!-- Contenido principal con margen para el sidebar en pantallas medianas y grandes -->
    <div :class="[
      'transition-all duration-300 ease-in-out',
      showSidebar ? 'md:ml-64' : ''
    ]">
      <router-view />
    </div>
    
    <!-- Sistema de notificaciones toast -->
    <Toast />
  </div>
</template>

<style>
/* All global styles will be managed through Tailwind classes */
</style>
