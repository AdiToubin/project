"""
API Controller - Handles general API endpoints
"""
from flask import jsonify
from app_mvc.models.business_logic import BusinessLogic

class ApiController:
    """Controller for general API endpoints"""

    def __init__(self):
        self.logic = BusinessLogic()

    def process(self, data):
        """Process incoming data"""
        try:
            result = self.logic.process_data(data)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    def calculate(self, data):
        """Perform calculations"""
        try:
            num1 = float(data.get('num1', 0))
            num2 = float(data.get('num2', 0))
            operation = data.get('operation', 'add')
            result = self.logic.calculate(num1, num2, operation)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    def health(self):
        """Health check endpoint"""
        return jsonify({'status': 'healthy'}), 200
