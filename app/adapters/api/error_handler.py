from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest, NotFound
from http import HTTPStatus

def register_error_handlers(app: Flask):
    """Register error handlers with the Flask app."""
    
    @app.errorhandler(ValueError)
    def handle_value_error(error):
        return jsonify({"error": str(error)}), HTTPStatus.BAD_REQUEST
    
    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({"error": str(error)}), HTTPStatus.BAD_REQUEST
    
    @app.errorhandler(NotFound)
    def handle_not_found(error):
        return jsonify({"error": "Resource not found"}), HTTPStatus.NOT_FOUND
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        return jsonify({"error": "Internal server error"}), HTTPStatus.INTERNAL_SERVER_ERROR 