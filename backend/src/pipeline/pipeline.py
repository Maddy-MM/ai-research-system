import time

from src.logging import get_logger
from src.metrics import PIPELINE_REQUESTS_TOTAL, PIPELINE_DURATION_SECONDS
from src.pipeline.graph import research_graph

logger = get_logger(__name__)


async def run_research_pipeline(topic: str, request_id: str) -> dict:
    pipeline_start = time.perf_counter()
    logger.info("Pipeline started", extra={"topic": topic, "request_id": request_id})

    result = await research_graph.ainvoke({
        "topic": topic,
        "request_id": request_id,
        "iteration_count": 0,
        "tokens_used": 0,
        "research_results": [],
    })

    total_duration = time.perf_counter() - pipeline_start
    PIPELINE_DURATION_SECONDS.observe(total_duration)
    PIPELINE_REQUESTS_TOTAL.labels(status="success").inc()
    tokens_used = result.get("tokens_used", 0)
    logger.info(
        "Pipeline complete",
        extra={"request_id": request_id, "total_duration_s": round(total_duration, 2), "total_tokens": tokens_used},
    )

    return result