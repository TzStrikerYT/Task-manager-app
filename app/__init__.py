from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from app.infrastructure.config import Config
from app.infrastructure.database import init_db
from app.adapters.postgresql_repository import PostgreSQLUserRepository, PostgreSQLTaskRepository
from app.application.service import UserService
from app.application.auth_service import AuthService
from app.application.task_service import TaskService
from app.adapters.api.auth_controller import auth_blueprint, AuthController
from app.adapters.api.user_controller import user_blueprint, UserController
from app.adapters.api.task_controller import task_blueprint, TaskController
from app.adapters.api.error_handler import register_error_handlers

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize the database
    init_db(app)
    
    # Initialize repositories and services
    user_repository = PostgreSQLUserRepository()
    task_repository = PostgreSQLTaskRepository()
    auth_service = AuthService(user_repository)
    user_service = UserService(user_repository, auth_service)
    task_service = TaskService(task_repository, user_repository)
    
    # JWT configuration
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, dict) and 'id' in user:
            return str(user['id'])
        return str(user)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return user_service.get_user_by_id(int(identity))
    
    # Register error handlers
    register_error_handlers(app)
    
    # Initialize controllers
    AuthController(auth_service, user_service)
    UserController(user_service)
    TaskController(task_service, user_service)
    
    # Register blueprints
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(task_blueprint)
    
    return app 