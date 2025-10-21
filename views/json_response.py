"""
JSON Response Utilities - Helper functions for formatting JSON responses
"""
from flask import jsonify

class JsonResponse:
    """Utility class for creating standardized JSON responses"""

    @staticmethod
    def success(data=None, message="Success", status_code=200):
        """Create a success response"""
        response = {
            'status': 'success',
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), status_code

    @staticmethod
    def error(message="Error occurred", status_code=400, details=None):
        """Create an error response"""
        response = {
            'status': 'error',
            'message': message
        }
        if details is not None:
            response['details'] = details
        return jsonify(response), status_code

    @staticmethod
    def created(data=None, message="Resource created", status_code=201):
        """Create a resource created response"""
        response = {
            'status': 'success',
            'message': message
        }
        if data is not None:
            response['data'] = data
        return jsonify(response), status_code
