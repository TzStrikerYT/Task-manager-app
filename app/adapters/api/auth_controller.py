from flask import Blueprint, jsonify, request
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app.domain.entity import Role
from app.application.auth_service import AuthService
from app.application.service import UserService

# Create blueprint
auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

class AuthController:
    """Controller for authentication endpoints."""
    
    def __init__(self, auth_service: AuthService, user_service: UserService):
        self.auth_service = auth_service
        self.user_service = user_service
        self._register_routes()
    
    def _register_routes(self):
        """Register routes with the blueprint."""
        auth_blueprint.route('/login', methods=['POST'])(self.login)
        auth_blueprint.route('/refresh', methods=['POST'])(self.refresh)
    
    def login(self):
        """Login endpoint."""
        data = request.get_json()
        
        if not all(key in data for key in ['email', 'password']):
            return jsonify({"error": "Email and password are required"}), HTTPStatus.BAD_REQUEST
        
        try:
            user = self.auth_service.authenticate(data['email'], data['password'])
            
            # Create tokens using user ID as identity
            user_data = user.to_dict()
            access_token = create_access_token(
                identity=user.id,
                additional_claims={"role": user.role.value if isinstance(user.role, Role) else user.role}
            )
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_data
            })
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.UNAUTHORIZED
    
    @jwt_required(refresh=True)
    def refresh(self):
        """Refresh token endpoint."""
        identity = get_jwt_identity()
        user = self.user_service.get_user_by_id(int(identity))
        if not user:
            return jsonify({"error": "User not found"}), HTTPStatus.NOT_FOUND
            
        access_token = create_access_token(
            identity=identity,
            additional_claims={"role": user.role.value if isinstance(user.role, Role) else user.role}
        )
        
        return jsonify({"access_token": access_token}) 