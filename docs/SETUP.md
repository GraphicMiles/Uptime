# Uptime — Compute Rental MVP — Skeleton Build

## ⚡ Quick Start (5 minutes)

### Prerequisites
- **Python 3.8+** ([download](https://www.python.org/))
- **Docker** ([download](https://www.docker.com/))

### Step 1: Start the Control Plane

**Windows:**
```bash
cd control_plane
run.bat
```

**macOS/Linux:**
```bash
cd control_plane
chmod +x run.sh
./run.sh
```

Control plane starts on `http://localhost:8000`

### Step 2: Start an Agent

**Windows:**
```bash
cd agent
run.bat
```

**macOS/Linux:**
```bash
cd agent
chmod +x run.sh
./run.sh
```

### Step 3: Open Frontend & Submit a Job

1. Open `http://localhost:8000`
2. Select your device from dropdown
3. Enter Docker image: `python:3.11`
4. Enter command: `echo "Hello from Uptime!"`
5. Click Submit Job
6. Paste Job ID to check results

---

## 🏗️ Architecture

### Control Plane (`control_plane/main.py`)
FastAPI + SQLite server with 7 endpoints:
- `POST /devices/register` — Device registration
- `GET /devices` — List devices
- `POST /jobs/submit` — Submit job
- `GET /jobs/pending/{device_id}` — Agent polls for jobs
- `POST /jobs/{id}/result` — Agent posts results
- `GET /jobs/{id}` — Check job status
- `GET /` — Frontend UI

### Agent (`agent/agent.py`)
Python script on your machine:
- Collects specs (CPU, RAM, disk) with `psutil`
- Registers with control plane
- Polls every 5 seconds for jobs
- Runs jobs in Docker (`docker run --rm`)
- Posts results back

**Run with:**
```bash
python agent.py --name "device-1" --price 0.10 --url http://localhost:8000
```

### Frontend
Interactive web UI:
- Device registry table
- Job submission form
- Results viewer

---

## 🧪 Test Scenarios

### Test 1: Basic Execution
```
Image: python:3.11
Command: echo "test123"
Result: test123 ✓
```

### Test 2: Python Code
```
Image: python:3.11
Command: python -c "print('Hello from Uptime!')"
Result: Hello from Uptime! ✓
```

### Test 3: Multiple Devices
Start 2+ agents → Submit jobs to different devices → Both execute

---

## ⚠️ Known Gaps (v1)

- No authentication/authorization
- No auto-scheduling (manual device selection)
- No sandboxing beyond Docker defaults
- No data persistence (SQLite data lost on restart)
- No multi-device orchestration
- No payment processing

---

## 🚀 Deployment

### Cloudflare Tunnel (Public URL)
```bash
cloudflared tunnel run --url http://localhost:8000
```

### Railway/Fly.io
Push to GitHub → Deploy via Railway or Fly.io

---

## 🐛 Troubleshooting

**Agent won't connect:**
- Is control plane running? `http://localhost:8000`
- Is Docker running?

**Jobs fail immediately:**
- Test Docker: `docker pull python:3.11`
- Linux may need: `sudo usermod -aG docker $USER`

**No devices showing:**
- Refresh browser page
- Check agent logs for errors

---

## 📋 File Structure

```
Uptime/
├── agent/
│   ├── agent.py              (Device agent)
│   ├── requirements.txt
│   ├── run.bat              (Windows launcher)
│   └── run.sh               (Unix launcher)
├── control_plane/
│   ├── main.py              (FastAPI server + frontend)
│   ├── database.py          (SQLite backend)
│   ├── requirements.txt
│   ├── run.bat              (Windows launcher)
│   └── run.sh               (Unix launcher)
├── README.md
└── SETUP.md                 (This file)
```

---

**Definition of Done (v1):** User starts agent → opens frontend → submits job → sees output within 30s ✓