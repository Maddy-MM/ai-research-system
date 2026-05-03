import time
import re

from src.logging import get_logger
from src.metrics import (
    PIPELINE_REQUESTS_TOTAL,
    PIPELINE_DURATION_SECONDS,
    PIPELINE_STEP_DURATION_SECONDS,
)
from src.pipeline.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

logger = get_logger(__name__)

def strip_thinking(text: str) -> str:
    # Remove <think>...</think> blocks if present (e.g., in Qwen3 models)
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

def run_research_pipeline(topic: str, request_id: str) -> dict:
    state = {}
    pipeline_start = time.perf_counter()
    logger.info("Pipeline started", extra={"topic": topic, "request_id": request_id})

    # ------------------------------------------------------------------
    # Step 1 — Search Agent
    # ------------------------------------------------------------------
    logger.info("Step 1: Search agent starting", extra={"request_id": request_id})
    step_start = time.perf_counter()

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = strip_thinking(search_result["messages"][-1].content)

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="search").observe(step_duration)
    logger.info("Step 1: Search complete", extra={"request_id": request_id, "duration_s": round(step_duration, 2)})

    # ------------------------------------------------------------------
    # Step 2 — Reader Agent
    # ------------------------------------------------------------------
    logger.info("Step 2: Reader agent starting", extra={"request_id": request_id})
    step_start = time.perf_counter()

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = strip_thinking(reader_result["messages"][-1].content)

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="scrape").observe(step_duration)
    logger.info("Step 2: Scrape complete", extra={"request_id": request_id, "duration_s": round(step_duration, 2)})

    # ------------------------------------------------------------------
    # Step 3 — Writer Chain
    # ------------------------------------------------------------------
    logger.info("Step 3: Writer starting", extra={"request_id": request_id})
    step_start = time.perf_counter()

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    state["report"] = strip_thinking(writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    }))

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="write").observe(step_duration)
    logger.info("Step 3: Report written", extra={"request_id": request_id, "duration_s": round(step_duration, 2)})

    # ------------------------------------------------------------------
    # Step 4 — Critic Chain
    # ------------------------------------------------------------------
    logger.info("Step 4: Critic starting", extra={"request_id": request_id})
    step_start = time.perf_counter()

    state["feedback"] = strip_thinking(critic_chain.invoke({
        "report": state["report"],
    }))

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="critique").observe(step_duration)
    logger.info("Step 4: Critique complete", extra={"request_id": request_id, "duration_s": round(step_duration, 2)})

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    total_duration = time.perf_counter() - pipeline_start
    PIPELINE_DURATION_SECONDS.observe(total_duration)
    PIPELINE_REQUESTS_TOTAL.labels(status="success").inc()
    logger.info(
        "Pipeline complete",
        extra={"request_id": request_id, "total_duration_s": round(total_duration, 2)},
    )

    return state