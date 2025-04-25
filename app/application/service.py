from typing import List, Optional
from app.domain.entity import User, Role
from app.application.ports import UserRepository
from app.application.auth_service import AuthService

class UserService:
    """Service for handling users."""
    
    def __init__(self, user_repository: UserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service
    
    def create_user(self, name: str, email: str, role: Role, password: str) -> User:
        """Create a new user."""
        # Check if email already exists
        existing_user = self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Hash the password
        password_hash = self.auth_service.hash_password(password)
        
        # Create and save the user
        user = User(name=name, email=email, role=role, password_hash=password_hash)
        return self.user_repository.create(user)
    
    def update_user(self, user_id: int, name: str = None, email: str = None, role: Role = None) -> User:
        """Update an existing user."""
        # Check if user exists
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # If email is being updated, check it's not already taken
        if email and email != user.email:
            existing_user = self.user_repository.get_by_email(email)
            if existing_user:
                raise ValueError(f"User with email {email} already exists")
        
        # Update fields if provided
        if name:
            user.name = name
        if email:
            user.email = email
        if role:
            user.role = role
        
        # Save and return updated user
        return self.user_repository.update(user)
    
    def get_all_users(self, role: Optional[Role] = None, search_term: Optional[str] = None) -> List[User]:
        """Get all users with optional filtering."""
        return self.user_repository.get_all(role, search_term)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.user_repository.get_by_id(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.user_repository.get_by_email(email) 