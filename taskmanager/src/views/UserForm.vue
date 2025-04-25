<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '../stores/users';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isEditMode = computed(() => !!route.params.id);
const title = computed(() => isEditMode.value ? 'Editar Usuario' : 'Crear Nuevo Usuario');

const form = ref({
  name: '',
  email: '',
  password: '',
  role: 'Desarrollador'
});

const loading = ref(false);
const error = ref('');
const successMessage = ref('');

onMounted(async () => {
  if (isEditMode.value) {
    loading.value = true;
    try {
      const userData = await userStore.fetchUserById(route.params.id);
      form.value.name = userData.name;
      form.value.email = userData.email;
      form.value.role = userData.role;
      // Note: We don't set the password for edit mode as it's usually not returned from API
    } catch (err) {
      error.value = 'Error al cargar datos del usuario. Por favor intente nuevamente.';
      console.error(err);
    } finally {
      loading.value = false;
    }
  }
});

const roleOptions = [
  { value: 'Desarrollador', label: 'Desarrollador' },
  { value: 'Líder Técnico', label: 'Líder Técnico' },
  { value: 'Administrador', label: 'Administrador' }
];

async function handleSubmit() {
  loading.value = true;
  error.value = '';
  successMessage.value = '';
  
  try {
    if (isEditMode.value) {
      // For edit, we may not want to send password if it's empty
      const userData = { ...form.value };
      if (!userData.password) {
        delete userData.password;
      }
      
      await userStore.updateUser(route.params.id, userData);
      successMessage.value = '¡Usuario actualizado correctamente!';
    } else {
      await userStore.createUser(form.value);
      successMessage.value = '¡Usuario creado correctamente!';
      // Reset form after successful creation
      form.value = {
        name: '',
        email: '',
        password: '',
        role: 'Desarrollador'
      };
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Error al guardar usuario. Por favor intente nuevamente.';
    console.error(err);
  } finally {
    loading.value = false;
  }
}

function goBack() {
  router.push('/users');
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 pb-12">
    <div class="container mx-auto max-w-2xl px-4 py-6">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-xl font-bold text-indigo-400">{{ title }}</h1>
        <button 
          @click="goBack" 
          class="px-4 py-2 border border-indigo-500 text-indigo-400 hover:bg-indigo-900/30 rounded-md transition-colors duration-200"
        >
          Volver a Usuarios
        </button>
      </div>
      
      <div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-700">
        <!-- Loading indicator -->
        <div v-if="loading" class="p-6 text-center">
          <svg class="animate-spin h-8 w-8 mx-auto mb-3 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p class="text-gray-400">Cargando datos del usuario...</p>
        </div>
        
        <!-- Error and success messages -->
        <div v-if="error" class="m-6 p-4 rounded bg-red-900/50 border border-red-700 text-red-200">
          {{ error }}
        </div>
        
        <div v-if="successMessage" class="m-6 p-4 rounded bg-green-900/50 border border-green-700 text-green-200">
          {{ successMessage }}
        </div>
        
        <!-- Form -->
        <form @submit.prevent="handleSubmit" class="p-6 space-y-6">
          <div>
            <label for="name" class="block text-sm font-medium text-gray-300 mb-2">Nombre</label>
            <input 
              id="name"
              v-model="form.name"
              type="text"
              required
              placeholder="Ingrese nombre del usuario"
              class="w-full px-4 py-3 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-300 mb-2">Email</label>
            <input 
              id="email"
              v-model="form.email"
              type="email"
              required
              placeholder="Ingrese email del usuario"
              :disabled="isEditMode"
              class="w-full px-4 py-3 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-300 mb-2">
              Contraseña 
              <span v-if="isEditMode" class="text-gray-500 text-xs">(Dejar en blanco para mantener la contraseña actual)</span>
            </label>
            <input 
              id="password"
              v-model="form.password"
              type="password"
              :required="!isEditMode"
              placeholder="Ingrese contraseña"
              class="w-full px-4 py-3 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
          </div>
          
          <div>
            <label for="role" class="block text-sm font-medium text-gray-300 mb-2">Rol</label>
            <select 
              id="role" 
              v-model="form.role" 
              required
              class="w-full px-4 py-3 rounded-md bg-gray-700 border border-gray-600 text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              <option v-for="option in roleOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
          
          <div class="flex justify-end space-x-4 pt-4">
            <button 
              type="button" 
              @click="goBack" 
              class="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-md transition-colors duration-200"
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              :disabled="loading"
              class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-md transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading" class="flex items-center">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Guardando...
              </span>
              <span v-else>{{ isEditMode ? 'Actualizar Usuario' : 'Crear Usuario' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Todos los estilos son manejados con clases de Tailwind */
</style> 