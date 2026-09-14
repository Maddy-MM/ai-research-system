import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.database import User, get_db
from src.models import ResearchReport
from src.logging import get_logger
from src.metrics import PIPELINE_REQUESTS_TOTAL
from src.pipeline.pipeline import run_research_pipeline

router = APIRouter(prefix="/research", tags=["Research"])
logger = get_logger(__name__)


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


@router.post("/run", response_model=ResearchResponse)
async def run_research(
    request: ResearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    request_id = str(uuid.uuid4())

    logger.info(
        "Research request received",
        extra={
            "topic": request.topic,
            "user": current_user.username,
            "request_id": request_id,
        },
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

    response_data = ResearchResponse(
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

    try:
        db_report = ResearchReport(
            request_id=request_id,
            user_id=current_user.id,
            username=current_user.username,
            topic=request.topic,
            report=response_data.report,
            feedback=response_data.feedback,
            verification=response_data.verification,
            clarifying_question=response_data.clarifying_question,
            critic_score=response_data.critic_score,
            iteration_count=response_data.iteration_count,
            tokens_used=response_data.tokens_used,
        )
        db_report.sub_questions = response_data.sub_questions
        db.add(db_report)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(
            "Failed to save report to database",
            extra={"error": str(e), "request_id": request_id},
        )

    return response_data


@router.get("/history", response_model=list[ResearchResponse])
def get_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reports = (
        db.query(ResearchReport)
        .filter(
            (ResearchReport.user_id == current_user.id)
            | (ResearchReport.username == current_user.username)
        )
        .order_by(ResearchReport.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        ResearchResponse(
            request_id=r.request_id,
            topic=r.topic,
            report=r.report,
            feedback=r.feedback,
            verification=r.verification,
            clarifying_question=r.clarifying_question,
            critic_score=r.critic_score,
            iteration_count=r.iteration_count,
            tokens_used=r.tokens_used,
            sub_questions=r.sub_questions,
        )
        for r in reports
    ]


@router.delete("/history")
def clear_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        db.query(ResearchReport).filter(
            (ResearchReport.user_id == current_user.id)
            | (ResearchReport.username == current_user.username)
        ).delete()
        db.commit()
        return {"status": "ok", "message": "History cleared"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not clear history: {str(e)}",
        )


@router.delete("/history/{request_id}")
def delete_history_item(
    request_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        deleted_count = (
            db.query(ResearchReport)
            .filter(
                (ResearchReport.user_id == current_user.id)
                | (ResearchReport.username == current_user.username),
                ResearchReport.request_id == request_id,
            )
            .delete()
        )
        db.commit()
        if deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found",
            )
        return {"status": "ok", "message": f"Report {request_id} deleted"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete report: {str(e)}",
        )
