<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTaskStore } from '../stores/tasks';
import { useUserStore } from '../stores/users';
import { useNotificationStore } from '../stores/notifications';

const route = useRoute();
const router = useRouter();
const taskStore = useTaskStore();
const userStore = useUserStore();
const notificationStore = useNotificationStore();

// Determine if we're in edit mode based on route
const isEditMode = computed(() => route.params.id !== undefined);
const formTitle = computed(() => isEditMode.value ? 'Editar Tarea' : 'Crear Nueva Tarea');

// Form data
const form = ref({
  title: '',
  description: '',
  priority: 'Media',
  due_date: '',
  assigned_users: [],
});

// UI states
const loading = ref(false);
const submitting = ref(false);
const error = ref('');
const successMessage = ref('');
const users = ref([]);
const userSearchTerm = ref('');
const showUserSelector = ref(false);

// Filtrar usuarios para la asignación
const filteredUsers = computed(() => {
  if (!users.value) return [];
  
  return users.value.filter(user => {
    // Filtrar por término de búsqueda (insensible a mayús./minús.)
    const matchesSearch = !userSearchTerm.value || 
      user.name.toLowerCase().includes(userSearchTerm.value.toLowerCase()) || 
      (user.email && user.email.toLowerCase().includes(userSearchTerm.value.toLowerCase())) ||
      user.role.toLowerCase().includes(userSearchTerm.value.toLowerCase());
    
    // Filtrar usuarios ya asignados
    const isAlreadyAssigned = form.value.assigned_users.includes(user.id);
    
    return matchesSearch && !isAlreadyAssigned;
  });
});

// Obtener usuarios ya asignados
const assignedUsers = computed(() => {
  if (!users.value) return [];
  
  return users.value.filter(user => 
    form.value.assigned_users.includes(user.id)
  );
});

// Alternar selector de usuarios
function toggleUserSelector() {
  showUserSelector.value = !showUserSelector.value;
  if (showUserSelector.value) {
    userSearchTerm.value = '';
  }
}

// Función para asignar un usuario
function assignUser(userId) {
  if (!form.value.assigned_users.includes(userId)) {
    form.value.assigned_users.push(userId);
  }
  userSearchTerm.value = '';
}

// Función para eliminar un usuario asignado
function removeUser(userId) {
  const index = form.value.assigned_users.indexOf(userId);
  if (index !== -1) {
    form.value.assigned_users.splice(index, 1);
  }
}

// Fetch users and task data (if in edit mode) when component mounts
onMounted(async () => {
  loading.value = true;
  try {
    users.value = await userStore.fetchUsers();
    
    if (isEditMode.value) {
      const taskData = await taskStore.fetchTaskById(route.params.id);
      form.value.title = taskData.title;
      form.value.description = taskData.description;
      form.value.priority = taskData.priority;
      form.value.due_date = formatDateForInput(taskData.due_date);
      
      // Manejar los usuarios asignados
      if (taskData.assigned_user_ids && taskData.assigned_user_ids.length > 0) {
        // Si la API devuelve assigned_user_ids, usamos estos directamente
        form.value.assigned_users = taskData.assigned_user_ids;
      } else if (taskData.assigned_users && taskData.assigned_users.length > 0) {
        // Si la API devuelve objetos de usuario, extraemos los IDs
        form.value.assigned_users = taskData.assigned_users.map(user => user.id);
      } else {
        form.value.assigned_users = [];
      }

      console.log('Usuarios asignados cargados:', form.value.assigned_users);
    }
  } catch (err) {
    error.value = 'Error al cargar los datos. Por favor, intente nuevamente.';
    console.error(err);
  } finally {
    loading.value = false;
  }
});

// Format date for input field
function formatDateForInput(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toISOString().split('T')[0];
}

// Submit the form
async function submitForm() {
  submitting.value = true;
  error.value = '';
  
  try {
    // Preparar los datos en el formato correcto que espera la API
    const taskData = {
      title: form.value.title,
      description: form.value.description,
      priority: form.value.priority,
      due_date: form.value.due_date,
      assigned_user_ids: form.value.assigned_users // Enviar IDs como assigned_user_ids
    };
    
    if (isEditMode.value) {
      await taskStore.updateTask(
        parseInt(route.params.id), 
        taskData
      );
      notificationStore.success('¡Tarea actualizada correctamente!');
    } else {
      await taskStore.createTask(taskData);
      notificationStore.success('¡Tarea creada correctamente!');
      // Reset form after successful creation
      form.value = {
        title: '',
        description: '',
        priority: 'Media',
        due_date: '',
        assigned_users: [],
      };
    }
  } catch (err) {
    const errorMsg = err.response?.data?.error || 'Error al guardar la tarea. Por favor, intente nuevamente.';
    error.value = errorMsg;
    notificationStore.error(errorMsg);
    console.error(err);
  } finally {
    submitting.value = false;
  }
}

// Go back to task list
function goBack() {
  router.push('/tasks');
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 pb-12">
    <div class="container mx-auto max-w-2xl px-4 py-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-xl font-bold text-indigo-400">{{ formTitle }}</h1>
        <button 
          @click="goBack" 
          class="px-4 py-2 border border-indigo-500 text-indigo-400 hover:bg-indigo-900/30 rounded-md transition-colors duration-200"
        >
          Volver a Tareas
        </button>
      </div>
      
      <!-- Loading state -->
      <div v-if="loading" class="bg-gray-800 rounded-lg shadow-lg p-12 text-center border border-gray-700">
        <svg class="animate-spin h-10 w-10 mx-auto mb-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-400">Cargando datos...</p>
      </div>

      <!-- Form -->
      <form v-else @submit.prevent="submitForm" class="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
        <!-- Error message -->
        <div v-if="error" class="mb-6 p-4 rounded bg-red-900/50 border border-red-700 text-red-200">
          {{ error }}
        </div>

        <!-- Title field -->
        <div class="mb-6">
          <label for="title" class="block text-sm font-medium text-gray-300 mb-2">Título</label>
          <input 
            type="text" 
            id="title" 
            v-model="form.title" 
            required
            class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Ingrese un título para la tarea"
          />
        </div>

        <!-- Description field -->
        <div class="mb-6">
          <label for="description" class="block text-sm font-medium text-gray-300 mb-2">Descripción</label>
          <textarea 
            id="description" 
            v-model="form.description" 
            rows="5"
            class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Describa la tarea en detalle"
          ></textarea>
        </div>

        <!-- Priority field -->
        <div class="mb-6">
          <label for="priority" class="block text-sm font-medium text-gray-300 mb-2">Prioridad</label>
          <select 
            id="priority" 
            v-model="form.priority"
            class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="Baja">Baja</option>
            <option value="Media">Media</option>
            <option value="Alta">Alta</option>
            <option value="Urgente">Urgente</option>
          </select>
        </div>

        <!-- Due date field -->
        <div class="mb-6">
          <label for="due_date" class="block text-sm font-medium text-gray-300 mb-2">Fecha de Vencimiento</label>
          <input 
            type="date" 
            id="due_date" 
            v-model="form.due_date"
            class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <!-- Assign users field -->
        <div class="mb-6">
          <div class="flex justify-between items-center pb-3 border-b border-gray-700 mb-4">
            <label class="text-sm font-medium text-gray-300">Usuarios Asignados</label>
            
            <button 
              type="button"
              @click="toggleUserSelector"
              class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 flex items-center text-sm"
            >
              <span v-if="!showUserSelector">Agregar Usuario</span>
              <span v-else>Cancelar</span>
            </button>
          </div>
          
          <!-- User selection interface -->
          <div v-if="showUserSelector" class="mb-4 bg-gray-750 p-4 rounded-md border border-gray-600">
            <div class="mb-3">
              <label for="user-search" class="block text-sm font-medium text-gray-300 mb-2">Buscar usuario</label>
              <input 
                id="user-search" 
                v-model="userSearchTerm" 
                type="text" 
                placeholder="Buscar por nombre, email o rol..." 
                class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            
            <div class="mb-3 max-h-48 overflow-y-auto border border-gray-600 rounded-md">
              <div v-if="filteredUsers.length === 0" class="p-4 text-center text-gray-400">
                <p v-if="userSearchTerm">No se encontraron usuarios para "{{ userSearchTerm }}"</p>
                <p v-else-if="users.length === 0">No hay usuarios disponibles</p>
                <p v-else>Todos los usuarios ya están asignados</p>
              </div>
              
              <div v-else class="divide-y divide-gray-700">
                <div 
                  v-for="user in filteredUsers" 
                  :key="user.id" 
                  @click="assignUser(user.id)"
                  class="p-3 flex justify-between items-center hover:bg-gray-700 cursor-pointer transition-colors duration-150"
                >
                  <div>
                    <span class="text-gray-200">{{ user.name }}</span>
                    <span class="text-gray-500 text-sm ml-2">({{ user.role }})</span>
                  </div>
                  <button type="button" class="text-indigo-400 hover:text-indigo-300">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <!-- List of assigned users -->
          <div v-if="assignedUsers.length === 0" class="text-gray-400 py-4 text-center bg-gray-750 rounded-md border border-gray-600 p-4">
            <p>Ningún usuario asignado. Asigne al menos un usuario responsable de la tarea.</p>
          </div>
          
          <div v-else class="space-y-2">
            <div class="mb-2 text-gray-400 text-sm">
              {{ assignedUsers.length }} usuario(s) asignado(s)
            </div>
            
            <div v-for="user in assignedUsers" :key="user.id" class="bg-gray-750 rounded-md p-3 flex justify-between items-center border border-gray-600">
              <div class="flex items-center">
                <div class="bg-indigo-600 w-8 h-8 rounded-full flex items-center justify-center text-white font-medium">
                  {{ user.name.substring(0, 1).toUpperCase() }}
                </div>
                <div class="ml-3">
                  <div class="text-gray-200">{{ user.name }}</div>
                  <div class="text-gray-500 text-sm">{{ user.role }}</div>
                </div>
              </div>
              <button 
                type="button"
                @click="removeUser(user.id)"
                class="text-red-400 hover:text-red-300 p-1"
                title="Eliminar asignación"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
          
          <!-- Hidden checkbox inputs to maintain form data -->
          <div class="hidden">
            <input 
              v-for="userId in form.assigned_users" 
              :key="userId"
              type="checkbox" 
              :value="userId" 
              v-model="form.assigned_users"
              checked
            />
          </div>
        </div>

        <!-- Submit button -->
        <div class="flex justify-end">
          <button 
            type="submit" 
            :disabled="submitting"
            class="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="submitting">
              <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Guardando...
            </span>
            <span v-else>{{ isEditMode ? 'Actualizar Tarea' : 'Crear Tarea' }}</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Todos los estilos son manejados con Tailwind */
</style> 