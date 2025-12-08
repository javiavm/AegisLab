"""
FastAPI server for Safety Agent.

Provides REST API endpoints to process safety observations through
the multi-agent pipeline.
"""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from safety_agent.schemas import (
    Observation,
    ObservationPotential,
    ObservationType,
    Hazard,
    ScoredHazard,
    ActionPlan,
)
from safety_agent.orchestrator.pipeline import ObservationPipeline, PipelineResult


def setup_logging():
    """Configure logging to show detailed pipeline output in console."""
    # Create a custom formatter with colors for better readability
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[36m',     # Cyan
            'INFO': '\033[32m',      # Green
            'WARNING': '\033[33m',   # Yellow
            'ERROR': '\033[31m',     # Red
            'CRITICAL': '\033[35m',  # Magenta
            'RESET': '\033[0m',      # Reset
        }

        def format(self, record):
            color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            reset = self.COLORS['RESET']

            # Format the message
            formatted = super().format(record)

            # Add color to the level name
            return f"{color}{formatted}{reset}"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler with colored formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    formatter = ColoredFormatter(
        '%(asctime)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set specific loggers to INFO level
    logging.getLogger('safety_agent').setLevel(logging.INFO)
    logging.getLogger('safety_agent.orchestrator').setLevel(logging.INFO)
    logging.getLogger('safety_agent.agents').setLevel(logging.INFO)

    # Reduce noise from other libraries
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)


# Setup logging on module import
setup_logging()

logger = logging.getLogger(__name__)


# Request/Response models for API
class ObservationRequest(BaseModel):
    """Request model for submitting an observation."""

    site: str = Field(..., min_length=1, description="Site location")
    potential: str = Field(..., description="Observation potential (NEAR_MISS, FIRST_AID, etc.)")
    type: str = Field(..., description="Observation type (UNSAFE_CONDITION, UNSAFE_ACT, etc.)")
    description: str = Field(..., min_length=1, description="Description of the observation")
    trade_category_id: Optional[str] = Field(None, alias="tradeCategoryId")
    trade_partner_id: Optional[str] = Field(None, alias="tradePartnerId")
    photo_id: Optional[str] = Field(None, alias="photoId")
    observed_at: Optional[datetime] = Field(None, alias="observedAt")

    class Config:
        populate_by_name = True


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


# Map frontend potential values to backend enum
POTENTIAL_MAPPING = {
    "NEAR_MISS": ObservationPotential.NEAR_MISS,
    "SAFE_PRACTICE": ObservationPotential.NEAR_MISS,  # Map to closest
    "AT_RISK_BEHAVIOR": ObservationPotential.NEAR_MISS,
    "HAZARD": ObservationPotential.FIRST_AID,
    "OTHER": ObservationPotential.NEAR_MISS,
    "FIRST_AID": ObservationPotential.FIRST_AID,
    "MEDICAL_TREATMENT": ObservationPotential.MEDICAL_TREATMENT,
    "LOST_TIME": ObservationPotential.LOST_TIME,
    "FATALITY": ObservationPotential.FATALITY,
}

# Map frontend type values to backend enum
TYPE_MAPPING = {
    "AREA_FOR_IMPROVEMENT": ObservationType.AREA_FOR_IMPROVEMENT,
    "POSITIVE_OBSERVATION": ObservationType.POSITIVE_OBSERVATION,
    "UNSAFE_CONDITION": ObservationType.UNSAFE_CONDITION,
    "UNSAFE_ACT": ObservationType.UNSAFE_ACT,
    "ENVIRONMENTAL": ObservationType.ENVIRONMENTAL,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Safety Agent API starting up...")
    yield
    logger.info("Safety Agent API shutting down...")


app = FastAPI(
    title="Safety Agent API",
    description="AI-powered safety observation pipeline with multi-agent architecture",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Check API health status."""
    return HealthResponse(status="healthy", version="0.1.0")


@app.post("/api/observations/analyze", response_model=PipelineResult)
async def analyze_observation(request: ObservationRequest):
    """
    Process a safety observation through the full AI pipeline.

    The pipeline runs three agents in sequence:
    1. Risk Analyzer - Detects hazards from the observation
    2. Score Manager - Scores hazards using risk matrix
    3. Action Planner - Generates OSHA-compliant action plans

    Returns the complete pipeline result with all hazards, scores, and action plans.
    """
    logger.info("")
    logger.info("*" * 80)
    logger.info("API REQUEST RECEIVED: POST /api/observations/analyze")
    logger.info("*" * 80)
    logger.info(f"Request Data:")
    logger.info(f"  - Site: {request.site}")
    logger.info(f"  - Potential: {request.potential}")
    logger.info(f"  - Type: {request.type}")
    logger.info(f"  - Description: {request.description[:100]}...")
    logger.info("*" * 80)

    try:
        # Map potential to enum
        potential = POTENTIAL_MAPPING.get(request.potential)
        if not potential:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid potential value: {request.potential}"
            )

        # Map type to enum
        obs_type = TYPE_MAPPING.get(request.type)
        if not obs_type:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid type value: {request.type}"
            )

        # Create observation object
        observation = Observation(
            id=str(uuid4()),
            observed_at=request.observed_at or datetime.now(),
            site=request.site,
            potential=potential,
            type=obs_type,
            description=request.description,
            trade_category_id=request.trade_category_id,
            trade_partner_id=request.trade_partner_id,
            photo_id=request.photo_id,
        )

        logger.info(f"Created Observation object with ID: {observation.id}")
        logger.info(f"Mapped potential '{request.potential}' -> {potential}")
        logger.info(f"Mapped type '{request.type}' -> {obs_type}")

        # Run the pipeline
        logger.info("")
        logger.info("Invoking ObservationPipeline...")
        pipeline = ObservationPipeline()
        result = pipeline.run(observation)

        if not result.success:
            logger.error(f"Pipeline failed: {result.error}")
            raise HTTPException(status_code=500, detail=result.error)

        logger.info("")
        logger.info("*" * 80)
        logger.info("API RESPONSE READY")
        logger.info("*" * 80)
        logger.info(f"Returning to frontend:")
        logger.info(f"  - Hazards: {len(result.hazards)}")
        logger.info(f"  - Scored Hazards: {len(result.scored_hazards)}")
        logger.info(f"  - Action Plans: {len(result.action_plans)}")
        logger.info(f"  - Success: {result.success}")
        logger.info("*" * 80)
        logger.info("")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error processing observation")
        raise HTTPException(status_code=500, detail=str(e))


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server using uvicorn."""
    import uvicorn
    uvicorn.run(
        "safety_agent.api.server:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    run_server(reload=True)
