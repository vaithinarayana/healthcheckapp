"""
Flask API for Health Check Application
Provides REST endpoints to monitor application health
"""

from flask import Flask, jsonify, request
from health_check import HealthChecker, HealthStatus
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.json.sort_keys = False

# Initialize health checker
health_checker = HealthChecker(service_name="MyApplication")


@app.route('/health', methods=['GET'])
def health_check():
    """
    Main health check endpoint
    Returns detailed health information for all system components
    """
    try:
        results = health_checker.run_all_checks()
        status_code = 200 if results["overall_status"] == HealthStatus.HEALTHY else 503
        return jsonify(results), status_code
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "error": "Health check failed",
            "message": str(e)
        }), 500


@app.route('/health/live', methods=['GET'])
def liveness_probe():
    """
    Liveness probe endpoint
    Used by container orchestration systems to determine if the app is running
    Returns 200 if the application is alive
    """
    return jsonify({
        "status": "alive",
        "message": "Application is running"
    }), 200


@app.route('/health/ready', methods=['GET'])
def readiness_probe():
    """
    Readiness probe endpoint
    Used by container orchestration systems to determine if the app is ready to receive traffic
    Performs quick health checks
    """
    try:
        summary = health_checker.get_summary()
        if summary["overall_status"] != HealthStatus.HEALTHY:
            return jsonify({
                "status": "not_ready",
                "message": "Application is not ready",
                "summary": summary
            }), 503
        
        return jsonify({
            "status": "ready",
            "message": "Application is ready to receive traffic"
        }), 200
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            "status": "not_ready",
            "message": str(e)
        }), 503


@app.route('/health/summary', methods=['GET'])
def health_summary():
    """
    Health summary endpoint
    Returns a brief summary of the health status
    """
    try:
        summary = health_checker.get_summary()
        return jsonify(summary), 200
    except Exception as e:
        logger.error(f"Summary check failed: {str(e)}")
        return jsonify({
            "error": "Summary check failed",
            "message": str(e)
        }), 500


@app.route('/health/cpu', methods=['GET'])
def check_cpu():
    """CPU health check endpoint"""
    try:
        result = health_checker.check_cpu()
        status_code = 200 if result["status"] == HealthStatus.HEALTHY else 503
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health/memory', methods=['GET'])
def check_memory():
    """Memory health check endpoint"""
    try:
        result = health_checker.check_memory()
        status_code = 200 if result["status"] == HealthStatus.HEALTHY else 503
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health/disk', methods=['GET'])
def check_disk():
    """Disk health check endpoint"""
    try:
        path = request.args.get('path', '/')
        result = health_checker.check_disk(path)
        status_code = 200 if result["status"] == HealthStatus.HEALTHY else 503
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health/network', methods=['GET'])
def check_network():
    """Network health check endpoint"""
    try:
        result = health_checker.check_network()
        status_code = 200 if result["status"] == HealthStatus.HEALTHY else 503
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/health/config', methods=['GET', 'PUT'])
def health_config():
    """
    Get or update health check configuration
    GET: Returns current thresholds
    PUT: Updates thresholds
    """
    if request.method == 'GET':
        return jsonify({
            "thresholds": health_checker.threshold_values
        }), 200
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            if data:
                health_checker.threshold_values.update(data)
            return jsonify({
                "message": "Configuration updated",
                "thresholds": health_checker.threshold_values
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 400


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API documentation"""
    return jsonify({
        "service": "Health Check Application",
        "endpoints": {
            "GET /health": "Full health check with all metrics",
            "GET /health/live": "Liveness probe",
            "GET /health/ready": "Readiness probe",
            "GET /health/summary": "Brief health summary",
            "GET /health/cpu": "CPU usage check",
            "GET /health/memory": "Memory usage check",
            "GET /health/disk": "Disk usage check (optional ?path parameter)",
            "GET /health/network": "Network connectivity check",
            "GET /health/config": "Get current thresholds",
            "PUT /health/config": "Update thresholds"
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": "Please check the API documentation at GET /"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
