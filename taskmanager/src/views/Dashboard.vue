<script setup>
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useTaskStore } from '../stores/tasks';

const router = useRouter();
const authStore = useAuthStore();
const taskStore = useTaskStore();
const user = ref(authStore.user);
const tasks = ref([]);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    // Fetch a small number of recent tasks for the dashboard
    const fetchedTasks = await taskStore.fetchTasks({ limit: 5 });
    tasks.value = fetchedTasks;
  } catch (error) {
    console.error('Failed to fetch tasks:', error);
  } finally {
    loading.value = false;
  }
});

function navigateTo(path) {
  router.push(path);
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 pb-12">
    <main class="container mx-auto px-4 py-6">
      <h1 class="text-xl font-bold text-indigo-400 mb-6">Panel Principal</h1>
      
      <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="md:col-span-1 bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
          <div class="p-5">
            <h3 class="text-lg font-semibold text-gray-200 pb-3 border-b border-gray-700 mb-4">Acciones Rápidas</h3>
            <div class="space-y-3">
              <button @click="navigateTo('/tasks/new')" class="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 flex items-center justify-center">
                <span class="mr-2">+</span> Crear Nueva Tarea
              </button>
              <button @click="navigateTo('/users/new')" class="w-full py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 rounded-md transition-colors duration-200 flex items-center justify-center">
                <span class="mr-2">+</span> Añadir Nuevo Usuario
              </button>
            </div>
          </div>
        </div>
        
        <div class="md:col-span-2 bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
          <div class="p-5">
            <h3 class="text-lg font-semibold text-gray-200 pb-3 border-b border-gray-700 mb-4">Tareas Recientes</h3>
            <div v-if="loading" class="text-gray-400 py-4 text-center">
              <svg class="animate-spin h-6 w-6 mx-auto mb-2 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Cargando tareas recientes...
            </div>
            <div v-else-if="tasks.length === 0" class="text-gray-400 py-6 text-center">
              <div class="mb-2">📋</div>
              No se encontraron tareas. ¡Crea tu primera tarea!
            </div>
            <ul v-else class="space-y-3">
              <li v-for="task in tasks" :key="task.id" class="bg-gray-750 rounded-md p-4 border border-gray-700">
                <div class="flex justify-between items-start mb-2">
                  <h4 class="font-medium text-gray-200">{{ task.title }}</h4>
                  <span :class="[
                    'px-2 py-1 text-xs rounded-full', 
                    task.priority.toLowerCase() === 'high' ? 'bg-red-900 text-red-200' : 
                    task.priority.toLowerCase() === 'medium' ? 'bg-yellow-900 text-yellow-200' : 
                    'bg-blue-900 text-blue-200'
                  ]">
                    {{ task.priority }}
                  </span>
                </div>
                <div class="flex justify-between items-center text-sm text-gray-400 mb-3">
                  <span :class="[
                    'px-2 py-1 rounded text-xs', 
                    task.status === 'Completed' ? 'bg-green-900 text-green-200' : 
                    task.status === 'In Progress' ? 'bg-indigo-900 text-indigo-200' : 
                    'bg-gray-700 text-gray-300'
                  ]">{{ task.status }}</span>
                  <span>Vence: {{ new Date(task.due_date).toLocaleDateString() }}</span>
                </div>
                <button @click="navigateTo(`/tasks/${task.id}`)" class="w-full py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded text-sm transition-colors duration-200">
                  Ver Detalles
                </button>
              </li>
            </ul>
            <div class="mt-4 text-center">
              <button @click="navigateTo('/tasks')" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-md transition-colors duration-200 text-sm">
                Ver Todas las Tareas
              </button>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
/* Todos los estilos son manejados con clases de Tailwind */
</style> 