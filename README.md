<h1 align='center'> 🛡️ RECALLIX — AI Security Incident Intelligence</h1>

<div align="center">

### An Intelligent Approach to Incident Investigation with Persistent Memory

**An AI-powered cybersecurity incident triage system that combines rule-based assessment, Large Language Model reasoning, outcome-aware platform memory, and fault-tolerant background queues.**

*Investigate. Analyze. Recall. Retain.*

<br/>

[![Python](https://shields.io)](https://python.org)
[![FastAPI](https://shields.io)](https://tiangolo.com)
[![React](https://shields.io)](https://react.dev)
[![TailwindCSS](https://shields.io)](https://tailwindcss.com)
[![License](https://shields.io)](LICENSE)

[![GitHub Stars](https://shields.io)](https://github.com)
[![GitHub Forks](https://shields.io)](https://github.com)
[![Last Commit](https://shields.io)](https://github.com)

</div>

## 📌 Overview

Traditional incident investigation platforms analyze security events using only currently visible indicators. Once an investigation finishes, its valuable analytical findings are trapped inside closed logs, databases, or single-use tickets.

This creates a critical operational constraint:
- When a similar security vector targets an enterprise weeks later, security analysts must repeat much of the previous investigation from scratch.
- Machine learning probabilities alone don't provide structural, deterministic logic.
- AI investigation assets fail or hit API quota boundaries when running synchronously.
- Retained memories risk losing traceability to their original source incidents.

**RECALLIX** bridges this gap by combining rule-based risk engines, high-speed LLM reasoning, historical memory matching via Hindsight, human-in-the-loop analyst verification, and an asynchronous background task runner to form an outcome-aware intelligence platform.

### 🔄 RECALLIX Pipeline

```text
                  INCIDENT SUBMISSION
                           │
                           ▼
               HISTORICAL MEMORY RETRIEVAL
                      (Hindsight)
                           │
                           ▼
               RULE-BASED RISK ENGINE
                           │
                           ▼
                GROQ LLM INVESTIGATION
                           │
                           ▼
               SQLITE SCHEMA PERSISTENCE
                           │
                           ▼
               ANALYST VERIFICATION LOOP
                           │
                           ▼
               FAULT-TOLERANT RETRY DAEMON
                           │
                           ▼
               HINDSIGHT MEMORY RETENTION
```

---

## 🧠 Core Intelligence Layers

RECALLIX utilizes a multi-layered verification framework to maintain data integrity across the platform lifecycle.

### 1. Rule-Based Risk Engine
To prevent LLM hallucination from dictating threat metrics, RECALLIX runs a deterministic rules pipeline. It checks evidence length and incident classification rules to build objective severity ratings.

| Parameter | Operational Threshold |
|---|---:|
| Base Match Score | 40% |
| Multi-Vector Addition | +20% |
| Identity Compromise Affected | +20% |

The final score drives security tier assignment (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) completely separately from AI reasoning loops.

### 2. Groq AI Investigation Module
Integrates the `llama-3.3-70b-specdec` model via Groq's high-speed inference layer to construct a structured investigation breakdown mapping execution gaps and next operational protocols.

**Enforced Response JSON Schema:**
- `executive_summary`: Concise incident narrative.
- `evidence_analysis`: Line-by-line validation logs.
- `historical_comparison`: Direct matching against past Hindsight knowledge.
- `uncertainties`: Known evidence gaps or validation failures.
- `next_investigation_steps`: Actionable containment sequences.
- `analyst_guidance`: Investigating protocols.

### 3. Hindsight Long-Term Memory (Recall & Retention)
Rather than treating incidents as isolated artifacts, RECALLIX queries a local Hindsight microservice (`127.0.0.1:8889`) across a dedicated cluster bank. When analysts click "Commit Verification," an idempotent document signature (`recallix-verified-incident-{id}`) is submitted, enabling stable, duplication-free long-term cross-incident recall.

---

## ⚙️ Risk Decision Matrix

The platform maps incident lifecycles across six separate conditions to isolate application failures:

```text
  [Incident Created] ──> [Risk Assessed] ──> [AI Analysis Generated]
                                                      │
  [Memory Retained] <── [Analyst Verified] <── [SQLite Persisted]
```

### Response States & Recovery Actions

| State Condition | Meaning | Recovery Action |
|:---:|---|---|
| **completed** | AI reasoning compiled and locally written. | Ready for analyst manual audit sign-off. |
| **quota_limited** | Upstream token thresholds hit (HTTP 429). | System defaults to deterministic rule metrics safely. |
| **connection_error** | Upstream provider network down. | Local database holds workspace for later manual retry. |

---

## 🖥️ RECALLIX Dark SOC Dashboard

RECALLIX is built around a custom, dark-themed Security Operations Center template featuring sub-300ms layout views:

* **Engine Status Checker:** Automatically hits the backend root endpoint `/` to confirm state connectivity (`● System online`) instead of throwing false offline errors.
* **Persistent AI Dossier View:** Bypasses standard React volatile state drops. AI reports are completely string-serialized into SQLite columns, ensuring data survives page refreshes and view changes.
* **Traceable Memory Cards:** Groups retrieved historical elements by their original `Source: INC-ID` parameters to maintain audit trails.

---

## 🏗️ Project Structure

```text
Recallix-security-intelligence/
│
├── backend/
│   └── app/
│       ├── database/
│       │   └── database.py
│       ├── models/
│       │   └── incident.py
│       ├── memory/
│       │   └── hindsight_service import.py
│       ├── routes/
│       │   └── incidents.py
│       ├── services/
│       │   ├── investigation_engine.py
│       │   └── llm_service.py
│       └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AIInvestigationReport.jsx
│   │   │   └── MemoryCard.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
│
├── requirements.txt
├── recallix.db
└── README.md
```

---

## 🛠️ Technology Stack

### Backend & Database Layer
![Python](https://shields.io)
![FastAPI](https://shields.io)
![SQLAlchemy](https://shields.io)
![SQLite](https://shields.io)

### AI & Knowledge Retention
![Groq](https://shields.io)
![Hindsight](https://shields.io)

### Frontend Layer
![React](https://shields.io)
![Vite](https://shields.io)
![TailwindCSS](https://shields.io)

---

## 💻 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com
cd Recallix-security-intelligence
```

### 2. Configure the Python Backend Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Create a root environment configuration file `.env` and fill in your variables:
```env
GROQ_API_KEY=your_secret_groq_api_token
GROQ_MODEL=llama-3.3-70b-specdec
HINDSIGHT_BASE_URL=http://127.0.0.1:8889
HINDSIGHT_BANK_ID=security-incident-intelligence
```

Start the application container:
```bash
uvicorn backend.app.main:app --reload --port 8000
```

### 3. Launch the React Web Frontend
```bash
cd frontend
npm install
npm run dev
```
Open your browser and navigate to `http://localhost:5173`.

---

## 🧩 Build Challenges & Technical Obstacles

### 1. SQLite Data Serialization Drops
**Problem:** SQLAlchemy's standard JSON column structures return raw unparsed strings when queried via basic dictionaries on fast reloads, causing frontend layout modules to break.

