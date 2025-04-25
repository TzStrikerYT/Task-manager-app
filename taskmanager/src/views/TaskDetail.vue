<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useTaskStore } from '../stores/tasks';
import { useUserStore } from '../stores/users';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notifications';

const route = useRoute();
const router = useRouter();
const taskStore = useTaskStore();
const userStore = useUserStore();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const task = ref(null);
const users = ref([]);
const loading = ref(false);
const error = ref('');
const currentUser = ref(authStore.user);

// For status update
const newStatus = ref('');
const statusOptions = [
  { value: 'Pendiente', label: 'Pendiente' },
  { value: 'En Progreso', label: 'En Progreso' },
  { value: 'Bloqueada', label: 'Bloqueada' },
  { value: 'En Revisión', label: 'En Revisión' },
  { value: 'Completada', label: 'Completada' }
];

// For priority update
const newPriority = ref('');
const priorityOptions = [
  { value: 'Baja', label: 'Baja' },
  { value: 'Media', label: 'Media' },
  { value: 'Alta', label: 'Alta' },
  { value: 'Urgente', label: 'Urgente' }
];

// For user assignment
const selectedUserId = ref('');
const userSearchTerm = ref('');
const showUserSelector = ref(false);

onMounted(async () => {
  await fetchTaskData();
  await fetchUsers();
  
  // Debug assigned users después de cargar los datos
  setTimeout(() => {
    if (task.value && task.value.assigned_users) {
      console.log('Usuarios asignados (después de cargar):', JSON.stringify(task.value.assigned_users));
    } else {
      console.log('No hay usuarios asignados o la estructura es diferente');
      console.log('Task:', task.value);
    }
  }, 1000);
});

async function fetchTaskData() {
  loading.value = true;
  error.value = '';
  
  try {
    const taskData = await taskStore.fetchTaskById(route.params.id);
    task.value = taskData;
    
    // Set current values for status and priority
    newStatus.value = taskData.status;
    newPriority.value = taskData.priority;
    
    // Debug assigned users
    console.log('Asignados a la tarea:', taskData.assigned_users);
    if (taskData.assigned_users) {
      console.log('Número de usuarios asignados:', taskData.assigned_users.length);
    }
  } catch (err) {
    error.value = 'Error al cargar los datos de la tarea. Por favor, intente nuevamente.';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function fetchUsers() {
  try {
    const fetchedUsers = await userStore.fetchUsers();
    users.value = fetchedUsers;
    console.log('Usuarios cargados:', fetchedUsers.length);
  } catch (err) {
    console.error('Error al cargar usuarios:', err);
  }
}

async function updateTaskStatus() {
  if (newStatus.value === task.value.status) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    await taskStore.updateTaskStatus(task.value.id, newStatus.value);
    notificationStore.success('¡Estado de la tarea actualizado correctamente!');
    await fetchTaskData(); // Refresh task data
  } catch (err) {
    const errorMsg = err.response?.data?.error || 'Error al actualizar el estado de la tarea.';
    error.value = errorMsg;
    notificationStore.error(errorMsg);
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function updateTaskPriority() {
  if (newPriority.value === task.value.priority) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    await taskStore.updateTaskPriority(task.value.id, newPriority.value);
    notificationStore.success('¡Prioridad de la tarea actualizada correctamente!');
    await fetchTaskData(); // Refresh task data
  } catch (err) {
    const errorMsg = err.response?.data?.error || 'Error al actualizar la prioridad de la tarea.';
    error.value = errorMsg;
    notificationStore.error(errorMsg);
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function assignUser() {
  if (!selectedUserId.value) return;
  
  loading.value = true;
  error.value = '';
  
  try {
    await taskStore.assignUserToTask(task.value.id, selectedUserId.value);
    notificationStore.success('¡Usuario asignado correctamente!');
    selectedUserId.value = ''; // Reset selection
    userSearchTerm.value = ''; // Clear search term
    showUserSelector.value = false; // Hide user selector
    await fetchTaskData(); // Refresh task data
  } catch (err) {
    const errorMsg = err.response?.data?.error || 'Error al asignar usuario a la tarea.';
    error.value = errorMsg;
    notificationStore.error(errorMsg);
    console.error(err);
  } finally {
    loading.value = false;
  }
}

async function unassignUser(userId) {
  loading.value = true;
  error.value = '';
  
  try {
    await taskStore.unassignUserFromTask(task.value.id, userId);
    notificationStore.success('¡Usuario desasignado correctamente!');
    await fetchTaskData(); // Refresh task data
  } catch (err) {
    const errorMsg = err.response?.data?.error || 'Error al desasignar usuario de la tarea.';
    error.value = errorMsg;
    notificationStore.error(errorMsg);
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function editTask() {
  router.push(`/tasks/${task.value.id}/edit`);
}

function goBack() {
  router.push('/tasks');
}

// Helper functions
function formatDate(dateString) {
  if (!dateString) return 'Sin fecha';
  const date = new Date(dateString);
  return date.toLocaleString();
}

function getPriorityClass(priority) {
  switch (priority.toLowerCase()) {
    case 'baja': return 'priority-baja';
    case 'media': return 'priority-media';
    case 'alta': return 'priority-alta';
    case 'urgente': return 'priority-urgente';
    default: return '';
  }
}

function getStatusClass(status) {
  switch (status.toLowerCase().replace(' ', '-')) {
    case 'pendiente': return 'status-pendiente';
    case 'en-progreso': return 'status-en-progreso';
    case 'bloqueada': return 'status-bloqueada';
    case 'en-revisión': return 'status-en-revision';
    case 'completada': return 'status-completada';
    default: return '';
  }
}

// Check if current user is assigned to the task
function isUserAssigned() {
  if (!task.value || !currentUser.value) return false;
  return task.value.assigned_users.some(user => user.id === currentUser.value.id);
}

// Check if current user can edit the task
function canEditTask() {
  if (!task.value || !currentUser.value) return false;
  
  // Admins and Tech Leads can always edit
  if (currentUser.value.role === 'Administrador' || currentUser.value.role === 'Líder Técnico') {
    return true;
  }
  
  // Task creator can edit
  if (task.value.creator_id === currentUser.value.id) {
    return true;
  }
  
  // Assigned users can edit some aspects
  return isUserAssigned();
}

// Filtered users for the dropdown
const filteredUsers = computed(() => {
  if (!users.value) {
    console.log('No hay usuarios cargados');
    return [];
  }
  
  if (!task.value) {
    console.log('No hay tarea cargada');
    return [];
  }
  
  console.log('Total usuarios:', users.value.length);
  console.log('Usuarios asignados:', task.value.assigned_users?.length || 0);
  
  // Si no hay assigned_users, mostrar todos los usuarios
  if (!task.value.assigned_users) {
    return users.value.filter(user => {
      return !userSearchTerm.value || 
        user.name.toLowerCase().includes(userSearchTerm.value.toLowerCase()) || 
        (user.email && user.email.toLowerCase().includes(userSearchTerm.value.toLowerCase())) ||
        user.role.toLowerCase().includes(userSearchTerm.value.toLowerCase());
    });
  }
  
  const filtered = users.value.filter(user => {
    // Filter out already assigned users
    const isAlreadyAssigned = task.value.assigned_users.some(assignedUser => assignedUser.id === user.id);
    
    // Filter by search term (case insensitive)
    const matchesSearch = !userSearchTerm.value || 
      user.name.toLowerCase().includes(userSearchTerm.value.toLowerCase()) || 
      (user.email && user.email.toLowerCase().includes(userSearchTerm.value.toLowerCase())) ||
      user.role.toLowerCase().includes(userSearchTerm.value.toLowerCase());
    
    return !isAlreadyAssigned && matchesSearch;
  });
  
  console.log('Usuarios filtrados disponibles:', filtered.length);
  return filtered;
});

// Toggle user selector
function toggleUserSelector() {
  showUserSelector.value = !showUserSelector.value;
  if (showUserSelector.value) {
    userSearchTerm.value = '';
    // Asegurar que los usuarios estén cargados
    if (users.value.length === 0) {
      fetchUsers();
    }
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 pb-12">
    <div class="container mx-auto max-w-4xl px-4 py-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-xl font-bold text-indigo-400">Detalles de la Tarea</h1>
        <div class="flex space-x-3">
          <button 
            @click="goBack" 
            class="px-4 py-2 border border-indigo-500 text-indigo-400 hover:bg-indigo-900/30 rounded-md transition-colors duration-200"
          >
            Volver a Tareas
          </button>
          <!-- <button 
            v-if="canEditTask()" 
            @click="editTask"
            class="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-md transition-colors duration-200"
          >
            Editar Tarea
          </button> -->
        </div>
      </div>
      
      <!-- Loading state -->
      <div v-if="loading" class="bg-gray-800 rounded-lg shadow-lg p-12 text-center border border-gray-700">
        <svg class="animate-spin h-10 w-10 mx-auto mb-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-400">Cargando detalles de la tarea...</p>
      </div>
      
      <!-- Error message -->
      <div v-else-if="error" class="bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-700">
        <div class="p-4 rounded bg-red-900/50 border border-red-700 text-red-200">
          {{ error }}
        </div>
        <div class="mt-4 text-center">
          <button @click="goBack" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-md transition-colors duration-200">
            Volver a Tareas
          </button>
        </div>
      </div>
      
      <!-- Task details -->
      <div v-else-if="task" class="space-y-6">
        <!-- Main task info -->
        <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
          <div class="p-6">
            <div class="flex justify-between items-start mb-4">
              <h2 class="text-xl font-semibold text-gray-200">{{ task.title }}</h2>
              <span :class="[
                'px-2 py-1 text-xs rounded-full', 
                task.priority === 'Baja' ? 'bg-blue-900 text-blue-200' :
                task.priority === 'Media' ? 'bg-yellow-900 text-yellow-200' :
                task.priority === 'Alta' ? 'bg-orange-900 text-orange-200' :
                'bg-red-900 text-red-200'
              ]">
                {{ task.priority }}
              </span>
            </div>
            
            <div class="mb-6">
              <span :class="[
                'px-2 py-1 text-xs rounded', 
                task.status === 'Pendiente' ? 'bg-gray-700 text-gray-300' :
                task.status === 'En Progreso' ? 'bg-indigo-900 text-indigo-200' :
                task.status === 'Bloqueada' ? 'bg-red-900 text-red-200' :
                task.status === 'En Revisión' ? 'bg-yellow-900 text-yellow-200' :
                'bg-green-900 text-green-200'
              ]">
                {{ task.status }}
              </span>
            </div>
            
            <div class="mb-6">
              <h3 class="text-md font-medium text-gray-300 mb-2">Descripción</h3>
              <p class="text-gray-400 whitespace-pre-line bg-gray-750 p-4 rounded-md">{{ task.description }}</p>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <h3 class="text-md font-medium text-gray-300 mb-2">Creada</h3>
                <p class="text-gray-400">{{ formatDate(task.created_at) }}</p>
              </div>
              
              <div>
                <h3 class="text-md font-medium text-gray-300 mb-2">Última Actualización</h3>
                <p class="text-gray-400">{{ formatDate(task.updated_at) }}</p>
              </div>
              
              <div>
                <h3 class="text-md font-medium text-gray-300 mb-2">Fecha de Vencimiento</h3>
                <p class="text-gray-400">{{ formatDate(task.due_date) }}</p>
              </div>
              
              <div>
                <h3 class="text-md font-medium text-gray-300 mb-2">Creada Por</h3>
                <p class="text-gray-400">{{ task.created_by ? task.created_by.name : 'Desconocido' }}</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Assigned users -->
        <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
          <div class="p-6">
            <div class="flex justify-between items-center pb-3 border-b border-gray-700 mb-4">
              <h3 class="text-lg font-semibold text-gray-200">Usuarios Asignados</h3>
              
              <button 
                v-if="canEditTask()" 
                @click="toggleUserSelector"
                class="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 flex items-center text-sm"
              >
                <span v-if="!showUserSelector">Agregar Usuario</span>
                <span v-else>Cancelar</span>
              </button>
            </div>
            
            <!-- User assignment UI -->
            <div v-if="showUserSelector && canEditTask()" class="mb-6 bg-gray-750 p-4 rounded-md border border-gray-600">
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
                  <p v-else-if="users.length === 0">
                    No hay usuarios cargados.
                    <button 
                      @click="fetchUsers" 
                      class="text-indigo-400 hover:text-indigo-300 ml-2 underline"
                    >
                      Recargar usuarios
                    </button>
                  </p>
                  <p v-else>
                    Todos los usuarios ya están asignados a esta tarea.
                  </p>
                </div>
                
                <div v-else class="divide-y divide-gray-700">
                  <div 
                    v-for="user in filteredUsers" 
                    :key="user.id" 
                    @click="selectedUserId = user.id; assignUser()"
                    class="p-3 flex justify-between items-center hover:bg-gray-700 cursor-pointer transition-colors duration-150"
                  >
                    <div>
                      <span class="text-gray-200">{{ user.name }}</span>
                      <span class="text-gray-500 text-sm ml-2">({{ user.role }})</span>
                    </div>
                    <button class="text-indigo-400 hover:text-indigo-300">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- List of assigned users -->
            <div v-if="!task || !task.assigned_users" class="text-gray-400 py-4 text-center">
              <p>Cargando usuarios asignados...</p>
            </div>
            
            <div v-else-if="task.assigned_users.length === 0" class="text-gray-400 py-4 text-center">
              <p>Aún no hay usuarios asignados a esta tarea.</p>
            </div>
            
            <div v-else class="space-y-2">
              <div class="mb-2 text-gray-400 text-sm">
                {{ task.assigned_users.length }} usuario(s) asignado(s)
              </div>
              
              <div v-for="user in task.assigned_users" :key="user.id" class="bg-gray-750 rounded-md p-3 flex justify-between items-center border border-gray-700">
                <div class="flex items-center">
                  <div class="bg-indigo-600 w-8 h-8 rounded-full flex items-center justify-center text-white font-medium">
                    {{ user.name && user.name.length > 0 ? user.name.substring(0, 1).toUpperCase() : '?' }}
                  </div>
                  <div class="ml-3">
                    <div class="text-gray-200">{{ user.name || 'Usuario' }}</div>
                    <div class="text-gray-500 text-sm">{{ user.role || 'Sin rol' }}</div>
                  </div>
                </div>
                <button 
                  v-if="canEditTask()" 
                  @click="unassignUser(user.id)"
                  class="text-red-400 hover:text-red-300 p-1"
                  :disabled="loading"
                  title="Eliminar asignación"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Update task status/priority section -->
        <div v-if="canEditTask()" class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
          <div class="p-6">
            <h3 class="text-lg font-semibold text-gray-200 pb-3 border-b border-gray-700 mb-4">Actualizar Tarea</h3>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label for="status-select" class="block text-sm font-medium text-gray-300 mb-2">Estado</label>
                <div class="flex items-end gap-3">
                  <select 
                    id="status-select" 
                    v-model="newStatus"
                    class="flex-1 px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                      {{ option.label }}
                    </option>
                  </select>
                  <button 
                    @click="updateTaskStatus" 
                    :disabled="newStatus === task.status || loading"
                    class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Actualizar
                  </button>
                </div>
              </div>
              
              <div>
                <label for="priority-select" class="block text-sm font-medium text-gray-300 mb-2">Prioridad</label>
                <div class="flex items-end gap-3">
                  <select 
                    id="priority-select" 
                    v-model="newPriority"
                    class="flex-1 px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  >
                    <option v-for="option in priorityOptions" :key="option.value" :value="option.value">
                      {{ option.label }}
                    </option>
                  </select>
                  <button 
                    @click="updateTaskPriority" 
                    :disabled="newPriority === task.priority || loading"
                    class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Actualizar
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Todos los estilos son manejados con clases de Tailwind */
</style> 