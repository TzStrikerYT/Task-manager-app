from datetime import datetime
from flask import Blueprint, jsonify, request
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

from app.domain.entity import TaskStatus, TaskPriority, Role
from app.application.task_service import TaskService
from app.application.service import UserService

# Create blueprint
task_blueprint = Blueprint('tasks', __name__, url_prefix='/tasks')

class TaskController:
    """Controller for task endpoints."""
    
    def __init__(self, task_service: TaskService, user_service: UserService):
        self.task_service = task_service
        self.user_service = user_service
        self._register_routes()
    
    def _register_routes(self):
        """Register routes with the blueprint."""
        task_blueprint.route('', methods=['POST'])(self.create_task)
        task_blueprint.route('', methods=['GET'])(self.get_tasks)
        task_blueprint.route('/<int:task_id>', methods=['GET'])(self.get_task)
        task_blueprint.route('/<int:task_id>', methods=['PUT'])(self.update_task)
        task_blueprint.route('/<int:task_id>/status', methods=['PUT'])(self.update_task_status)
        task_blueprint.route('/<int:task_id>/priority', methods=['PUT'])(self.update_task_priority)
        task_blueprint.route('/<int:task_id>/assign/<int:user_id>', methods=['POST'])(self.assign_user)
        task_blueprint.route('/<int:task_id>/unassign/<int:user_id>', methods=['DELETE'])(self.unassign_user)
    
    def _get_current_user(self):
        """Get the current user from JWT."""
        user_id = get_jwt_identity()
        return self.user_service.get_user_by_id(int(user_id))
    
    @jwt_required()
    def create_task(self):
        """Create task endpoint."""
        current_user = self._get_current_user()
        data = request.get_json()
        
        # Validate required fields
        if not all(key in data for key in ['title', 'description', 'priority']):
            return jsonify({"error": "Title, description, and priority are required"}), HTTPStatus.BAD_REQUEST
        
        # Validate and parse due date if provided
        due_date = None
        if 'due_date' in data and data['due_date']:
            try:
                due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({"error": "Invalid due_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), HTTPStatus.BAD_REQUEST
        
        # Validate priority
        try:
            priority = TaskPriority(data['priority'])
        except ValueError:
            return jsonify({
                "error": f"Invalid priority. Valid options are: {[p.value for p in TaskPriority]}"
            }), HTTPStatus.BAD_REQUEST
        
        # Get assigned users
        assigned_user_ids = data.get('assigned_user_ids', [])
        if not isinstance(assigned_user_ids, list):
            return jsonify({"error": "assigned_user_ids must be a list"}), HTTPStatus.BAD_REQUEST
        
        try:
            task = self.task_service.create_task(
                title=data['title'],
                description=data['description'],
                priority=priority,
                due_date=due_date,
                assigned_user_ids=assigned_user_ids,
                creator_id=current_user.id
            )
            return jsonify(task.to_dict()), HTTPStatus.CREATED
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
    @jwt_required()
    def update_task(self, task_id):
        """Update task endpoint."""
        current_user = self._get_current_user()
        data = request.get_json()
        
        # Get the existing task
        task = self.task_service.get_task_by_id(task_id, current_user)
        if not task:
            return jsonify({"error": f"Task with ID {task_id} not found"}), HTTPStatus.NOT_FOUND
        
        # Validate permission (only creator, admin or tech lead can update a task)
        is_creator = task.creator_id == current_user.id
        is_admin_or_lead = current_user.role in [Role.ADMIN, Role.TECH_LEAD]
        
        if not (is_creator or is_admin_or_lead):
            return jsonify({"error": "You don't have permission to update this task"}), HTTPStatus.FORBIDDEN
        
        # Process updates
        updates = {}
        
        # Update status if provided
        if 'status' in data:
            try:
                updates['status'] = TaskStatus(data['status'])
            except ValueError:
                return jsonify({
                    "error": f"Invalid status. Valid options are: {[s.value for s in TaskStatus]}"
                }), HTTPStatus.BAD_REQUEST
                
        # Update priority if provided
        if 'priority' in data:
            try:
                updates['priority'] = TaskPriority(data['priority'])
            except ValueError:
                return jsonify({
                    "error": f"Invalid priority. Valid options are: {[p.value for p in TaskPriority]}"
                }), HTTPStatus.BAD_REQUEST
        
        # Update title if provided
        if 'title' in data:
            updates['title'] = data['title']
            
        # Update description if provided
        if 'description' in data:
            updates['description'] = data['description']
            
        # Update due date if provided
        if 'due_date' in data and data['due_date']:
            try:
                updates['due_date'] = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({"error": "Invalid due_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), HTTPStatus.BAD_REQUEST
        
        # Update assigned users if provided
        if 'assigned_user_ids' in data:
            assigned_user_ids = data['assigned_user_ids']
            if not isinstance(assigned_user_ids, list):
                return jsonify({"error": "assigned_user_ids must be a list"}), HTTPStatus.BAD_REQUEST
            updates['assigned_user_ids'] = assigned_user_ids
        
        try:
            # Call service method to update task
            updated_task = self.task_service.update_task(task_id, updates, current_user)
            return jsonify(updated_task.to_dict())
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
    @jwt_required()
    def get_tasks(self):
        """Get tasks endpoint."""
        current_user = self._get_current_user()
        
        # Parse query parameters
        status_param = request.args.get('status')
        priority_param = request.args.get('priority')
        user_id_param = request.args.get('user_id')
        due_date_param = request.args.get('due_date')
        
        # Parse status if provided
        status = None
        if status_param:
            try:
                status = TaskStatus(status_param)
            except ValueError:
                return jsonify({
                    "error": f"Invalid status. Valid options are: {[s.value for s in TaskStatus]}"
                }), HTTPStatus.BAD_REQUEST
        
        # Parse priority if provided
        priority = None
        if priority_param:
            try:
                priority = TaskPriority(priority_param)
            except ValueError:
                return jsonify({
                    "error": f"Invalid priority. Valid options are: {[p.value for p in TaskPriority]}"
                }), HTTPStatus.BAD_REQUEST
        
        # Parse user_id if provided
        user_id = None
        if user_id_param:
            try:
                user_id = int(user_id_param)
            except ValueError:
                return jsonify({"error": "user_id must be an integer"}), HTTPStatus.BAD_REQUEST
        
        # Parse due_date if provided
        due_date = None
        if due_date_param:
            try:
                due_date = datetime.fromisoformat(due_date_param)
            except ValueError:
                return jsonify({"error": "Invalid due_date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), HTTPStatus.BAD_REQUEST
        
        tasks = self.task_service.get_tasks(
            status=status,
            priority=priority,
            user_id=user_id,
            due_date=due_date,
            requesting_user=current_user
        )
        
        return jsonify([task.to_dict() for task in tasks])
    
    @jwt_required()
    def get_task(self, task_id):
        """Get task endpoint."""
        current_user = self._get_current_user()
        
        task = self.task_service.get_task_by_id(task_id, current_user)
        if not task:
            return jsonify({"error": f"Task with ID {task_id} not found"}), HTTPStatus.NOT_FOUND
        
        return jsonify(task.to_dict())
    
    @jwt_required()
    def update_task_status(self, task_id):
        """Update task status endpoint."""
        current_user = self._get_current_user()
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({"error": "Status is required"}), HTTPStatus.BAD_REQUEST
        
        try:
            status = TaskStatus(data['status'])
        except ValueError:
            return jsonify({
                "error": f"Invalid status. Valid options are: {[s.value for s in TaskStatus]}"
            }), HTTPStatus.BAD_REQUEST
        
        try:
            task = self.task_service.update_task_status(task_id, status, current_user)
            return jsonify(task.to_dict())
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
    @jwt_required()
    def update_task_priority(self, task_id):
        """Update task priority endpoint."""
        current_user = self._get_current_user()
        data = request.get_json()
        
        if 'priority' not in data:
            return jsonify({"error": "Priority is required"}), HTTPStatus.BAD_REQUEST
        
        try:
            priority = TaskPriority(data['priority'])
        except ValueError:
            return jsonify({
                "error": f"Invalid priority. Valid options are: {[p.value for p in TaskPriority]}"
            }), HTTPStatus.BAD_REQUEST
        
        try:
            task = self.task_service.update_task_priority(task_id, priority, current_user)
            return jsonify(task.to_dict())
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
    @jwt_required()
    def assign_user(self, task_id, user_id):
        """Assign user to task endpoint."""
        current_user = self._get_current_user()
        
        try:
            task = self.task_service.assign_user_to_task(task_id, user_id, current_user)
            return jsonify(task.to_dict())
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    
    @jwt_required()
    def unassign_user(self, task_id, user_id):
        """Unassign user from task endpoint."""
        current_user = self._get_current_user()
        
        try:
            task = self.task_service.unassign_user_from_task(task_id, user_id, current_user)
            return jsonify(task.to_dict())
        except ValueError as e:
            return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST 