from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.incidents import router as incidents_router
from backend.app.database.database import (
    Base,
    engine,
    migrate_incident_table,
)
from backend.app.models.incident import Incident


app = FastAPI(
    title="RECALLIX AI Security Intelligence",
    description="AI-powered security incident investigation with persistent memory.",
    version="1.0.0",
)


# Initialize database tables
Base.metadata.create_all(bind=engine)

# Apply migrations to existing database
migrate_incident_table()


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register API routes
app.include_router(incidents_router)
@app.get("/")
def root():
    return {
        "success": True,
        "message": "RECALLIX AI Security Intelligence API is running.",
        "version": "1.0.0",
    }