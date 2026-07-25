# Uptime — Compute Rental MVP

A tangibility skeleton to prove: devices register → jobs submit → jobs execute on devices → output returns.

## Quick Start (5 minutes)

### 1. Start the Control Plane
```bash
cd control_plane
pip install -r requirements.txt
python main.py
```
Runs on `http://localhost:8000`

### 2. Start an Agent (on your machine or another)
```bash
cd agent
pip install -r requirements.txt
python agent.py --price 0.10 --name "device-1"
```

### 3. Submit a Job via Frontend
Open `http://localhost:8000/` (served by FastAPI)
- See your registered device
- Pick it from the dropdown
- Enter a Docker image + command (e.g., `python:3.11` + `python -c "print('hello')"`)
- Submit → job runs on the agent → output appears

## Architecture

### Control Plane (`control_plane/main.py`)
FastAPI server with SQLite backend.

**Endpoints:**
- `POST /devices/register` — device registers itself
- `GET /devices` — list all devices
- `POST /jobs/submit` — submit a job to a device
- `GET /jobs/pending/{device_id}` — agent polls for jobs
- `POST /jobs/{id}/result` — agent posts job output
- `GET /jobs/{id}` — check job status

### Agent (`agent/agent.py`)
Python script runs on device owner's machine.

- Collects specs: CPU cores, RAM, disk, GPU flag
- Registers with control plane
- Polls for jobs every 5s
- Runs jobs in Docker containers
- Posts results back

### Frontend
Single static page (served by FastAPI at `/`) with:
- Device registry table
- Job submission form
- Results viewer

## Known Gaps (Not Fixing in v1)
- No authentication or authorization
- No scheduler intelligence (manual device selection)
- Docker runs with default security (not hardened)
- No payment processing (manual logging only)
- No persistence across restarts (SQLite is ephemeral)

## Deployment
Use **Cloudflare Tunnel** to expose the control plane:
```bash
cloudflared tunnel run --url http://localhost:8000
```
This gives you a public URL without port forwarding.

---

**Definition of Done:** One person starts an agent, opens the frontend, submits a job targeting that device, and sees output within ~30s.
