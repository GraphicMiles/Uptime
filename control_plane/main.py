from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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
    <title>Uptime - Distributed Compute Network</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #3b82f6;
            --primary-dark: #1e40af;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark-bg: #0f172a;
            --card-bg: #1e293b;
            --border: #334155;
            --text-primary: #e2e8f0;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
            background: linear-gradient(135deg, var(--dark-bg) 0%, #1a2847 100%);
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        .navbar {
            background: rgba(15, 23, 42, 0.95);
            border-bottom: 1px solid var(--border);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }

        .navbar-content {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .navbar-logo {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .navbar-status {
            display: flex;
            gap: 20px;
            align-items: center;
            font-size: 0.9rem;
        }

        .status-indicator {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--success);
            animation: pulse-status 2s infinite;
        }

        @keyframes pulse-status {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .header {
            margin-bottom: 50px;
            text-align: center;
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header p {
            font-size: 1.1rem;
            color: var(--text-secondary);
            margin-bottom: 20px;
        }

        .stats-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            border-color: var(--primary);
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.15);
            transform: translateY(-2px);
        }

        .stat-number {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 5px;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        @media (max-width: 1024px) {
            .main-grid {
                grid-template-columns: 1fr;
            }
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 30px;
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: var(--primary);
            box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1);
        }

        .card h2 {
            font-size: 1.3rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: var(--primary);
        }

        .card-icon {
            font-size: 1.5rem;
        }

        .devices-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        .devices-table th {
            background: rgba(59, 130, 246, 0.1);
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: var(--primary);
            border-bottom: 2px solid var(--border);
            font-size: 0.9rem;
        }

        .devices-table td {
            padding: 14px 12px;
            border-bottom: 1px solid var(--border);
            font-size: 0.9rem;
        }

        .devices-table tr:hover {
            background: rgba(59, 130, 246, 0.05);
        }

        .device-name {
            font-weight: 600;
            color: var(--primary);
        }

        .device-specs {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }

        .device-price {
            color: var(--success);
            font-weight: 600;
        }

        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            white-space: nowrap;
        }

        .status-idle {
            background: rgba(139, 92, 246, 0.2);
            color: #c4b5fd;
        }

        .status-running {
            background: rgba(249, 115, 22, 0.2);
            color: #fed7aa;
        }

        .status-completed {
            background: rgba(16, 185, 129, 0.2);
            color: #86efac;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--text-primary);
            font-size: 0.95rem;
        }

        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(15, 23, 42, 0.5);
            color: var(--text-primary);
            font-family: inherit;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }

        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            background: rgba(15, 23, 42, 0.8);
        }

        textarea {
            resize: vertical;
            font-family: "Courier New", monospace;
            font-size: 0.9rem;
        }

        button {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.95rem;
        }

        button:hover {
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
            transform: translateY(-2px);
        }

        button:active {
            transform: translateY(0);
        }

        .alert {
            padding: 14px 16px;
            border-radius: 8px;
            margin-bottom: 15px;
            display: none;
            border-left: 4px solid;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .alert.show {
            display: block;
        }

        .alert.success {
            background: rgba(16, 185, 129, 0.1);
            color: #86efac;
            border-left-color: var(--success);
        }

        .alert.error {
            background: rgba(239, 68, 68, 0.1);
            color: #fca5a5;
            border-left-color: var(--danger);
        }

        .result-box {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            margin-top: 12px;
            max-height: 400px;
            overflow-y: auto;
            font-family: "Courier New", monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #86efac;
        }

        .result-box.error {
            color: #fca5a5;
        }

        .job-id-display {
            margin-top: 20px;
            padding: 16px;
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            border-radius: 8px;
            display: none;
        }

        .job-id-display.show {
            display: block;
        }

        .job-id-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .job-id-value {
            background: rgba(15, 23, 42, 0.8);
            padding: 12px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.9rem;
            color: var(--primary);
            word-break: break-all;
            border: 1px solid var(--border);
        }

        .job-status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .status-item {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }

        .status-item-label {
            color: var(--text-secondary);
            font-size: 0.8rem;
            margin-bottom: 4px;
        }

        .status-item-value {
            color: var(--primary);
            font-weight: 600;
            font-size: 1rem;
        }

        .loading {
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
        }

        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 10px;
        }

        .footer {
            text-align: center;
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <div class="navbar-logo">⚡ Uptime</div>
            <div class="navbar-status">
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span>Distributed Compute Network</span>
                </div>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="header">
            <h1>⚡ Uptime Compute Network</h1>
            <p>Securely execute jobs on distributed devices with real-time monitoring</p>
        </div>

        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-number" id="device-count">0</div>
                <div class="stat-label">Active Devices</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="job-count">0</div>
                <div class="stat-label">Total Jobs</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="computing-power">0</div>
                <div class="stat-label">Total CPU Cores</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="network-ram">0 GB</div>
                <div class="stat-label">Network RAM</div>
            </div>
        </div>

        <div class="main-grid">
            <div class="card">
                <h2><span class="card-icon">📊</span> Network Devices</h2>
                <div id="devices-list" style="margin-top: 15px;">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>No devices registered yet</p>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2><span class="card-icon">🚀</span> Submit a Compute Job</h2>
                <div id="submit-msg" class="alert"></div>
                <form id="job-form">
                    <div class="form-group">
                        <label for="device">Target Device</label>
                        <select id="device" required>
                            <option value="">-- Select a device --</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="image">Docker Image <small style="color: var(--text-secondary);">(sandboxed)</small></label>
                        <input type="text" id="image" placeholder="e.g., python:3.11, node:18" required>
                    </div>
                    <div class="form-group">
                        <label for="command">Command to Execute</label>
                        <textarea id="command" placeholder="e.g., python -c 'print(\"Hello World!\")" rows="4" required></textarea>
                    </div>
                    <button type="submit">▶️ Submit Job</button>
                </form>
                <div id="job-id-display" class="job-id-display">
                    <div class="job-id-label">✓ Job Submitted Successfully</div>
                    <div class="job-id-value" id="job-id-value"></div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2><span class="card-icon">📋</span> Check Job Status & Results</h2>
            <div id="check-msg" class="alert"></div>
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <input type="text" id="check-job-id" placeholder="Paste job ID here..." style="flex: 1;">
                <button onclick="checkJobStatus()" style="flex: 0 0 auto;">🔍 Check Status</button>
            </div>
            <div id="job-status"></div>
        </div>

        <div class="footer">
            <p>🔒 All jobs execute in isolated Docker containers. Device data is protected.</p>
            <p style="margin-top: 10px;">Uptime © 2026 | Distributed Compute Network</p>
        </div>
    </div>

    <script>
        let allDevices = [];

        async function loadDevices() {
            try {
                const response = await fetch('/devices');
                const data = await response.json();
                allDevices = data.devices;
                displayDevices(data.devices);
                populateDeviceDropdown(data.devices);
                updateStats(data.devices);
            } catch (e) {
                console.error('Error loading devices:', e);
            }
        }

        function updateStats(devices) {
            document.getElementById('device-count').textContent = devices.length;
            
            let totalCores = 0;
            let totalRam = 0;

            for (const device of devices) {
                const specs = device.specs ? JSON.parse(device.specs) : {};
                totalCores += specs.cpu_cores || 0;
                totalRam += specs.ram_gb || 0;
            }

            document.getElementById('computing-power').textContent = totalCores;
            document.getElementById('network-ram').textContent = totalRam.toFixed(1) + ' GB';
        }

        function displayDevices(devices) {
            const list = document.getElementById('devices-list');
            if (devices.length === 0) {
                list.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📭</div><p>No devices registered yet</p></div>';
                return;
            }
            
            let html = '<table class="devices-table"><thead><tr><th>Device Name</th><th>Specifications</th><th>Price/Unit</th><th>Status</th></tr></thead><tbody>';
            
            for (const device of devices) {
                const specs = device.specs ? JSON.parse(device.specs) : {};
                const statusClass = 'status-' + (device.status || 'idle');
                const statusLabel = device.status === 'idle' ? '🟣 Idle' : device.status === 'running' ? '🟠 Running' : '🟢 Ready';
                
                html += `
                    <tr>
                        <td><span class="device-name">${device.name}</span></td>
                        <td><span class="device-specs">${specs.cpu_cores || '?'} CPU cores • ${specs.ram_gb || '?'} GB RAM • ${specs.disk_gb || '?'} GB disk</span></td>
                        <td><span class="device-price">$${device.price.toFixed(2)}</span></td>
                        <td><span class="status-badge ${statusClass}">${statusLabel}</span></td>
                    </tr>
                `;
            }
            html += '</tbody></table>';
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
            el.className = `alert show ${type}`;
            setTimeout(() => el.classList.remove('show'), 5000);
        }

        document.getElementById('job-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const deviceId = document.getElementById('device').value;
            const image = document.getElementById('image').value;
            const command = document.getElementById('command').value;
            
            if (!deviceId) {
                showMessage('submit-msg', '⚠️ Please select a device', 'error');
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
                    showMessage('submit-msg', '✅ Job submitted successfully!', 'success');
                    document.getElementById('job-id-value').textContent = data.job_id;
                    document.getElementById('job-id-display').classList.add('show');
                    document.getElementById('job-form').reset();
                    document.getElementById('check-job-id').value = data.job_id;
                } else {
                    showMessage('submit-msg', '❌ Error submitting job', 'error');
                }
            } catch (e) {
                showMessage('submit-msg', '❌ Network error', 'error');
            }
        });

        async function checkJobStatus() {
            const jobId = document.getElementById('check-job-id').value.trim();
            if (!jobId) { 
                showMessage('check-msg', '⚠️ Please enter a job ID', 'error');
                return; 
            }
            
            const statusDiv = document.getElementById('job-status');
            statusDiv.innerHTML = '<div style="text-align: center; padding: 40px;"><div class="loading" style="font-size: 2rem; display: inline-block;">⏳</div></div>';
            
            try {
                const response = await fetch(`/jobs/${jobId}`);
                if (response.ok) {
                    const job = await response.json();
                    displayJobStatus(job);
                } else if (response.status === 404) {
                    statusDiv.innerHTML = '<div class="empty-state"><div class="empty-state-icon">❌</div><p>Job not found</p></div>';
                }
            } catch (e) {
                statusDiv.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔌</div><p>Network error</p></div>';
            }
        }

        function displayJobStatus(job) {
            const statusDiv = document.getElementById('job-status');
            const statusEmoji = {'pending': '⏳', 'running': '🔄', 'completed': '✅', 'error': '❌'}[job.status] || '❓';
            
            let html = `
                <div class="job-status-grid">
                    <div class="status-item">
                        <div class="status-item-label">Status</div>
                        <div class="status-item-value">${statusEmoji} ${job.status}</div>
                    </div>
                    <div class="status-item">
                        <div class="status-item-label">Created</div>
                        <div class="status-item-value" style="font-size: 0.9rem;">${new Date(job.created_at).toLocaleTimeString()}</div>
                    </div>
                    ${job.exit_code !== null ? `<div class="status-item">
                        <div class="status-item-label">Exit Code</div>
                        <div class="status-item-value" style="color: ${job.exit_code === 0 ? '#86efac' : '#fca5a5'};">${job.exit_code}</div>
                    </div>` : ''}
                </div>
            `;
            
            if (job.output) {
                html += `<div><label style="margin-bottom: 8px;">📤 Output:</label><div class="result-box">${escapeHtml(job.output)}</div></div>`;
            }
            
            if (job.error) {
                html += `<div style="margin-top: 15px;"><label style="margin-bottom: 8px;">⚠️ Errors:</label><div class="result-box error">${escapeHtml(job.error)}</div></div>`;
            }
            
            statusDiv.innerHTML = html;
        }

        function escapeHtml(text) {
            const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'};
            return text.replace(/[&<>"]/g, m => map[m]);
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