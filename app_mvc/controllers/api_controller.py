"""
════════════════════════════════════════════════════════════════════════════════
API CONTROLLER - GENERAL PURPOSE API ENDPOINTS
════════════════════════════════════════════════════════════════════════════════

בקר API - טיפול בנקודות קצה כלליות של ה API

PURPOSE:
   This controller handles general-purpose API endpoints that are not related
   to news processing. It provides three main functions:
   1. Data processing endpoint - generic data handling
   2. Mathematical calculations - basic arithmetic operations
   3. Health check - application status monitoring

ENDPOINTS:
   - POST /api/process - Process generic data
   - POST /api/calculate - Perform arithmetic operations
   - GET /health - Health check status

DEPENDENCIES:
   - BusinessLogic: Core business logic operations

ERROR HANDLING:
   All endpoints return HTTP status codes:
   - 200: Success
   - 400: Bad request or calculation error
   - Always returns JSON response with status field

────────────────────────────────────────────────────────────────────────────────
"""
from flask import jsonify
from app_mvc.models.business_logic import BusinessLogic

class ApiController:
    """
    API CONTROLLER CLASS
    ────────────────────
    Handles general-purpose API operations and health monitoring
    טיפול בפעולות API כלליות וניטור בריאות היישום

    RESPONSIBILITIES:
    1. Data processing - generic data transformation
    2. Calculations - arithmetic operations
    3. Health monitoring - status checks for monitoring systems

    ATTRIBUTES:
    - logic (BusinessLogic): Instance of business logic handler
    """

    def __init__(self):
        """
        Initialize API Controller
        ────────────────────────
        Create instance of BusinessLogic for request handling
        """
        self.logic = BusinessLogic()

    def process(self, data):
        """
        PROCESS GENERIC DATA ENDPOINT
        ──────────────────────────────
        עבד נתונים כלליים דרך API
        Process incoming data using business logic

        ENDPOINT: POST /api/process
        Content-Type: application/json

        REQUEST BODY:
        Any JSON object that BusinessLogic.process_data() can handle

        RETURNS: Tuple (JSON response, HTTP status)
           Success: (processed_result, 200)
           Error: ({"status": "error", "message": error_details}, 400)

        RESPONSE FORMAT:
        {
            "status": "success|error",
            "result": {...}  // if successful
            "message": "..."  // if error
        }

        ERROR HANDLING:
        - Catches all exceptions from business logic
        - Returns HTTP 400 with error message
        - Does not expose internal stack traces

        USE CASES:
        - Generic data transformation
        - Data validation
        - Custom business logic operations
        """
        try:
            result = self.logic.process_data(data)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 400

    
    def health(self):
        """
        HEALTH CHECK ENDPOINT
        ─────────────────────
        בדיקת בריאות היישום - בדיקה שהשרת פעיל
        Health check for monitoring and load balancing

        ENDPOINT: GET /health
        No parameters required

        RETURNS: Tuple (JSON response, HTTP status)
           Always: ({"status": "healthy"}, 200)

        RESPONSE:
        {
            "status": "healthy"
        }

        ALWAYS SUCCEEDS:
        This endpoint always returns HTTP 200 if the server is running.
        It's a simple indicator that the application is alive.

        USE CASES:
        - Docker container health checks
        - Kubernetes liveness probes
        - Load balancer health monitoring
        - Application monitoring systems (Prometheus, Datadog, etc.)
        - Uptime monitoring services

        IMPLEMENTATION:
        - No database queries
        - No external API calls
        - No processing logic
        - Immediate response (< 1ms)

        RESPONSE TIME: <1ms (instant response)

        MONITORING TIPS:
        - Set up alerts if endpoint returns non-200 status
        - Monitor response time for server performance
        - Use as baseline for other endpoint SLOs
        - Check endpoint every 30-60 seconds for continuous monitoring
        """
        return jsonify({'status': 'healthy'}), 200
