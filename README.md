# 👁️ Optic: AI Reliability Engineer for Dockerized Applications

<p align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python\&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Container%20Monitoring-2496ED?logo=docker\&logoColor=white)
![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4)
![LangGraph](https://img.shields.io/badge/Multi--Agent-LangGraph-000000)
![Status](https://img.shields.io/badge/Status-Early%20Development-orange)
![License](https://img.shields.io/badge/License-MIT-green)

</p>

<p align="center">
<b>An AI-powered reliability engineering system that monitors Dockerized applications, investigates production failures, explains root causes, and evolves toward autonomous incident response.</b>
</p>

---

# 📖 Table of Contents

* Overview
* Why Optic?
* Core Features
* Design Philosophy
* High-Level Architecture
* Incident Lifecycle
* Current Development Status

---

# 🌍 Overview

Modern software development has become dramatically faster.

With AI-assisted coding tools, developers can build and deploy applications in minutes. Yet when something fails in production, diagnosing the problem is still a largely manual process.

Developers often find themselves asking:

* Why did my container crash?
* Which service failed first?
* Where should I start looking?
* Which logs actually matter?
* How can I fix this without hours of debugging?

Existing observability platforms excel at collecting telemetry, dashboards, and alerts—but they still depend on humans to interpret the evidence and determine the next step.

**Optic** explores a different approach.

Instead of only collecting information, Optic aims to understand it.

Beginning with Dockerized applications, Optic continuously watches running services, detects failures, gathers relevant evidence, and prepares structured incident reports for AI-assisted investigation.

Over time, the project evolves beyond monitoring into an autonomous reliability engineering platform capable of reasoning about failures, learning from historical incidents, and assisting developers with remediation.

---

# ❓ Why Optic?

A traditional debugging workflow often looks like this:

```text
Build Application
        │
        ▼
Deploy Application
        │
        ▼
Application Fails
        │
        ▼
Search Logs
        │
        ▼
Guess Root Cause
        │
        ▼
Attempt Fix
```

This process is repetitive, time-consuming, and heavily dependent on experience.

Optic transforms that workflow into:

```text
Build Application
        │
        ▼
Deploy Application
        │
        ▼
Failure Detected
        │
        ▼
Collect Evidence
        │
        ▼
AI Investigation
        │
        ▼
Root Cause Analysis
        │
        ▼
Suggested Fix
```

The long-term objective is to reduce the cognitive load of incident investigation by allowing AI to perform much of the repetitive analysis that engineers perform today.

---

# ✨ Core Features

## 🐳 Docker Event Monitoring

Optic continuously observes Docker containers to detect operational changes.

Current monitoring targets include:

* Container lifecycle events
* Container crashes
* Exit codes
* Startup failures
* Service availability

---

## 📂 Evidence Collection

When an incident occurs, Optic gathers the information required for investigation.

Evidence may include:

* Container logs
* Exit status
* Runtime metadata
* Service information
* Failure timestamps

Rather than forcing developers to manually gather this information, Optic prepares a structured incident snapshot.

---

## 🧠 AI-Assisted Investigation

Once evidence has been collected, Gemini analyzes the incident to identify likely causes.

The investigation focuses on questions such as:

* What failed?
* Why did it fail?
* Which component is responsible?
* What evidence supports that conclusion?
* What remediation steps are recommended?

The goal is explanation—not simply summarization.

---

## 📑 Structured Incident Reports

Every detected failure is transformed into a structured incident report.

Typical reports contain:

* Incident summary
* Observed symptoms
* Supporting evidence
* Root cause hypothesis
* Severity assessment *(planned)*
* Recommended actions

These reports create a consistent debugging experience regardless of application complexity.

---

## 🧠 Memory & Learning *(Planned)*

As Optic evolves, incidents will no longer be treated as isolated events.

Instead, the platform will maintain a historical knowledge base capable of:

* Retrieving similar incidents
* Comparing previous fixes
* Identifying recurring failures
* Improving future investigations

This transforms Optic from an investigation tool into a continuously learning reliability assistant.

---

# 🧭 Design Philosophy

Optic is built around four core principles.

---

## Observe First

Reliable diagnosis begins with accurate observation.

Rather than immediately asking an LLM to reason about failures, Optic first gathers objective evidence from the running system.

---

## Evidence Before Reasoning

Every AI investigation is grounded in collected system data.

This minimizes speculation and encourages explanations that are supported by observable evidence.

---

## Modular Agents

Instead of relying on one large autonomous agent, Optic separates responsibilities into specialized components responsible for:

* Monitoring
* Collection
* Investigation
* Recommendation
* Remediation *(future)*

This modular architecture improves reliability and simplifies future expansion.

---

## Human-Centered Reliability

Optic is designed to assist engineers—not replace them.

Its primary objective is to reduce debugging time by providing structured investigations, clear explanations, and actionable recommendations while keeping developers in control of production systems.

---

# 🏗 High-Level Architecture

Current architecture (Version 1):

```text
Docker Engine
      │
      ▼
┌─────────────────────┐
│   Watcher Agent     │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Evidence Collector  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Incident Builder    │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ AI Investigation    │
│     (Gemini)        │
└─────────┬───────────┘
          │
          ▼
Root Cause Report
```

---

### Long-Term Architecture

As the project evolves, additional autonomous agents will extend the pipeline into a complete AI-driven SRE workflow.

```text
Incident Event
      │
      ▼
Watcher Agent
      │
      ▼
Collector Agent
      │
      ▼
Investigator Agent
      │
      ▼
Recommendation Agent
      │
      ▼
Healer Agent
      │
      ▼
GitHub Pull Request
      │
      ▼
Developer Review
```

Future versions will also support integrations with:

* GitHub Actions
* Sentry
* Prometheus
* Grafana
* Kubernetes
* Cloud-native deployment environments

---

# 🔄 Incident Lifecycle

Every detected incident passes through a structured investigation pipeline.

```text
Container Failure
        │
        ▼
Failure Detection
        │
        ▼
Evidence Collection
        │
        ▼
Incident Snapshot
        │
        ▼
AI Investigation
        │
        ▼
Root Cause Analysis
        │
        ▼
Suggested Remediation
```

As additional capabilities are introduced, this lifecycle will expand to include automated validation, code patch generation, and pull request creation.

---

# 🚧 Current Development Status

Optic is currently in **Phase 1: Docker Event Monitoring**.

### Implemented

* Local development environment
* Docker-based test application
* Project architecture
* Initial monitoring pipeline
* Incident investigation design

### In Progress

* Docker event stream monitoring
* Crash detection
* Log collection
* Incident snapshot generation

### Planned

* AI root cause analysis
* Incident memory
* Multi-agent orchestration with LangGraph
* Automated remediation
* GitHub integration
* Kubernetes support
* Enterprise observability integrations

> **Project Status:** Early Development
> Optic is being built publicly as a hands-on exploration of Reliability Engineering, Observability, AI Agents, Distributed Systems, and Production Infrastructure.

---
# ⚙️ Core Architecture

Optic is designed as an event-driven reliability engineering platform where every component has a single responsibility.

Instead of building one monolithic AI agent, Optic decomposes the incident investigation process into specialized modules that cooperate to detect failures, collect evidence, analyze incidents, and (in future versions) assist with remediation.

This modular architecture makes the platform easier to test, extend, and eventually scale from local Docker environments to enterprise infrastructure.

---

# 🐳 Watcher Agent

**Primary Responsibility:** Observe the runtime environment.

The Watcher Agent continuously monitors the Docker Engine for significant runtime events.

Rather than periodically polling containers, the long-term design is event-driven—allowing Optic to react immediately whenever something changes.

## Responsibilities

* Monitor Docker lifecycle events
* Detect container crashes
* Observe container state changes
* Track startup failures
* Identify abnormal runtime behavior

The Watcher Agent never performs analysis itself.

Its sole responsibility is answering one question:

> **"Has something happened that requires investigation?"**

---

### Input

```text id="4a2k9m"
Docker Engine

↓

Container Events

↓

Runtime State Changes
```

---

### Output

```text id="n2m8sq"
Incident Trigger

↓

Container Identifier

↓

Failure Metadata
```

---

# 📂 Evidence Collector

**Primary Responsibility:** Gather all relevant debugging evidence.

Once a failure is detected, the Collector begins assembling everything needed for an investigation.

Rather than requiring engineers to manually inspect multiple sources, Optic automatically gathers relevant runtime information into a structured incident snapshot.

## Evidence Sources

* Container logs
* Exit codes
* Runtime metadata
* Container configuration
* Failure timestamps
* Service status

Future versions may also include:

* Environment variables
* Resource utilization
* Network information
* Dependency graphs
* Kubernetes events

---

### Evidence Pipeline

```text id="x0wp8e"
Incident Trigger

↓

Collect Logs

↓

Collect Metadata

↓

Collect Exit Codes

↓

Build Incident Snapshot
```

---

# 📄 Incident Builder

**Primary Responsibility:** Convert raw telemetry into structured context.

Raw logs are valuable, but they are rarely organized in a way that is useful for AI reasoning.

The Incident Builder transforms collected evidence into a standardized incident document that can be analyzed consistently regardless of the application.

A typical incident contains:

* Application information
* Failure summary
* Timeline
* Logs
* Exit status
* Runtime environment
* Supporting evidence

By separating evidence collection from investigation, Optic keeps the reasoning layer independent of infrastructure-specific details.

---

# 🧠 Investigator Agent

**Primary Responsibility:** Understand what happened.

The Investigator Agent is the reasoning engine of Optic.

Using Gemini, it analyzes structured incident data to produce a human-readable explanation of the failure.

Instead of simply summarizing logs, the investigator attempts to establish a logical chain between observed symptoms and probable causes.

Typical questions include:

* What failed?
* Why did it fail?
* Which component is responsible?
* Which evidence supports this conclusion?
* How confident is the diagnosis?
* What should the developer investigate next?

Future versions will support severity scoring and confidence estimation.

---

### Investigation Pipeline

```text id="9bg2up"
Incident Snapshot

↓

Gemini Analysis

↓

Root Cause Hypothesis

↓

Suggested Investigation
```

---

# 💡 Recommendation Engine *(Planned)*

Understanding the failure is only the first step.

Future versions of Optic will generate actionable remediation guidance.

Rather than only reporting the problem, the Recommendation Engine will suggest practical next steps such as:

* Configuration changes
* Dependency fixes
* Environment corrections
* Deployment recommendations
* Infrastructure improvements
* Documentation references

The objective is to reduce the time between identifying a problem and resolving it.

---

# 🩹 Autonomous Healer *(Future Vision)*

One of Optic's long-term goals is to evolve from diagnosis to assisted remediation.

When sufficient confidence exists, the Healer Agent will:

* Locate affected source files
* Generate targeted code patches
* Produce structured diffs
* Validate proposed changes
* Open GitHub Pull Requests for developer review

Importantly, Optic is designed around a **human-in-the-loop** workflow.

Code changes are intended to be proposed—not silently deployed—allowing engineers to review every modification before merging.

---

# 🧭 Orchestrator

As the platform grows, multiple agents will need to cooperate.

The Orchestrator coordinates this workflow.

It determines:

* Which type of incident occurred
* Which agents should execute
* What evidence should be collected
* Which investigation strategy to use
* When the workflow is complete

Future deployments may support multiple entry points, including:

* Docker events
* GitHub Actions
* Sentry webhooks
* Kubernetes events
* Manual investigations

The Orchestrator acts as the central coordinator while allowing individual agents to remain independent.

---

# 🌐 Deployment Modes

Optic is designed to operate in multiple environments.

## 🖥️ Local Development

Current development focuses on Dockerized applications running locally.

This environment enables rapid experimentation with common deployment failures such as:

* Missing dependencies
* Port conflicts
* Startup errors
* Configuration mistakes
* Application crashes

---

## ⚙️ CI/CD Pipelines *(Future)*

Optic will integrate into continuous integration workflows.

Potential capabilities include:

* Investigating failed builds
* Analyzing failed tests
* Reviewing deployment failures
* Creating debugging reports

---

## ☁️ Production Infrastructure *(Future)*

Long-term, Optic aims to integrate with production observability systems including:

* Sentry
* Prometheus
* Alertmanager
* Grafana
* Kubernetes
* Cloud platforms

This would allow investigations to begin automatically whenever production incidents occur.

---

# 📊 Observability

Because Optic investigates distributed systems, it must also observe itself.

Future versions will include comprehensive telemetry for every stage of the investigation pipeline.

Areas of interest include:

* Agent execution time
* LLM latency
* Investigation duration
* Token usage
* Error rates
* Failure frequency
* Pipeline success rate

Understanding the behavior of Optic itself is essential for ensuring reliability as the platform grows.

---

# 🗄️ Data Model

Optic treats every incident as a reusable piece of operational knowledge.

Rather than discarding failures after they are resolved, the platform stores structured incident data for future analysis.

---

## Incidents

Each incident records:

* Unique identifier
* Timestamp
* Application
* Failure summary
* Runtime environment
* Current status

---

## Evidence

Associated evidence includes:

* Logs
* Exit codes
* Metadata
* Runtime information
* Supporting artifacts

---

## Investigations *(Planned)*

Stores AI-generated reasoning including:

* Root cause analysis
* Confidence score
* Severity
* Suggested remediation
* Supporting evidence references

---

## Knowledge Base *(Future)*

As Optic evolves, historical investigations will become searchable.

This enables:

* Similar incident retrieval
* Pattern recognition
* Organizational memory
* Retrieval-Augmented Generation (RAG)
* Faster future investigations

---

# 🔄 End-to-End Investigation Flow

```text id="3jv6rd"
Docker Event
      │
      ▼
Watcher Agent
      │
      ▼
Evidence Collector
      │
      ▼
Incident Builder
      │
      ▼
Investigator Agent
      │
      ▼
Root Cause Report
      │
      ▼
Recommendation Engine
      │
      ▼
Human Review
      │
      ▼
Future Healer Agent
```

This pipeline reflects Optic's core philosophy:

**Observe → Collect → Understand → Recommend → Improve**

Each stage builds upon the previous one, enabling reliable, evidence-driven investigations while laying the foundation for future autonomous remediation.

---
# 🛠️ Technology Stack

Optic combines modern AI tooling with infrastructure-focused technologies to build an event-driven reliability engineering platform.

| Category                | Technologies                                                                  |
| ----------------------- | ----------------------------------------------------------------------------- |
| **Language**            | Python 3.10+                                                                  |
| **Container Runtime**   | Docker & Docker SDK                                                           |
| **AI Model**            | Google Gemini                                                                 |
| **Agent Framework**     | LangGraph *(planned)*                                                         |
| **Database**            | SQLite (development), PostgreSQL *(planned)*                                  |
| **Observability**       | Docker Events, Structured Logging                                             |
| **Future Integrations** | Prometheus, Alertmanager, Grafana, Sentry, Kubernetes, GitHub MCP, Docker MCP |

---

# 📂 Repository Structure

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
├── prompts/
├── requirements.txt
└── README.md
```

As the platform evolves, this structure will expand to include dedicated agent modules, orchestration components, persistent storage, and enterprise integrations while preserving a modular architecture.

---

# 🚀 Getting Started

## Prerequisites

Before running Optic, ensure you have:

* Python 3.10+
* Docker Desktop (or Docker Engine)
* Docker SDK
* A Gemini API Key *(for AI investigation features)*

---

## Clone the Repository

```bash
git clone https://github.com/deepanshg3/optic.git

cd optic
```

---

## Create a Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

```env
GEMINI_API_KEY=your_api_key
```

As Optic grows, additional configuration options will be introduced for services such as Sentry, Prometheus, Kubernetes, GitHub, and PostgreSQL.

---

# ▶️ Running Optic

During the current development phase, Optic focuses on monitoring local Dockerized applications.

Start your test application and then launch Optic:

```bash
python app/main.py
```

The initial test environment consists of a Dockerized React Tic-Tac-Toe application intentionally configured to generate realistic deployment failures, including:

* Missing dependencies
* Syntax errors
* Startup failures
* Port conflicts
* Environment variable issues

These controlled failures provide reproducible incident data for developing and evaluating Optic's investigation pipeline.

---

# 🔧 Development Roadmap

Optic is being developed in incremental phases.

## ✅ Phase 1 — Docker Awareness *(Current)*

* Local development environment
* Dockerized test application
* Docker event monitoring
* Crash detection
* Log collection

---

## 🚧 Phase 2 — Incident Collection

* Incident snapshot generation
* Exit code capture
* Persistent incident storage
* Historical incident database

---

## 🔮 Phase 3 — AI Investigation

* Gemini-powered reasoning
* Root cause analysis
* Severity classification
* Suggested remediation
* Structured investigation reports

---

## 🧠 Phase 4 — Memory & Learning

* Incident knowledge base
* Similarity search
* Historical retrieval
* Retrieval-Augmented Generation (RAG)

---

## 🤖 Phase 5 — Multi-Agent Reliability Platform

Migration to a cooperative multi-agent architecture powered by LangGraph.

Planned agents include:

* Watcher Agent
* Collector Agent
* Investigator Agent
* Recommendation Agent
* Healer Agent

---

## ☁️ Phase 6 — Enterprise Integrations

Expand beyond local Docker environments into production infrastructure through integrations with:

* Sentry
* Prometheus
* Alertmanager
* Grafana
* Kubernetes
* GitHub
* Cloud Platforms

---

# 🔮 Future Vision

Optic begins as an AI Reliability Engineer for Dockerized applications.

Its long-term vision is considerably broader.

Rather than functioning as another monitoring dashboard, Optic aims to become an intelligent reliability platform capable of understanding software systems, investigating failures, learning from historical incidents, and assisting engineers throughout the incident response lifecycle.

The evolution of the project can be summarized as:

```text
Docker Monitoring
        │
        ▼
Incident Collection
        │
        ▼
AI Investigation
        │
        ▼
Historical Learning
        │
        ▼
Multi-Agent Collaboration
        │
        ▼
Autonomous Reliability Engineering
```

As the platform matures, future versions may extend beyond investigation into AI-assisted remediation, automated pull request generation, and intelligent operational recommendations—always with engineers remaining in control of production changes.

---

# 🤝 Contributing

Contributions of all kinds are welcome.

Whether you're interested in reliability engineering, observability, AI agents, distributed systems, or backend development, there are many ways to contribute.

Areas where help is especially valuable include:

* Docker monitoring
* Incident collection
* Prompt engineering
* Agent orchestration
* Documentation
* Testing
* Kubernetes integrations
* Observability tooling

If you'd like to contribute:

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Test your implementation.
5. Open a Pull Request with a clear description of your work.

---

# 📄 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for additional details.

---

# 👨‍💻 Author

**Deepansh Gupta**

Optic is being built publicly as a hands-on systems engineering project exploring the intersection of:

* Reliability Engineering
* Observability
* Distributed Systems
* AI-Assisted Operations (AIOps)
* Multi-Agent Systems
* DevOps & Site Reliability Engineering
* Production Infrastructure
* Large Language Models

The goal is not simply to build another monitoring tool, but to explore how AI can augment the incident response process by helping engineers understand failures faster and with greater confidence.

---

# 🙏 Acknowledgements

Optic builds upon an incredible ecosystem of open-source projects and developer platforms.

Special thanks to:

* Docker
* Google Gemini
* LangGraph
* Python
* Prometheus
* Grafana
* Kubernetes
* Sentry
* The open-source observability community

---

<div align="center">

# 👁️ Optic

### **Observe • Investigate • Understand • Improve**

*Building toward a future where AI assists engineers in understanding systems—not just monitoring them.*

</div>
