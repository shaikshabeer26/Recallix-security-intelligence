
import json
import os 
import re
from datetime import datetime, timezone
from typing import Literal
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.app.database.database import get_db
from backend.app.models.incident import Incident
from backend.app.services.investigation_engine import analyze_incident
from backend.app.services.llm_service import analyze_with_groq
from backend.app.memory.hindsight_service import (
    recall_incident_context,
    retain_verified_lesson,
)

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Investigation"],
)


class IncidentRequest(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    incident_type: Literal[
        "auth", "network", "malware", "phishing"
    ]
    description: str = Field(min_length=10, max_length=5000)
    evidence: list[str] = Field(default_factory=list, max_length=30)


class IncidentVerificationRequest(BaseModel):
    verified: bool
    analyst_notes: str = Field(default="", max_length=2000)


def _memory_text(item) -> str:
    """Convert a recalled memory into searchable text."""
    if isinstance(item, str):
        return item

    try:
        return json.dumps(item, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(item)



def _filter_current_incident_memories(
    memories,
    incident_id=None,
    title=None,
):
    """
    Exclude memories belonging to the incident currently
    being investigated or viewed.

    Prefer structured Hindsight metadata. Use text matching
    only as a fallback for older memories.
    """

    filtered = []

    normalized_title = (
        " ".join(title.lower().split())
        if title
        else None
    )

    for memory in memories or []:
        metadata = memory.get("metadata") or {}

        # Primary check: structured source incident ID.
        source_incident_id = metadata.get("incident_id")

        if (
            incident_id is not None
            and source_incident_id is not None
            and str(source_incident_id) == str(incident_id)
        ):
            continue

        # Fallback for older memories without metadata.
        memory_text = " ".join(
            (memory.get("text") or "").lower().split()
        )

        if normalized_title and normalized_title in memory_text:
            continue

        filtered.append(memory)

    return filtered


def _incident_payload(incident):
    return {
        "id": incident.id,
        "title": incident.title,
        "incident_type": incident.incident_type,
        "description": incident.description,
        "evidence": incident.evidence or [],
        "severity": incident.severity,
        "risk_score": incident.risk_score,
        "indicators": incident.indicators or [],
        "risk_factors": incident.risk_factors or [],
        "recommendations": incident.recommendations or [],
        "analysis_method": incident.analysis_method,
        "memory_used": bool(incident.memory_used),
        "verified": bool(incident.verified),
        "verified_at": (
            incident.verified_at.isoformat()
            if incident.verified_at else None
        ),
        "verification_notes": incident.verification_notes,
        "memory_retained": bool(incident.memory_retained),
        "created_at": incident.created_at.isoformat(),
        "llm_analysis": incident.llm_analysis,
        "llm_status": incident.llm_status,
        "llm_model": incident.llm_model,
        "llm_error": incident.llm_error,
    }


@router.post("/analyze")
async def investigate_incident(
    incident: IncidentRequest,
    db: Session = Depends(get_db),
):
    try:
        # -------------------------------------------------
        # 1. Retrieve relevant historical Hindsight memories
        # -------------------------------------------------
        memory_query = (
            f"Security incident category: {incident.incident_type}. "
            f"Title: {incident.title}. "
            f"Description: {incident.description}. "
            f"Evidence: {'; '.join(incident.evidence)}. "
            "Find relevant lessons and response recommendations "
            "from previous security investigations. "
            "Do not treat historical information as proof of this incident."
        )

        historical_context = []
        memory_error = None

        try:
            historical_context = await recall_incident_context(memory_query)

            historical_context = _filter_current_incident_memories(
                historical_context,
                title=incident.title,
            )

        except Exception as error:
            memory_error = str(error)

        # -------------------------------------------------
        # 2. Existing rule-based risk assessment
        # -------------------------------------------------
        result = analyze_incident(
            incident_type=incident.incident_type,
            title=incident.title,
            description=incident.description,
            evidence=incident.evidence,
            historical_context=historical_context,
        )

        # -------------------------------------------------
        # 3. Hindsight status
        # -------------------------------------------------
        if memory_error:
            result["memory_used"] = False
            result["memory_status"] = "unavailable"
            result["memory_error"] = memory_error
        else:
            result["memory_used"] = bool(historical_context)
            result["memory_status"] = (
                "recalled"
                if historical_context
                else "no_relevant_memories"
            )

        # -------------------------------------------------
        # 4. Groq investigation reasoning
        # -------------------------------------------------
        from backend.app.services.llm_service import classify_groq_error

        llm_analysis = None
        llm_error = None

        try:
            llm_analysis = await analyze_with_groq(
                incident_type=incident.incident_type,
                title=incident.title,
                description=incident.description,
                evidence=incident.evidence,
                historical_context=historical_context,
            )

            result["analysis_method"] = (
                "Rule-based risk assessment + "
                "Groq AI investigation reasoning + "
                "Hindsight historical context"
            )

        except Exception as error:
            llm_error = classify_groq_error(error)

            result["analysis_method"] = (
                "Rule-based evidence assessment"
                + (
                    " + Hindsight historical context"
                    if historical_context
                    else ""
                )
            )

        # -------------------------------------------------
        # 5. Attach AI status without changing risk score
        # -------------------------------------------------
        result["llm_analysis"] = llm_analysis
        result["llm_status"] = (
            "completed"
            if llm_analysis
            else (
                llm_error["status"]
                if llm_error
                else "unavailable"
            )
        )
        result["llm_error"] = llm_error
        result["llm_model"] = (
            "Groq / " + os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
            if llm_analysis
            else None
        )

        # -------------------------------------------------
        # 6. Save incident in SQLite
        # -------------------------------------------------
        db_incident = Incident(
            title=incident.title,
            incident_type=incident.incident_type,
            description=incident.description,
            evidence=incident.evidence,

            severity=result["severity"],
            risk_score=result["risk_score"],
            indicators=result["indicators"],
            risk_factors=result["risk_factors"],
            recommendations=result["recommendations"],
            analysis_method=result["analysis_method"],
            memory_used=result["memory_used"],

            # Persist the Groq investigation report
            llm_analysis=llm_analysis,
            llm_status=result["llm_status"],
            llm_model=result["llm_model"],
            llm_error=llm_error,

            verified=False,
            memory_retained=False,
        )

        db.add(db_incident)
        db.commit()
        db.refresh(db_incident)

        return {
            "success": True,
            "incident_id": db_incident.id,
            "created_at": db_incident.created_at.isoformat(),
            "incident": incident.model_dump(),
            "investigation": result,
            "storage": "saved",
            "verification_endpoint": (
                f"/api/incidents/{db_incident.id}/verify"
            ),
        }

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Incident investigation failed: {str(error)}",
        )

async def periodic_retention_retry(incident_id: int, lesson_content: str, incident_type: str, db_session_factory):
    """
    Asynchronous background worker. Handles exponential retries if the 
    upstream AI provider encounters a temporary quota limitation.
    """
    max_retries = 3
    delay = 15  # Start with a conservative delay or dynamic parsing if needed
    
    for attempt in range(1, max_retries + 1):
        # We wait asynchronously so we don't freeze the main web server threads
        await asyncio.sleep(delay)
        
        try:
            print(f"[RECALLIX BACKGROUND WORKER] Executing retention push retry attempt {attempt}/{max_retries} for INC-{incident_id}...")
            retain_result = await retain_verified_lesson(
                content=lesson_content,
                incident_id=incident_id,
                incident_type=incident_type,
            )
            
            if isinstance(retain_result, dict) and retain_result.get("success") is True:
                # Open an isolated session to commit changes safely
                db = db_session_factory()
                incident = db.query(Incident).filter(Incident.id == incident_id).first()
                if incident:
                    incident.memory_retained = True
                    db.commit()
                db.close()
                print(f"[RECALLIX BACKGROUND WORKER] SUCCESS: Incident {incident_id} successfully retained in Hindsight.")
                break
                
        except Exception as err:
            print(f"[RECALLIX BACKGROUND WORKER] WARNING: Attempt {attempt} failed with error: {str(err)}")
            delay *= 2  # Exponential backoff (15s -> 30s -> 60s)

@router.post("/{incident_id}/verify")
async def verify_incident(
    incident_id: int,
    verification: IncidentVerificationRequest,
    background_tasks: BackgroundTasks,  # Injected cleanly via FastAPI
    db: Session = Depends(get_db),
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    # An explicit negative verification must not erase a previously
    # retained analyst-verified lesson.
    if not verification.verified:
        if incident.memory_retained:
            return {
                "success": True,
                "verified": True,
                "retained": True,
                "incident_id": incident.id,
                "message": (
                    "This incident already has a retained, "
                    "analyst-verified lesson."
                ),
            }

        incident.verified = False
        incident.verified_at = None
        incident.verification_notes = verification.analyst_notes
        incident.memory_retained = False

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Could not save analyst verification status.",
            )

        return {
            "success": True,
            "verified": False,
            "retained": False,
            "incident_id": incident.id,
            "message": "Not verified. No lesson was retained.",
        }

    # Save verification independently before attempting external retention.
    incident.verified = True
    incident.verified_at = datetime.now(timezone.utc)
    incident.verification_notes = verification.analyst_notes

    try:
        db.commit()
        db.refresh(incident)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save analyst verification status.",
        )

    # Do not retain the same lesson again if retention already succeeded.
    if incident.memory_retained:
        return {
            "success": True,
            "verified": True,
            "retained": True,
            "incident_id": incident.id,
            "memory_bank": "security-incident-intelligence",
            "message": "This verified lesson was already retained in Hindsight.",
        }

    lesson = (
        f"RECALLIX VERIFIED INVESTIGATION LESSON. "
        f"Incident ID: {incident.id}. "
        f"Category: {incident.incident_type}. "
        f"Title: {incident.title}. "
        f"Description: {incident.description}. "
        f"Evidence: {'; '.join(incident.evidence or [])}. "
        f"Severity assessed: {incident.severity}. "
        f"Risk score assessed: {incident.risk_score}. "
        f"Indicators: {'; '.join(incident.indicators or [])}. "
        f"Recommended actions: {'; '.join(incident.recommendations or [])}. "
        f"Analyst verification notes: "
        f"{verification.analyst_notes or 'No additional notes.'}. "
        "This outcome was explicitly verified by an analyst."
    )

    from backend.app.database.database import SessionLocal  # Import factory session maker securely

    try:
        retain_result = await retain_verified_lesson(
            content=lesson,
            incident_id=incident.id,
            incident_type=incident.incident_type,
        )

        # Require an explicit successful result before marking retention.
        if not (
            isinstance(retain_result, dict)
            and retain_result.get("success") is True
        ):
            # TRIGGER 1: Trigger background retries if Hindsight explicitly flags a non-success state
            background_tasks.add_task(
                periodic_retention_retry,
                incident_id=incident.id,
                lesson_content=lesson,
                incident_type=incident.incident_type,
                db_session_factory=SessionLocal
            )
            return {
                "success": True,
                "verified": True,
                "retained": False,
                "incident_id": incident.id,
                "message": (
                    "Analyst verification was saved, but Hindsight did not confirm "
                    "instantaneous retention. Automated retry engine has been spawned in the background."
                ),
                "retention": retain_result,
            }

        incident.memory_retained = True
        db.commit()
        db.refresh(incident)

        return {
            "success": True,
            "verified": True,
            "retained": True,
            "incident_id": incident.id,
            "memory_bank": "security-incident-intelligence",
            "message": "Analyst-verified investigation lesson retained in Hindsight.",
            "retention": retain_result,
        }

    except Exception as error:
        db.rollback()

        # TRIGGER 2: Trigger background retries if a physical connection/rate limit exception hits the app
        background_tasks.add_task(
            periodic_retention_retry,
            incident_id=incident.id,
            lesson_content=lesson,
            incident_type=incident.incident_type,
            db_session_factory=SessionLocal
        )

        return {
            "success": True,
            "verified": True,
            "retained": False,
            "incident_id": incident.id,
            "message": (
                "Analyst verification was saved locally, but Hindsight retention "
                "failed due to rate thresholds. Autonomous retry daemon queued."
            ),
            "retention_error": str(error),
        }

@router.get("/")
def get_all_incidents(db: Session = Depends(get_db)):
    incidents = (
        db.query(Incident)
        .order_by(Incident.id.desc())
        .all()
    )

    return {
        "success": True,
        "total": len(incidents),
        "incidents": [
            {
                "id": item.id,
                "title": item.title,
                "incident_type": item.incident_type,
                "severity": item.severity,
                "risk_score": item.risk_score,
                "created_at": item.created_at.isoformat(),
                "memory_used": bool(item.memory_used),
                "verified": bool(item.verified),
                "memory_retained": bool(item.memory_retained),
            }
            for item in incidents
        ],
    }


@router.get("/{incident_id}")
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    historical_context = []
    memory_status = "not_requested"
    memory_error = None

    memory_query = (
        f"Security incident category: {incident.incident_type}. "
        f"Title: {incident.title}. "
        f"Description: {incident.description}. "
        f"Evidence: {'; '.join(incident.evidence or [])}. "
        "Find related historical security investigation lessons. "
        "Exclude the current incident and prioritize other verified investigations."
    )

    try:
        historical_context = await recall_incident_context(memory_query)

        historical_context = _filter_current_incident_memories(
            historical_context,
            incident_id=incident.id,
            title=incident.title,
        )

        memory_status = (
            "recalled" if historical_context else "no_relevant_memories"
        )

    except Exception as error:
        memory_status = "unavailable"
        memory_error = str(error)

    return {
        "success": True,
        "incident": _incident_payload(incident),
        "historical_context": historical_context,
        "memory_status": memory_status,
        "memory_error": memory_error,
        "historical_context_note": (
            "Historical memories are reference material, not proof "
            "of the current incident."
        ),
    }
