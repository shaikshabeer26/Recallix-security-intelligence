
import os
from pathlib import Path

from dotenv import load_dotenv
from hindsight_client import Hindsight


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

BACKEND_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(BACKEND_ENV)

API_KEY = os.getenv("HINDSIGHT_API_KEY")

BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "http://127.0.0.1:8889",
)

BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "security-incident-intelligence",
)

_client = None


# ---------------------------------------------------------
# CLIENT
# ---------------------------------------------------------

def get_client():
    global _client

    if _client is None:
        _client = Hindsight(
            base_url=BASE_URL,
            api_key=API_KEY or None,
            timeout=90.0,
        )

    return _client


# ---------------------------------------------------------
# SAFE RESPONSE HELPERS
# ---------------------------------------------------------

def _get_value(obj, key, default=None):
    """Read a field from either a dictionary or SDK object."""

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def _as_dict(value):
    """Convert metadata into a safe dictionary."""

    if isinstance(value, dict):
        return value

    if hasattr(value, "model_dump"):
        converted = value.model_dump()
        return converted if isinstance(converted, dict) else {}

    return {}


def _as_list(value):
    """Convert optional collection fields into lists."""

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return []


def _serialize_memory(memory):
    """Serialize a Hindsight memory while preserving provenance."""

    metadata = _as_dict(
        _get_value(memory, "metadata", {})
    )

    tags = _as_list(
        _get_value(memory, "tags", [])
    )

    return {
        "id": _get_value(memory, "id"),
        "text": _get_value(memory, "text", "") or "",
        "type": _get_value(memory, "type"),
        "context": _get_value(memory, "context"),
        "metadata": metadata,
        "tags": tags,
        "entities": _as_list(
            _get_value(memory, "entities", [])
        ),
        "occurred_start": _get_value(
            memory, "occurred_start"
        ),
        "occurred_end": _get_value(
            memory, "occurred_end"
        ),
        "mentioned_at": _get_value(
            memory, "mentioned_at"
        ),
        "document_id": _get_value(
            memory, "document_id"
        ),
        "chunk_id": _get_value(
            memory, "chunk_id"
        ),
        "source_fact_ids": _as_list(
            _get_value(memory, "source_fact_ids", [])
        ),
        "source_facts": [],
    }


# ---------------------------------------------------------
# MEMORY DEDUPLICATION
# ---------------------------------------------------------

def _deduplicate_memories(memories):
    """
    Remove exact duplicate text while preserving Hindsight
    ranking and the first occurrence.

    Consolidated observation preference is handled by Hindsight
    itself during recall.
    """

    unique_memories = []
    seen_text = set()
    seen_ids = set()

    for memory in memories:
        text = " ".join(
            (memory.get("text") or "").lower().split()
        )

        memory_id = memory.get("id")

        if not text:
            continue

        if memory_id and memory_id in seen_ids:
            continue

        if text in seen_text:
            continue

        seen_text.add(text)

        if memory_id:
            seen_ids.add(memory_id)

        unique_memories.append(memory)

    return unique_memories


# ---------------------------------------------------------
# RECALL
# ---------------------------------------------------------

async def recall_incident_context(query: str) -> list[dict]:
    """
    Recall relevant historical memories and attach the original
    facts that contributed to each consolidated observation.
    """

    client = get_client()

    result = await client.arecall(
        bank_id=BANK_ID,
        query=query,
        types=[
            "world",
            "experience",
            "observation",
        ],
        max_tokens=2500,
        budget="mid",
        include_entities=False,
        include_source_facts=True,
        max_source_facts_tokens=2500,
        prefer_observations=True,
    )

    # Serialize the main recalled memories.
    memories = [
        _serialize_memory(memory)
        for memory in (result.results or [])
    ]

    # Hindsight returns source facts in a dictionary keyed by fact ID.
    source_fact_map = _get_value(result, "source_facts", {}) or {}

    # Attach the original facts to the observation that references them.
    for memory in memories:
        attached_facts = []

        for fact_id in memory.get("source_fact_ids", []):
            source_fact = (
                source_fact_map.get(fact_id)
                if isinstance(source_fact_map, dict)
                else None
            )

            if source_fact is not None:
                attached_facts.append(
                    _serialize_memory(source_fact)
                )

        memory["source_facts"] = attached_facts

    # Remove exact duplicate main memories without losing provenance.
    unique_memories = []
    seen_text = set()

    for memory in memories:
        normalized_text = " ".join(
            (memory.get("text") or "").lower().split()
        )

        if not normalized_text or normalized_text in seen_text:
            continue

        seen_text.add(normalized_text)
        unique_memories.append(memory)

    return unique_memories[:8]


# ---------------------------------------------------------
# REFLECT
# ---------------------------------------------------------

async def reflect_on_incident(query: str) -> dict:
    """Generate a contextual reflection using Hindsight."""

    client = get_client()

    response = await client.areflect(
        bank_id=BANK_ID,
        query=query,
    )

    return {
        "text": response.text,
        "based_on": [
            str(source)
            for source in (response.based_on or [])
        ],
    }


# ---------------------------------------------------------
# RETAIN VERIFIED LESSON
# ---------------------------------------------------------

# async def retain_verified_lesson(
#     content: str,
#     incident_id: int,
#     incident_type: str,
# ) -> dict:
#     """
#     Retain an investigation lesson only after analyst
#     verification has been completed by the API route.
#     """

#     client = get_client()

#     result = await client.aretain(
#         bank_id=BANK_ID,
#         content=content,
#         context="RECALLIX analyst-verified security investigation",
#         metadata={
#             "source": "RECALLIX",
#             "incident_id": str(incident_id),
#             "incident_type": incident_type,
#             "verification_status": "analyst_verified",
#         },
#         tags=[
#             "source:recallix",
#             "status:analyst_verified",
#             f"type:{incident_type}",
#         ],
#     )

#     return {
#         "success": True,
#         "incident_id": incident_id,
#         "result": str(result),
#     }

async def retain_verified_lesson(
    content: str,
    incident_id: int,
    incident_type: str,
) -> dict:
    """
    Retain an analyst-verified investigation lesson.

    A stable document ID makes retries idempotent:
    the same incident updates its existing Hindsight document.
    """

    client = get_client()

    document_id = f"recallix-verified-incident-{incident_id}"

    result = await client.aretain(
        bank_id=BANK_ID,
        content=content,
        context="RECALLIX analyst-verified security investigation",
        document_id=document_id,
        update_mode="replace",
        metadata={
            "source": "RECALLIX",
            "incident_id": str(incident_id),
            "incident_type": incident_type,
            "verification_status": "analyst_verified",
        },
        tags=[
            "source:recallix",
            "status:analyst_verified",
            f"type:{incident_type}",
        ],
    )

    return {
        "success": True,
        "incident_id": incident_id,
        "document_id": document_id,
        "result": str(result),
    }



# ---------------------------------------------------------
# STATUS
# ---------------------------------------------------------

def hindsight_status() -> dict:
    return {
        "configured": True,
        "base_url": BASE_URL,
        "bank_id": BANK_ID,
    }
