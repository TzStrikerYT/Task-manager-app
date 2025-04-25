from enum import Enum
from datetime import datetime
from typing import List, Optional

class Role(Enum):
    DEVELOPER = "Desarrollador"
    TECH_LEAD = "Líder Técnico"
    ADMIN = "Administrador"

class TaskStatus(Enum):
    PENDING = "Pendiente"
    IN_PROGRESS = "En Progreso"
    BLOCKED = "Bloqueada"
    IN_REVIEW = "En Revisión"
    COMPLETED = "Completada"

class TaskPriority(Enum):
    LOW = "Baja"
    MEDIUM = "Media"
    HIGH = "Alta"
    URGENT = "Urgente"

class User:
    """User entity."""
    
    def __init__(self, id=None, name="", email="", role=Role.DEVELOPER, password=None, password_hash=None):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.password = password  # Used only for password setting, never stored
        self.password_hash = password_hash  # Stored password hash
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value if isinstance(self.role, Role) else self.role
        }
    
    def to_auth_dict(self):
        """Return user data with authentication info for JWT."""
        user_dict = self.to_dict()
        user_dict['auth_role'] = self.role.value if isinstance(self.role, Role) else self.role
        return user_dict
    
    def has_permission(self, action: str, resource: Optional[object] = None) -> bool:
        """Check if the user has permission to perform an action on a resource."""
        
        if self.role == Role.ADMIN and action != "view_all_completed_tasks":
            return True
            
        if action == "view_all_completed_tasks":
            return self.role == Role.TECH_LEAD
            
        return False

class Task:
    """Task entity."""
    
    def __init__(
        self,
        id=None,
        title="",
        description="",
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        created_at=None,
        updated_at=None,
        due_date=None,
        assigned_users=None,
        creator_id=None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
        self.due_date = due_date
        self.assigned_users = assigned_users if assigned_users else []
        self.creator_id = creator_id
    
    def to_dict(self, include_users=True):
        result = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value if isinstance(self.status, TaskStatus) else self.status,
            "priority": self.priority.value if isinstance(self.priority, TaskPriority) else self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "creator_id": self.creator_id
        }
        
        if include_users:
            result["assigned_users"] = [
                user.to_dict() if hasattr(user, 'to_dict') else user 
                for user in (self.assigned_users or [])
            ]
        
        return result
        
    def add_user(self, user):
        """Add a user to the assigned users list."""
        # Check if the user is already assigned
        if user.id not in [u.id for u in self.assigned_users if hasattr(u, 'id')]:
            self.assigned_users.append(user)
    
    def remove_user(self, user_id):
        """Remove a user from the assigned users list."""
        self.assigned_users = [u for u in self.assigned_users if getattr(u, 'id', None) != user_id]
    
    def update_status(self, status):
        """Update the task status."""
        self.status = status
        self.updated_at = datetime.now()
    
    def update_priority(self, priority):
        """Update the task priority."""
        self.priority = priority
        self.updated_at = datetime.now() 