<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useTaskStore } from '../stores/tasks';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const taskStore = useTaskStore();
const authStore = useAuthStore();

const tasks = ref([]);
const loading = ref(false);
const error = ref('');
const currentUser = ref(authStore.user);

// Filters
const filters = ref({
  status: '',
  priority: '',
  user_id: '',
  due_date: ''
});

// Sorting
const sortBy = ref('due_date');
const sortDirection = ref('asc');

onMounted(async () => {
  await fetchTasks();
});

async function fetchTasks() {
  loading.value = true;
  error.value = '';
  
  try {
    // Build filter params
    const params = {};
    if (filters.value.status) {
      params.status = filters.value.status;
    }
    if (filters.value.priority) {
      params.priority = filters.value.priority;
    }
    if (filters.value.user_id) {
      params.user_id = filters.value.user_id;
    }
    if (filters.value.due_date) {
      params.due_date = filters.value.due_date;
    }
    
    const fetchedTasks = await taskStore.fetchTasks(params);
    
    // Client-side sorting if API doesn't support it
    tasks.value = sortTasks(fetchedTasks);
  } catch (err) {
    error.value = 'Error al cargar las tareas. Por favor intente nuevamente.';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function sortTasks(taskList) {
  return [...taskList].sort((a, b) => {
    let valueA, valueB;
    
    // Determine values to compare based on sort field
    switch(sortBy.value) {
      case 'title':
        valueA = a.title.toLowerCase();
        valueB = b.title.toLowerCase();
        break;
      case 'status':
        valueA = a.status;
        valueB = b.status;
        break;
      case 'priority':
        // Custom priority order: Urgente > Alta > Media > Baja
        const priorityOrder = { 'Urgente': 4, 'Alta': 3, 'Media': 2, 'Baja': 1 };
        valueA = priorityOrder[a.priority] || 0;
        valueB = priorityOrder[b.priority] || 0;
        break;
      case 'due_date':
        valueA = new Date(a.due_date || '9999-12-31');
        valueB = new Date(b.due_date || '9999-12-31');
        break;
      default:
        valueA = a[sortBy.value];
        valueB = b[sortBy.value];
    }
    
    // Compare values based on direction
    if (sortDirection.value === 'asc') {
      return valueA > valueB ? 1 : -1;
    } else {
      return valueA < valueB ? 1 : -1;
    }
  });
}

function applyFilters() {
  fetchTasks();
}

function resetFilters() {
  filters.value = {
    status: '',
    priority: '',
    user_id: '',
    due_date: ''
  };
  fetchTasks();
}

function setSorting(field) {
  if (sortBy.value === field) {
    // Toggle direction if clicking on the same field
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    // Set new field and default to ascending
    sortBy.value = field;
    sortDirection.value = 'asc';
  }
  
  // Re-sort the current tasks
  tasks.value = sortTasks(tasks.value);
}

function createTask() {
  router.push('/tasks/new');
}

function viewTaskDetails(id) {
  router.push(`/tasks/${id}`);
}

function editTask(id) {
  router.push(`/tasks/${id}/edit`);
}

// Options for filters
const statusOptions = [
  { value: '', label: 'Todos los Estados' },
  { value: 'Pendiente', label: 'Pendiente' },
  { value: 'En Progreso', label: 'En Progreso' },
  { value: 'Bloqueada', label: 'Bloqueada' },
  { value: 'En Revisión', label: 'En Revisión' },
  { value: 'Completada', label: 'Completada' }
];

const priorityOptions = [
  { value: '', label: 'Todas las Prioridades' },
  { value: 'Baja', label: 'Baja' },
  { value: 'Media', label: 'Media' },
  { value: 'Alta', label: 'Alta' },
  { value: 'Urgente', label: 'Urgente' }
];

// Get priority color class
function getPriorityClass(priority) {
  switch (priority.toLowerCase()) {
    case 'baja': return 'priority-baja';
    case 'media': return 'priority-media';
    case 'alta': return 'priority-alta';
    case 'urgente': return 'priority-urgente';
    default: return '';
  }
}

// Get status color class
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

// Format date
function formatDate(dateString) {
  if (!dateString) return 'Sin fecha';
  const date = new Date(dateString);
  return date.toLocaleDateString();
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 pb-12">
    <div class="container mx-auto px-4 py-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-xl font-bold text-indigo-400">Tareas</h1>
        <button @click="createTask" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 flex items-center">
          <span class="mr-2">+</span> Crear Nueva Tarea
        </button>
      </div>
      
      <div class="bg-gray-800 rounded-lg shadow-lg p-6 mb-6 border border-gray-700">
        <h2 class="text-lg font-semibold text-gray-200 pb-3 border-b border-gray-700 mb-4">Filtros</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Estado</label>
            <select 
              v-model="filters.status" 
              class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option v-for="option in statusOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Prioridad</label>
            <select 
              v-model="filters.priority" 
              class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option v-for="option in priorityOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-300 mb-2">Fecha de Vencimiento</label>
            <input 
              type="date" 
              v-model="filters.due_date" 
              class="w-full px-3 py-2 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          
          <div class="flex items-end gap-2">
            <button 
              @click="applyFilters" 
              class="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200"
            >
              Aplicar Filtros
            </button>
            <button 
              @click="resetFilters" 
              class="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-md transition-colors duration-200"
            >
              Reiniciar
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
          <p class="text-gray-400">Cargando tareas...</p>
        </div>
        
        <div v-else-if="tasks.length === 0" class="text-center py-12">
          <div class="text-5xl mb-3">📋</div>
          <p class="text-gray-400">No se encontraron tareas. Intente cambiar los filtros o crear una nueva tarea.</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-750">
              <tr class="text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                <th 
                  @click="setSorting('title')" 
                  class="px-6 py-3 cursor-pointer hover:text-indigo-400"
                >
                  Título 
                  <span v-if="sortBy === 'title'">
                    {{ sortDirection === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th 
                  @click="setSorting('status')" 
                  class="px-6 py-3 cursor-pointer hover:text-indigo-400"
                >
                  Estado 
                  <span v-if="sortBy === 'status'">
                    {{ sortDirection === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th 
                  @click="setSorting('priority')" 
                  class="px-6 py-3 cursor-pointer hover:text-indigo-400"
                >
                  Prioridad 
                  <span v-if="sortBy === 'priority'">
                    {{ sortDirection === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th 
                  @click="setSorting('due_date')" 
                  class="px-6 py-3 cursor-pointer hover:text-indigo-400"
                >
                  Fecha de Vencimiento 
                  <span v-if="sortBy === 'due_date'">
                    {{ sortDirection === 'asc' ? '↑' : '↓' }}
                  </span>
                </th>
                <th class="px-6 py-3">Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="task in tasks" :key="task.id" class="bg-gray-800 border-t border-gray-700 hover:bg-gray-750 transition-colors duration-150">
                <td class="px-6 py-4 font-medium text-gray-200">{{ task.title }}</td>
                <td class="px-6 py-4">
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
                </td>
                <td class="px-6 py-4">
                  <span :class="[
                    'px-2 py-1 text-xs rounded-full',
                    task.priority === 'Baja' ? 'bg-blue-900 text-blue-200' :
                    task.priority === 'Media' ? 'bg-yellow-900 text-yellow-200' :
                    task.priority === 'Alta' ? 'bg-orange-900 text-orange-200' :
                    'bg-red-900 text-red-200'
                  ]">
                    {{ task.priority }}
                  </span>
                </td>
                <td class="px-6 py-4 text-gray-400">{{ formatDate(task.due_date) }}</td>
                <td class="px-6 py-4">
                  <div class="flex items-center space-x-2">
                    <button 
                      @click="viewTaskDetails(task.id)" 
                      class="p-1 text-indigo-400 hover:text-indigo-300"
                      title="Ver"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                        <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd" />
                      </svg>
                    </button>
                    <!-- <button 
                      @click="editTask(task.id)" 
                      class="p-1 text-yellow-500 hover:text-yellow-400"
                      title="Editar"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                      </svg>
                    </button> -->
                  </div>
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