#!/usr/bin/env python3
"""
Health check script for IRCAM V24.
Monitors system health and performs recovery actions if needed.
"""
import requests
import psutil
import os
import sys
import logging
import subprocess
import time
import socket
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ircam/health.log'),
        logging.StreamHandler()
    ]
)

class InternetMonitor:
    def __init__(self):
        # List of reliable endpoints to check (hostname, port)
        self.endpoints = [
            ("8.8.8.8", 53),      # Google DNS
            ("1.1.1.1", 53),      # Cloudflare DNS
            ("208.67.222.222", 53) # OpenDNS
        ]
        
        # HTTP endpoints for connectivity check
        self.http_endpoints = [
            "https://www.google.com",
            "https://www.cloudflare.com",
            "https://api.github.com"
        ]
        
        self.timeout = 5
        self.min_successful = 2  # Minimum number of successful checks required

    def check_dns_connectivity(self, endpoint: Tuple[str, int]) -> bool:
        """Test TCP connection to a specific endpoint"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect(endpoint)
            sock.close()
            return True
        except:
            return False

    def check_http_connectivity(self, url: str) -> bool:
        """Test HTTP connectivity to a specific endpoint"""
        try:
            response = requests.get(url, timeout=self.timeout)
            return response.status_code == 200
        except:
            return False

    def check_internet(self) -> Tuple[bool, str]:
        """
        Check internet connectivity using multiple methods.
        Returns: (is_connected: bool, status_message: str)
        """
        # First, check DNS servers using TCP
        successful_dns = 0
        with ThreadPoolExecutor(max_workers=3) as executor:
            dns_futures = {executor.submit(self.check_dns_connectivity, endpoint): endpoint 
                         for endpoint in self.endpoints}
            
            for future in as_completed(dns_futures):
                endpoint = dns_futures[future]
                if future.result():
                    successful_dns += 1
                    logging.debug(f"Successfully connected to DNS {endpoint[0]}")
                else:
                    logging.warning(f"Failed to connect to DNS {endpoint[0]}")

        # If DNS checks fail, try HTTP endpoints
        if successful_dns < self.min_successful:
            successful_http = 0
            with ThreadPoolExecutor(max_workers=3) as executor:
                http_futures = {executor.submit(self.check_http_connectivity, url): url 
                              for url in self.http_endpoints}
                
                for future in as_completed(http_futures):
                    url = http_futures[future]
                    if future.result():
                        successful_http += 1
                        logging.debug(f"Successfully connected to {url}")
                    else:
                        logging.warning(f"Failed to connect to {url}")

            if successful_http >= self.min_successful:
                return True, "Internet connection available (HTTP)"
            return False, f"Internet connection failed (DNS: {successful_dns}/{len(self.endpoints)}, HTTP: {successful_http}/{len(self.http_endpoints)})"

        return True, "Internet connection available (DNS)"

class HealthMonitor:
    def __init__(self):
        self.api_url = "http://localhost:8000"
        self.service_name = "ircam"
        self.max_memory_percent = 85
        self.max_cpu_percent = 90
        self.min_free_disk_space = 500  # MB
        self.consecutive_failures = 0
        self.max_failures = 3
        self.internet_monitor = InternetMonitor()
        self.last_internet_status = True

    def check_api_health(self) -> bool:
        """Check if the API is responding"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/health")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"API health check failed: {e}")
            return False

    def check_system_resources(self) -> bool:
        """Check system resource usage"""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.max_cpu_percent:
                logging.warning(f"High CPU usage: {cpu_percent}%")
                return False

            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.max_memory_percent:
                logging.warning(f"High memory usage: {memory.percent}%")
                return False

            # Check disk space
            disk = psutil.disk_usage('/')
            free_mb = disk.free / (1024 * 1024)
            if free_mb < self.min_free_disk_space:
                logging.warning(f"Low disk space: {free_mb:.2f}MB free")
                return False

            return True
        except Exception as e:
            logging.error(f"System resource check failed: {e}")
            return False

    def check_database_connection(self) -> bool:
        """Check if database is accessible"""
        try:
            response = requests.get(f"{self.api_url}/api/v1/settings")
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Database connection check failed: {e}")
            return False

    def restart_service(self):
        """Restart the IRCAM service"""
        try:
            subprocess.run(['systemctl', 'restart', self.service_name], check=True)
            logging.info("Service restarted successfully")
            # Wait for service to start
            time.sleep(10)
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to restart service: {e}")

    def perform_recovery(self):
        """Perform recovery actions"""
        logging.warning("Initiating recovery procedure")
        
        # Stop service
        subprocess.run(['systemctl', 'stop', self.service_name], check=True)
        
        # Clear any temporary files
        tmp_dir = "/opt/ircam-v24/tmp"
        if os.path.exists(tmp_dir):
            for file in os.listdir(tmp_dir):
                try:
                    os.remove(os.path.join(tmp_dir, file))
                except Exception as e:
                    logging.error(f"Failed to remove temp file {file}: {e}")
        
        # Start service
        subprocess.run(['systemctl', 'start', self.service_name], check=True)
        
        # Reset failure counter
        self.consecutive_failures = 0
        logging.info("Recovery procedure completed")

    def check_tailscale_status(self) -> bool:
        """Check if Tailscale is connected and running"""
        try:
            result = subprocess.run(['tailscale', 'status', '--json'], 
                                 capture_output=True, text=True, check=True)
            status = json.loads(result.stdout)
            
            is_running = status.get('BackendState') == 'Running'
            tailscale_ip = status.get('TailscaleIPs', [None])[0]
            
            if is_running and tailscale_ip:
                logging.info(f"Tailscale connected - IP: {tailscale_ip}")
                return True
            else:
                logging.warning("Tailscale not connected")
                return False
        except Exception as e:
            logging.error(f"Error checking Tailscale status: {e}")
            return False

    def check_internet_connection(self) -> bool:
        """Check if internet connection is available"""
        is_connected, message = self.internet_monitor.check_internet()
        
        # Log only when status changes
        if is_connected != self.last_internet_status:
            if is_connected:
                logging.info(f"Internet connection restored: {message}")
            else:
                logging.warning(f"Internet connection lost: {message}")
            self.last_internet_status = is_connected
        
        return is_connected

    def run_checks(self):
        """Run all health checks"""
        checks = [
            (self.check_internet_connection, "Internet Connection"),
            (self.check_tailscale_status, "Tailscale VPN"),
            (self.check_api_health, "API"),
            (self.check_system_resources, "System Resources"),
            (self.check_database_connection, "Database")
        ]

        all_healthy = True
        for check_func, name in checks:
            try:
                if not check_func():
                    logging.warning(f"{name} check failed")
                    all_healthy = False
                else:
                    logging.info(f"{name} check passed")
            except Exception as e:
                logging.error(f"Error during {name} check: {e}")
                all_healthy = False

        if not all_healthy:
            self.consecutive_failures += 1
            logging.warning(f"Health check failed. Consecutive failures: {self.consecutive_failures}")
            
            if self.consecutive_failures >= self.max_failures:
                logging.error("Maximum consecutive failures reached. Initiating recovery.")
                self.perform_recovery()
        else:
            self.consecutive_failures = 0
            logging.info("All health checks passed")

def main():
    monitor = HealthMonitor()
    
    # Create log directory if it doesn't exist
    os.makedirs('/var/log/ircam', exist_ok=True)
    
    while True:
        try:
            monitor.run_checks()
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
        
        # Wait for next check
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
