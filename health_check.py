"""
Health Check Application
A comprehensive health check system for monitoring application and system metrics
"""

import psutil
import socket
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Optional
from enum import Enum


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthStatus(str, Enum):
    """Health status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthChecker:
    """Main health checker class"""
    
    def __init__(
        self,
        service_name: str = "Application",
        network_host: str = "8.8.8.8",
        network_port: int = 53,
        cache_ttl: int = 0,
        cpu_threshold: float = 80,
        memory_threshold: float = 85,
        disk_threshold: float = 90,
        critical_threshold: float = 95
    ):
        """
        Initialize the health checker.
        
        Args:
            service_name: Name of the service being monitored
            network_host: Host to use for network connectivity check
            network_port: Port to use for network connectivity check
            cache_ttl: Time-to-live for cached results in seconds (0 = no cache)
            cpu_threshold: CPU usage warning threshold (%)
            memory_threshold: Memory usage warning threshold (%)
            disk_threshold: Disk usage warning threshold (%)
            critical_threshold: Critical threshold for all metrics (%)
        """
        self.service_name = service_name
        self.network_host = network_host
        self.network_port = network_port
        self.cache_ttl = cache_ttl
        self.critical_threshold = critical_threshold
        
        self.threshold_values = {
            "cpu_percent": cpu_threshold,
            "memory_percent": memory_threshold,
            "disk_percent": disk_threshold,
        }
        
        self.checks: Dict[str, Callable] = {}
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_time: Dict[str, float] = {}
        
        logger.info(f"HealthChecker initialized for service: {service_name}")
    
    def register_check(self, check_name: str, check_func: Callable) -> None:
        """
        Register a custom health check function.
        
        Args:
            check_name: Name of the check
            check_func: Callable that returns a dict with check results
        """
        self.checks[check_name] = check_func
        logger.info(f"Registered custom check: {check_name}")
    
    def _determine_status(
        self,
        value: float,
        warning_threshold: float,
        critical_threshold: Optional[float] = None
    ) -> HealthStatus:
        """
        Determine health status based on value and thresholds.
        
        Args:
            value: The metric value to evaluate
            warning_threshold: Threshold for DEGRADED status
            critical_threshold: Threshold for UNHEALTHY status (defaults to self.critical_threshold)
        
        Returns:
            HealthStatus enum value
        """
        if critical_threshold is None:
            critical_threshold = self.critical_threshold
        
        if value > critical_threshold:
            return HealthStatus.UNHEALTHY
        elif value > warning_threshold:
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY
    
    def _get_cached_result(self, check_key: str) -> Optional[Dict[str, Any]]:
        """
        Get cached result if available and not expired.
        
        Args:
            check_key: The cache key
        
        Returns:
            Cached result or None if not available/expired
        """
        if self.cache_ttl <= 0:
            return None
        
        if check_key in self.cache:
            elapsed = time.time() - self.cache_time[check_key]
            if elapsed < self.cache_ttl:
                logger.debug(f"Using cached result for {check_key}")
                return self.cache[check_key]
            else:
                del self.cache[check_key]
                del self.cache_time[check_key]
        
        return None
    
    def _cache_result(self, check_key: str, result: Dict[str, Any]) -> None:
        """
        Cache a check result.
        
        Args:
            check_key: The cache key
            result: The result to cache
        """
        if self.cache_ttl > 0:
            self.cache[check_key] = result
            self.cache_time[check_key] = time.time()
    
    def check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage"""
        cached = self._get_cached_result("cpu")
        if cached:
            return cached
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            status = self._determine_status(
                cpu_percent,
                self.threshold_values["cpu_percent"]
            )
            
            result = {
                "name": "CPU",
                "status": status,
                "value": round(cpu_percent, 2),
                "unit": "%",
                "threshold": self.threshold_values["cpu_percent"],
                "message": f"CPU usage is {cpu_percent}%"
            }
            
            self._cache_result("cpu", result)
            return result
        except Exception as e:
            logger.error(f"Error checking CPU: {str(e)}")
            return {
                "name": "CPU",
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Failed to check CPU: {str(e)}"
            }
    
    def check_memory(self) -> Dict[str, Any]:
        """Check memory usage"""
        cached = self._get_cached_result("memory")
        if cached:
            return cached
        
        try:
            memory = psutil.virtual_memory()
            status = self._determine_status(
                memory.percent,
                self.threshold_values["memory_percent"]
            )
            
            result = {
                "name": "Memory",
                "status": status,
                "value": round(memory.percent, 2),
                "unit": "%",
                "threshold": self.threshold_values["memory_percent"],
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "message": f"Memory usage is {memory.percent}%"
            }
            
            self._cache_result("memory", result)
            return result
        except Exception as e:
            logger.error(f"Error checking memory: {str(e)}")
            return {
                "name": "Memory",
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Failed to check memory: {str(e)}"
            }
    
    def check_disk(self, path: str = "/") -> Dict[str, Any]:
        """Check disk usage"""
        cache_key = f"disk_{path}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        try:
            disk = psutil.disk_usage(path)
            status = self._determine_status(
                disk.percent,
                self.threshold_values["disk_percent"]
            )
            
            result = {
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
            
            self._cache_result(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error checking disk: {str(e)}")
            return {
                "name": "Disk",
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Failed to check disk: {str(e)}"
            }
    
    def check_process_count(self) -> Dict[str, Any]:
        """Check number of running processes"""
        cached = self._get_cached_result("processes")
        if cached:
            return cached
        
        try:
            process_count = len(psutil.pids())
            
            result = {
                "name": "Process Count",
                "status": HealthStatus.HEALTHY,
                "value": process_count,
                "message": f"Total running processes: {process_count}"
            }
            
            self._cache_result("processes", result)
            return result
        except Exception as e:
            logger.error(f"Error checking process count: {str(e)}")
            return {
                "name": "Process Count",
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Failed to check process count: {str(e)}"
            }
    
    def check_network(self) -> Dict[str, Any]:
        """Check network connectivity"""
        cached = self._get_cached_result("network")
        if cached:
            return cached
        
        try:
            # Try to connect to configured host
            socket.create_connection(
                (self.network_host, self.network_port),
                timeout=3
            )
            result = {
                "name": "Network",
                "status": HealthStatus.HEALTHY,
                "message": "Network connectivity is available"
            }
            
            self._cache_result("network", result)
            return result
        except Exception as e:
            logger.warning(f"Network connectivity check failed: {str(e)}")
            return {
                "name": "Network",
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Network connectivity check failed: {str(e)}"
            }
    
    def check_custom(self, check_func: Callable, check_name: str) -> Dict[str, Any]:
        """
        Run a custom health check function.
        
        Args:
            check_func: Callable that returns check results
            check_name: Name of the check
        
        Returns:
            Health check result dictionary
        """
        cache_key = f"custom_{check_name}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached
        
        try:
            result = check_func()
            formatted_result = {
                "name": check_name,
                "status": result.get("status", HealthStatus.HEALTHY),
                "message": result.get("message", "Check completed"),
                **{k: v for k, v in result.items() if k not in ["status", "message"]}
            }
            
            self._cache_result(cache_key, formatted_result)
            return formatted_result
        except Exception as e:
            logger.error(f"Custom check '{check_name}' failed: {str(e)}")
            return {
                "name": check_name,
                "status": HealthStatus.UNHEALTHY,
                "error": str(e),
                "message": f"Custom check failed: {str(e)}"
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all health checks.
        
        Returns:
            Dictionary containing all check results and overall status
        """
        start_time = time.time()
        
        results = {
            "service": self.service_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {
                "cpu": self.check_cpu(),
                "memory": self.check_memory(),
                "disk": self.check_disk(),
                "processes": self.check_process_count(),
                "network": self.check_network(),
            }
        }
        
        # Add registered custom checks
        for check_name, check_func in self.checks.items():
            results["checks"][check_name] = self.check_custom(check_func, check_name)
        
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
        """
        Get a brief health summary.
        
        Returns:
            Dictionary containing summary of health status
        """
        results = self.run_all_checks()
        healthy_count = sum(
            1 for check in results["checks"].values()
            if check["status"] == HealthStatus.HEALTHY
        )
        total_checks = len(results["checks"])
        
        return {
            "service": self.service_name,
            "overall_status": results["overall_status"],
            "healthy_checks": healthy_count,
            "total_checks": total_checks,
            "timestamp": results["timestamp"]
        }
    
    def to_http_response(self) -> tuple:
        """
        Get health check results formatted for HTTP response.
        
        Returns:
            Tuple of (response_dict, status_code)
        """
        results = self.run_all_checks()
        
        # Determine HTTP status code based on overall health
        if results["overall_status"] == HealthStatus.HEALTHY:
            status_code = 200
        elif results["overall_status"] == HealthStatus.UNHEALTHY:
            status_code = 503  # Service Unavailable
        else:  # DEGRADED
            status_code = 200  # Still operational, just degraded
        
        return results, status_code
