# Stage 2 — Containerize & Ship a Microservices Application

## Overview
Took a broken multi-service job processing application, fixed all bugs, containerized every service with Dockerfiles, and built a full CI/CD pipeline using GitHub Actions.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    GitHub Actions                    │
│lint → test → build → security → integration → deploy │
└─────────────────────────┬────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────┐
│                   Docker Network                    │
│                                                     │
│  ┌─────────────┐        ┌─────────────┐             │
│  │   Frontend  │───────▶│     API    │             │
│  │  (Node.js)  │        │  (FastAPI)  │             │
│  │  Port 3000  │        │  Port 8000  │             │
│  └─────────────┘        └──────┬──────┘             │
│                                │                    │
│                    ┌───────────▼──────────┐         │
│                    │        Redis         │         │
│                    │   (Job Queue/Store)  │         │
│                    └───────────┬──────────┘         │
│                                │                    │
│                    ┌───────────▼──────────┐         │
│                    │        Worker        │         │
│                    │   (Job Processor)    │         │
│                    └──────────────────────┘         │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

- **Frontend:** Node.js 20, Express.js
- **API:** Python 3.11, FastAPI, Uvicorn
- **Worker:** Python 3.11
- **Queue/Store:** Redis 7 Alpine
- **Containerization:** Docker, Docker Compose
- **CI/CD:** GitHub Actions
- **Security Scanning:** Trivy
- **Linting:** flake8, ESLint, hadolint

---

## Prerequisites

Make sure the following are installed on your machine:

| Tool | Version | Install |
|---|---|---|
| Docker | 24.0+ | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | v2.0+ | Included with Docker Desktop |
| Git | any | [git-scm.com](https://git-scm.com/) |

Verify installations:
```bash
docker --version
docker compose version
git --version
```

---

## Getting Started — Clean Machine Setup

### 1. Clone the Repository
```bash
git clone https://github.com/tuucay4/stage2-hng14-devops.git
cd stage2-hng14-devops
```

### 2. Create Your Environment File
```bash
cp .env.example .env
```

Open `.env` and set your values:
```bash
REDIS_PASSWORD=your_secure_password_here
APP_ENV=production
API_URL=http://api:8000
```

> Leave `REDIS_PASSWORD` empty to run without Redis authentication (fine for local development).

### 3. Build and Start the Stack
```bash
docker compose up --build
```

To run in the background:
```bash
docker compose up --build -d
```

### 4. Verify Everything Is Running
```bash
docker compose ps
```

Expected output:
```
NAME                          STATUS
stage2-hng14-devops-redis-1   Up (healthy)
stage2-hng14-devops-api-1     Up (healthy)
stage2-hng14-devops-worker-1  Up (healthy)
stage2-hng14-devops-frontend-1 Up (healthy)
```

---

## What a Successful Startup Looks Like

When the stack is healthy you should see logs like this:

```
redis-1    | * Ready to accept connections tcp
api-1      | INFO: Uvicorn running on http://0.0.0.0:8000
api-1      | INFO: Application startup complete.
worker-1   | Worker started, listening on jobs queue...
frontend-1 | Frontend running on port 3000
```

Open your browser at **http://localhost:3000** — you should see the Job Processor Dashboard.

Click **Submit New Job** — a job ID appears and status updates from `queued` → `completed` within a few seconds.

---

## Verify the API Directly
```bash
# Submit a job
curl -X POST http://localhost:3000/submit

# Check job status (replace JOB_ID with the returned id)
curl http://localhost:3000/status/JOB_ID
```

Expected responses:
```json
// POST /submit
{"job_id": "550e8400-e29b-41d4-a716-446655440000"}

// GET /status/:id
{"job_id": "550e8400-e29b-41d4-a716-446655440000", "status": "completed"}
```

---

## Useful Commands

```bash
docker compose up --build        # build and start all services
docker compose up --build -d     # run in background
docker compose down              # stop and remove containers
docker compose down -v           # stop and remove containers + volumes
docker compose ps                # check container status
docker compose logs -f           # live logs all services
docker compose logs api -f       # live logs specific service
docker compose restart api       # restart a single service
docker images                    # list all images
docker system prune              # clean up unused resources
```

---

## CI/CD Pipeline

The pipeline runs automatically on every push to `main` in strict order:

```
lint → test → build → security scan → integration test → deploy
```

| Stage | What It Does |
|---|---|
| **lint** | Runs flake8 (Python), ESLint (JavaScript), hadolint (Dockerfiles) |
| **test** | Runs pytest with mocked Redis, uploads coverage report as artifact |
| **build** | Builds all three images, tags with git SHA and latest, pushes to local registry |
| **security** | Scans all images with Trivy, fails on any CRITICAL severity finding |
| **integration** | Brings full stack up on runner, submits a job, polls until completed, tears down |
| **deploy** | Performs rolling update — new container must pass health check before old one stops |

A failure at any stage stops all subsequent stages from running.

---

## Bugs Fixed
This repository is a forked and fixed version of chukwukelu2023/hng14-stage2-devops.
See [FIXES.md](./FIXES.md) for a full breakdown of every bug found in the starter code  including file, line number, what the problem was, and how it was fixed.

---