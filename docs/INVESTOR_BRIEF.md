# Uptime — Distributed Compute Network
## Executive Brief for Investors & Partners

---

## 🎯 Executive Summary

**Uptime** is a decentralized compute marketplace that allows individuals and businesses to monetize idle computing resources while providing affordable, scalable compute power to users. Think Airbnb for compute—owners list their devices as compute nodes, users submit jobs, and the network executes them securely in isolated sandboxes.

### The Problem
- **Cloud costs** are prohibitively expensive ($0.30-$2.00/hour for compute)
- **Idle hardware** sits unused on millions of desks, laptops, and servers
- **Vendor lock-in** makes migrating workloads between providers difficult
- **Data sovereignty** concerns prevent some organizations from using centralized clouds

### The Solution
**Uptime Network**: A peer-to-peer compute marketplace where:
- Device owners register unused capacity and set prices
- Users submit containerized jobs (Docker images + commands)
- The network matches jobs to devices and executes in secure sandboxes
- Results are returned in real-time
- Transactions are recorded for payment settlement

### Market Opportunity
- **TAM**: $30B+ cloud computing market (IaaS segment)
- **Initial Target**: Edge computing, CI/CD pipelines, data processing, AI inference
- **Unit Economics**: 50-70% cheaper than AWS/GCP/Azure

---

## 🏗️ Product Architecture

### Current State (v1 MVP - Complete ✓)

```
User Browser (Frontend UI)
        ↓
┌───────────────────────────────────────┐
│   Control Plane (FastAPI + SQLite)    │
│   - Device Registry                   │
│   - Job Queue & Scheduler             │
│   - Result Storage                    │
└───────────────────────────────────────┘
        ↑                       ↑
        │                       │
   Agent (Device A)        Agent (Device B)
   [Docker Sandbox]        [Docker Sandbox]
```

### Three Core Components

#### 1. **Control Plane** (`control_plane/main.py`)
- **Tech Stack**: FastAPI, SQLite, Python 3.11
- **Role**: Central orchestrator
- **Responsibilities**:
  - Device registration and heartbeat tracking
  - Job queue management
  - Device-to-job matching
  - Result aggregation
  - Pricing & billing ledger
  
**Endpoints**:
```
POST   /devices/register          → Device registers itself
GET    /devices                   → List all devices + specs
POST   /jobs/submit               → Submit a job to a device
GET    /jobs/pending/{device_id}  → Agent polls for jobs
POST   /jobs/{id}/result          → Agent posts execution results
GET    /jobs/{id}                 → Check job status & output
GET    /                          → Web UI dashboard
```

#### 2. **Agent** (`agent/agent.py`)
- **Tech Stack**: Python 3.11, Docker, psutil
- **Role**: Edge compute worker
- **Responsibilities**:
  - Device capability detection (CPU, RAM, disk, GPU)
  - Self-registration with control plane
  - Job polling (every 5 seconds)
  - Docker container management
  - Job execution with security sandbox
  - Result submission

**Security Features** (v1):
```
✓ Docker container isolation
✓ Read-only filesystem
✓ Dropped all Linux capabilities
✓ Memory limit: 512MB per job
✓ CPU limit: 1 core per job
✓ Network isolation (no internet)
✓ Process limit: 512 processes max
✓ Execution timeout: 60 seconds
```

#### 3. **Frontend** (`control_plane/main.py` - embedded)
- **Tech Stack**: HTML5, Vanilla JS, CSS Grid
- **Features**:
  - Real-time device registry with specs
  - Job submission form (image + command)
  - Live job status monitoring
  - Result viewer with syntax highlighting
  - Network statistics dashboard
  - Mobile responsive design

---

## 📊 Current MVP Capabilities

### What Works Today (v1)
✅ Device self-registration with auto-detection  
✅ Job submission to specific devices  
✅ Docker containerized execution  
✅ Real-time result retrieval  
✅ Web dashboard with live metrics  
✅ Security sandbox isolation  
✅ Multi-device support  
✅ Cross-platform (Windows, Mac, Linux)  

### Example Workflow
```
1. Device owner starts agent:
   $ python agent.py --name "RTX4090-Node" --price 0.15

2. Device registers: { cpu_cores: 16, ram_gb: 64, disk_gb: 2000 }

3. User submits job: python:3.11 + "import torch; print(torch.__version__)"

4. Control plane assigns job to device

5. Agent receives job, executes in sandbox:
   docker run --rm --read-only --memory=512m --cpus=1 \
     --cap-drop=ALL python:3.11 /bin/sh -c "..."

6. Results returned within 30 seconds

7. Ledger updated for billing (future v2)
```

---

## 🛡️ Security Model

### Sandbox Architecture (v1)
Every job runs in an **isolated Docker container** with:

| Control | Implementation | Benefit |
|---------|---------------|---------| 
| **Filesystem** | Read-only root + `/tmp` tmpfs | No persistence attacks |
| **Capabilities** | Dropped all, selective re-enable | No privilege escalation |
| **Memory** | Hard limit 512MB | No OOM DoS |
| **CPU** | 1 core max | Fair resource sharing |
| **Network** | None (`--network=none`) | No exfiltration |
| **Processes** | Max 512 | No fork bombs |
| **Runtime** | 60s timeout | No infinite loops |

### What This Protects Against
- ✓ Container escape attempts
- ✓ Data theft from host
- ✓ Privilege escalation
- ✓ Resource exhaustion DoS
- ✓ Network-based attacks
- ✓ Malware persistence

### Known Limitations (v1)
- No kernel-level isolation (requires VM-based containers for that)
- Docker daemon runs as root (mitigated by sandbox flags)
- Device owner responsibility to keep Docker updated
- No attestation/verification of code integrity (v2+)

---

## 💰 Business Model

### Revenue Streams (v2 Phase)
1. **Compute Margin**: 20-30% cut on job transactions
   - User pays $0.15/hour → Device owner gets $0.10 → Uptime takes $0.05

2. **Device Premium**: $9.99/month subscription for advanced features
   - Priority job matching
   - Analytics dashboard
   - Custom pricing rules
   - Earnings withdrawal (bank/crypto)

3. **Enterprise Contracts**: Fixed fees for dedicated capacity
   - AI/ML teams needing consistent compute
   - Batch processing workloads
   - Dev/test environments

### Unit Economics (Projected)
- **User Acquisition Cost**: $2-5 (SEO + content)
- **Device Acquisition Cost**: $0.50 (viral loop + referrals)
- **Lifetime Value (Device)**: $150-300 (18-24 month horizon)
- **Gross Margin**: 35-50% (after infrastructure costs)

---

## 🚀 Roadmap: Phases Before Production

### Phase 1: MVP (Current - v1) ✓
**Timeline**: Weeks 1-2  
**Status**: Complete  
**Deliverables**:
- [x] Device registration flow
- [x] Job submission & execution
- [x] Web UI dashboard
- [x] Docker sandbox security
- [x] Results retrieval
- [x] Documentation

**Cost**: ~$0 (open-source tech stack)

---

### Phase 2: Authentication & Authorization (v1.1)
**Timeline**: Weeks 3-4  
**Deliverables**:
- API key authentication (device + user)
- Role-based access control (admin, power user, free tier)
- Rate limiting per tier
- Audit logging (who ran what, when)
- Device ownership verification

**Tech**:
- JWT/OAuth2 for auth
- Redis for session caching
- PostgreSQL for audit logs (replaces SQLite)

**Estimated Cost**: $2-5K engineering

---

### Phase 3: Payments & Billing (v2.0)
**Timeline**: Weeks 5-8  
**Deliverables**:
- Stripe/PayPal integration for user payouts
- Ledger system (record all transactions)
- Automated monthly settlements
- Wallet system (store credits for jobs)
- Invoice generation
- Tax compliance (1099, VAT)

**Tech**:
- Stripe Connect for payouts
- PostgreSQL with transaction tables
- AWS SNS for notifications
- Scheduled batch processors for settlement

**Estimated Cost**: $8-12K engineering + compliance

---

### Phase 4: Intelligent Scheduling (v2.1)
**Timeline**: Weeks 9-12  
**Deliverables**:
- Job auto-matching (find best device without manual selection)
- Priority queue (urgent jobs pay more)
- Price negotiation (user wants cheap, device wants high pay)
- Geographic routing (latency optimization)
- Predictive availability (ML model predicts uptime)

**Tech**:
- Python + scikit-learn for ML
- Redis for job queue
- GraphQL API for complex queries
- PostgreSQL JSONB for device metadata

**Estimated Cost**: $15-20K engineering

---

### Phase 5: Advanced Security & Compliance (v2.5)
**Timeline**: Weeks 13-16  
**Deliverables**:
- Code signing & attestation
- Hardware-backed job sandboxes (Nitro Enclaves)
- SOC 2 Type II certification
- GDPR compliance (data deletion, export)
- Device reputation scoring
- Job whitelist/blacklist (malware prevention)

**Tech**:
- AWS Nitro Enclaves
- Code verification (GPG keys)
- Kubernetes for orchestration
- Prometheus + Grafana for monitoring

**Estimated Cost**: $25-30K engineering + compliance

---

### Phase 6: Enterprise Features (v3.0)
**Timeline**: Weeks 17-20  
**Deliverables**:
- Multi-cloud federation (connect other Uptime networks)
- Custom container registries (pull from ECR, Harbor, etc.)
- Job dependency graphs (DAGs)
- Persistent storage (S3 integration)
- VPN/private networks
- SLA guarantees & insurance

**Tech**:
- Kubernetes + Istio
- S3 / MinIO
- ArgoCD for declarative deployment
- Prometheus + PagerDuty for SLA monitoring

**Estimated Cost**: $40-50K engineering

---

### Phase 7: Production Hardening (v3.1)
**Timeline**: Weeks 21-24  
**Deliverables**:
- Load testing (10K+ concurrent jobs)
- Chaos engineering & failure recovery
- Multi-region deployment
- Disaster recovery (backup/restore)
- DDoS mitigation
- 99.9% uptime SLA

**Tech**:
- CloudFlare + AWS DDoS protection
- Multi-AZ PostgreSQL + read replicas
- Terraform for IaC
- Prometheus + AlertManager

**Estimated Cost**: $20-25K DevOps

---

## 📈 Growth Projections

### Year 1 Targets (Post-Launch)
- **Devices**: 5,000 → 50,000
- **Monthly Active Users**: 1,000 → 15,000
- **Monthly Compute Jobs**: 100K → 2M
- **Monthly Revenue**: $0 → $150K
- **Gross Margin**: 40% → 50%

### Year 2-3 Vision
- **Devices**: 500,000 global
- **Users**: 200K+ active
- **Revenue**: $5M+ ARR
- **Market Position**: Top 3 decentralized compute network

---

## 🎯 Competitive Advantages

| Factor | Uptime | AWS | Render | Vast.ai |
|--------|--------|-----|--------|----------|
| **Price** | $0.08-0.20/hr | $0.25-2.00/hr | $0.12-0.40/hr | $0.08-0.15/hr |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Sandbox Security** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Decentralization** | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐ | ⭐⭐⭐ |
| **Device Earnings** | ⭐⭐⭐⭐⭐ | N/A | ❌ | ⭐⭐⭐⭐ |

---

## 💼 Investment Ask

### Seed Round: $2M
**Use of Funds**:
- 40% ($800K): Engineering (team of 4-5)
- 25% ($500K): Infrastructure & DevOps
- 20% ($400K): Sales & Marketing
- 15% ($300K): Legal, Compliance, Operations

**Expected Milestones**:
- Months 1-3: Phase 2-3 (Auth + Payments)
- Months 4-6: Phase 4-5 (Scheduling + Security)
- Months 6-9: Beta launch (1,000 devices, 5,000 users)
- Months 9-12: Public launch (production hardened)

**Projected Outcomes** (12-month horizon):
- ARR: $500K-1M
- Devices: 50K+
- Monthly Active Users: 10K+
- Burn Rate: Decreasing (unit economics positive by month 9)

---

## 🔮 Long-Term Vision (3-5 Years)

### Becoming the "Linux of Compute"
1. **Neutrality**: Platform-agnostic, works with any container runtime
2. **Interoperability**: Connect multiple regional Uptime networks
3. **Standardization**: Contribute to OCI (Open Container Initiative)
4. **Decentralization**: Migrate to blockchain for payments (optional)
5. **Global Scale**: 1M+ devices across 180+ countries

### Potential Exit Paths
- **Acquisition** by cloud providers (AWS, Google, Azure) seeking edge capacity
- **IPO** if revenue reaches $50M+ ARR
- **DAO Conversion** into decentralized autonomous organization (long-term)

---

## ⚠️ Risks & Mitigation

| Risk | Severity | Mitigation |
|------|----------|----------|
| **Malware/hacks on devices** | High | Sandboxing, image whitelisting, insurance fund |
| **Device owners going offline** | Medium | SLA penalties, reputation scoring |
| **Regulatory (labor, taxes)** | High | Legal team, compliance consulting, KYC |
| **Market adoption (chicken-egg)** | High | Free tier for users, device subsidies |
| **Tech obsolescence** | Low | Modular architecture, cloud-native stack |
| **Vendor lock-in (Docker)** | Low | Support containerd, Podman alternatives |

---

## 📞 Contact & Next Steps

**Schedule a Demo**: See the MVP in action (live execution, real-time results)

**Questions**:
- Technical deep dive on sandbox security
- Unit economics & growth modeling
- Competitive analysis & market positioning

**Timeline**: Target funding close in Q2 2026, product launch Q4 2026

---

**Uptime: Monetize Your Hardware. Democratize Compute.**

*"Just like Uber transformed idle cars into a transportation network, Uptime transforms idle computers into a global compute marketplace."*