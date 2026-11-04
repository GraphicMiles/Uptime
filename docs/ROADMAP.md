# Uptime Core WOW Factors - Build Roadmap

## 🎯 Skip Analytics & Auth → Focus on Core Wow Factors

We're building the **magical experience** that makes users say "this is insane."

---

## Phase 1: Device Marketplace Core (Week 1-2)
**Goal**: Users can list idle hardware and earn money. Frictionless signup.

### 1.1 Device Registration & Auto-Detection ✨
```
What: Device owners connect their machine, we auto-detect specs
Why Wow: "One click and you're earning $X/month"

Implementation:
├── Browser agent download (binary for Mac/Win/Linux)
├── Auto-detect: GPU model, VRAM, CPU cores, RAM, storage, bandwidth
├── Send telemetry to Uptime: specs + location + availability
└── Backend stores in device registry

Code Structure:
uptime/
├── device-agent/
│   ├── cli.ts (download & setup)
│   ├── hardware-detect.ts (nvidia-smi, cpu info, etc)
│   ├── availability.ts (online/offline tracking)
│   └── build/ (executable binaries)
├── backend/
│   ├── routes/devices/register.ts
│   ├── models/Device.ts
│   └── services/DeviceRegistry.ts
└── frontend/
    ├── pages/earn-money.tsx
    └── components/DeviceStats.tsx

Real User Flow:
1. User lands on app → "Earn $100-500/month with idle GPU"
2. Click "Download Agent" → agent.exe / agent.dmg / agent.sh
3. Run agent → auto-detects RTX 4090 + 32GB RAM + 8-core CPU
4. Shows: "You can earn ~$200/month"
5. Click "Start Earning" → device goes online
6. Dashboard shows: "Device Online - Earning $0.08/hr"
```

### 1.2 Device Marketplace UI
```
Frontend: React + TailwindCSS
├── Dashboard: "Your Device"
│   ├── Status (Online, Offline, Busy)
│   ├── Real-time earnings counter
│   ├── Current job running (if any)
│   └── Availability schedule (optional)
├── Settings
│   ├── Min/max price per hour
│   ├── Max concurrent jobs
│   └── Pause earnings
└── Analytics
    ├── Total earnings this month
    ├── Jobs completed
    └── Uptime %

Tech Stack:
- Frontend: Next.js (React) + TailwindCSS
- Backend: Node.js/Express + PostgreSQL
- Real-time: WebSocket (earnings ticker)
- Payments: Stripe (payout to users)
```

---

## Phase 2: Job Execution Engine (Week 2-3)
**Goal**: Submit Docker jobs, they execute on devices instantly. Magic.

### 2.1 Job Submission API
```
What: Users submit Docker image + command, job runs on best device
Why Wow: "My 100-GPU training ran in 2 hours for $50"

API Endpoint:
POST /api/jobs/submit
{
  "name": "llm-finetuning-gpt2",
  "docker_image": "pytorch/pytorch:2.0-cuda11.8-runtime",
  "command": "python finetune.py --model gpt2 --epochs 10",
  "resources": {
    "gpu_count": 4,
    "gpu_type": "A100",  // optional filter
    "ram_gb": 128,
    "cpu_cores": 32,
    "storage_gb": 500
  },
  "timeout_seconds": 86400,
  "storage": {
    "input": "s3://my-bucket/training-data/",
    "output": "s3://my-bucket/models/"
  },
  "retry_count": 2,
  "max_cost": 500  // stop if >$500
}

Response:
{
  "job_id": "job_xyz123",
  "status": "queued",
  "estimated_wait": 15,  // seconds
  "estimated_cost": 120,
  "device_assigned": null  // assigned once running
}
```

### 2.2 Job Matching & Scheduling
```
Algorithm: Match jobs to best device (cost + speed + reliability)

Matching Logic:
1. Filter devices by resource requirements
2. Score by: cost/hour × (1 - reliability_factor) × (distance_latency)
3. Pick cheapest + fastest + most reliable
4. Assign job to device

Backend Architecture:
├── JobQueue (Redis/Bull)
│   ├── pending_jobs
│   ├── running_jobs
│   └── completed_jobs
├── DeviceRegistry (PostgreSQL)
│   ├── device_id
│   ├── specs (GPU, CPU, RAM)
│   ├── price_per_hour
│   ├── reliability_score (0-100)
│   └── location (for latency)
├── Scheduler (Node.js service)
│   └── Continuously matches jobs→devices
└── JobExecutor (WebSocket agent)
    └── Receives job → runs container → reports back
```

### 2.3 Docker Execution on Device
```
Device Agent Flow:
1. Agent connects to server via WebSocket
2. Server: "Run this job"
   {
     "job_id": "job_xyz",
     "docker_image": "pytorch/pytorch:2.0",
     "command": "python train.py",
     "env": { "HF_TOKEN": "hf_xxx" }
   }
3. Agent pulls image: docker pull pytorch/pytorch:2.0
4. Agent runs: docker run --gpus all pytorch/pytorch:2.0 python train.py
5. Agent streams: stdout/stderr → server in real-time
6. User sees live logs in dashboard
7. Job completes → upload results to S3
8. Device agent marks job done, awaits next

Code (Device Agent):
// agent/src/executor.ts
async function executeJob(job) {
  const container = await docker.pull(job.docker_image);
  const stream = await docker.run(container, [
    'sh', '-c', job.command
  ], {
    Env: Object.entries(job.env).map(([k,v]) => `${k}=${v}`),
    HostConfig: {
      gpus: 'all'  // Pass all GPUs
    }
  });
  
  // Stream logs to server
  stream.on('data', (chunk) => {
    ws.send(JSON.stringify({
      job_id: job.job_id,
      type: 'log',
      content: chunk.toString()
    }));
  });
  
  stream.on('end', async () => {
    // Upload results
    await uploadToS3(job.output_dir, job.storage.output);
    ws.send({job_id: job.job_id, type: 'done', status: 'success'});
  });
}
```

---

## Phase 3: Real-Time Job Monitoring & Dashboard (Week 3-4)
**Goal**: Users see live job execution, logs, cost ticker. Addictive.

### 3.1 Job Dashboard
```
Frontend Component:
┌─ Job Details ────────────────────────────────────┐
│ Job: llm-finetuning                              │
│ Status: [████████░░] 80% complete (4h 12m)      │
│                                                  │
│ Device: RTX 4090 #42 (California)                │
│ Cost So Far: $45.20 | Est. Total: $56.50        │
│ Cost Per Hour: $13.50 (avg market: $20)         │
│                                                  │
│ ┌─ Live Logs ──────────────────────────────────┐ │
│ │ Epoch 1/10: loss=2.341, val_loss=2.105     │ │
│ │ Epoch 2/10: loss=1.923, val_loss=1.842     │ │
│ │ Epoch 3/10: loss=1.456, val_loss=1.521     │ │
│ │ [Auto-scroll] [Download Logs] [Stop Job]    │ │
│ └──────────────────────────────────────────────┘ │
│                                                  │
│ GPU Usage: ████████████ 95%                      │
│ Memory: ████████░░ 67% (21.4GB / 32GB)          │
│ Network: ↓↑ 125MB/s                             │
│                                                  │
│ [Cancel Job] [Duplicate] [View Results]         │
└──────────────────────────────────────────────────┘

Tech Stack:
- Real-time updates: WebSocket (server → browser)
- Charts: Recharts (GPU usage, cost, progress)
- Logs: VirtualList (handle 100K+ log lines)
- Updates: Every 500ms (cost, progress)
```

### 3.2 Cost Ticker & Notifications
```
Real-time cost counter:
$45.20 → $45.21 → $45.22 → $45.23
(Updates every ~2 seconds)

Visual indicators:
✅ Job progressing normally
⚠️ GPU temp high
🔴 Device connection unstable
💰 Cost exceeded 80% of max_cost budget

Browser notifications (optional):
- "Your job completed in 2h 15m - Results ready"
- "Job cost exceeded $100 - Job stopped"
```

---

## Phase 4: Parallelization & Batch Jobs (Week 4-5)
**Goal**: "Run 1000 jobs in parallel" feels effortless.

### 4.1 Batch Job Submission
```
POST /api/jobs/batch
{
  "name": "image-generation-1M",
  "template": {
    "docker_image": "stability/stable-diffusion:latest",
    "command": "python generate.py --prompt '{prompt}' --output /tmp/output.png",
    "resources": { "gpu_count": 1, "ram_gb": 12 }
  },
  "items": [
    { "prompt": "A cat sitting on a chair" },
    { "prompt": "A dog playing fetch" },
    // ... 1000 items total
  ],
  "max_parallel": 100  // Run 100 at a time
}

Response:
{
  "batch_id": "batch_abc123",
  "total_jobs": 1000,
  "created_jobs": 1000,
  "estimated_total_time": "2h 30m",
  "estimated_cost": 750
}
```

### 4.2 Progress Aggregation
```
GET /api/batches/batch_abc123
{
  "batch_id": "batch_abc123",
  "status": "running",
  "progress": {
    "total": 1000,
    "completed": 342,
    "in_progress": 98,
    "queued": 560,
    "failed": 0,
    "percent": 34.2
  },
  "cost_so_far": 256.50,
  "estimated_total_cost": 750,
  "estimated_time_remaining": "1h 45m",
  "jobs": [
    {
      "job_id": "job_001",
      "status": "completed",
      "device": "RTX 4090 #42",
      "duration": "2m 15s",
      "cost": 0.75,
      "output": "s3://results/image_001.png"
    },
    // ... more jobs
  ]
}

Real-time Updates (WebSocket):
ws.on('message', (msg) => {
  if (msg.type === 'batch_progress') {
    // Update progress bar: 342 → 343 / 1000
    // Update cost: $256.50 → $256.75
    // Update ETA
  }
});
```

### 4.3 Result Aggregation
```
After all jobs complete:
GET /api/batches/batch_abc123/results
{
  "batch_id": "batch_abc123",
  "status": "completed",
  "total_jobs": 1000,
  "successful": 998,
  "failed": 2,
  "total_cost": 749.50,
  "total_time": "2h 28m",
  "results_location": "s3://results/batch_abc123/",
  "artifacts": {
    "all_outputs.tar.gz": "s3://results/batch_abc123/all.tar.gz",
    "logs.zip": "s3://results/batch_abc123/logs.zip",
    "manifest.json": [
      { "job_id": "job_001", "output": "image_001.png", "cost": 0.75 },
      // ... all 1000 jobs
    ]
  }
}
```

---

## Phase 5: Device Marketplace Economics (Week 5-6)
**Goal**: Device owners see real earnings, users see savings. Magic.

### 5.1 Smart Pricing
```
Pricing Strategy:
├── Market-driven pricing
│   ├── Device owner sets minimum price
│   ├── System auto-adjusts based on demand
│   └── Higher demand = higher price (natural equilibrium)
├── Example:
│   ├── Off-peak (night): RTX 4090 = $0.08/hr
│   ├── Peak (day): RTX 4090 = $0.15/hr
│   └── AWS comparable: $0.30/hr (2x Uptime)

Database:
├── devices table
│   ├── gpu_model, vram, cpu_cores, ram_gb
│   ├── base_price_per_hour
│   ├── min_price, max_price
│   ├── current_price (dynamic)
│   └── reputation_score
├── pricing_history table
│   ├── device_id, date, price, num_jobs, utilization%
│   └── avg_earnings_per_day
```

### 5.2 Device Owner Dashboard
```
UI: React Dashboard

┌─ Your Earnings ───────────────────────────────┐
│ Total Lifetime Earnings: $1,248.50            │
│ This Month: $287.30                            │
│ This Week: $52.10                              │
│ Today: $8.45                                   │
│                                                │
│ Monthly Projection: $715/month (if continues) │
├─ Your Device ─────────────────────────────────┤
│ Status: Online ✅                              │
│ Device: RTX 4090 + 32GB RAM + 8-core CPU     │
│                                               │
│ Current Price: $0.12/hour                      │
│ Market Average: $0.10/hour                     │
│ Your Earnings Rank: Top 5% 🏆                │
│                                               │
│ Price Control:                                 │
│ ├── Min: $0.05/hr                              │
│ ├── Max: $0.25/hr                              │
│ └── Current (automatic): $0.12/hr              │
│                                               │
│ This Hour: $0.12 earned                        │
│ Last Job: 45m ago (Stable Diffusion)          │
│ Uptime This Week: 99.2%                        │
├─ Earnings Breakdown ──────────────────────────┤
│ Machine Learning: 45% ($129.29)               │
│ 3D Rendering: 30% ($86.19)                    │
│ Data Processing: 25% ($71.82)                 │
└───────────────────────────────────────────────┘

Actions:
- [Pause Earnings] [View Logs] [Contact Support]
```

### 5.3 Job Cost Transparency
```
User sees when submitting job:
┌─ Cost Estimate ────────────────────────────┐
│ Job: LLM Fine-tuning                       │
│ Duration: ~10 hours                         │
│ Device Type: RTX 4090 (A100 not available) │
│ Price/Hour: $0.12                           │
│ Estimated Cost: $1.20                       │
│                                             │
│ AWS SageMaker equivalent: $4.50             │
│ You save: $3.30 (73% cheaper!)             │
│                                             │
│ [Proceed] [Find Cheaper Device] [Cancel]  │
└────────────────────────────────────────────┘

Comparison table:
Service               | Cost  | Speed | Reliability
Uptime (RTX 4090)    | $1.20 | Fast  | 98%
AWS SageMaker        | $4.50 | Fast  | 99.9%
Lambda (CPU-only)    | $0.50 | Slow  | 99.99%
Local (your laptop)  | $0.00 | Vary  | Your uptime
```

---

## 🔥 THE WOW MOMENTS (Priority Order)

### Wow #1: "One Click to Earn"
**Device owners see**: Click button → device goes online → earnings counter ticks up
```
Visual: $0.00 → $0.05 → $0.10 → $0.15 (every 30s during job)
Goal: Make money feel **real and immediate**
```

### Wow #2: "Jobs Run in Seconds, Not Hours"
**Job submitted**: "Assigning device..." → "Device assigned RTX 4090 in California!" (0.3s)
**Job starts**: Container pulled, code running, logs streaming live
**Alternative experience**: AWS takes 2-5 minutes to boot instance
```
Goal: Speed = quality, reliability
```

### Wow #3: "Cost is 3-10x Cheaper"
**User submits LLM training**:
```
Uptime:  $50-100 for full job
AWS:     $300-500 for same job
```
**Dashboard shows**: "Saved $200 with Uptime!" badge
```
Goal: ROI is obvious
```

### Wow #4: "Real-Time Tracking"
**Live dashboard shows**:
```
GPU Usage:    ████████████ 98%
Memory:       ████████░░ 72% (23GB / 32GB)
Cost Ticker:  $0.00 → $5.23 (updates every 2s)
Progress:     [████████░░] 65% (2h 15m remaining)
Device Temp:  78°C (healthy)
Network:      ↓ 250MB/s
```
**Goal**: Users *feel in control*

### Wow #5: "Scale Without Friction"
**User submits 1000 parallel jobs**:
```
Uptime:
├── API call: 3 seconds
├── Jobs created: 1000
├── Assigned across 500 devices
└── All running within 30 seconds

AWS:
├── Manual setup: 30 minutes
├── Provision instances: 5 minutes
├── Deploy code: 10 minutes
├── All running: 45 minutes total
```
**Goal**: Democratize scale

---

## 📊 Technical Stack Summary

| Component | Tech | Why |
|-----------|------|-----|
| Device Agent | Rust / Node.js | Lightweight, fast, minimal overhead |
| Backend API | Node.js + Express | Fast iteration, JavaScript ecosystem |
| Database | PostgreSQL + Redis | Reliability + speed |
| Frontend | React + Next.js | Modern, real-time capabilities |
| Real-time | WebSocket | Low-latency cost/progress updates |
| Container Runtime | Docker + containerd | Standard, secure |
| Storage | AWS S3 | Reliable, cost-effective, integrations |
| Messaging | Bull/Redis | Job queue, reliable delivery |

---

## 🚀 Success Metrics (MVP)

- ✅ Device can run Docker jobs in <5s after assignment
- ✅ Real-time cost ticker accurate within ±$0.02
- ✅ 99%+ job success rate (can re-try failed)
- ✅ Dashboard loads in <2s
- ✅ Earnings visible to device owner in real-time
- ✅ Cost 3-5x cheaper than AWS for same workload
- ✅ Device owner makes $50-500/month (meaningful earnings)
- ✅ 1000 parallel jobs execute in <1 minute

---

## 📅 Timeline

```
Week 1: Device agent + registration
Week 2: Job execution engine + API
Week 3: Dashboard + real-time updates
Week 4: Batch jobs + parallelization
Week 5: Smart pricing + economics
Week 6: Polish, testing, launch

Launch: Day 1 → 5 beta users (hand-picked)
         Day 7 → Public launch (Product Hunt)
         Day 30 → 100 users, $5K MRR, 50 devices online
```

---

## 🎯 What We're NOT Building Yet

- ❌ Complex auth (simple API key for MVP)
- ❌ Analytics (logging / dashboards come later)
- ❌ Advanced scheduling (simple FIFO queue works)
- ❌ High-availability (single server is fine for MVP)
- ❌ Complex compliance (we're SaaS for now, not FedRAMP)
- ❌ Advanced networking (no private VPCs yet)

**Focus**: Core **WOW** first. Polish later.

---

**Next Step**: Start with Phase 1 device agent. Let's build the fastest, smoothest device registration experience possible.
