# Uptime

A working skeleton for renting out idle compute. A machine registers itself, a job
is submitted to it, the job runs in a container, and the output comes back.

The whole loop is here and it runs in about a minute: FastAPI control plane,
SQLite, a Python agent on the worker, and a single page to drive it. It exists to
prove the loop rather than to be deployed.

## Why it exists

"Rent out your spare compute" is easy to say and hard to believe until you watch a
container start on someone else's machine and hand back a result. This is the
smallest version that proves it: registration, dispatch, execution, result.

## What you can do

- **Register a device.** The agent reports CPU cores, RAM, disk and whether there
  is a GPU.
- **Submit a job** to a device: a Docker image and a command.
- **Watch it run** on the agent, which polls every five seconds and executes in a
  container.
- **Read the output** in the frontend once the agent posts the result.
- **Inspect the API**: `POST /devices/register`, `GET /devices`,
  `POST /jobs/submit`, `GET /jobs/pending/{device_id}`,
  `POST /jobs/{id}/result`, `GET /jobs/{id}`.

## Running it

Three terminals, or two machines:

```bash
# 1. control plane
cd control_plane
pip install -r requirements.txt
python main.py            # http://localhost:8000

# 2. agent, on the machine that will do the work
cd agent
pip install -r requirements.txt
python agent.py --price 0.10 --name "device-1"

# 3. open http://localhost:8000/
```

Pick the device, enter an image and a command such as `python:3.11` with
`python -c "print('hello')"`, submit, and watch the output appear. `run.sh` and
`run.bat` wrap the same commands. Docker must be available to the agent.

To expose the control plane, a Cloudflare tunnel is enough:

```bash
cloudflared tunnel run --url http://localhost:8000
```

## What is not here

No authentication, no authorisation, no scheduler intelligence (you pick the
device), no payment processing, and no persistence worth the name: SQLite is
ephemeral, so a restart loses the registry. Containers run with default Docker
settings and are not hardened.

Those are recorded as gaps rather than left to be discovered. Do not put this on
the public internet with a token you care about.

## How it is built

```
control_plane/    FastAPI app, SQLite models, static frontend
agent/            the worker: registration, polling, container execution
docs/             SETUP.md, ROADMAP.md, INVESTOR_BRIEF.md
```

## Licence

No licence file is included in this repository.
