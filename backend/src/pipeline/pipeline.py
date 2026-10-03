import time

from src.logging import get_logger
from src.metrics import PIPELINE_REQUESTS_TOTAL, PIPELINE_DURATION_SECONDS
from src.pipeline.graph import research_graph

logger = get_logger(__name__)


async def run_research_pipeline(topic: str, request_id: str) -> dict:
    pipeline_start = time.perf_counter()
    logger.info("Pipeline started", extra={"topic": topic, "request_id": request_id})

    result = await research_graph.ainvoke(
        {
            "topic": topic,
            "request_id": request_id,
            "iteration_count": 0,
            "tokens_used": 0,
            "research_results": [],
        }
    )

    total_duration = time.perf_counter() - pipeline_start
    PIPELINE_DURATION_SECONDS.observe(total_duration)
    PIPELINE_REQUESTS_TOTAL.labels(status="success").inc()
    tokens_used = result.get("tokens_used", 0)
    logger.info(
        "Pipeline complete",
        extra={
            "request_id": request_id,
            "total_duration_s": round(total_duration, 2),
            "total_tokens": tokens_used,
        },
    )

    return result


async def stream_research_pipeline(topic: str, request_id: str):
    """
    Yields real-time step execution events from LangGraph state machine.
    Emits events:
      - step_start: when an agent node begins or transitions
      - loop_revision: when critic rejects draft and loops back to planner or writer
      - complete: yields final aggregated state
    """
    pipeline_start = time.perf_counter()
    logger.info("Pipeline streaming started", extra={"topic": topic, "request_id": request_id})

    state_input = {
        "topic": topic,
        "request_id": request_id,
        "iteration_count": 0,
        "tokens_used": 0,
        "research_results": [],
    }

    # Initial event: Planner starting
    yield {
        "event": "step_start",
        "step_index": 0,
        "agent": "planner",
        "message": "Planning focused research questions...",
        "sub_message": "Decomposing inquiry into targeted investigation tracks",
    }

    last_state = dict(state_input)

    try:
        async for chunk in research_graph.astream(state_input, stream_mode="updates"):
            # chunk is a dict of {node_name: update_dict}
            for node_name, node_update in chunk.items():
                if isinstance(node_update, dict):
                    last_state.update(node_update)

                if node_name == "planner":
                    clarifying = node_update.get("clarifying_question")
                    if clarifying:
                        yield {
                            "event": "clarification_needed",
                            "step_index": 0,
                            "agent": "planner",
                            "clarifying_question": clarifying,
                            "message": "Ambiguity detected. Clarification required.",
                        }
                    else:
                        sub_qs = node_update.get("sub_questions", [])
                        count = len(sub_qs)
                        yield {
                            "event": "step_start",
                            "step_index": 1,
                            "agent": "researcher",
                            "message": f"Investigating {count} sub-questions in parallel...",
                            "sub_message": "Dispatching MCP sub-agents across arXiv & Tavily",
                            "sub_questions": sub_qs,
                        }

                elif node_name == "researcher":
                    # Researcher parallel nodes report in
                    yield {
                        "event": "step_start",
                        "step_index": 2,
                        "agent": "writer",
                        "message": "Synthesizing raw findings into draft report...",
                        "sub_message": "Aggregating multi-source evidence and structuring sections",
                    }

                elif node_name == "write":
                    yield {
                        "event": "step_start",
                        "step_index": 3,
                        "agent": "critique",
                        "message": "Evaluating draft and routing revisions...",
                        "sub_message": "Scoring technical rigor, clarity and citation integrity",
                    }

                elif node_name == "critique":
                    critic_score = node_update.get("critic_score", 1.0)
                    issue_type = node_update.get("issue_type", "none")
                    iteration = last_state.get("iteration_count", 1)

                    from src.pipeline.graph import CRITIC_THRESHOLD, MAX_ITERATIONS, TOKEN_BUDGET_PER_RUN
                    tokens = last_state.get("tokens_used", 0)

                    needs_loop = (
                        critic_score < CRITIC_THRESHOLD
                        and iteration < MAX_ITERATIONS
                        and tokens < TOKEN_BUDGET_PER_RUN
                    )

                    if needs_loop:
                        target_step = 0 if issue_type == "missing_info" else 2
                        target_agent = "planner" if issue_type == "missing_info" else "writer"
                        target_msg = (
                            f"Critic score: {int(critic_score * 10)}/10 • Gaps found ➔ Re-planning inquiry (Loop {iteration + 1})"
                            if issue_type == "missing_info"
                            else f"Critic score: {int(critic_score * 10)}/10 • Re-routing to Synthesizer for revision (Loop {iteration + 1})"
                        )
                        yield {
                            "event": "loop_revision",
                            "from_step": 3,
                            "to_step": target_step,
                            "target_agent": target_agent,
                            "critic_score": critic_score,
                            "iteration": iteration,
                            "message": target_msg,
                            "sub_message": f"Iterative self-correction triggered by Critic ({issue_type})",
                        }
                    else:
                        yield {
                            "event": "step_start",
                            "step_index": 4,
                            "agent": "verify",
                            "message": "Independently cross-verifying key claims...",
                            "sub_message": "Running independent fact-checking against external sources",
                        }

                elif node_name == "verify":
                    # Verifier completed
                    pass

        total_duration = time.perf_counter() - pipeline_start
        PIPELINE_DURATION_SECONDS.observe(total_duration)
        PIPELINE_REQUESTS_TOTAL.labels(status="success").inc()

        yield {
            "event": "complete",
            "state": last_state,
            "execution_time_seconds": round(total_duration, 2),
        }

    except Exception as e:
        PIPELINE_REQUESTS_TOTAL.labels(status="error").inc()
        logger.error(
            "Streaming pipeline error",
            extra={"request_id": request_id, "error": str(e)},
        )
        yield {
            "event": "error",
            "error": str(e),
        }

