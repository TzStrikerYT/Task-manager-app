from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from app.domain.entity import Task, TaskPriority, TaskStatus

class TaskFactory(ABC):
    """Abstract task factory."""
    
    @abstractmethod
    def create_task(self, title: str, description: str, due_date: Optional[datetime] = None,
                   assigned_users: List = None, creator_id: Optional[int] = None) -> Task:
        """Create a task with default properties based on type."""
        pass


class LowPriorityTaskFactory(TaskFactory):
    """Factory for low priority tasks."""
    
    def create_task(self, title: str, description: str, due_date: Optional[datetime] = None,
                   assigned_users: List = None, creator_id: Optional[int] = None) -> Task:
        """Create a low priority task."""
        return Task(
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=TaskPriority.LOW,
            due_date=due_date,
            assigned_users=assigned_users or [],
            creator_id=creator_id
        )


class MediumPriorityTaskFactory(TaskFactory):
    """Factory for medium priority tasks."""
    
    def create_task(self, title: str, description: str, due_date: Optional[datetime] = None,
                   assigned_users: List = None, creator_id: Optional[int] = None) -> Task:
        """Create a medium priority task."""
        return Task(
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=TaskPriority.MEDIUM,
            due_date=due_date,
            assigned_users=assigned_users or [],
            creator_id=creator_id
        )


class HighPriorityTaskFactory(TaskFactory):
    """Factory for high priority tasks."""
    
    def create_task(self, title: str, description: str, due_date: Optional[datetime] = None,
                   assigned_users: List = None, creator_id: Optional[int] = None) -> Task:
        """Create a high priority task."""
        return Task(
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            due_date=due_date,
            assigned_users=assigned_users or [],
            creator_id=creator_id
        )


class UrgentPriorityTaskFactory(TaskFactory):
    """Factory for urgent priority tasks."""
    
    def create_task(self, title: str, description: str, due_date: Optional[datetime] = None,
                   assigned_users: List = None, creator_id: Optional[int] = None) -> Task:
        """Create an urgent priority task."""
        return Task(
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=TaskPriority.URGENT,
            due_date=due_date,
            assigned_users=assigned_users or [],
            creator_id=creator_id
        )


class TaskFactoryProvider:
    """Provider class for obtaining the appropriate task factory."""
    
    @staticmethod
    def get_factory(priority: TaskPriority) -> TaskFactory:
        """Get the appropriate factory based on priority."""
        factories = {
            TaskPriority.LOW: LowPriorityTaskFactory(),
            TaskPriority.MEDIUM: MediumPriorityTaskFactory(),
            TaskPriority.HIGH: HighPriorityTaskFactory(),
            TaskPriority.URGENT: UrgentPriorityTaskFactory(),
        }
        
        return factories.get(priority, MediumPriorityTaskFactory()) 