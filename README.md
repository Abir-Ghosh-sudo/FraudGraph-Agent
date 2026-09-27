# 🕵️ FraudGraph-Agent

<p align="center">
  <img src="https://img.shields.io/badge/FraudGraph--Agent-000000?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LangGraph-Agentic%20AI-000000?style=for-the-badge" />
  <img src="https://img.shields.io/badge/TigerGraph-Graph%20Intelligence-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/TigerGraph%20MCP-MCP-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/LightGBM-Fraud%20ML-green?style=for-the-badge" />
  <img src="https://img.shields.io/badge/GraphRAG-Evidence%20Reasoning-red?style=for-the-badge" />
</p>

<p align="center">
  <strong>AI-Powered Agentic Fraud Investigation & Next-Best Action Engine</strong>
</p>

<p align="center">
  <i>Investigate. Connect. Reason. Decide. Act. Learn.</i>
</p>

---

## 🚨 Overview

**FraudGraph-Agent** is an AI-powered, agentic fraud investigation platform designed to investigate suspicious financial activity, connect fragmented evidence, assess fraud risk, reason under uncertainty, recommend the **Next Best Action (NBA)**, and maintain case memory for future investigations.

Traditional fraud systems often stop at:

> **"This transaction looks suspicious."**

FraudGraph-Agent goes further:

> **"Why is it suspicious? What evidence supports it? What entities are connected? How certain are we? What should happen next? Does the action require approval? What happened in similar historical cases?"**

The platform combines:

* 🤖 Agentic AI
* 🧠 LangGraph
* 🌐 TigerGraph
* 🔌 TigerGraph MCP
* 📊 LightGBM
* 🔎 GraphRAG
* 🧠 Case Memory
* 🔬 Fraud Pattern Detection
* ⚖️ Policy Reasoning
* 👤 Human-in-the-Loop Approval
* 🎯 Next Best Action Recommendation

into a unified investigation workflow.

---

# 🖥️ Dashboard

FraudGraph-Agent provides a visual investigation dashboard for monitoring:

* Fraud activity
* Investigation cases
* Risk levels
* Graph relationships
* Evidence
* Agent activity
* Recommendations
* Approval requests
* Investigation history

### 📸 Dashboard Preview
![Uploading image.png…]()


# 🎯 The Problem

Modern financial fraud rarely exists as an isolated transaction.

A suspicious transaction may be connected to:

```text
Customer
   │
   ├── Card
   │
   ├── Device
   │
   ├── IP / Connection
   │
   ├── Previous Transactions
   │
   └── Previous Fraud Cases
```

A transaction-level fraud score alone cannot reveal the complete relationship network behind suspicious activity.

Fraud investigators therefore need to answer:

* Is this transaction actually fraudulent?
* What type of fraud is occurring?
* Which customers, cards, devices, and IPs are connected?
* Has this entity appeared in previous fraud cases?
* How strong is the evidence?
* Is additional evidence required?
* Should the transaction be allowed, declined, monitored, or escalated?
* Does the action require human approval?
* What happened in similar historical cases?

FraudGraph-Agent addresses this gap through an **evidence-driven, graph-aware and policy-controlled agentic investigation workflow**.

---

# 💡 Core Concept

Instead of using a single ML score as the final decision, FraudGraph-Agent combines multiple sources of intelligence:

```text
Fraud Signal / Customer Report / Analyst Request
                    │
                    ▼
             ┌─────────────┐
             │  LangGraph  │
             │    Agent    │
             └──────┬──────┘
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      LightGBM  TigerGraph  GraphRAG
        ML        + MCP     + Memory
          │         │         │
          └─────────┼─────────┘
                    ▼
            Evidence + Risk +
               Uncertainty
                    │
                    ▼
             Policy Engine
                    │
                    ▼
             Next Best Action
                    │
             ┌──────┴──────┐
             ▼             ▼
       Human Approval   Allowed Action
             │             │
             └──────┬──────┘
                    ▼
                Explanation
                    │
                    ▼
                Case Memory
```

---

# 🤖 Agentic Investigation

The investigation is orchestrated through **LangGraph**.

The workflow contains:

```text
TRIGGER
   ↓
INVESTIGATE
   ↓
GATHER EVIDENCE
   ↓
DETECT PATTERNS
   ↓
ASSESS RISK
   ↓
ASSESS UNCERTAINTY
   ↓
REQUEST EVIDENCE
   ↓
REASSESS
   ↓
RECOMMEND ACTION
   ↓
APPROVAL
   ↓
EXECUTE ACTION
   ↓
EXPLAIN
   ↓
UPDATE MEMORY
   ↓
COMPLETE
```

The workflow can conditionally request additional evidence when the current evidence is insufficient.

This prevents the system from blindly acting on a single suspicious signal.

---

# 🧠 Machine Learning

## LightGBM Fraud Prediction

The transaction-level fraud prediction model uses:

**LightGBM — Gradient Boosted Decision Trees (GBDT)**

The model generates a probability between `0` and `1`.

```text
Transaction
     ↓
Feature Engineering
     ↓
147 Features
     ↓
LightGBM
     ↓
Fraud Probability
     ↓
Risk Assessment
```

The model uses:

* Transaction information
* Card information
* Customer information
* Identity information
* Device information
* Behavioral information
* Temporal information

The ML model is intentionally **not treated as the final decision maker**.

Instead:

```text
ML Probability
      +
Graph Evidence
      +
Historical Cases
      +
Fraud Patterns
      +
Policy
      +
Uncertainty
      ↓
Agent Decision
```

The currently retrained model is **v1.1.0**, with calibrated probability behavior designed to avoid the degenerate behavior observed in the initial fraud-heavy training setup.

---

# 🌐 TigerGraph

TigerGraph provides the **graph intelligence layer**.

Fraud is often a relationship problem rather than an isolated transaction problem.

The graph can represent relationships such as:

```text
Customer
   │
   ├──── owns ────► Card
   │                   │
   │                   └──── performs ────► Transaction
   │                                              │
   │                                              ├── uses ──► Device
   │                                              │
   │                                              └── originates ──► IP
   │
   └──── related to ────► Other Customer
```

This enables investigation of:

* Shared devices
* Shared IP addresses
* Connected customers
* Connected cards
* Transaction relationships
* Suspicious entity clusters
* Repeated behavioral patterns
* Historical relationships

### Graph

```text
Transaction_Fraud
```

---

# 🔌 TigerGraph MCP

FraudGraph-Agent uses **TigerGraph MCP (Model Context Protocol)** as the bridge between the AI agent and TigerGraph.

Conceptually:

```text
LangGraph Agent
      │
      ▼
  MCP Client
      │
      ▼
TigerGraph MCP
      │
      ▼
 TigerGraph
```

This architecture avoids tightly coupling the reasoning layer to a collection of custom graph wrappers.

TigerGraph MCP can expose capabilities related to:

* Graph discovery
* Schema inspection
* Vertex operations
* Edge operations
* GSQL
* Queries
* Loading operations
* Graph statistics
* Vector operations
* Tool discovery

### Installation

```bash
pip install tigergraph-mcp
```

Run:

```bash
tigergraph-mcp -vv
```

---

# 🔎 GraphRAG

FraudGraph-Agent combines graph retrieval with contextual document and historical-case retrieval.

```text
                 Investigation
                      │
             ┌────────┴────────┐
             ▼                 ▼
      Graph Retrieval    Document Retrieval
             │                 │
             ▼                 ▼
      Entities + Paths    Policies + Cases
             │                 │
             └────────┬────────┘
                      ▼
               Hybrid Retrieval
                      │
                      ▼
                  Reranking
                      │
                      ▼
            Investigation Context
```

GraphRAG allows the agent to reason over:

* Graph relationships
* Historical cases
* Fraud patterns
* Policies
* Regulatory context
* Previous decisions
* Investigation evidence

---

# 🧠 Case Memory

FraudGraph-Agent maintains investigation memory so previous investigations can inform future investigations.

Memory can contain:

* Findings
* Evidence
* Decisions
* Actions
* Outcomes
* Historical patterns
* Investigation context

Similar cases can be retrieved through:

```text
Vector Similarity
       +
Keyword Search
       ↓
Similar Case Retrieval
       ↓
Current Investigation
```

This creates a continuous investigation loop:

```text
Investigation
      ↓
Decision
      ↓
Outcome
      ↓
Case Memory
      ↓
Future Investigation
```

---

# 🎯 Next Best Action

The goal is not simply to classify transactions.

The agent must determine:

> **What should happen next?**

Possible actions include:

```text
ALLOW_TRANSACTION
DECLINE_TRANSACTION
MONITOR_CARD
MONITOR_CONNECTED_CARDS
WARN_CUSTOMER
VERIFY_WITH_CUSTOMER
STEP_UP_AUTH
BLOCK_CARD
BLOCK_ALL_CARDS
CREATE_CASE
GENERATE_REPORT
FILE_REPORT
ESCALATE_TO_ANALYST
CLOSE_NO_FRAUD
```

The NBA engine considers:

```text
Risk
+
Evidence
+
Fraud Pattern
+
Uncertainty
+
Exposure
+
Policy
+
Historical Outcomes
+
Approval Requirements
```

---

# ⚖️ Policy-Aware Decisions

The agent does not have unrestricted authority.

Before sensitive actions:

```text
Recommendation
      ↓
Policy Check
      ↓
Action Allowed?
      ↓
Approval Required?
      ↓
Approval
      ↓
Execution
```

This creates a clear separation between:

```text
AI Recommendation
        ≠
Action Authorization
```

---

# 🔐 Human-in-the-Loop Safety

Sensitive actions can require human approval.

Example:

```text
Agent
  ↓
BLOCK_CARD
  ↓
Approval Required
  ↓
Human Reviewer
  ↓
APPROVED
  ↓
Execute
```

The workflow checks approval status before execution, while the action layer independently verifies authorization.

The system follows a **fail-closed** approach for sensitive operations.

---

# 🔬 Fraud Pattern Detection

The system detects known and potentially undocumented fraud behaviors.

## Card Testing

Repeated small authorization attempts used to test whether a compromised card is active.

## Card-Not-Present Fraud

Suspicious online/card-not-present transaction behavior.

## Card-Not-Present + New Device

Suspicious transaction activity combined with a previously unseen device.

## Out-of-Region Usage

Transaction behavior inconsistent with the customer's established geographic pattern.

## Account Takeover

Signals suggesting compromised credentials or account control.

The system can also identify **undocumented or coordinated abuse patterns** when observed behavior does not fit predefined categories.

---

# 📚 Dataset

FraudGraph-Agent uses the **HHGOA / IEEE fraud investigation dataset**.

The dataset contains:

```text
transactions.csv
identity.csv
closed_cases_history.csv
case_pack.csv
README.md
```

### Approximate Scale

| Dataset          |  Size |
| ---------------- | ----: |
| Transactions     | ~590K |
| Identity Records | ~144K |
| Closed Cases     | ~5.5K |
| Benchmark Cases  |    20 |

Historical cases contain information such as:

* Confirmed fraud
* Cleared investigations
* Fraud patterns
* Transaction IDs
* Exposure
* Connected cards
* Actions taken
* Reports
* Analyst notes

The benchmark contains **20 investigation cases**.

> The official benchmark answer key is hidden; therefore model predictions should not be presented as official benchmark accuracy.

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │      Dashboard      │
                         │   Investigation UI  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │       REST API      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      LangGraph      │
                         │    Agent Workflow   │
                         └──────────┬──────────┘
                                    │
             ┌──────────────────────┼────────────────────────┐
             │                      │                        │
             ▼                      ▼                        ▼
      ┌────────────┐        ┌─────────────┐          ┌─────────────┐
      │  LightGBM  │        │ TigerGraph  │          │   GraphRAG  │
      │ Fraud ML   │        │ + MCP       │          │ + Memory    │
      └──────┬─────┘        └──────┬──────┘          └──────┬──────┘
             │                     │                        │
             └─────────────────────┼────────────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │ Evidence + Risk +   │
                         │ Uncertainty Engine  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Policy Engine    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   NBA Engine        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Approval / Action   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Explanation +       │
                         │ Case Memory         │
                         └─────────────────────┘
```

---

# 🗂️ Project Structure

```text
FraudGraph-Agent/
│
├── backend/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── state.py
│   │   ├── workflow.py
│   │   ├── nodes/
│   │   └── tools/
│   │
│   ├── fraud/
│   ├── ml/
│   ├── risk/
│   ├── nba/
│   ├── evidence/
│   ├── cases/
│   ├── memory/
│   ├── graphrag/
│   ├── tigergraph/
│   ├── policy/
│   ├── actions/
│   ├── sar/
│   └── app/
│
├── frontend/
│
├── data/
│   └── raw/
│
├── models/
│   └── fraud_model.joblib
│
├── scripts/
│
├── tests/
│
├── .env.example
├── pyproject.toml
└── README.md
```

---

# ⚙️ Technology Stack

| Layer               | Technology                 |
| ------------------- | -------------------------- |
| Backend             | Python                     |
| API                 | FastAPI                    |
| Agent Orchestration | LangGraph                  |
| LLM                 | Ollama / Llama 3.1 8B      |
| Fraud ML            | LightGBM                   |
| Graph Database      | TigerGraph                 |
| Agent ↔ Graph       | TigerGraph MCP             |
| Graph Intelligence  | GraphRAG                   |
| Memory              | Vector + Keyword Retrieval |
| Frontend            | React / TypeScript         |
| Dataset             | HHGOA / IEEE Fraud Dataset |

---

# 🤖 LLM Layer

The reasoning layer uses:

```text
Provider: Ollama
Model: Llama 3.1 8B
```

Example configuration:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

The LLM is responsible for:

* Agent reasoning
* Investigation interpretation
* Evidence synthesis
* Explanation generation
* Action rationale

It is **not the primary fraud classifier**.

The fraud classifier is **LightGBM**.

---

# 🧪 Example Investigation

Suppose the system receives:

```text
Transaction: 3514030
Customer: C12382
Bank Risk Score: 0.61
```

The agent can investigate:

```text
Transaction
    ↓
ML Fraud Probability
    ↓
Customer History
    ↓
Card Relationships
    ↓
Device Relationships
    ↓
IP / Connection Relationships
    ↓
Historical Cases
    ↓
Fraud Pattern Detection
    ↓
Risk Assessment
    ↓
Uncertainty Assessment
    ↓
Additional Evidence
    ↓
Next Best Action
    ↓
Approval
    ↓
Action
    ↓
Explanation
    ↓
Case Memory
```

---

# 📋 Explainability

Every recommendation should be understandable to a human analyst.

Example:

```text
Risk Level:
HIGH

Fraud Probability:
0.87

Detected Pattern:
Card-not-present + new device

Key Evidence:
• Elevated ML fraud probability
• New device association
• Related suspicious activity
• Connected entity evidence
• Similar historical cases

Uncertainty:
Medium

Recommended Action:
STEP_UP_AUTH

Reason:
The available evidence indicates elevated risk,
while customer verification can materially reduce
uncertainty before stronger action is taken.

Approval:
Required
```

---

# 🚀 Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Abir-Ghosh-sudo/FraudGraph-Agent.git
cd FraudGraph-Agent
```

## 2. Create Virtual Environment

```bash
python -m venv .venv
```

### Windows

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install Dependencies

```bash
pip install -e .
```

## 4. Install Ollama Model

```bash
ollama pull llama3.1:8b
```

## 5. Start Backend

```bash
uvicorn backend.app.main:app --reload
```

## 6. Start Frontend

```bash
cd frontend
npm run dev
```

## 7. Run Tests

```bash
pytest
```

---

# 🌐 Environment Configuration

Create a `.env` file based on `.env.example`.

```env
APP_ENV=development

LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

TIGERGRAPH_HOST=<YOUR_HOST>
TIGERGRAPH_USERNAME=<YOUR_USERNAME>
TIGERGRAPH_API_TOKEN=<YOUR_TOKEN>
TIGERGRAPH_GRAPH_NAME=Transaction_Fraud
TIGERGRAPH_MCP_ENABLED=true

AGENT_MAX_STEPS=20
AGENT_REQUIRE_APPROVAL=true
```

> ⚠️ **Never commit real credentials, passwords, API tokens, or secrets.**

---

# 📈 Investigation Philosophy

FraudGraph-Agent is built around several principles.

### 🔍 Evidence Before Action

Investigate before taking high-impact action.

### 📊 ML Is Probabilistic

A fraud score is evidence, not absolute truth.

### 🌐 Fraud Is Relational

Graph relationships can reveal patterns invisible at transaction level.

### 👤 Human Control

Sensitive actions remain subject to approval.

### 📋 Explainability

Every recommendation should have an evidence-backed rationale.

### 🧠 Memory

Previous investigations should improve future investigations.

### ⚙️ Controlled Autonomy

The agent can investigate autonomously while remaining bounded by policies and permissions.

---

# 🏆 Why FraudGraph-Agent?

## Traditional Fraud Detection

```text
Transaction
     ↓
Fraud Score
     ↓
Alert
```

## FraudGraph-Agent

```text
Transaction
     ↓
ML Prediction
     +
Graph Investigation
     +
Historical Cases
     +
Fraud Patterns
     +
Policy
     +
Uncertainty
     ↓
Agentic Investigation
     ↓
Next Best Action
     ↓
Human Approval
     ↓
Action
     ↓
Explanation
     ↓
Case Memory
```

The core transformation is:

> **From fraud detection → to evidence-driven agentic fraud investigation.**

---

# 🏁 Hackathon Demo Flow

A complete demonstration can follow:

```text
1. Trigger suspicious transaction
        ↓
2. Agent starts investigation
        ↓
3. Graph relationships appear
        ↓
4. ML fraud probability is calculated
        ↓
5. Historical evidence is retrieved
        ↓
6. Fraud patterns are detected
        ↓
7. Risk + uncertainty are assessed
        ↓
8. Next Best Action is generated
        ↓
9. Human approval is requested
        ↓
10. Action is executed / simulated
        ↓
11. Agent explains the decision
        ↓
12. Case memory is updated
```

---

# 🔒 Security

FraudGraph-Agent follows a **fail-closed approach** for sensitive operations.

Security considerations include:

* API authentication
* Server-side approval verification
* Action validation
* Approval binding
* Unknown-action rejection
* Human approval
* Policy constraints
* Credential protection

For shared or production deployments:

```env
AUTH_ENABLED=true
```

should be enabled.

---

# 🔗 Architecture Summary

```text
┌─────────────────────────────────────────────────────────┐
│                    FraudGraph-Agent                     │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  React / TypeScript Investigation Dashboard             │
│                       │                                 │
│                       ▼                                 │
│                  FastAPI REST API                       │
│                       │                                 │
│                       ▼                                 │
│                  LangGraph Agent                       │
│                       │                                 │
│        ┌──────────────┼──────────────┐                  │
│        ▼              ▼              ▼                  │
│    LightGBM       TigerGraph      GraphRAG              │
│   Fraud Model        + MCP        + Memory              │
│        │              │              │                  │
│        └──────────────┼──────────────┘                  │
│                       ▼                                 │
│             Evidence + Risk +                           │
│                Uncertainty                              │
│                       │                                 │
│                       ▼                                 │
│                 Policy Engine                           │
│                       │                                 │
│                       ▼                                 │
│                Next Best Action                         │
│                       │                                 │
│              ┌────────┴────────┐                        │
│              ▼                 ▼                        │
│       Human Approval      Allowed Action                │
│              │                 │                        │
│              └────────┬────────┘                        │
│                       ▼                                 │
│             Explanation + Memory                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

# 📚 References

* **TigerGraph MCP:** https://github.com/tigergraph/tigergraph-mcp
* **TigerGraph:** https://www.tigergraph.com/
* **LangGraph:** https://github.com/langchain-ai/langgraph
* **LightGBM:** https://github.com/microsoft/LightGBM
* **Ollama:** https://ollama.com/

---

# 👨‍💻 FraudGraph-Agent

### AI × Graph Intelligence × Agentic Reasoning × Fraud Analytics

> **Don't just detect fraud. Investigate it. Understand it. Explain it. Act on it.**

---

<p align="center">
  <strong>FraudGraph-Agent</strong>
</p>

<p align="center">
  Built for intelligent, explainable, graph-aware fraud investigation.
</p>
