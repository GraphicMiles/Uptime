from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import uuid
import json
from database import Database

app = FastAPI(title="Uptime Control Plane")
db = Database()

class DeviceRegistration(BaseModel):
    device_id: str
    name: str
    price: float
    status: str
    specs: dict

class JobSubmit(BaseModel):
    docker_image: str
    command: str
    target_device_id: str

class JobResult(BaseModel):
    job_id: str
    output: str
    error: str
    exit_code: int
    completed_at: str

@app.post("/devices/register")
def register_device(device: DeviceRegistration):
    db.register_device(
        device.device_id,
        device.name,
        device.price,
        device.status,
        device.specs
    )
    return {
        "status": "registered",
        "device_id": device.device_id,
        "message": f"Device {device.name} registered successfully"
    }

@app.get("/devices")
def list_devices():
    devices = db.get_devices()
    for device in devices:
        if device.get("specs"):
            device["specs"] = json.loads(device["specs"])
    return {"devices": devices}

@app.post("/jobs/submit")
def submit_job(job: JobSubmit):
    device = db.get_device(job.target_device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    job_id = str(uuid.uuid4())[:12]
    db.create_job(job_id, job.target_device_id, job.docker_image, job.command)
    
    return {
        "status": "submitted",
        "job_id": job_id,
        "device_id": job.target_device_id,
        "message": "Job submitted successfully"
    }

@app.get("/jobs/pending/{device_id}")
def get_pending_job(device_id: str):
    job = db.get_pending_job(device_id)
    if not job:
        return None
    
    db.mark_job_started(job["id"])
    return dict(job)

@app.post("/jobs/{job_id}/result")
def post_job_result(job_id: str, result: JobResult):
    db.save_result(
        job_id,
        result.output,
        result.error,
        result.exit_code,
        result.completed_at
    )
    
    return {
        "status": "received",
        "job_id": job_id,
        "message": "Result saved successfully"
    }

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    job = db.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return dict(job)

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uptime - Compute Rental MVP</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { font-size: 2.5rem; margin-bottom: 10px; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
        .subtitle { color: #94a3b8; margin-bottom: 40px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 40px; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 24px; }
        .card h2 { font-size: 1.5rem; margin-bottom: 20px; color: #60a5fa; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { background: #0f172a; font-weight: 600; color: #93c5fd; }
        tr:hover { background: #0f172a; }
        .form-group { margin-bottom: 18px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #cbd5e1; }
        input, select, textarea { width: 100%; padding: 10px 12px; border: 1px solid #334155; border-radius: 6px; background: #0f172a; color: #e2e8f0; font-family: inherit; font-size: 14px; }
        input:focus, select:focus, textarea:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
        button { background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: all 0.3s; }
        button:hover { box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); transform: translateY(-2px); }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .status-idle { background: #7c3aed; color: #e9d5ff; }
        .status-running { background: #f97316; color: #fed7aa; }
        .status-completed { background: #22c55e; color: #dcfce7; }
        .result-box { background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 15px; margin-top: 15px; max-height: 300px; overflow-y: auto; font-family: "Courier New", monospace; font-size: 13px; white-space: pre-wrap; word-wrap: break-word; }
        .success { color: #22c55e; }
        .error { color: #ef4444; }
        .loading { animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .msg { padding: 12px; border-radius: 6px; margin-bottom: 15px; display: none; }
        .msg.show { display: block; }
        .msg.success { background: #065f46; color: #86efac; border: 1px solid #10b981; }
        .msg.error { background: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Uptime</h1>
        <p class="subtitle">Compute Rental MVP - Submit jobs to registered devices</p>
        
        <div class="grid">
            <div class="card">
                <h2>📊 Registered Devices</h2>
                <div id="devices-list" style="margin-top: 15px;">
                    <p style="color: #64748b;">Loading devices...</p>
                </div>
            </div>
            
            <div class="card">
                <h2>🚀 Submit a Job</h2>
                <div id="submit-msg" class="msg"></div>
                <form id="job-form">
                    <div class="form-group">
                        <label for="device">Target Device</label>
                        <select id="device" required>
                            <option value="">-- Select a device --</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="image">Docker Image</label>
                        <input type="text" id="image" placeholder="e.g., python:3.11" required>
                    </div>
                    <div class="form-group">
                        <label for="command">Command</label>
                        <textarea id="command" placeholder="e.g., python -c 'print(\\"hello\\")" rows="3" required></textarea>
                    </div>
                    <button type="submit">Submit Job</button>
                </form>
                <div id="job-id-display" style="margin-top: 15px; display: none;">
                    <p style="color: #94a3b8; font-size: 12px;">Job ID:</p>
                    <div style="background: #0f172a; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 13px; color: #60a5fa; word-break: break-all;" id="job-id-value"></div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📋 Check Job Status</h2>
            <div style="display: flex; gap: 10px;">
                <input type="text" id="check-job-id" placeholder="Paste job ID here..." style="flex: 1;">
                <button onclick="checkJobStatus()" style="flex: 0 0 auto;">Check</button>
            </div>
            <div id="job-status" style="margin-top: 20px;"></div>
        </div>
    </div>

    <script>
        async function loadDevices() {
            try {
                const response = await fetch('/devices');
                const data = await response.json();
                displayDevices(data.devices);
                populateDeviceDropdown(data.devices);
            } catch (e) {
                document.getElementById('devices-list').innerHTML = '<p style="color: #ef4444;">Error loading devices</p>';
            }
        }

        function displayDevices(devices) {
            const list = document.getElementById('devices-list');
            if (devices.length === 0) {
                list.innerHTML = '<p style="color: #64748b;">No devices registered yet. Start an agent to register a device.</p>';
                return;
            }
            
            let html = '<table><tr><th>Name</th><th>Specs</th><th>Price</th><th>Status</th></tr>';
            for (const device of devices) {
                const specs = device.specs ? JSON.parse(device.specs) : {};
                const statusClass = 'status-' + (device.status || 'idle');
                html += `<tr><td>${device.name}</td><td style="font-size: 12px; color: #94a3b8;">${specs.cpu_cores || '?'} CPU • ${specs.ram_gb || '?'} GB RAM</td><td>$${device.price}</td><td><span class="status-badge ${statusClass}">${device.status}</span></td></tr>`;
            }
            html += '</table>';
            list.innerHTML = html;
        }

        function populateDeviceDropdown(devices) {
            const select = document.getElementById('device');
            while (select.options.length > 1) { select.remove(1); }
            for (const device of devices) {
                const option = document.createElement('option');
                option.value = device.device_id;
                option.textContent = device.name;
                select.appendChild(option);
            }
        }

        function showMessage(elementId, message, type) {
            const el = document.getElementById(elementId);
            el.textContent = message;
            el.className = `msg show ${type}`;
            setTimeout(() => el.classList.remove('show'), 5000);
        }

        document.getElementById('job-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const deviceId = document.getElementById('device').value;
            const image = document.getElementById('image').value;
            const command = document.getElementById('command').value;
            
            if (!deviceId) {
                showMessage('submit-msg', 'Please select a device', 'error');
                return;
            }
            
            try {
                const response = await fetch('/jobs/submit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ docker_image: image, command: command, target_device_id: deviceId })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    showMessage('submit-msg', '✓ Job submitted! ID: ' + data.job_id, 'success');
                    document.getElementById('job-id-value').textContent = data.job_id;
                    document.getElementById('job-id-display').style.display = 'block';
                    document.getElementById('job-form').reset();
                    document.getElementById('check-job-id').value = data.job_id;
                } else {
                    showMessage('submit-msg', '✗ Error submitting job', 'error');
                }
            } catch (e) {
                showMessage('submit-msg', '✗ Network error: ' + e.message, 'error');
            }
        });

        async function checkJobStatus() {
            const jobId = document.getElementById('check-job-id').value.trim();
            if (!jobId) { alert('Please enter a job ID'); return; }
            
            const statusDiv = document.getElementById('job-status');
            statusDiv.innerHTML = '<p class="loading">Checking...</p>';
            
            try {
                const response = await fetch(`/jobs/${jobId}`);
                if (response.ok) {
                    const job = await response.json();
                    displayJobStatus(job);
                } else if (response.status === 404) {
                    statusDiv.innerHTML = '<p class="error">Job not found</p>';
                } else {
                    statusDiv.innerHTML = '<p class="error">Error checking job</p>';
                }
            } catch (e) {
                statusDiv.innerHTML = '<p class="error">Network error: ' + e.message + '</p>';
            }
        }

        function displayJobStatus(job) {
            const statusDiv = document.getElementById('job-status');
            const statusClass = 'status-' + (job.status || 'unknown');
            
            let html = `<div style="margin-bottom: 15px;"><div><strong>Status:</strong> <span class="status-badge ${statusClass}">${job.status}</span></div><div style="margin-top: 10px; color: #94a3b8; font-size: 12px;"><div>Created: ${new Date(job.created_at).toLocaleString()}</div>${job.completed_at ? '<div>Completed: ' + new Date(job.completed_at).toLocaleString() + '</div>' : ''}</div></div>`;
            
            if (job.exit_code !== null) {
                html += `<div style="margin-bottom: 15px;"><strong>Exit Code:</strong> <span class="${job.exit_code === 0 ? 'success' : 'error'}">${job.exit_code}</span></div>`;
            }
            
            if (job.output) { html += `<div><strong>Output:</strong><div class="result-box">${escapeHtml(job.output)}</div></div>`; }
            if (job.error) { html += `<div style="margin-top: 15px;"><strong>Error:</strong><div class="result-box error">${escapeHtml(job.error)}</div></div>`; }
            
            statusDiv.innerHTML = html;
        }

        function escapeHtml(text) {
            const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'};
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        loadDevices();
        setInterval(loadDevices, 10000);
    </script>
</body>
</html>"""

@app.get("/")
def serve_frontend():
    return HTMLResponse(HTML_CONTENT)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)