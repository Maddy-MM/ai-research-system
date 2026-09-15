from mcp.server.fastmcp import FastMCP

from src.config import get_settings
from src.mcp_server.tools_impl import (
    web_search_impl,
    scrape_url_impl,
    arxiv_search_impl,
    calculator_impl,
)

settings = get_settings()
mcp_server = FastMCP(
    "researchmind-tools", host=settings.MCP_HOST, port=settings.MCP_PORT
)


@mcp_server.tool()
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns titles, URLs and snippets."""
    return web_search_impl(query)


@mcp_server.tool()
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    return scrape_url_impl(url)


@mcp_server.tool()
def arxiv_search(query: str) -> str:
    """Search academic research papers (via arXiv or academic fallback) using 3-5 concise keywords (e.g. 'data center energy efficiency')."""
    return arxiv_search_impl(query)


@mcp_server.tool()
def calculator(expression: str) -> str:
    """Evaluate a numeric arithmetic expression, e.g. '(3 + 4) * 2 / 7'. Use for any sub-question requiring computation."""
    return calculator_impl(expression)


if __name__ == "__main__":
    mcp_server.run(transport="streamable-http")
