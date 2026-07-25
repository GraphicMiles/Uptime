import psutil
import requests
import subprocess
import time
import argparse
import json
import sys
import os
import uuid
from datetime import datetime

class Agent:
    def __init__(self, name, price, control_plane_url):
        self.device_id = str(uuid.uuid4())[:8]
        self.name = name
        self.price = price
        self.control_plane_url = control_plane_url.rstrip('/')
        self.status = "idle"
        self.specs = self.collect_specs()
        
    def collect_specs(self):
        """Collect device specifications using psutil."""
        return {
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_logical": psutil.cpu_count(logical=True),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
            "has_gpu": False
        }
    
    def register(self):
        """Register device with control plane."""
        payload = {
            "device_id": self.device_id,
            "name": self.name,
            "price": self.price,
            "status": self.status,
            "specs": self.specs
        }
        try:
            response = requests.post(
                f"{self.control_plane_url}/devices/register",
                json=payload,
                timeout=5
            )
            if response.status_code in [200, 201]:
                print(f"✓ Registered device: {self.name} ({self.device_id})")
                return True
            else:
                print(f"✗ Registration failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Registration error: {e}")
            return False
    
    def poll_jobs(self):
        """Poll for pending jobs every 5 seconds."""
        try:
            response = requests.get(
                f"{self.control_plane_url}/jobs/pending/{self.device_id}",
                timeout=5
            )
            if response.status_code == 200:
                job = response.json()
                if job:
                    return job
        except Exception as e:
            print(f"✗ Poll error: {e}")
        return None
    
    def run_job(self, job):
        """Run a job in Docker and capture output."""
        job_id = job.get("id")
        docker_image = job.get("docker_image")
        command = job.get("command")
        
        print(f"\n► Running job {job_id}...")
        print(f"  Image: {docker_image}")
        print(f"  Command: {command}")
        
        try:
            docker_cmd = [
                "docker", "run", "--rm",
                docker_image,
                "/bin/sh", "-c", command
            ]
            
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout
            error = result.stderr
            exit_code = result.returncode
            
            return {
                "output": output,
                "error": error,
                "exit_code": exit_code,
                "success": exit_code == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "output": "",
                "error": "Job timeout (60s)",
                "exit_code": -1,
                "success": False
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "exit_code": -1,
                "success": False
            }
    
    def post_result(self, job_id, result):
        """Post job result back to control plane."""
        payload = {
            "job_id": job_id,
            "output": result["output"],
            "error": result["error"],
            "exit_code": result["exit_code"],
            "completed_at": datetime.now().isoformat()
        }
        try:
            response = requests.post(
                f"{self.control_plane_url}/jobs/{job_id}/result",
                json=payload,
                timeout=5
            )
            if response.status_code in [200, 201]:
                print(f"✓ Result posted for job {job_id}")
                return True
            else:
                print(f"✗ Failed to post result: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Post result error: {e}")
            return False
    
    def run(self):
        """Main agent loop."""
        print(f"\n{'='*60}")
        print(f"Uptime Agent v1 — {self.name}")
        print(f"Device ID: {self.device_id}")
        print(f"Control Plane: {self.control_plane_url}")
        print(f"{'='*60}\n")
        
        print("Specs:")
        for key, val in self.specs.items():
            print(f"  {key}: {val}")
        print()
        
        if not self.register():
            print("Failed to register. Exiting.")
            sys.exit(1)
        
        print("\n► Polling for jobs (press Ctrl+C to stop)...\n")
        try:
            while True:
                job = self.poll_jobs()
                if job:
                    result = self.run_job(job)
                    self.post_result(job["id"], result)
                    print()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n\n✓ Agent stopped.")

def main():
    parser = argparse.ArgumentParser(description="Uptime Agent")
    parser.add_argument("--name", default="device-1", help="Device name")
    parser.add_argument("--price", type=float, default=0.10, help="Price per compute unit")
    parser.add_argument("--url", default="http://localhost:8000", help="Control plane URL")
    
    args = parser.parse_args()
    
    agent = Agent(args.name, args.price, args.url)
    agent.run()

if __name__ == "__main__":
    main()