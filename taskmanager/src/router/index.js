import { createRouter, createWebHistory } from 'vue-router';
import authService from '../services/auth';

// Lazy-loaded components
const Login = () => import('../views/Login.vue');
const Dashboard = () => import('../views/Dashboard.vue');
const NotFound = () => import('../views/NotFound.vue');
const TaskList = () => import('../views/TaskList.vue');
const TaskDetail = () => import('../views/TaskDetail.vue');
const TaskForm = () => import('../views/TaskForm.vue');
const UserList = () => import('../views/UserList.vue');
const UserForm = () => import('../views/UserForm.vue');

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks',
    name: 'TaskList',
    component: TaskList,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/new',
    name: 'CreateTask',
    component: TaskForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/:id',
    name: 'TaskDetail',
    component: TaskDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/tasks/:id/edit',
    name: 'EditTask',
    component: TaskForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserList',
    component: UserList,
    meta: { requiresAuth: true }
  },
  {
    path: '/users/new',
    name: 'CreateUser',
    component: UserForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/users/:id/edit',
    name: 'EditUser',
    component: UserForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.isAuthenticated();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    next('/dashboard');
  } else {
    next();
  }
});

export default router; 