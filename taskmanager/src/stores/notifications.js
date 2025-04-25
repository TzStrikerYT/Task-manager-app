import { defineStore } from 'pinia';

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    nextId: 1
  }),

  actions: {
    add(notification) {
      const id = this.nextId++;
      const newNotification = {
        id,
        message: notification.message,
        type: notification.type || 'info',
        timeout: notification.timeout || 5000,
        timestamp: new Date()
      };
      
      this.notifications.push(newNotification);
      
      // Eliminar automáticamente después del tiempo especificado
      if (newNotification.timeout > 0) {
        setTimeout(() => {
          this.remove(id);
        }, newNotification.timeout);
      }
      
      return id;
    },
    
    success(message, timeout = 5000) {
      return this.add({
        message,
        type: 'success',
        timeout
      });
    },
    
    error(message, timeout = 8000) {
      return this.add({
        message,
        type: 'error',
        timeout
      });
    },
    
    info(message, timeout = 5000) {
      return this.add({
        message,
        type: 'info',
        timeout
      });
    },
    
    warning(message, timeout = 6000) {
      return this.add({
        message,
        type: 'warning',
        timeout
      });
    },
    
    remove(id) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index !== -1) {
        this.notifications.splice(index, 1);
      }
    },
    
    clear() {
      this.notifications = [];
    }
  }
}); 