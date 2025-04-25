from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entity import User, Role, Task, TaskStatus, TaskPriority

class UserRepository(ABC):
    """Port for user repository."""
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user in the repository."""
        pass
    
    @abstractmethod
    def get_all(self, role: Optional[Role] = None, search_term: Optional[str] = None) -> List[User]:
        """Get all users, optionally filtered by role and search term."""
        pass
    
    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        pass
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Update a user in the repository."""
        pass

class TaskRepository(ABC):
    """Port for task repository."""
    
    @abstractmethod
    def create(self, task: Task) -> Task:
        """Create a new task in the repository."""
        pass
    
    @abstractmethod
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks, optionally filtered."""
        pass
    
    @abstractmethod
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        pass
    
    @abstractmethod
    def update(self, task: Task) -> Task:
        """Update a task in the repository."""
        pass
    
    @abstractmethod
    def delete(self, task_id: int) -> bool:
        """Delete a task from the repository."""
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: int, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks assigned to a user, optionally filtered."""
        pass
    
    @abstractmethod
    def get_by_status(self, status: TaskStatus, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks with a specific status, optionally filtered."""
        pass
    
    @abstractmethod
    def get_by_priority(self, priority: TaskPriority, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks with a specific priority, optionally filtered."""
        pass
    
    @abstractmethod
    def get_by_due_date(self, due_date: datetime, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks with a specific due date, optionally filtered."""
        pass
    
    @abstractmethod
    def assign_user(self, task_id: int, user_id: int) -> Task:
        """Assign a user to a task."""
        pass
    
    @abstractmethod
    def unassign_user(self, task_id: int, user_id: int) -> Task:
        """Unassign a user from a task."""
        pass 