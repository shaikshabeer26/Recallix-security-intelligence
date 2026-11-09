from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text,
)

from backend.app.database.database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(150), nullable=False)
    incident_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)

    evidence = Column(JSON, nullable=False, default=list)

    severity = Column(String(20), nullable=False)
    risk_score = Column(Integer, nullable=False)

    indicators = Column(JSON, nullable=False, default=list)
    risk_factors = Column(JSON, nullable=False, default=list)
    recommendations = Column(JSON, nullable=False, default=list)

    analysis_method = Column(String(150), nullable=False)
    memory_used = Column(Boolean, default=False)

    # Persistent Groq AI investigation report
    llm_analysis = Column(JSON, nullable=True)
    llm_status = Column(String(40), nullable=True)
    llm_model = Column(String(120), nullable=True)
    llm_error = Column(JSON, nullable=True)

    # Analyst verification
    verified = Column(Boolean, nullable=False, default=False)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(Text, nullable=True)

    # Hindsight retention status
    memory_retained = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )