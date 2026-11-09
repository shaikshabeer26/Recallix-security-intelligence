from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


# Database configuration
BACKEND_DIR = Path(__file__).resolve().parents[2]
DATABASE_PATH = BACKEND_DIR / "recallix.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# Database dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Safely migrate existing SQLite database
def migrate_incident_table():
    """
    Add missing columns without deleting existing incident records.
    Safe to execute repeatedly.
    """
    inspector = inspect(engine)

    if not inspector.has_table("incidents"):
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("incidents")
    }

    migrations = {
        "verified": (
            "ALTER TABLE incidents "
            "ADD COLUMN verified BOOLEAN NOT NULL DEFAULT 0"
        ),
        "verified_at": (
            "ALTER TABLE incidents ADD COLUMN verified_at DATETIME"
        ),
        "verification_notes": (
            "ALTER TABLE incidents ADD COLUMN verification_notes TEXT"
        ),
        "memory_retained": (
            "ALTER TABLE incidents "
            "ADD COLUMN memory_retained BOOLEAN NOT NULL DEFAULT 0"
        ),
        "llm_analysis": (
            "ALTER TABLE incidents ADD COLUMN llm_analysis JSON"
        ),
        "llm_status": (
            "ALTER TABLE incidents ADD COLUMN llm_status VARCHAR(40)"
        ),
        "llm_model": (
            "ALTER TABLE incidents ADD COLUMN llm_model VARCHAR(120)"
        ),
        "llm_error": (
            "ALTER TABLE incidents ADD COLUMN llm_error JSON"
        ),
    }

    with engine.begin() as connection:
        for column_name, migration_sql in migrations.items():
            if column_name not in existing_columns:
                connection.execute(text(migration_sql))
                print(f"Database migration: added {column_name}")