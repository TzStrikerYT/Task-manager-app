from typing import List, Optional, Dict, Any
from datetime import datetime
from app.domain.entity import Task, User, TaskStatus, TaskPriority, Role
from app.domain.observer import TaskNotifier, TaskCompletionObserver
from app.domain.factory import TaskFactoryProvider
from app.application.ports import TaskRepository, UserRepository

class TaskService:
    """Service for handling tasks."""
    
    def __init__(self, task_repository: TaskRepository, user_repository: UserRepository):
        self.task_repository = task_repository
        self.user_repository = user_repository
        
        # Initialize the task notifier and observer
        self.task_notifier = TaskNotifier()
        self.task_completion_observer = TaskCompletionObserver()
        self.task_notifier.attach(self.task_completion_observer)
    
    def create_task(
        self,
        title: str,
        description: str,
        priority: TaskPriority,
        due_date: Optional[datetime],
        assigned_user_ids: List[int],
        creator_id: int
    ) -> Task:
        """Create a new task using the Factory pattern."""
        # Validate that the creator exists
        creator = self.user_repository.get_by_id(creator_id)
        if not creator:
            raise ValueError(f"Creator with ID {creator_id} not found")
        
        # Get assigned users
        assigned_users = []
        for user_id in assigned_user_ids:
            user = self.user_repository.get_by_id(user_id)
            if user:
                assigned_users.append(user)
            else:
                raise ValueError(f"User with ID {user_id} not found")
        
        # Use the factory to create a task with the appropriate priority
        factory = TaskFactoryProvider.get_factory(priority)
        task = factory.create_task(
            title=title,
            description=description,
            due_date=due_date,
            assigned_users=assigned_users,
            creator_id=creator_id
        )
        
        return self.task_repository.create(task)
    
    def get_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        user_id: Optional[int] = None,
        due_date: Optional[datetime] = None,
        requesting_user: Optional[User] = None
    ) -> List[Task]:
        """Get tasks with optional filtering."""
        filters = {}
        
        # If user doesn't have permission to view completed tasks and we're not explicitly 
        # requesting completed tasks, filter them out
        if requesting_user and not requesting_user.has_permission("view_all_completed_tasks"):
            if status == TaskStatus.COMPLETED:
                # Only Tech Leads should see completed tasks, return empty list for other roles
                return []
        
        # Apply provided filters
        if user_id:
            tasks = self.task_repository.get_by_user_id(user_id, filters)
        elif status:
            tasks = self.task_repository.get_by_status(status, filters)
        elif priority:
            tasks = self.task_repository.get_by_priority(priority, filters)
        elif due_date:
            tasks = self.task_repository.get_by_due_date(due_date, filters)
        else:
            tasks = self.task_repository.get_all(filters)
        
        # Filter out completed tasks for non-Tech Leads when getting all tasks
        if not status and requesting_user and not requesting_user.has_permission("view_all_completed_tasks"):
            tasks = [task for task in tasks if task.status != TaskStatus.COMPLETED]
            
        return tasks
    
    def get_task_by_id(self, task_id: int, user: Optional[User] = None) -> Optional[Task]:
        """Get a task by ID."""
        task = self.task_repository.get_by_id(task_id)
        
        # Check permissions for viewing completed tasks
        if task and task.status == TaskStatus.COMPLETED and user:
            if not user.has_permission("view_all_completed_tasks"):
                # Only Tech Leads can see completed tasks
                return None
        
        return task
    
    def update_task_status(self, task_id: int, status: TaskStatus, user: User) -> Task:
        """Update the status of a task."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Check if user is assigned to this task or has special permissions
        is_assigned = any(assigned_user.id == user.id for assigned_user in task.assigned_users)
        is_creator = task.creator_id == user.id
        is_admin_or_lead = user.role in [Role.ADMIN, Role.TECH_LEAD]
        
        if not (is_assigned or is_creator or is_admin_or_lead):
            raise ValueError("You don't have permission to update this task")
        
        # Check if moving to completed, which might have restrictions
        if status == TaskStatus.COMPLETED and not user.has_permission("complete_any_task"):
            # Only allow if user is assigned to the task
            if not is_assigned and not is_admin_or_lead:
                raise ValueError("You don't have permission to mark this task as completed")
        
        # Update the task status
        old_status = task.status
        task.update_status(status)
        updated_task = self.task_repository.update(task)
        
        # Notify observers if task is completed
        if status == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
            # Get all tech leads
            tech_leads = self.user_repository.get_all(Role.TECH_LEAD)
            
            # Notify the observer
            self.task_notifier.notify_task_completion(updated_task, tech_leads)
        
        return updated_task
    
    def update_task_priority(self, task_id: int, priority: TaskPriority, user: User) -> Task:
        """Update the priority of a task."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Only creators, admins and tech leads can change priority
        is_creator = task.creator_id == user.id
        is_admin_or_lead = user.role in [Role.ADMIN, Role.TECH_LEAD]
        
        if not (is_creator or is_admin_or_lead):
            raise ValueError("You don't have permission to update this task's priority")
        
        task.update_priority(priority)
        return self.task_repository.update(task)
    
    def assign_user_to_task(self, task_id: int, user_id: int, assigning_user: User) -> Task:
        """Assign a user to a task."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check if assigning user has permission
        is_creator = task.creator_id == assigning_user.id
        is_admin_or_lead = assigning_user.role in [Role.ADMIN, Role.TECH_LEAD]
        
        if not (is_creator or is_admin_or_lead):
            raise ValueError("You don't have permission to assign users to this task")
        
        return self.task_repository.assign_user(task_id, user_id)
    
    def unassign_user_from_task(self, task_id: int, user_id: int, assigning_user: User) -> Task:
        """Unassign a user from a task."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Check if assigning user has permission
        is_creator = task.creator_id == assigning_user.id
        is_admin_or_lead = assigning_user.role in [Role.ADMIN, Role.TECH_LEAD]
        is_self_unassign = assigning_user.id == user_id
        
        if not (is_creator or is_admin_or_lead or is_self_unassign):
            raise ValueError("You don't have permission to unassign users from this task")
        
        return self.task_repository.unassign_user(task_id, user_id)
    
    def update_task(self, task_id: int, updates: Dict[str, Any], user: User) -> Task:
        """Update multiple fields of a task at once."""
        task = self.task_repository.get_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Verify permissions (only creator, admin or tech lead can update all fields)
        is_creator = task.creator_id == user.id
        is_admin_or_lead = user.role in [Role.ADMIN, Role.TECH_LEAD]
        
        if not (is_creator or is_admin_or_lead):
            # Regular users can only update status if they're assigned
            if set(updates.keys()) != {'status'}:
                raise ValueError("You don't have permission to update this task's details")
            
            # For status updates, check if user is assigned
            is_assigned = any(assigned_user.id == user.id for assigned_user in task.assigned_users)
            if not is_assigned:
                raise ValueError("You don't have permission to update this task's status")
        
        # Update basic fields directly
        if 'title' in updates:
            task.title = updates['title']
        
        if 'description' in updates:
            task.description = updates['description']
        
        if 'due_date' in updates:
            task.due_date = updates['due_date']
        
        # Handle status updates with notification logic
        if 'status' in updates:
            old_status = task.status
            new_status = updates['status']
            task.update_status(new_status)
            
            # Handle completion notification logic
            if new_status == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
                # Get all tech leads for notification
                tech_leads = self.user_repository.get_all(Role.TECH_LEAD)
                # Notify the observer
                self.task_notifier.notify_task_completion(task, tech_leads)
        
        # Handle priority updates
        if 'priority' in updates:
            task.update_priority(updates['priority'])
        
        # Handle assigned users updates
        if 'assigned_user_ids' in updates:
            # Get current assigned user IDs
            current_user_ids = {assigned_user.id for assigned_user in task.assigned_users}
            new_user_ids = set(updates['assigned_user_ids'])
            
            # Users to remove
            for user_id in current_user_ids - new_user_ids:
                self.task_repository.unassign_user(task_id, user_id)
            
            # Users to add
            for user_id in new_user_ids - current_user_ids:
                # Verify user exists
                if not self.user_repository.get_by_id(user_id):
                    raise ValueError(f"User with ID {user_id} not found")
                self.task_repository.assign_user(task_id, user_id)
        
        # Save the updated task
        return self.task_repository.update(task) 