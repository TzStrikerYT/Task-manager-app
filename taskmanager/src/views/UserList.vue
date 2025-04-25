<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/users';

const router = useRouter();
const userStore = useUserStore();

const users = ref([]);
const loading = ref(false);
const error = ref('');

// Filters
const filters = ref({
  role: '',
  search: ''
});

onMounted(async () => {
  await fetchUsers();
});

async function fetchUsers() {
  loading.value = true;
  error.value = '';
  
  try {
    // Build filter params
    const params = {};
    if (filters.value.role) {
      params.role = filters.value.role;
    }
    if (filters.value.search) {
      params.search = filters.value.search;
    }
    
    const fetchedUsers = await userStore.fetchUsers(params);
    users.value = fetchedUsers;
  } catch (err) {
    error.value = 'Error al obtener usuarios. Por favor intente nuevamente.';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function applyFilters() {
  fetchUsers();
}

function resetFilters() {
  filters.value = {
    role: '',
    search: ''
  };
  fetchUsers();
}

function createUser() {
  router.push('/users/new');
}

function editUser(id) {
  router.push(`/users/${id}/edit`);
}

const roleOptions = [
  { value: '', label: 'Todos los Roles' },
  { value: 'Desarrollador', label: 'Desarrollador' },
  { value: 'Líder Técnico', label: 'Líder Técnico' },
  { value: 'Administrador', label: 'Administrador' }
];
</script>

<template>
  <div class="min-h-screen bg-gray-900 pb-12">
    <div class="container mx-auto px-4 py-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-xl font-bold text-indigo-400">Usuarios</h1>
        <button @click="createUser" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 flex items-center">
          <span class="mr-2">+</span> Crear Nuevo Usuario
        </button>
      </div>
      
      <div class="bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border border-gray-700">
        <h2 class="text-lg font-semibold text-gray-200 pb-3 border-b border-gray-700 mb-4">Filtros</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-300 mb-2">Buscar por Nombre o Email</label>
            <input 
              v-model="filters.search" 
              type="text" 
              placeholder="Buscar..." 
              class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Rol</label>
            <select 
              v-model="filters.role" 
              class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option v-for="option in roleOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <div class="md:col-span-3 flex justify-end space-x-4 mt-2">
            <button 
              @click="resetFilters" 
              class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-md transition-colors duration-200"
            >
              Reiniciar
            </button>
            <button 
              @click="applyFilters" 
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200"
            >
              Aplicar Filtros
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="error" class="mb-6 p-4 rounded bg-red-900/50 border border-red-700 text-red-200">
        {{ error }}
      </div>
      
      <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
        <div v-if="loading" class="text-center py-12">
          <svg class="animate-spin h-8 w-8 mx-auto mb-3 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-gray-400">Cargando usuarios...</p>
        </div>
        
        <div v-else-if="users.length === 0" class="text-center py-12">
          <div class="text-5xl mb-3">👤</div>
          <p class="text-gray-400">No se encontraron usuarios. Intente cambiar los filtros o crear un nuevo usuario.</p>
          <button @click="createUser" class="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200">
            Crear Nuevo Usuario
          </button>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-750">
              <tr class="text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <th class="px-6 py-3">Nombre</th>
                <th class="px-6 py-3">Email</th>
                <th class="px-6 py-3">Rol</th>
                <th class="px-6 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="bg-gray-800 border-t border-gray-700 hover:bg-gray-750 transition-colors duration-150">
                <td class="px-6 py-4 font-medium text-gray-200">{{ user.name }}</td>
                <td class="px-6 py-4 text-gray-400">{{ user.email }}</td>
                <td class="px-6 py-4">
                  <span :class="[
                    'px-2 py-1 text-xs rounded',
                    user.role === 'Administrador' ? 'bg-purple-900 text-purple-200' :
                    user.role === 'Líder Técnico' ? 'bg-yellow-900 text-yellow-200' :
                    'bg-blue-900 text-blue-200'
                  ]">
                    {{ user.role }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <button 
                    @click="editUser(user.id)" 
                    class="p-1 text-yellow-500 hover:text-yellow-400"
                    title="Editar"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Todos los estilos son manejados con clases de Tailwind */
</style> 