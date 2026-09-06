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
    report: str | None = None
    feedback: str | None = None
    verification: str | None = None
    clarifying_question: str | None = None
    critic_score: float | None = None
    iteration_count: int | None = None
    tokens_used: int | None = None
    sub_questions: list[str] | None = None


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
        state = await run_research_pipeline(
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
        report=state.get("report"),
        feedback=state.get("feedback"),
        verification=state.get("verification_summary"),
        clarifying_question=state.get("clarifying_question") or None,
        critic_score=state.get("critic_score"),
        iteration_count=state.get("iteration_count"),
        tokens_used=state.get("tokens_used"),
        sub_questions=state.get("sub_questions"),
    )