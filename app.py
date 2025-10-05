"""
Flask Application Server
"""
from flask import Flask, render_template, request, jsonify
from model.logic import BusinessLogic
import os

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize business logic
logic = BusinessLogic()


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/process', methods=['POST'])
def process():
    """API endpoint to process data"""
    try:
        data = request.get_json()
        result = logic.process_data(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/calculate', methods=['POST'])
def calculate():
    """API endpoint for calculations"""
    try:
        data = request.get_json()
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        operation = data.get('operation', 'add')

        result = logic.calculate(num1, num2, operation)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
