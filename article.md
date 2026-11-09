<div align="center">

# 🛡️ Why I Decoupled Deterministic Threat Scoring from Hindsight Memory Lookup

### An architectural case study on cybersecurity ingestion and fault-isolated AI memory pipelines

**RECALLIX** · FastAPI · SQLAlchemy · SQLite · React · Groq · Hindsight

</div>

---

## 📑 Contents

1. [The failure that started this](#-the-failure-that-started-this)
2. [How RECALLIX hangs together](#-how-recallix-hangs-together)
3. [Defending against upstream failure](#-defending-against-upstream-failure)
4. [Code-backed deep dive](#-code-backed-deep-dive)
5. [System behavior under live load](#-system-behavior-under-live-load)
6. [Lessons learned](#-lessons-learned)
7. [Limitations and next steps](#-limitations-and-next-steps)

---

## 🚨 The failure that started this

Feeding raw, unvetted alert logs into a Large Language Model and asking it to decide how severe a breach is can fail badly. Last month, while auditing our automated triage pipeline, we watched a simulated credential-harvesting alert get ignored because the model downplayed the threat score, thrown off by formatting quirks in the raw logs.

That failure led us to build **RECALLIX**, an AI-powered cybersecurity incident intelligence and investigation platform. We made one opinionated architectural decision:

> **Deterministic risk scoring must never depend on, or be influenced by, the memory layer or the LLM.**

We built a strict firewall between three components:

- the **deterministic rules engine**
- the **contextual memory layer**, powered by the [Hindsight](https://github.com/vectorize-io/hindsight) agent-memory system
- the **asynchronous LLM reporting pipeline**

This article covers how we structured that pipeline, why we isolated human analyst validation from external network boundaries, and what we learned about operational resilience when upstream AI models choke.

---

## 📌 How RECALLIX hangs together

RECALLIX is an outcome-aware incident intelligence platform built around durable state. Traditional triage relies on stateless search or flat, siloed tickets. When a complex authentication exploit hits an enterprise, analysts spend hours tracking indicators, and those insights get trapped in a closed ticket once the incident is resolved.

RECALLIX replaces that with an active lifecycle:

```mermaid
flowchart LR
    A[Ingestion] --> B[Deterministic<br/>Risk Assessment]
    B --> C[Historical Memory<br/>Retrieval]
    C --> D[Structured AI<br/>Investigation]
    D --> E[SQLite<br/>Persistence]
    E --> F[Analyst<br/>Verification]
    F --> G[Hindsight<br/>Retention]
```

### Architecture at a glance

| Layer | Technology | Responsibility |
|---|---|---|
| **Web** | React + Tailwind CSS | Dark, low-latency UI built for SOC environments |
| **Core engine** | FastAPI + SQLAlchemy | API routing and transactional boundaries |
| **Local persistence** | SQLite (`recallix.db`) | Primary source of truth for all incident state |
| **Long-term context** | Hindsight at `127.0.0.1:8889` | Isolated memory service on the `security-incident-intelligence` bank |

### Memory retrieval

When an alert arrives, RECALLIX runs a multi-strategy lookup against the memory bank. Standard vector databases strip out temporal relationships. [Vectorize's agent memory](https://vectorize.io) instead runs a **4-way parallel search** (semantic, keyword, graph, and temporal). That lets us pull historical experiences, consolidated observations, and raw facts at the same time, giving the analyst deep operational context in their workspace.

---

## 🧠 Defending against upstream failure

The hardest engineering problem was the fragility of external AI and memory vendors. During integration testing, our inference provider regularly exhausted its daily quota, returning rate-limit errors or timing out on heavy payloads.

If those calls run **synchronously inside the HTTP ingestion thread**, an upstream rate limit becomes a system failure for the SOC analyst. It gets worse if human-validation state and the memory push are coupled, because one failed remote call can erase local tracking records.

We solved this with an asynchronous, fault-isolated lifecycle inside the FastAPI router, built on three rules:

1. **Score first, never wait.** The risk engine assesses input parameters without waiting on any external LLM request.
2. **Commit locally before going remote.** When an analyst signs off on an incident dossier, RECALLIX commits the verification to SQLite in its own isolated transaction *before* attempting any external call.
3. **Retry in the background.** If the Hindsight push fails because of an upstream rate barrier, the exception is caught and FastAPI's `BackgroundTasks` schedules retries with exponential backoff. The analyst moves straight to the next threat, with no UI blocking.

---

## 🛠️ Code-backed deep dive

### Safe payload serialization

The `_incident_payload()` function in `backend/app/routes/incidents.py` sanitizes every database record before it reaches the frontend. This prevents nested serialization anomalies from crashing React components when state reloads.

```python
def _incident_payload(incident):
    """
    Ensures raw database text blobs are safely de-serialized back into valid
    JSON maps and arrays for reliable frontend component parsing.
    """
    def safe_json_load(field_data):
        if field_data is None:
            return None
        if isinstance(field_data, (dict, list)):
            return field_data
        try:
            return json.loads(field_data)
        except (ValueError, TypeError):
            return field_data

    return {
        "id": incident.id,
        "title": incident.title,
        "incident_type": incident.incident_type,
        "description": incident.description,
        "evidence": safe_json_load(incident.evidence) or [],
        "severity": incident.severity,
        "risk_score": incident.risk_score,
        "indicators": safe_json_load(incident.indicators) or [],
        "risk_factors": safe_json_load(incident.risk_factors) or [],
        "recommendations": safe_json_load(incident.recommendations) or [],
        "analysis_method": incident.analysis_method,
        "memory_used": bool(incident.memory_used),
        "verified": bool(incident.verified),
        "created_at": incident.created_at.isoformat(),
        "llm_analysis": safe_json_load(incident.llm_analysis),
        "llm_status": incident.llm_status,
        "llm_model": incident.llm_model,
        "llm_error": safe_json_load(incident.llm_error),
    }
```

### Two-tier verification endpoint

The verification endpoint handles the multi-tier state transaction. The local SQL record is committed inside its own `try/except` boundary (**Tier 1**). Only then does the endpoint attempt the Hindsight push (**Tier 2**). If that fails, it queues `periodic_retention_retry` to absorb the load asynchronously.

```python
@router.post("/{incident_id}/verify")
async def verify_incident(
    incident_id: int,
    verification: IncidentVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident tracking vector not found")

    # Tier 1: save human analyst validation locally first
    incident.verified = True
    incident.verified_at = datetime.now(timezone.utc)
    incident.verification_notes = verification.analyst_notes

    try:
        db.commit()
        db.refresh(incident)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Local persistence ledger commit failure.")

    if incident.memory_retained:
        return {"success": True, "message": "Verified lesson already locked in Hindsight."}

    lesson = (
        f"RECALLIX VERIFIED LESSON. ID: {incident.id}. "
        f"Category: {incident.incident_type}. Context: {incident.description}."
    )
    from backend.app.database.database import SessionLocal

    # Tier 2: push to the memory bank, with a background fallback
    try:
        retain_result = await retain_verified_lesson(
            content=lesson,
            incident_id=incident.id,
            incident_type=incident.incident_type,
        )

        if isinstance(retain_result, dict) and retain_result.get("success") is True:
            incident.memory_retained = True
            db.commit()
            return {"success": True, "verified": True, "retained": True}

    except Exception as error:
        db.rollback()

        # Queue the background worker to absorb upstream rate limits
        background_tasks.add_task(
            periodic_retention_retry,
            incident_id=incident.id,
            lesson_content=lesson,
            incident_type=incident.incident_type,
            db_session_factory=SessionLocal,
        )

        return {
            "success": True,
            "verified": True,
            "retained": False,
            "message": (
                "Analyst verification saved locally. Hindsight rate limits "
                "encountered; automatic retry worker queued."
            ),
            "retention_error": str(error),
        }
```

### Background retry worker

The retry handler runs a non-blocking asynchronous loop with exponential backoff, so we don't hammer the remote gateway while the vendor's rate-limit window is still active.

```python
async def periodic_retention_retry(
    incident_id: int,
    lesson_content: str,
    incident_type: str,
    db_session_factory,
):
    """
    Asynchronous worker. Re-attempts memory ingestion without
    blocking primary ASGI application processes.
    """
    max_retries = 3
    delay = 15

    for attempt in range(1, max_retries + 1):
        await asyncio.sleep(delay)
        try:
            retain_result = await retain_verified_lesson(
                content=lesson_content,
                incident_id=incident_id,
                incident_type=incident_type,
            )
            if isinstance(retain_result, dict) and retain_result.get("success") is True:
                db = db_session_factory()
                incident = db.query(Incident).filter(Incident.id == incident_id).first()
                if incident:
                    incident.memory_retained = True
                    db.commit()
                db.close()
                break
        except Exception:
            delay *= 2  # exponential backoff: 15s -> 30s -> 60s
```

---

## 📊 System behavior under live load

To see how the system behaves under realistic conditions, here is an ingestion trace from our diagnostic telemetry during a simulated identity attack.

### Scenario: geographic anomaly

An alert reports that one user account completed two successful logins from geographically impossible locations within a 5-minute window: the local enterprise network, then an unfamiliar foreign endpoint.

**Submitted logs**

```text
Login success from IP 192.168.1.50
Login success from unfamiliar foreign IP
Impossible travel alert triggered
```

### Processing breakdown

| Step | Stage | What happened |
|:---:|---|---|
| 1 | **Rule evaluation** | A strict keyword sweep flags *impossible travel* and scores the incident **80/100**, forcing severity to `HIGH`. |
| 2 | **Hindsight query** | `recall()` filters out matches from the current file context and returns past incidents **INC-2** and **INC-8**, showing that identical geographic mismatches preceded MFA-bypass attempts last month. |
| 3 | **Upstream congestion** | Groq returns an explicit **HTTP 429** rate-limit error. |
| 4 | **Graceful isolation** | RECALLIX catches the error, marks the investigation `quota_limited`, keeps the deterministic risk results, and writes the full payload to SQLite. |

The application stays online and shows the complete rule assessment and historical memory matches on the dashboard. When the analyst logs a confirmation note, the record is marked `"verified": true` immediately. The background worker then retries the Hindsight push with backoff and commits it as soon as upstream capacity returns.

---

## 🚀 Lessons learned

Building RECALLIX taught us four concrete lessons about resilient, AI-driven operational tools.

**1. Isolate your state boundaries early.**
Never let an external API call sit inside your critical data-writing path. If a service can fail, time out, or rate-limit your keys, decouple its execution from your primary relational transactions.

**2. Vector embeddings are not memory.**
Basic vector search has no temporal awareness. An outcome-aware memory system links facts to canonical entities and tracks how knowledge evolves, which turns simple log lookups into compounding institutional knowledge.

**3. Enforce strict schema contracts.**
LLMs are non-deterministic. If you don't map inference output to strict JSON schema definitions at the router layer, raw text outputs will eventually corrupt your frontend.

**4. Budget in tokens, not result counts.**
Traditional backends paginate by integer count. AI agent architectures should budget inputs in tokens to improve signal-to-noise inside the context window and avoid the degradation that long contexts cause.

---

## 🔭 Limitations and next steps

- **Retries are in-process.** `BackgroundTasks` retries live in application memory, so a server restart drops any pending retry. A persistent queue (or a startup sweep for incidents where `verified = true` and `memory_retained = false`) would close that gap.
- **Bounded retries.** The worker gives up after three attempts, so unresolved incidents need that sweep to be picked up later.

---

<div align="center">

**RECALLIX** · Built to make every investigation count 🛡️

[⭐ Star on GitHub](https://github.com/YOUR_USERNAME/Recallix-security-intelligence)

</div>
