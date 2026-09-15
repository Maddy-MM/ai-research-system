import ast
import operator as op

import concurrent.futures
import re

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


_STOP_WORDS = {
    "how", "what", "which", "why", "when", "where", "who", "do", "does", "did",
    "is", "are", "was", "were", "the", "a", "an", "and", "or", "of", "in", "on",
    "for", "with", "to", "at", "by", "from", "including", "can", "affect",
}


def _clean_arxiv_query(query: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", " ", query)
    words = cleaned.split()
    meaningful = [w for w in words if w.lower() not in _STOP_WORDS]
    keywords = meaningful[:5] if meaningful else words[:5]
    return " ".join(keywords)


class _TimeoutHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, *args, timeout=5.0, **kwargs):
        self.timeout = timeout
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


def _fetch_arxiv(query_str: str) -> list[str]:
    client = arxiv.Client(page_size=3, delay_seconds=1.0, num_retries=0)
    adapter = _TimeoutHTTPAdapter(timeout=5.0)
    client._session.mount("https://", adapter)
    client._session.mount("http://", adapter)
    search = arxiv.Search(
        query=query_str, max_results=3, sort_by=arxiv.SortCriterion.Relevance
    )
    return [
        f"Title: {r.title}\nURL: {r.entry_id}\nSummary: {r.summary[:500]}"
        for r in client.results(search)
    ]


def arxiv_search_impl(query: str) -> str:
    logger.info("Running arXiv search", extra={"query": query})
    clean_query = _clean_arxiv_query(query)

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_fetch_arxiv, clean_query or query)
            output = future.result(timeout=8.0)
            if output:
                return "\n-----\n".join(output)
            logger.info(
                "arXiv returned 0 results, falling back to academic web search",
                extra={"query": query, "clean_query": clean_query},
            )
    except Exception as e:
        logger.warning(
            "arXiv search failed or timed out, falling back to academic web search",
            extra={"query": query, "clean_query": clean_query, "error": str(e)},
        )

    # Fallback to Tavily academic search
    fallback_query = f"{clean_query or query} research paper arxiv"
    try:
        return web_search_impl(fallback_query)
    except Exception as e:
        logger.error(
            "Academic fallback search failed",
            extra={"query": fallback_query, "error": str(e)},
        )
        return "No academic research results found."


_ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
    ast.FloorDiv: op.floordiv,
}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](
            _eval_node(node.left), _eval_node(node.right)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


def calculator_impl(expression: str) -> str:
    logger.info("Running calculator", extra={"expression": expression})
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_eval_node(tree.body))
    except Exception as e:
        logger.error(
            "Calculator failed", extra={"expression": expression, "error": str(e)}
        )
        return f"Could not evaluate expression: {str(e)}"
