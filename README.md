# Health Check Application

A comprehensive Python-based health check application that monitors system resources and application health. Includes both a REST API and CLI interface.

## Features

- 🔍 **System Monitoring**: CPU, Memory, Disk, Network, and Process count checks
- 🌐 **REST API**: Full HTTP API for health checks with multiple endpoints
- 💻 **CLI Tool**: Command-line interface for quick health checks
- 📊 **Detailed Metrics**: Rich information including thresholds, current values, and trends
- 🎯 **Configurable Thresholds**: Adjust alert thresholds dynamically
- 🚀 **Kubernetes Ready**: Includes liveness and readiness probes
- 🔧 **Extensible**: Easy to add custom health checks

## Installation

```bash
# Clone the repository
git clone https://github.com/vaithinarayana/healthcheckapp.git
cd healthcheckapp

# Install dependencies
pip install -r requirements.txt
```

## Usage

### REST API

```bash
# Start the Flask server
python app.py
```

The application will be available at `http://localhost:5000`

#### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation and available endpoints |
| `/health` | GET | Full health check with all metrics |
| `/health/live` | GET | Liveness probe (container orchestration) |
| `/health/ready` | GET | Readiness probe (container orchestration) |
| `/health/summary` | GET | Brief health summary |
| `/health/cpu` | GET | CPU usage check |
| `/health/memory` | GET | Memory usage check |
| `/health/disk` | GET | Disk usage check (optional `?path` parameter) |
| `/health/network` | GET | Network connectivity check |
| `/health/config` | GET/PUT | Get or update thresholds |

#### Example API Calls

```bash
# Full health check
curl http://localhost:5000/health

# CPU check
curl http://localhost:5000/health/cpu

# Memory check
curl http://localhost:5000/health/memory

# Disk check (specific path)
curl http://localhost:5000/health/disk?path=/home

# Get current thresholds
curl http://localhost:5000/health/config

# Update thresholds
curl -X PUT http://localhost:5000/health/config \
  -H "Content-Type: application/json" \
  -d '{"cpu_percent": 75, "memory_percent": 80}'

# Liveness probe (for Kubernetes)
curl http://localhost:5000/health/live

# Readiness probe (for Kubernetes)
curl http://localhost:5000/health/ready
```

### CLI Tool

```bash
# Show help
python health_check_cli.py --help

# Run full health check
python health_check_cli.py check

# Show summary
python health_check_cli.py summary

# Check CPU
python health_check_cli.py cpu

# Check memory
python health_check_cli.py memory

# Check disk
python health_check_cli.py disk --path /home

# Check network
python health_check_cli.py network

# Output as JSON
python health_check_cli.py check --format json

# Custom service name
python health_check_cli.py --service "MyService" check
```

## Response Examples

### Full Health Check

```json
{
  "service": "MyApplication",
  "timestamp": "2024-01-15T10:30:45.123456",
  "overall_status": "healthy",
  "checks": {
    "cpu": {
      "name": "CPU",
      "status": "healthy",
      "value": 45.23,
      "unit": "%",
      "threshold": 80,
      "message": "CPU usage is 45.23%"
    },
    "memory": {
      "name": "Memory",
      "status": "healthy",
      "value": 62.15,
      "unit": "%",
      "threshold": 85,
      "total_gb": 16.0,
      "available_gb": 6.04,
      "message": "Memory usage is 62.15%"
    },
    "disk": {
      "name": "Disk",
      "status": "healthy",
      "value": 55.8,
      "unit": "%",
      "threshold": 90,
      "total_gb": 500.0,
      "used_gb": 279.0,
      "free_gb": 221.0,
      "message": "Disk usage is 55.8%"
    },
    "processes": {
      "name": "Process Count",
      "status": "healthy",
      "value": 156,
      "message": "Total running processes: 156"
    },
    "network": {
      "name": "Network",
      "status": "healthy",
      "message": "Network connectivity is available"
    }
  },
  "response_time_ms": 125.45
}
```

### Summary Response

```json
{
  "service": "MyApplication",
  "overall_status": "healthy",
  "healthy_checks": 5,
  "total_checks": 5,
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

## Status Codes

- **200 (OK)**: All checks passed, system is healthy
- **503 (Service Unavailable)**: One or more checks failed, system is degraded or unhealthy
- **500 (Internal Server Error)**: Error occurred during health check

## Health Status Levels

- **healthy**: All metrics are within normal thresholds
- **degraded**: Some metrics are approaching or have exceeded thresholds
- **unhealthy**: System has critical issues

## Configuration

### Adjusting Thresholds

Default thresholds can be modified via the API:

```bash
curl -X PUT http://localhost:5000/health/config \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_percent": 70,
    "memory_percent": 80,
    "disk_percent": 85
  }'
```

## Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t health-check-app .
docker run -p 5000:5000 health-check-app
```

## Kubernetes Integration

Use the health check endpoints in your Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: health-check-app
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: app
        image: health-check-app:latest
        ports:
        - containerPort: 5000
        livenessProbe:
          httpGet:
            path: /health/live
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 10
```

## Project Structure

```
healthcheckapp/
├── app.py                   # Flask API application
├── health_check.py          # Core health checking logic
├── health_check_cli.py      # CLI interface
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker compose configuration
└── README.md               # This file
```

## Features Breakdown

### Core Health Checks

1. **CPU Monitoring**: Real-time CPU usage percentage
2. **Memory Monitoring**: RAM usage with breakdown of total/available
3. **Disk Monitoring**: Storage usage for any path
4. **Network Monitoring**: Internet connectivity verification
5. **Process Monitoring**: Count of running processes

### API Features

- RESTful endpoints for each health check
- Dynamic threshold configuration
- Kubernetes-compatible liveness/readiness probes
- JSON responses with detailed metrics
- Appropriate HTTP status codes

### CLI Features

- Multiple output formats (table, JSON)
- Individual check commands
- Exit codes for script integration
- Custom service naming

## Custom Health Checks

You can extend the health checker with custom checks:

```python
from health_check import HealthChecker

checker = HealthChecker()

def custom_check():
    # Your check logic here
    return {
        "status": "healthy",
        "message": "Custom check passed"
    }

result = checker.check_custom(custom_check, "CustomCheck")
```

## Dependencies

- **flask**: Web framework for REST API
- **requests**: HTTP library
- **psutil**: System and process utilities
- **pydantic**: Data validation
- **tabulate**: Pretty-print tabular data

## License

MIT License

## Contributing

Contributions are welcome! Feel free to open issues and pull requests.

## Support

For issues and questions, please open a GitHub issue in the repository.
