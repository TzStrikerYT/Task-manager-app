from abc import ABC, abstractmethod
from typing import List, Set
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Observer(ABC):
    """Observer interface."""
    
    @abstractmethod
    def update(self, subject, *args, **kwargs):
        """Update method called by the subject."""
        pass


class Subject(ABC):
    """Subject interface."""
    
    def __init__(self):
        self._observers: Set[Observer] = set()
    
    def attach(self, observer: Observer):
        """Attach an observer to the subject."""
        self._observers.add(observer)
    
    def detach(self, observer: Observer):
        """Detach an observer from the subject."""
        self._observers.discard(observer)
    
    def notify(self, *args, **kwargs):
        """Notify all observers."""
        for observer in self._observers:
            observer.update(self, *args, **kwargs)


class TaskCompletionObserver(Observer):
    """Observer for task completion events."""
    
    def update(self, subject, *args, **kwargs):
        """Handle task completion notification."""
        task = kwargs.get('task')
        if task:
            # Log the notification
            logger.info(f"Task '{task.title}' (ID: {task.id}) has been completed!")
            
            # Simulate email sending to tech leads
            for user in kwargs.get('tech_leads', []):
                logger.info(f"Sending email notification to Tech Lead: {user.name} <{user.email}>")
                

class TaskNotifier(Subject):
    """Subject class for task notifications."""
    
    def notify_task_completion(self, task, tech_leads):
        """Notify observers about task completion."""
        self.notify(task=task, tech_leads=tech_leads) 