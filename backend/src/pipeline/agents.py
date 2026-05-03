from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.agents import create_agent

from src.config import get_settings
from src.pipeline.tools import web_search, scrape_url

settings = get_settings()

# ---------------------------------------------------------------------------
# Model
# LLM is instantiated once at module level. All agents and chains share it.
# ---------------------------------------------------------------------------
llm = ChatGroq(
    # model="meta-llama/llama-4-scout-17b-16e-instruct",
    # model="llama-3.3-70b-versatile",
    model="qwen/qwen3-32b",
    temperature=0,
    api_key=settings.GROQ_API_KEY,
)

def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt="You are a research assistant. You MUST call the 'web_search' tool to find information. Never answer from your own knowledge. Always use the tool first before responding.",
    )


def build_reader_agent():
    return create_agent(model=llm, tools=[scrape_url])


writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
    ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
])

writer_chain = writer_prompt | llm | StrOutputParser()


critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()