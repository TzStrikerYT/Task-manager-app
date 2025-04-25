from flask import Blueprint, jsonify, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required

from app.domain.entity import Role
from app.application.service import UserService

# Create blueprint
user_blueprint = Blueprint('users', __name__, url_prefix='/users')

class UserController:
    """Controller for user endpoints."""
    
    def __init__(self, user_service: UserService):
        self.user_service = user_service
        self._register_routes()
    
    def _register_routes(self):
        """Register routes with the blueprint."""
        user_blueprint.route('', methods=['POST'])(self.create_user)
        user_blueprint.route('', methods=['GET'])(self.get_users)
        user_blueprint.route('/<int:user_id>', methods=['GET'])(self.get_user)
        user_blueprint.route('/<int:user_id>', methods=['PUT'])(self.update_user)
    
    def create_user(self):
        """Create user endpoint."""
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['name', 'email', 'role', 'password']):
            return jsonify({"error": "Name, email, role, and password are required"}), HTTPStatus.BAD_REQUEST
        
        # Validate role
        try:
            role = Role(data['role'])
        except ValueError:
            return jsonify({
                "error": f"Invalid role. Valid options are: {[r.value for r in Role]}"
            }), HTTPStatus.BAD_REQUEST
        
        try:
            user = self.user_service.create_user(
                name=data['name'],
                email=data['email'],
                role=role,
                password=data['password']
            )
            return jsonify(user.to_dict()), HTTPStatus.CREATED
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
    @jwt_required()
    def update_user(self, user_id):
        """Update user endpoint."""
        data = request.get_json()
        
        # Check if at least one field is provided
        if not any(key in data for key in ['name', 'email', 'role']):
            return jsonify({"error": "At least one of: name, email, or role is required"}), HTTPStatus.BAD_REQUEST
        
        # Get values
        name = data.get('name')
        email = data.get('email')
        
        # Validate role if provided
        role = None
        if 'role' in data:
            try:
                role = Role(data['role'])
            except ValueError:
                return jsonify({
                    "error": f"Invalid role. Valid options are: {[r.value for r in Role]}"
                }), HTTPStatus.BAD_REQUEST
        
        try:
            user = self.user_service.update_user(
                user_id=user_id,
                name=name,
                email=email,
                role=role
            )
            return jsonify(user.to_dict()), HTTPStatus.OK
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
    @jwt_required()
    def get_users(self):
        """Get users endpoint."""
        # Parse query parameters
        role_param = request.args.get('role')
        search_term = request.args.get('search')
        
        role = None
        if role_param:
            try:
                role = Role(role_param)
            except ValueError:
                return jsonify({
                    "error": f"Invalid role. Valid options are: {[r.value for r in Role]}"
                }), HTTPStatus.BAD_REQUEST
        
        users = self.user_service.get_all_users(role, search_term)
        return jsonify([user.to_dict() for user in users])
    
    @jwt_required()
    def get_user(self, user_id):
        """Get user by ID endpoint."""
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), HTTPStatus.NOT_FOUND
        
        return jsonify(user.to_dict()) 