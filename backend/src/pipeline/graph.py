import asyncio
import time

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from src.config import get_settings
from src.logging import get_logger
from src.metrics import PIPELINE_STEP_DURATION_SECONDS
from src.pipeline.agents import (
    build_researcher_agent,
    build_verifier_agent,
    writer_chain,
    critic_chain,
    planner_chain,
    verifier_chain,
)
from src.pipeline.state import ResearchState
from src.pipeline.utils import strip_thinking, sum_tokens

logger = get_logger(__name__)

CRITIC_THRESHOLD = 0.7
MAX_ITERATIONS = 1
TOKEN_BUDGET_PER_RUN = 30000

_mcp_tools_cache = None
_mcp_lock = asyncio.Lock()


async def _get_mcp_tools():
    global _mcp_tools_cache
    if _mcp_tools_cache is None:
        async with _mcp_lock:
            if _mcp_tools_cache is None:
                settings = get_settings()
                client = MultiServerMCPClient(
                    {
                        "researchmind_tools": {
                            "url": settings.MCP_SERVER_URL,
                            "transport": "streamable_http",
                        },
                    }
                )
                _mcp_tools_cache = await client.get_tools()
    return _mcp_tools_cache


def planner_node(state: ResearchState) -> dict:
    step_start = time.perf_counter()
    logger.info(
        "Step: Planner starting",
        extra={
            "request_id": state["request_id"],
            "iteration": state.get("iteration_count", 0),
        },
    )

    feedback_context = ""
    if state.get("issue_type") == "missing_info" and state.get("feedback"):
        feedback_context = (
            f"A previous draft was critiqued as missing information:\n{state['feedback']}\n\n"
            "Generate sub-questions that specifically fill these gaps — don't repeat ground already covered."
        )

    result = planner_chain.invoke(
        {"topic": state["topic"], "feedback_context": feedback_context}
    )
    plan = result["parsed"]
    raw = result["raw"]
    tokens = (
        raw.usage_metadata.get("total_tokens", 0)
        if getattr(raw, "usage_metadata", None)
        else 0
    )

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="plan").observe(step_duration)
    logger.info(
        "Step: Planner complete",
        extra={
            "request_id": state["request_id"],
            "sub_questions": plan.sub_questions,
            "duration_s": round(step_duration, 2),
        },
    )

    return {
        "sub_questions": plan.sub_questions,
        "clarifying_question": plan.clarifying_question,
        "tokens_used": tokens,
        "agent_timings": {"planner": round(step_duration, 2)},
    }


def route_after_planner(state: ResearchState):
    if state["clarifying_question"]:
        return END
    return [
        Send(
            "researcher",
            {
                "topic": state["topic"],
                "request_id": state["request_id"],
                "sub_question": sq,
            },
        )
        for sq in state["sub_questions"]
    ]


async def researcher_node(state: ResearchState) -> dict:
    sub_question = state["sub_question"]
    step_start = time.perf_counter()
    logger.info(
        "Researcher starting",
        extra={"request_id": state["request_id"], "sub_question": sub_question},
    )

    tools = await _get_mcp_tools()
    researcher_agent = build_researcher_agent(tools)
    result = await researcher_agent.ainvoke(
        {
            "messages": [
                ("user", f"Research this sub-question thoroughly: {sub_question}")
            ]
        }
    )
    content = strip_thinking(result["messages"][-1].content)
    tokens = sum_tokens(result["messages"])

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="research").observe(step_duration)
    logger.info(
        "Researcher complete",
        extra={
            "request_id": state["request_id"],
            "sub_question": sub_question,
            "duration_s": round(step_duration, 2),
        },
    )

    return {
        "research_results": [{"sub_question": sub_question, "content": content}],
        "tokens_used": tokens,
        "research_timings": [{"sub_question": sub_question, "duration_s": round(step_duration, 2)}],
    }


def write_node(state: ResearchState) -> dict:
    step_start = time.perf_counter()
    logger.info(
        "Step: Writer starting",
        extra={
            "request_id": state["request_id"],
            "iteration": state.get("iteration_count", 0),
        },
    )

    research_combined = "\n\n".join(
        f"SUB-QUESTION: {r['sub_question']}\nFINDINGS:\n{r['content']}"
        for r in state["research_results"]
    )

    feedback_context = ""
    if state.get("feedback") and state.get("report"):
        feedback_context = (
            f"\nPREVIOUS DRAFT:\n{state['report']}\n\n"
            f"CRITIQUE & REQUIRED REVISIONS:\n{state['feedback']}\n\n"
            "Please revise the draft above to directly address this critique and ensure all claims are clear and supported."
        )

    response = writer_chain.invoke(
        {
            "topic": state["topic"],
            "research": research_combined,
            "feedback_context": feedback_context,
        }
    )
    tokens = (
        response.usage_metadata.get("total_tokens", 0)
        if getattr(response, "usage_metadata", None)
        else 0
    )

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="write").observe(step_duration)
    logger.info(
        "Step: Report written",
        extra={
            "request_id": state["request_id"],
            "duration_s": round(step_duration, 2),
        },
    )

    research_timings = state.get("research_timings", [])
    max_research_duration = max((rt.get("duration_s", 0) for rt in research_timings), default=0)

    return {
        "report": strip_thinking(response.content),
        "tokens_used": tokens,
        "agent_timings": {
            "researcher": round(max_research_duration, 2),
            "writer": round(step_duration, 2),
        },
    }


def critique_node(state: ResearchState) -> dict:
    step_start = time.perf_counter()
    logger.info("Step: Critic starting", extra={"request_id": state["request_id"]})

    result = critic_chain.invoke({"report": state["report"]})
    verdict = result["parsed"]
    raw = result["raw"]
    tokens = (
        raw.usage_metadata.get("total_tokens", 0)
        if getattr(raw, "usage_metadata", None)
        else 0
    )

    feedback = (
        f"Score: {verdict.score}/1.0\n\n"
        "Strengths:\n" + "\n".join(f"- {s}" for s in verdict.strengths) + "\n\n"
        "Areas to Improve:\n"
        + "\n".join(f"- {a}" for a in verdict.areas_to_improve)
        + "\n\n"
        f"One line verdict:\n{verdict.verdict}"
    )

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="critique").observe(step_duration)
    logger.info(
        "Step: Critique complete",
        extra={
            "request_id": state["request_id"],
            "score": verdict.score,
            "issue_type": verdict.issue_type,
            "duration_s": round(step_duration, 2),
        },
    )

    return {
        "feedback": feedback,
        "critic_score": verdict.score,
        "issue_type": verdict.issue_type,
        "iteration_count": state.get("iteration_count", 0) + 1,
        "tokens_used": tokens,
        "agent_timings": {"critic": round(step_duration, 2)},
    }


async def verify_node(state: ResearchState) -> dict:
    step_start = time.perf_counter()
    logger.info("Step: Verifier starting", extra={"request_id": state["request_id"]})

    research_combined = "\n\n".join(
        f"SUB-QUESTION: {r['sub_question']}\nFINDINGS:\n{r['content']}"
        for r in state["research_results"]
    )

    tools = await _get_mcp_tools()
    verifier_agent = build_verifier_agent(tools)
    agent_result = await verifier_agent.ainvoke(
        {
            "messages": [
                (
                    "user",
                    f"Report to fact-check:\n{state['report']}\n\n"
                    "Pick the 2-3 most load-bearing factual claims and independently verify them "
                    "with your tools. Summarize what you find, including any claim that turns out "
                    "to be wrong or unsupported by an independent source.",
                )
            ]
        }
    )
    independent_findings = strip_thinking(agent_result["messages"][-1].content)
    agent_tokens = sum_tokens(agent_result["messages"])

    combined_research = (
        f"{research_combined}\n\n"
        f"INDEPENDENT VERIFICATION RESEARCH (fresh sources, not the original research above):\n{independent_findings}"
    )

    result = verifier_chain.invoke(
        {"research": combined_research, "report": state["report"]}
    )
    outcome = result["parsed"]
    raw = result["raw"]
    tokens = agent_tokens + (
        raw.usage_metadata.get("total_tokens", 0)
        if getattr(raw, "usage_metadata", None)
        else 0
    )

    total = len(outcome.claims)
    if total == 0:
        summary = "No verifiable factual claims were extracted from the report."
        no_count = 0
        partial_count = 0
    else:
        no_count = sum(1 for c in outcome.claims if c.verdict == "no")
        partial_count = sum(1 for c in outcome.claims if c.verdict == "partial")
        unsupported_lines = "\n".join(
            f"- [{c.verdict}] {c.claim}" for c in outcome.claims if c.verdict != "yes"
        )

        summary = (
            f"{total - no_count - partial_count}/{total} claims fully supported, "
            f"{partial_count} partial, {no_count} unsupported.\n"
            + (
                f"\nFlagged claims:\n{unsupported_lines}"
                if unsupported_lines
                else "\nNo issues found."
            )
        )

    step_duration = time.perf_counter() - step_start
    PIPELINE_STEP_DURATION_SECONDS.labels(step="verify").observe(step_duration)
    logger.info(
        "Step: Verifier complete",
        extra={
            "request_id": state["request_id"],
            "unsupported": no_count,
            "partial": partial_count,
            "total": total,
            "duration_s": round(step_duration, 2),
        },
    )

    return {
        "verification_summary": summary,
        "tokens_used": tokens,
        "agent_timings": {"verifier": round(step_duration, 2)},
    }


def route_after_critic(state: ResearchState) -> str:
    if state["critic_score"] >= CRITIC_THRESHOLD:
        return "end"
    if state["iteration_count"] >= MAX_ITERATIONS:
        return "end"
    if state["tokens_used"] >= TOKEN_BUDGET_PER_RUN:
        return "end"
    if state["issue_type"] == "missing_info":
        return "planner"
    return "write"


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("write", write_node)
    graph.add_node("critique", critique_node)
    graph.add_node("verify", verify_node)

    graph.add_edge(START, "planner")
    graph.add_conditional_edges("planner", route_after_planner, ["researcher", END])
    graph.add_edge("researcher", "write")
    graph.add_edge("write", "critique")
    graph.add_conditional_edges(
        "critique",
        route_after_critic,
        {"planner": "planner", "write": "write", "end": "verify"},
    )
    graph.add_edge("verify", END)

    return graph.compile()


research_graph = build_graph()
