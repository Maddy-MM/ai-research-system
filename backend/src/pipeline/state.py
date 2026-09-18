from typing import TypedDict, Annotated, Literal
import operator


class ResearchState(TypedDict):
    topic: str
    request_id: str

    sub_questions: list[str]
    clarifying_question: str

    sub_question: str
    research_results: Annotated[list[dict], operator.add]

    report: str
    feedback: str
    verification_summary: str
    critic_score: float
    issue_type: Literal["missing_info", "unclear_writing", "unsupported_claims", "none"]
    iteration_count: int
    tokens_used: Annotated[int, operator.add]
    agent_timings: Annotated[dict[str, float], operator.or_]
    research_timings: Annotated[list[dict], operator.add]
