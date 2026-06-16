# Optic

> An AI Reliability Engineer for Dockerized Applications.

Optic is an open-source AI system that continuously monitors deployed applications, detects failures, investigates incidents, and helps developers understand what broke and how to fix it.

The project is being built publicly from first principles, starting with simple Dockerized frontend applications and gradually evolving toward enterprise-grade reliability engineering.

---

## Vision

Modern developers can deploy applications faster than ever before using AI-assisted development tools.

However, when something breaks in production, most developers struggle to answer:

* Why did my application crash?
* Which component failed?
* What logs should I look at?
* How do I fix it?

Optic aims to become an AI Reliability Engineer that observes deployed systems, understands failures, and guides developers toward recovery.

---

## Problem Statement

A typical developer workflow today looks like this:

```text
Build Application
        ↓
Deploy Application
        ↓
Application Fails
        ↓
Manually Search Logs
        ↓
Guess Root Cause
```

Optic transforms that into:

```text
Build Application
        ↓
Deploy Application
        ↓
Application Fails
        ↓
Optic Investigates
        ↓
Root Cause Analysis
        ↓
Suggested Fix
```

---

## Current Scope (V1)

Optic V1 focuses on Dockerized applications.

The system continuously monitors:

* Container lifecycle events
* Container crashes
* Exit codes
* Application logs
* Service availability

When a failure occurs, Optic collects evidence and prepares an incident report for AI analysis.

---

## Architecture

```text
Docker Engine
      │
      ▼
┌───────────────┐
│ Watcher Agent │
└───────────────┘
      │
      ▼
┌────────────────────┐
│ Evidence Collector │
└────────────────────┘
      │
      ▼
┌──────────────────┐
│ Incident Builder │
└──────────────────┘
      │
      ▼
┌─────────────────┐
│ AI Investigation│
└─────────────────┘
      │
      ▼
Root Cause Report
```

---

## Development Roadmap

### Phase 1 — Docker Awareness

* [x] Create local development environment
* [x] Deploy victim application in Docker
* [ ] Monitor Docker event stream
* [ ] Detect container crashes
* [ ] Capture container logs

---

### Phase 2 — Incident Collection

* [ ] Build incident snapshot generator
* [ ] Capture exit codes
* [ ] Store incident history
* [ ] Maintain incident database

---

### Phase 3 — AI Investigation

* [ ] Gemini integration
* [ ] Root cause analysis
* [ ] Severity classification
* [ ] Suggested remediation steps

---

### Phase 4 — Memory & Learning

* [ ] Incident knowledge base
* [ ] Similarity search
* [ ] Historical incident retrieval
* [ ] Advanced RAG implementation

---

### Phase 5 — Multi-Agent System

* [ ] Watcher Agent
* [ ] Collector Agent
* [ ] Investigator Agent
* [ ] Recommendation Agent

Built using LangGraph.

---

### Phase 6 — Enterprise Integrations

* [ ] Prometheus
* [ ] AlertManager
* [ ] Grafana
* [ ] GitHub
* [ ] Kubernetes
* [ ] Cloud Platforms

---

## Repository Structure

```text
optic/
│
├── app/
│   └── main.py
│
├── backend/
│   ├── watcher.py
│   ├── collector.py
│   ├── analyzer.py
│   └── models.py
│
├── data/
│   ├── incidents/
│   ├── logs/
│   └── snapshots/
│
├── docs/
│   └── PRODUCT.md
│
├── frontend/
│
├── prompts/
│
├── requirements.txt
│
└── README.md
```

---

## Technology Stack

### Core

* Python
* Docker SDK
* LangGraph
* Gemini

### Future Integrations

* Prometheus
* AlertManager
* Grafana
* Kubernetes
* GitHub MCP
* Docker MCP

---

## Initial Test Environment

The first test application is a Dockerized React Tic-Tac-Toe application.

The purpose of this application is to intentionally generate deployment failures such as:

* Missing dependencies
* Syntax errors
* Port conflicts
* Environment variable issues
* Startup failures

These incidents will be used to train and evaluate Optic's reasoning capabilities.

---

## Long-Term Goal

Optic is not intended to be another monitoring dashboard.

The long-term vision is to build a system that understands software systems, detects abnormal behavior, investigates incidents, remembers previous failures, and eventually assists with remediation.

Starting point:

```text
Dockerized Frontend Apps
```

Future destination:

```text
Enterprise Infrastructure Reliability Platform
```

---

## Status

🚧 Early Development

Optic is currently in Phase 1: Docker Event Monitoring.

The project is being built publicly as a learning journey into:

* Reliability Engineering
* Observability
* Multi-Agent Systems
* AI-Assisted Operations
* Distributed Systems
* Production Infrastructure

---

## License

MIT License
