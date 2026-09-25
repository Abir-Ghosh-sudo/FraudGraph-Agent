# 🕸️ FraudGraph-Agent

### **Agentic AI for Intelligent Fraud Detection, Investigation & Explainable Risk Analysis**

<p align="center">

**Fraud doesn't happen in isolation — it happens in networks.**

FraudGraph-Agent combines **Graph Intelligence, Agentic AI, Risk Analysis, and Explainable Investigation** to transform suspicious financial activity into an actionable investigation workflow.

</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![AI](https://img.shields.io/badge/AI-Agentic%20AI-8B5CF6?style=for-the-badge)
![Graph](https://img.shields.io/badge/Graph-GraphRAG-06B6D4?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white)
![Neo4j](https://img.shields.io/badge/Graph-Neo4j-4581C3?style=for-the-badge\&logo=neo4j\&logoColor=white)
![React](https://img.shields.io/badge/UI-React-61DAFB?style=for-the-badge\&logo=react\&logoColor=black)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</p>

---

## 🚨 The Problem

Modern financial fraud is rarely limited to a single transaction.

A suspicious transaction may be connected to:

* 👤 Multiple accounts
* 💳 Shared payment instruments
* 📱 Common devices
* 🌐 Reused IP addresses
* 🏦 Multiple merchants
* 🔁 Repeated transaction patterns
* 🕸️ Coordinated fraud rings
* 🧩 Hidden relationships between seemingly unrelated entities

Traditional rule-based systems often analyze transactions independently.

That creates a major problem:

> **A fraudulent transaction may look normal by itself while becoming highly suspicious when its relationships are examined.**

FraudGraph-Agent approaches the problem differently.

Instead of asking only:

**"Is this transaction fraudulent?"**

the system asks:

> **"What is connected to this transaction, why is it suspicious, what evidence supports the suspicion, and how should an investigator respond?"**

---

# 🧠 What is FraudGraph-Agent?

**FraudGraph-Agent** is an intelligent fraud investigation platform that combines:

```text
Financial Transactions
        │
        ▼
┌──────────────────────┐
│   Risk Detection     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Graph Analysis     │
│ Accounts • Devices   │
│ Cards • IPs • Links  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Agentic Reasoning  │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Evidence Retrieval   │
│      + GraphRAG      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Investigation Report │
└──────────────────────┘
```

The result is not simply a fraud score.

The platform produces an **investigation-oriented explanation** backed by relationships, evidence, and reasoning.

---

# ✨ Core Capabilities

## 🕸️ 1. Graph-Based Fraud Detection

Financial entities are represented as an interconnected graph.

Example:

```text
                 ┌──────────────┐
                 │   Device     │
                 └──────┬───────┘
                        │
                        │ USED_BY
                        ▼
┌──────────┐       ┌──────────┐
│ Account A │──────▶│ Account B│
└────┬─────┘ TRANS └────┬─────┘
     │                   │
     │                   │
     ▼                   ▼
┌──────────┐       ┌──────────┐
│ Merchant │       │ Account C│
└──────────┘       └──────────┘
```

This makes it possible to detect patterns such as:

* Shared devices
* Account clusters
* Suspicious transaction chains
* Mule-account relationships
* Repeated counterparties
* Coordinated transaction activity
* Potential fraud rings

---

# 🤖 2. Agentic AI Investigation

FraudGraph-Agent uses specialized AI agents instead of relying on a single monolithic model.

Each agent has a specific responsibility.

```text
                    ┌─────────────────┐
                    │ Investigation   │
                    │    Request      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Agent Orchestrator│
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   ┌────────────┐     ┌────────────┐     ┌────────────┐
   │ Risk Agent │     │ Graph Agent│     │ Evidence   │
   │            │     │            │     │ Agent      │
   └────────────┘     └────────────┘     └────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Reasoning Agent │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Final Investigator│
                    │     Report      │
                    └─────────────────┘
```

This architecture allows the system to break a complex investigation into smaller, specialized reasoning tasks.

---

# 🔍 3. Explainable Risk Analysis

Instead of returning only:

```text
Fraud Probability: 94%
```

the system can provide contextual evidence such as:

```text
Risk Level: HIGH

Reasons:
• Account shares a device with 7 other accounts.
• 4 connected accounts were previously flagged.
• Transaction velocity increased significantly.
• Graph analysis detected a dense suspicious cluster.
• Multiple accounts share overlapping identifiers.
```

This makes the result easier for human analysts to understand and verify.

---

# 🧩 4. GraphRAG

FraudGraph-Agent combines:

**Graph Retrieval + Semantic Retrieval + Agentic Reasoning**

to provide context-aware investigations.

```text
                 User Question
                       │
                       ▼
              ┌─────────────────┐
              │ Query Understanding│
              └────────┬────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      ┌──────────────┐    ┌──────────────┐
      │ Graph Search │    │ Vector Search│
      └──────┬───────┘    └──────┬───────┘
             │                   │
             └─────────┬─────────┘
                       ▼
               ┌──────────────┐
               │ Hybrid Context│
               └───────┬──────┘
                       ▼
               ┌──────────────┐
               │ AI Reasoning │
               └───────┬──────┘
                       ▼
                Investigation
                   Response
```

This allows the system to reason over both:

* **Structured relationships**
* **Unstructured evidence**

---

# 🕵️ Investigation Workflow

A typical investigation follows this pipeline:

```text
1. Suspicious Activity Detected
              │
              ▼
2. Transaction / Entity Identification
              │
              ▼
3. Risk Assessment
              │
              ▼
4. Graph Expansion
              │
              ▼
5. Relationship Discovery
              │
              ▼
6. Evidence Retrieval
              │
              ▼
7. Agentic Reasoning
              │
              ▼
8. Fraud Pattern Identification
              │
              ▼
9. Explainable Investigation Report
              │
              ▼
10. Analyst Decision
```

---

# 🧠 Fraud Intelligence

The graph enables investigation across multiple entity types.

### Core Entities

| Entity         | Description                         |
| -------------- | ----------------------------------- |
| 👤 Account     | Customer or financial account       |
| 💳 Card        | Payment instrument                  |
| 📱 Device      | Device fingerprint                  |
| 🌐 IP Address  | Network identity                    |
| 🏦 Merchant    | Transaction destination             |
| 💸 Transaction | Financial activity                  |
| 🧑 Customer    | Identity associated with an account |

### Example Relationships

```text
Account ──USES──▶ Device

Account ──OWNS──▶ Card

Account ──PERFORMED──▶ Transaction

Transaction ──PAID_TO──▶ Merchant

Account ──CONNECTED_TO──▶ IP

Account ──TRANSFERRED_TO──▶ Account
```

---

# 🚩 Fraud Patterns

FraudGraph-Agent is designed around relational fraud patterns such as:

### 🔗 Shared Identity Infrastructure

```text
Account A ──┐
Account B ──┼──▶ Device X
Account C ──┘
```

Multiple accounts using the same device can become an investigation signal.

### 🕸️ Fraud Ring

```text
A ───▶ B
▲     │
│     ▼
D ◀── C
```

Dense or unusual transaction relationships may indicate coordinated activity.

### 🔄 Mule Account Chain

```text
Source
   │
   ▼
Account A
   │
   ▼
Account B
   │
   ▼
Account C
   │
   ▼
Destination
```

### ⚡ Transaction Burst

```text
Transaction Frequency

        ▲
        │             █
        │             █
        │         █   █
        │     █   █   █
        │ █   █   █   █
        └──────────────────▶ Time
```

Sudden changes in transaction behavior can be investigated as potential anomalies.

---

# 🏗️ System Architecture

```text
                         ┌────────────────────┐
                         │   Analyst / User   │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │   Web Dashboard    │
                         └─────────┬──────────┘
                                   │
                                   ▼
                         ┌────────────────────┐
                         │    FastAPI API     │
                         └─────────┬──────────┘
                                   │
                                   ▼
                    ┌────────────────────────────┐
                    │    Agent Orchestrator      │
                    └─────────────┬──────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
      ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
      │ Risk Agent   │    │ Graph Agent  │    │ RAG Agent    │
      └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
             │                   │                   │
             └───────────────────┼───────────────────┘
                                 ▼
                       ┌───────────────────┐
                       │ Hybrid Retrieval  │
                       └─────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
             ┌─────────────┐          ┌─────────────┐
             │ Graph Store │          │ Vector Store│
             └─────────────┘          └─────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                       ┌───────────────────┐
                       │ AI Reasoning / LLM│
                       └─────────┬─────────┘
                                 │
                                 ▼
                       ┌───────────────────┐
                       │ Investigation     │
                       │ Report            │
                       └───────────────────┘
```

---

# 🎯 Why Graph + AI?

Traditional fraud detection often focuses on individual records.

FraudGraph-Agent focuses on **relationships**.

Consider:

```text
Transaction A
Amount: ₹9,500
Status: Normal
```

Individually, it may not look suspicious.

But graph analysis may reveal:

```text
Transaction A
      │
      ▼
Account X
  │       │
  │       └──── Shared Device ──── Account Y
  │                                  │
  └──────── Previous Fraud Flag ◀────┘
                                      │
                                      ▼
                              Multiple Accounts
```

The surrounding network changes the context.

That is the core idea behind FraudGraph-Agent:

> **Fraud intelligence should understand relationships, not just rows.**

---

# 🖥️ Intelligent Analyst Dashboard

The frontend is designed around an investigation-first workflow.

### Dashboard

```text
┌─────────────────────────────────────────────────────────────┐
│ FRAUDGRAPH                                  Analyst Console │
├─────────────┬───────────────────────────────────────────────┤
│             │                                               │
│ Dashboard   │     Risk Overview                             │
│             │                                               │
│ Cases       │   ┌────────┐ ┌────────┐ ┌────────┐           │
│             │   │ HIGH   │ │ MEDIUM │ │ LOW    │           │
│ Graph       │   │   24   │ │   61   │ │  142   │           │
│             │   └────────┘ └────────┘ └────────┘           │
│ Agents      │                                               │
│             │       Fraud Network Visualization             │
│ Reports     │                                               │
│             │             ●──────●                           │
│ Settings    │           ╱   ╲    │                           │
│             │         ●───────●──●                           │
│             │                                               │
└─────────────┴───────────────────────────────────────────────┘
```

The interface is intended to help analysts move from:

**Alert → Graph → Evidence → Reasoning → Report**

without switching between disconnected tools.

---

# ⚙️ Technology Stack

| Layer         | Technology                       |
| ------------- | -------------------------------- |
| Frontend      | React / Modern Web UI            |
| Backend       | FastAPI                          |
| Language      | Python                           |
| AI            | Agentic AI / LLM                 |
| Retrieval     | GraphRAG / Hybrid Retrieval      |
| Graph         | Neo4j / Graph-based analysis     |
| Database      | SQL / Structured storage         |
| ML            | Fraud & anomaly detection models |
| API           | REST / WebSocket where required  |
| Visualization | Interactive graph visualization  |
| Deployment    | Docker-ready architecture        |

---

# 📂 Project Structure

```text
FraudGraph-Agent/
│
├── backend/
│   │
│   ├── api/
│   ├── agents/
│   ├── graph/
│   ├── graphrag/
│   ├── models/
│   ├── services/
│   ├── database/
│   └── core/
│
├── frontend/
│   │
│   ├── components/
│   ├── pages/
│   ├── dashboard/
│   ├── graph/
│   ├── cases/
│   └── services/
│
├── data/
│
├── docs/
│
├── tests/
│
├── scripts/
│
├── .env.example
├── docker-compose.yml
├── requirements.txt
└── README.md
```

> The exact structure may evolve as the platform continues to develop.

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/Abir-Ghosh-sudo/FraudGraph-Agent.git

cd FraudGraph-Agent
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv

.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If the project uses a frontend:

```bash
cd frontend

npm install
```

---

## 4. Configure environment variables

Create:

```text
.env
```

from:

```text
.env.example
```

Configure the required database, graph, AI, and application settings.

---

# ▶️ Running the Application

### Backend

```bash
uvicorn backend.main:app --reload
```

The API will be available at:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

### Frontend

```bash
cd frontend

npm run dev
```

The frontend will typically be available at:

```text
http://localhost:3000
```

---

# 🔎 Example Investigation

### Question

```text
Why is account ACC-10492 considered high risk?
```

### Agent Pipeline

```text
User Query
    │
    ▼
Query Understanding
    │
    ▼
Account Lookup
    │
    ▼
Risk Analysis
    │
    ▼
Graph Expansion
    │
    ├── Connected Accounts
    ├── Shared Devices
    ├── Transactions
    ├── IP Addresses
    └── Merchants
    │
    ▼
Evidence Retrieval
    │
    ▼
Agent Reasoning
    │
    ▼
Investigation Report
```

### Example Result

```text
Risk Level: HIGH

Primary Signals

1. Shared device detected across multiple accounts.
2. Unusual transaction velocity observed.
3. Multiple connected entities have historical risk indicators.
4. Graph structure contains a suspicious high-density cluster.
5. Recent activity differs significantly from historical behavior.

Conclusion

The account requires further investigation based on the
combination of transactional, behavioral, and relational signals.
```

---

# 📊 Explainability First

A key design principle of FraudGraph-Agent is:

> **Every important risk signal should be explainable.**

The system aims to expose:

```text
Risk Score
    │
    ├── Transaction Signals
    │
    ├── Behavioral Signals
    │
    ├── Graph Signals
    │
    ├── Historical Signals
    │
    └── Retrieved Evidence
```

This makes the platform suitable for human-in-the-loop investigation workflows.

---

# 🛡️ Human-in-the-Loop

FraudGraph-Agent is designed to **assist investigators**, not blindly replace them.

```text
                 AI Investigation
                       │
                       ▼
                Evidence + Reasoning
                       │
                       ▼
                Human Analyst
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
         Confirm     Review     Escalate
```

This approach keeps the final investigation decision with the responsible analyst.

---

# ⚡ Design Principles

### 01 — Relationship First

Fraud is often a network problem.

### 02 — Explainability

Risk signals should be understandable.

### 03 — Specialized Agents

Complex investigations are decomposed into focused tasks.

### 04 — Evidence Grounding

AI responses should be supported by retrieved information.

### 05 — Human Oversight

Critical decisions remain reviewable by human investigators.

### 06 — Modular Architecture

Components can evolve independently.

---

# 🔮 Future Roadmap

* [ ] Real-time transaction streaming
* [ ] Advanced Graph Neural Networks
* [ ] Automated fraud-ring discovery
* [ ] Real-time graph updates
* [ ] Advanced GraphRAG reasoning
* [ ] Investigator feedback loop
* [ ] Case management system
* [ ] Evidence timeline visualization
* [ ] Automated regulatory report generation
* [ ] Multi-model agent orchestration
* [ ] Model monitoring and drift detection
* [ ] Production-grade observability
* [ ] Role-based access control
* [ ] Audit logging
* [ ] Scalable distributed deployment

---

# 🧪 Research & Engineering Direction

FraudGraph-Agent explores the intersection of:

```text
Artificial Intelligence
        +
Machine Learning
        +
Graph Intelligence
        +
Retrieval-Augmented Generation
        +
Agentic Systems
        +
Financial Crime Investigation
```

The central research direction is:

> **How can intelligent agents combine graph relationships and contextual evidence to make fraud investigation faster, more explainable, and more actionable?**

---

# 🌐 Use Cases

FraudGraph-Agent can support investigation workflows involving:

* 💳 Payment fraud
* 🏦 Banking fraud
* 🪪 Identity-related fraud
* 🕸️ Fraud-ring discovery
* 💸 Suspicious transaction analysis
* 📱 Device-network investigation
* 🌐 IP/network relationship analysis
* 🔍 AML investigation support
* 📊 Financial risk analysis
* 🧑‍💼 Analyst decision support

---

# 🏆 Project Vision

Most fraud systems answer:

> **"Is this transaction suspicious?"**

FraudGraph-Agent aims to answer a much more useful question:

> **"Why is this activity suspicious, what is it connected to, what evidence supports the finding, and what should the investigator examine next?"**

By combining **graph intelligence with agentic reasoning**, FraudGraph-Agent turns isolated financial events into an interconnected investigation landscape.

---

# 👨‍💻 Author

### **Abir Ghosh**

B.Tech — Information Technology

Built with a focus on:

**AI • Machine Learning • Graph Intelligence • Agentic Systems • Full-Stack Engineering**

---

# ⭐ Support the Project

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

Your support helps the project grow and encourages further development.

---

# 📜 License

This project is licensed under the **MIT License**.

See the `LICENSE` file for details.

---

<p align="center">

### 🕸️ FraudGraph-Agent

**See the transaction.
Understand the network.
Find the pattern.
Investigate the fraud.**

</p>
