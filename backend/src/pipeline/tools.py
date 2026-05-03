import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from tavily import TavilyClient

from src.config import get_settings
from src.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)

# -------------------------
# WEB SEARCH TOOL: TAVILY
# -------------------------

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns titles, URLs and snippets."""

    logger.info("Running web search", extra={"query": query})

    search_results = tavily.search(query=query, max_results=3)

    output = []
    for result in search_results["results"]:
        output.append(
            f"Title: {result['title']}\nURL: {result['url']}\nSnippet: {result['content']}"
        )

    return "\n-----\n".join(output)


# -------------------------
# MOCK TOOL: START
# -------------------------

# @tool
# def web_search(query: str) -> str:
#     """Search the web for recent and reliable information on a topic. Returns titles, URLs and snippets."""

#     logger.info("Running web search (MOCK)", extra={"query": query})

#     return (
#         "Title: Mock Result 1 — AI Research Breakthroughs\n"
#         "URL: https://example.com/ai-research\n"
#         "Snippet: Scientists have made significant progress in large language models, "
#         "with new architectures showing 40% efficiency gains over previous baselines.\n"
#         "-----\n"
#         "Title: Mock Result 2 — Industry Adoption Trends\n"
#         "URL: https://example.com/industry-trends\n"
#         "Snippet: Enterprise adoption of AI tools has accelerated in 2025, "
#         "with over 60% of Fortune 500 companies integrating LLM-based workflows.\n"
#         "-----\n"
#         "Title: Mock Result 3 — Open Source Landscape\n"
#         "URL: https://example.com/open-source\n"
#         "Snippet: The open source AI ecosystem continues to grow, with models like "
#         "LLaMA and Mistral closing the gap with proprietary offerings on key benchmarks."
#     )

# -------------------------
# MOCK TOOL: END
# -------------------------


# -------------------------
# WEB SCRAPING TOOL: bs4
# -------------------------

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""

    logger.info("Scraping URL", extra={"url": url})

    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)[:3000]
        logger.info("Scrape successful", extra={"url": url, "chars": len(text)})
        return text

    except Exception as e:
        logger.error("Scrape failed", extra={"url": url, "error": str(e)})
        return f"Could not scrape URL: {str(e)}"