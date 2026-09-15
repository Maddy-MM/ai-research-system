from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import create_agent
from pydantic import BaseModel, Field

from src.config import get_settings

settings = get_settings()

model_name = settings.OPENAI_MODEL.lower()

llm_kwargs = {
    "model": settings.OPENAI_MODEL,
    "temperature": 0,
    "api_key": settings.OPENAI_API_KEY,
    "max_retries": 5,
}
if settings.OPENAI_REASONING_EFFORT:
    if settings.OPENAI_REASONING_EFFORT == "none" and "nano" in model_name:
        pass
    else:
        llm_kwargs["reasoning_effort"] = settings.OPENAI_REASONING_EFFORT

llm = ChatOpenAI(**llm_kwargs)

tool_llm_kwargs = {
    "model": settings.OPENAI_MODEL,
    "temperature": 0,
    "api_key": settings.OPENAI_API_KEY,
    "max_retries": 5,
}
if "luna" in model_name:
    tool_llm_kwargs["reasoning_effort"] = "none"
elif settings.OPENAI_REASONING_EFFORT and settings.OPENAI_REASONING_EFFORT != "none":
    tool_llm_kwargs["reasoning_effort"] = settings.OPENAI_REASONING_EFFORT
elif settings.OPENAI_REASONING_EFFORT == "none" and "nano" not in model_name:
    tool_llm_kwargs["reasoning_effort"] = "none"

tool_llm = ChatOpenAI(**tool_llm_kwargs)


def build_researcher_agent(tools):
    tool_names = ", ".join(f"`{t.name}`" for t in tools)
    return create_agent(
        model=tool_llm,
        tools=tools,
        system_prompt=(
            f"You are a focused research assistant with access to EXACTLY these tools: {tool_names}. "
            "You must call tools using these exact names — never invent, abbreviate, or guess a "
            "different name. Call at most 1 or 2 relevant tools (e.g. web_search or arxiv_search) "
            "to gather facts. Use concise search queries (3-5 keywords, no full sentences). "
            "Do not enter multi-step search loops. Summarize key findings concisely once retrieved."
        ),
    )


def build_verifier_agent(tools):
    tool_names = ", ".join(f"`{t.name}`" for t in tools)
    return create_agent(
        model=tool_llm,
        tools=tools,
        system_prompt=(
            f"You are an independent fact-checker with access to EXACTLY these tools: {tool_names}. "
            "You must call tools using these exact names — never invent, abbreviate, or guess a "
            "different name. Given a report, pick the 1-2 most critical factual claims. Use at most 1 targeted "
            "web_search or arxiv_search (using 3-5 concise keywords) to verify them quickly. Do not execute recursive search loops. "
            "Briefly summarize what was confirmed or unsupported."
        ),
    )


writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert research writer. Write clear, structured and insightful reports.",
        ),
        (
            "human",
            """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}
{feedback_context}
Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional.""",
        ),
    ]
)

writer_chain = writer_prompt | llm


class CriticVerdict(BaseModel):
    score: float = Field(description="Overall quality score from 0.0 to 1.0")
    issue_type: Literal[
        "missing_info", "unclear_writing", "unsupported_claims", "none"
    ] = Field(
        description="The report's single biggest issue, or 'none' if it has no significant issue"
    )
    strengths: list[str] = Field(description="What the report does well")
    areas_to_improve: list[str] = Field(description="Specific weaknesses to address")
    verdict: str = Field(description="One-line overall verdict")


critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp and constructive research critic. Be honest and specific.",
        ),
        (
            "human",
            """Review the research report below and evaluate it strictly.

Report:
{report}

Score it from 0.0 to 1.0. Set issue_type to the ONE label that best describes the report's
biggest weakness: 'missing_info' (gaps in coverage — needs more research), 'unclear_writing'
(structure/clarity problems — needs a rewrite), 'unsupported_claims' (claims without grounding —
needs a rewrite), or 'none' if there's no significant issue.""",
        ),
    ]
)

critic_chain = critic_prompt | llm.with_structured_output(
    CriticVerdict, include_raw=True
)


class PlannerOutput(BaseModel):
    sub_questions: list[str] = Field(
        description="Focused sub-questions that together cover the topic. "
        "Use exactly 1 for a simple factual query; 2-4 for a multi-faceted or comparison topic. "
        "Leave empty if clarifying_question is set instead."
    )
    clarifying_question: str = Field(
        default="",
        description="A question to ask the user before researching, ONLY if the topic is too "
        "ambiguous to research meaningfully as stated. Leave as empty string otherwise.",
    )


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a research planner. Break the user's topic into 2 to 3 sharply focused "
            "sub-questions whose answers together make a complete report. Keep sub-questions concise "
            "and targeted so they can be researched effectively.",
        ),
        ("human", "Topic: {topic}\n\n{feedback_context}"),
    ]
)

planner_chain = planner_prompt | llm.with_structured_output(
    PlannerOutput, include_raw=True
)


class ClaimVerdict(BaseModel):
    claim: str = Field(
        description="The factual claim from the report, quoted or closely paraphrased"
    )
    verdict: Literal["yes", "no", "partial"] = Field(
        description="'yes' if the research content fully supports this claim, 'no' if it's "
        "unsupported or fabricated, 'partial' if only loosely or partially supported"
    )


class VerificationOutput(BaseModel):
    claims: list[ClaimVerdict] = Field(
        description="Every distinct factual claim made in the report, each evaluated against the research content"
    )


verifier_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a rigorous fact-checker. You will be given research content (the ground "
            "truth this report is supposed to be grounded in) and a report written from it. "
            "Identify every distinct factual claim in the report and verdict whether the research "
            "content actually supports it. Be strict — a claim that sounds plausible but isn't "
            "traceable to the research content is 'no', not 'yes'.",
        ),
        (
            "human",
            "RESEARCH CONTENT (ground truth):\n{research}\n\nREPORT TO VERIFY:\n{report}",
        ),
    ]
)

verifier_chain = verifier_prompt | llm.with_structured_output(
    VerificationOutput, include_raw=True
)
