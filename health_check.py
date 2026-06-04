"""
Health Check Application
A comprehensive health check system for monitoring application and system metrics
"""

import psutil
import socket
import time
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """Main health checker class"""
    
    def __init__(self, service_name: str = "Application"):
        self.service_name = service_name
        self.checks = {}
        self.threshold_values = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90,
        }
    
    def check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        status = HealthStatus.HEALTHY
        
        if cpu_percent > self.threshold_values["cpu_percent"]:
            status = HealthStatus.DEGRADED if cpu_percent < 95 else HealthStatus.UNHEALTHY
        
        return {
            "name": "CPU",
            "status": status,
            "value": round(cpu_percent, 2),
            "unit": "%",
            "threshold": self.threshold_values["cpu_percent"],
            "message": f"CPU usage is {cpu_percent}%"
        }
    
    def check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        memory = psutil.virtual_memory()
        status = HealthStatus.HEALTHY
        
        if memory.percent > self.threshold_values["memory_percent"]:
            status = HealthStatus.DEGRADED if memory.percent < 95 else HealthStatus.UNHEALTHY
        
        return {
            "name": "Memory",
            "status": status,
            "value": round(memory.percent, 2),
            "unit": "%",
            "threshold": self.threshold_values["memory_percent"],
            "total_gb": round(memory.total / (1024**3), 2),
            "available_gb": round(memory.available / (1024**3), 2),
            "message": f"Memory usage is {memory.percent}%"
        }
    
    def check_disk(self, path: str = "/") -> Dict[str, Any]:
        """Check disk usage"""
        try:
            disk = psutil.disk_usage(path)
            status = HealthStatus.HEALTHY
            
            if disk.percent > self.threshold_values["disk_percent"]:
                status = HealthStatus.DEGRADED if disk.percent < 95 else HealthStatus.UNHEALTHY
            
            return {
                "name": "Disk",
                "status": status,
                "value": round(disk.percent, 2),
                "unit": "%",
                "threshold": self.threshold_values["disk_percent"],
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "message": f"Disk usage is {disk.percent}%"
            }
        except Exception as e:
            return {
                "name": "Disk",
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Failed to check disk: {str(e)}"
            }
    
    def check_process_count(self) -> Dict[str, Any]:
        """Check number of running processes"""
        process_count = len(psutil.pids())
        
        return {
            "name": "Process Count",
            "status": HealthStatus.HEALTHY,
            "value": process_count,
            "message": f"Total running processes: {process_count}"
        }
    
    def check_network(self) -> Dict[str, Any]:
        """Check network connectivity"""
        try:
            # Try to connect to a reliable server
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return {
                "name": "Network",
                "status": HealthStatus.HEALTHY,
                "message": "Network connectivity is available"
            }
        except Exception as e:
            return {
                "name": "Network",
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Network connectivity check failed: {str(e)}"
            }
    
    def check_custom(self, check_func, check_name: str) -> Dict[str, Any]:
        """Run a custom health check function"""
        try:
            result = check_func()
            return {
                "name": check_name,
                "status": result.get("status", HealthStatus.HEALTHY),
                "message": result.get("message", "Check completed"),
                **{k: v for k, v in result.items() if k not in ["status", "message"]}
            }
        except Exception as e:
            return {
                "name": check_name,
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Custom check failed: {str(e)}"
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        start_time = time.time()
        
        results = {
            "service": self.service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "cpu": self.check_cpu(),
                "memory": self.check_memory(),
                "disk": self.check_disk(),
                "processes": self.check_process_count(),
                "network": self.check_network(),
            }
        }
        
        # Determine overall status
        statuses = [check["status"] for check in results["checks"].values()]
        
        if all(status == HealthStatus.HEALTHY for status in statuses):
            results["overall_status"] = HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            results["overall_status"] = HealthStatus.UNHEALTHY
        else:
            results["overall_status"] = HealthStatus.DEGRADED
        
        results["response_time_ms"] = round((time.time() - start_time) * 1000, 2)
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a brief health summary"""
        results = self.run_all_checks()
        healthy_count = sum(1 for check in results["checks"].values() if check["status"] == HealthStatus.HEALTHY)
        total_checks = len(results["checks"])
        
        return {
            "service": self.service_name,
            "overall_status": results["overall_status"],
            "healthy_checks": healthy_count,
            "total_checks": total_checks,
            "timestamp": results["timestamp"]
        }
