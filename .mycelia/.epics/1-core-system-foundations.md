---
name: "Epic: Core System Foundations"
about: "Establish the base infrastructure and dev tooling for Mycelia"
title: "[Epic] Core System Foundations"
labels: ["epic"]
assignees: []
---

### 🧩 Epic / Area
Core System Foundations

### 📝 Description
Bootstrapping the core system architecture of Mycelia. This epic establishes the monorepo layout, containerized local development environment, pub/sub layer, observability tooling, and a working example agent. It provides the foundation for all further modular development.

### ✅ Acceptance Criteria
- Local environment runs via Docker Compose
- Devs can start services and see logs/metrics from agents
- A sample agent can receive and send messages
- Initial toolchain for CI, metrics, and agent development is available

---

## 🛠 Subtasks

### 1. Initialize Git repository and monorepo layout with essential directories and files.
**Details:**
Set up the root folder structure of the project with all necessary directories: `agents/`, `cli/`, `frontend/`, `infra/`, `docs/`, `dapr-components/`, etc. Initialize with a clean Git repo, `.gitignore`, and `README.md`.

---

### 2. Create base docker-compose.yml with core services: NATS JetStream, Dapr placement service, Prometheus, Grafana.
**Details:**
Compose configuration should boot:
- NATS JetStream (port 4222 / 8222)
- dapr_placement (port 50005)
- Prometheus (9090)
- Grafana (3001)

Include shared volume for metrics and network bridge.

---

### 3. Add Makefile and .env.example for local bootstrapping and developer setup.
**Details:**
Makefile should include:
- `make up` → `docker-compose up --build`
- `make agent` → run new agent with Dapr
- `make stop` → shutdown stack

`.env.example` to define ports, Dapr app ID, dev keys.

---

### 4. Create Dapr component definitions for pubsub, state, and bindings.
**Details:**
Add files to `dapr-components/`:
- `pubsub-nats.yaml`
- `state-supabase.yaml`
- `bindings-cron.yaml`

These define NATS topics and Supabase as key-value state backend.

---

### 5. Implement first agent (agent_hello) using FastAPI + Dapr pubsub to validate local message routing.
**Details:**
Agent should:
- Subscribe to `hello.request`
- Return a static response on `hello.response`
- Log incoming messages
- Use `agent_runtime`

Use FastAPI with Dapr pubsub + optional MCP registration.

---

### 6. Set up .github folder with CI/CD scaffolding and GitHub Actions for linting and container builds.
**Details:**
Create `.github/workflows/main.yml` to:
- Lint Python with ruff/black
- Run container build test
- Add README badge for build status

Add labels + issue templates to `.github/ISSUE_TEMPLATE/`.

---

### 7. Configure Prometheus scraping and basic Grafana dashboards for agent health and message throughput.
**Details:**
- Prometheus config scrapes NATS, Dapr, and `/metrics` from agents
- Grafana should include:
  - Agent uptime dashboard
  - Pubsub throughput chart
  - Dapr system metrics panel

Preload dashboards into `infra/grafana/` as JSON.

---

Let me know when you're ready to split these into GitHub issues or run them through the automation. Each task above is fully scoped for one issue. ✅
