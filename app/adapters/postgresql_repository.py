from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload
from app.application.ports import UserRepository, TaskRepository
from app.domain.entity import User, Role, Task, TaskStatus, TaskPriority
from app.infrastructure.database import db

class UserModel(db.Model):
    """SQLAlchemy model for users."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Relationship with tasks
    assigned_tasks = db.relationship('TaskUserModel', back_populates='user')
    
    @classmethod
    def from_entity(cls, entity: User) -> 'UserModel':
        """Create a model from an entity."""
        return cls(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            role=entity.role.value if isinstance(entity.role, Role) else entity.role,
            password_hash=entity.password_hash
        )
    
    def to_entity(self) -> User:
        """Convert model to entity."""
        return User(
            id=self.id,
            name=self.name,
            email=self.email,
            role=Role(self.role) if self.role else Role.DEVELOPER,
            password_hash=self.password_hash
        )


class TaskUserModel(db.Model):
    """SQLAlchemy model for the many-to-many relationship between tasks and users."""
    
    __tablename__ = 'task_users'
    
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    
    # Relationships
    task = db.relationship('TaskModel', back_populates='assigned_users')
    user = db.relationship('UserModel', back_populates='assigned_tasks')


class TaskModel(db.Model):
    """SQLAlchemy model for tasks."""
    
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    assigned_users = db.relationship('TaskUserModel', back_populates='task', cascade="all, delete-orphan")
    
    @classmethod
    def from_entity(cls, entity: Task) -> 'TaskModel':
        """Create a model from an entity."""
        return cls(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            status=entity.status.value if isinstance(entity.status, TaskStatus) else entity.status,
            priority=entity.priority.value if isinstance(entity.priority, TaskPriority) else entity.priority,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            due_date=entity.due_date,
            creator_id=entity.creator_id
        )
    
    def to_entity(self, include_users=True) -> Task:
        """Convert model to entity."""
        # Get assigned users if needed
        assigned_users = []
        if include_users and self.assigned_users:
            for task_user in self.assigned_users:
                assigned_users.append(task_user.user.to_entity())
        
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            status=TaskStatus(self.status) if self.status else TaskStatus.PENDING,
            priority=TaskPriority(self.priority) if self.priority else TaskPriority.MEDIUM,
            created_at=self.created_at,
            updated_at=self.updated_at,
            due_date=self.due_date,
            assigned_users=assigned_users,
            creator_id=self.creator_id
        )


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL implementation of user repository."""
    
    def create(self, user: User) -> User:
        """Create a new user in the database."""
        user_model = UserModel.from_entity(user)
        db.session.add(user_model)
        db.session.commit()
        return user_model.to_entity()
    
    def update(self, user: User) -> User:
        """Update a user in the database."""
        user_model = UserModel.query.get(user.id)
        if not user_model:
            raise ValueError(f"User with ID {user.id} not found")
        
        # Update fields
        user_model.name = user.name
        user_model.email = user.email
        user_model.role = user.role.value if isinstance(user.role, Role) else user.role
        
        db.session.commit()
        return user_model.to_entity()
    
    def get_all(self, role: Optional[Role] = None, search_term: Optional[str] = None) -> List[User]:
        """Get all users, optionally filtered by role and search term."""
        query = UserModel.query
        
        if role:
            query = query.filter(UserModel.role == role.value)
        
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    UserModel.name.ilike(search),
                    UserModel.email.ilike(search)
                )
            )
        
        return [user_model.to_entity() for user_model in query.all()]
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        user_model = UserModel.query.get(user_id)
        return user_model.to_entity() if user_model else None
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        user_model = UserModel.query.filter_by(email=email).first()
        return user_model.to_entity() if user_model else None


class PostgreSQLTaskRepository(TaskRepository):
    """PostgreSQL implementation of task repository."""
    
    def create(self, task: Task) -> Task:
        """Create a new task in the database."""
        # Create the task model
        task_model = TaskModel.from_entity(task)
        db.session.add(task_model)
        db.session.flush()  # Flush to get the task ID
        
        # Add assigned users
        if task.assigned_users:
            for user in task.assigned_users:
                task_user = TaskUserModel(task_id=task_model.id, user_id=user.id)
                db.session.add(task_user)
        
        db.session.commit()
        
        # Recargar el modelo para asegurar que incluya los usuarios actualizados
        refreshed_model = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).get(task_model.id)
        
        return refreshed_model.to_entity()
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks, optionally filtered."""
        query = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        )
        
        if filters:
            for key, value in filters.items():
                if hasattr(TaskModel, key):
                    query = query.filter(getattr(TaskModel, key) == value)
        
        return [task_model.to_entity() for task_model in query.all()]
    
    def get_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by ID."""
        # Usar joinedload para cargar explícitamente los usuarios asignados
        task_model = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).get(task_id)
        
        return task_model.to_entity() if task_model else None
    
    def update(self, task: Task) -> Task:
        """Update a task in the database."""
        task_model = TaskModel.query.get(task.id)
        if not task_model:
            raise ValueError(f"Task with ID {task.id} not found")
        
        # Update task fields
        task_model.title = task.title
        task_model.description = task.description
        task_model.status = task.status.value if isinstance(task.status, TaskStatus) else task.status
        task_model.priority = task.priority.value if isinstance(task.priority, TaskPriority) else task.priority
        task_model.updated_at = task.updated_at
        task_model.due_date = task.due_date
        
        # Update assigned users if provided
        if task.assigned_users is not None:  # Verificamos contra None para incluir listas vacías
            # Clear existing assignments
            TaskUserModel.query.filter_by(task_id=task.id).delete()
            
            # Add new assignments
            for user in task.assigned_users:
                task_user = TaskUserModel(task_id=task.id, user_id=user.id)
                db.session.add(task_user)
        
        db.session.commit()
        
        # Recargar el modelo para asegurar que incluya los usuarios actualizados
        refreshed_model = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).get(task.id)
        
        return refreshed_model.to_entity()
    
    def delete(self, task_id: int) -> bool:
        """Delete a task from the database."""
        task_model = TaskModel.query.get(task_id)
        if not task_model:
            return False
        
        db.session.delete(task_model)
        db.session.commit()
        return True
    
    def get_by_user_id(self, user_id: int, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks assigned to a user, optionally filtered."""
        # Join with TaskUserModel to get tasks assigned to the user
        query = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).join(
            TaskUserModel, TaskModel.id == TaskUserModel.task_id
        ).filter(TaskUserModel.user_id == user_id)
        
        if filters:
            for key, value in filters.items():
                if hasattr(TaskModel, key):
                    query = query.filter(getattr(TaskModel, key) == value)
        
        return [task_model.to_entity() for task_model in query.all()]
    
    def get_by_status(self, status: TaskStatus, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks with a specific status, optionally filtered."""
        query = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).filter_by(
            status=status.value if isinstance(status, TaskStatus) else status
        )
        
        if filters:
            for key, value in filters.items():
                if hasattr(TaskModel, key):
                    query = query.filter(getattr(TaskModel, key) == value)
        
        return [task_model.to_entity() for task_model in query.all()]
    
    def get_by_priority(self, priority: TaskPriority, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks with a specific priority, optionally filtered."""
        query = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).filter_by(
            priority=priority.value if isinstance(priority, TaskPriority) else priority
        )
        
        if filters:
            for key, value in filters.items():
                if hasattr(TaskModel, key):
                    query = query.filter(getattr(TaskModel, key) == value)
        
        return [task_model.to_entity() for task_model in query.all()]
    
    def get_by_due_date(self, due_date: datetime, filters: Optional[Dict[str, Any]] = None) -> List[Task]:
        """Get all tasks with a specific due date, optionally filtered."""
        query = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).filter(TaskModel.due_date == due_date)
        
        if filters:
            for key, value in filters.items():
                if hasattr(TaskModel, key):
                    query = query.filter(getattr(TaskModel, key) == value)
        
        return [task_model.to_entity() for task_model in query.all()]
    
    def assign_user(self, task_id: int, user_id: int) -> Task:
        """Assign a user to a task."""
        # Check if task exists
        task_model = TaskModel.query.get(task_id)
        if not task_model:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Check if user exists
        user_model = UserModel.query.get(user_id)
        if not user_model:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check if assignment already exists
        existing = TaskUserModel.query.filter_by(task_id=task_id, user_id=user_id).first()
        if not existing:
            task_user = TaskUserModel(task_id=task_id, user_id=user_id)
            db.session.add(task_user)
            db.session.commit()
        
        # Recarga el modelo para incluir los usuarios actualizados
        refreshed_task = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).get(task_id)
        
        return refreshed_task.to_entity()
    
    def unassign_user(self, task_id: int, user_id: int) -> Task:
        """Unassign a user from a task."""
        # Check if task exists
        task_model = TaskModel.query.get(task_id)
        if not task_model:
            raise ValueError(f"Task with ID {task_id} not found")
        
        # Delete the assignment if it exists
        TaskUserModel.query.filter_by(task_id=task_id, user_id=user_id).delete()
        db.session.commit()
        
        # Recarga el modelo para incluir los usuarios actualizados
        refreshed_task = TaskModel.query.options(
            joinedload(TaskModel.assigned_users).joinedload(TaskUserModel.user)
        ).get(task_id)
        
        return refreshed_task.to_entity() 