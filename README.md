# Mycelia

**Modular AI agent infrastructure for autonomy, orchestration, and self-hosted intelligence.**

Mycelia is a composable, developer-friendly AI platform that enables individuals and teams to spin up containerized, tool-using agents to automate creative, personal, and operational tasks. Run it locally, scale it globally, or drop it into your own stack—Mycelia is built for freedom.

---

## ✨ Features
- 🔌 **Modular agent architecture** using FastAPI, pubsub, and MCP
- 📡 **Real-time communication** via NATS JetStream
- 📦 **Self-hostable stack**: works with Docker Compose and K8s
- 🧩 **Plugin system** for tools, connectors, workflows
- 🛠️ **CLI-first development**: init, run, scaffold workflows
- 🧠 **LLM-ready**: tools and workflows support GPT-style agents
- 🧾 **Workflow YAML support** for declarative pipelines
- 📊 **Observability included**: Prometheus, Grafana dashboards
- 🪟 **Frontend dashboard** with React + Supabase auth

---

## 🧱 Architecture Overview
```bash
mycelia/
├── agents/              # Modular agents (FastAPI + MCP)
├── cli/                 # Dev CLI tool for scaffolding + workflow mgmt
├── orchestrator/        # Optional workflow controller (WIP)
├── tools/               # Agent-exposed tools + integrations
├── workflows/           # YAML-based workflow definitions
├── dapr-components/     # NATS, state, bindings
├── infra/               # Compose + K8s setup
├── frontend/            # React dashboard
├── docs/                # Markdown or Docusaurus site
└── .github/             # CI/CD and templates
```

---

## 🛠️ Getting Started (Local)

```bash
# Clone + bootstrap
git clone https://github.com/mycelia-ai/mycelia
cd mycelia
cp .env.example .env

# Start everything locally
make up
```

Access:
- Dashboard → http://localhost:3000
- NATS Console → http://localhost:8222
- Prometheus → http://localhost:9090
- Grafana → http://localhost:3001

---

## 🧠 Build Your First Agent
```bash
# Scaffold a new agent
mycelia agent init daily_briefing

# Run agent in dev mode
mycelia run agent daily_briefing
```

---

## 🔄 Define a Workflow
```yaml
# workflows/summarize_daily.yaml
name: summarize_daily
steps:
  - uses: calendar.reader
  - uses: news.fetcher
  - uses: summarizer.llm
```
```bash
mycelia workflow run summarize_daily
```

---

## 🌐 Bring Your Own Stack
Use `infra-profiles/` to:
- Swap Supabase for Azure Postgres or CosmosDB
- Use Pinecone instead of local vector DB
- Connect to .NET Aspire or existing tools

Mycelia is built to integrate, not replace.

---

## 📚 Docs & Community
- Getting started → [`/docs/`](./docs)
- Connector spec → [`/tools/`](./tools)
- Agent templates → [`/agents/`](./agents)
- Join discussions → GitHub Discussions (soon)

---

## 📄 License
MIT — do what you want, fork it, extend it, run it anywhere.

> Built for autonomy. Designed for developers. Owned by you.
