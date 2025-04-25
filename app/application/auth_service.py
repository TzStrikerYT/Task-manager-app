from passlib.hash import bcrypt
from app.application.ports import UserRepository
from app.domain.entity import User

class AuthService:
    """Service for handling authentication and passwords."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return bcrypt.hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against a hash."""
        return bcrypt.verify(password, password_hash)
    
    def authenticate(self, email: str, password: str) -> User:
        """Authenticate a user with email and password."""
        user = self.user_repository.get_by_email(email)
        
        if not user or not user.password_hash:
            raise ValueError("Invalid email or password")
        
        if not self.verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")
        
        return user 