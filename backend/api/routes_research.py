import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.auth import TokenData, get_current_user
from src.logging import get_logger
from src.metrics import PIPELINE_REQUESTS_TOTAL
from src.pipeline.pipeline import run_research_pipeline

router = APIRouter(prefix="/research", tags=["Research"])
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Schemas — define the shape of request and response bodies
# ---------------------------------------------------------------------------

class ResearchRequest(BaseModel):
    topic: str


class ResearchResponse(BaseModel):
    request_id: str
    topic: str
    report: str
    feedback: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.post("/run", response_model=ResearchResponse)
async def run_research(
    request: ResearchRequest,
    current_user: TokenData = Depends(get_current_user),
):

    # A unique ID per request — lets you grep logs for a full trace
    request_id = str(uuid.uuid4())

    logger.info(
        "Research request received",
        extra={"topic": request.topic, "user": current_user.username, "request_id": request_id},
    )

    try:
        # sync call inside an async route — fine for a pipeline this heavy
        # since LLM calls dominate the time, not the event loop
        state = run_research_pipeline(
            topic=request.topic,
            request_id=request_id,
        )
    except Exception as e:
        PIPELINE_REQUESTS_TOTAL.labels(status="error").inc()
        logger.error(
            "Pipeline failed",
            extra={"request_id": request_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Pipeline failed: {str(e)}",
        )

    return ResearchResponse(
        request_id=request_id,
        topic=request.topic,
        report=state["report"],
        feedback=state["feedback"],
    )