import ast
import operator as op

import arxiv
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient

from src.config import get_settings
from src.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()

tavily = TavilyClient(api_key=settings.TAVILY_API_KEY)


def web_search_impl(query: str) -> str:
    logger.info("Running web search", extra={"query": query})
    search_results = tavily.search(query=query, max_results=3)
    output = [
        f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content']}"
        for r in search_results["results"]
    ]
    return "\n-----\n".join(output)


def scrape_url_impl(url: str) -> str:
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


def arxiv_search_impl(query: str) -> str:
    logger.info("Running arXiv search", extra={"query": query})
    try:
        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=3, sort_by=arxiv.SortCriterion.Relevance)
        output = [
            f"Title: {r.title}\nURL: {r.entry_id}\nSummary: {r.summary[:500]}"
            for r in client.results(search)
        ]
        return "\n-----\n".join(output) if output else "No arXiv results found."
    except Exception as e:
        logger.error("arXiv search failed", extra={"query": query, "error": str(e)})
        return f"Could not search arXiv: {str(e)}"


_ALLOWED_OPS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
    ast.Pow: op.pow, ast.USub: op.neg, ast.Mod: op.mod, ast.FloorDiv: op.floordiv,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


def calculator_impl(expression: str) -> str:
    logger.info("Running calculator", extra={"expression": expression})
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
    except Exception as e:
        logger.error("Calculator failed", extra={"expression": expression, "error": str(e)})
        return f"Could not evaluate expression: {str(e)}"