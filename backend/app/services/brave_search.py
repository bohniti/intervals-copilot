"""
Brave Search API client for route validation and enrichment.
Docs: https://api.search.brave.com/app/documentation/web-search/get-started

Strategy: try preferred climbing databases first (thecrag.com, bergsteigen.com,
mountainproject.com) via site: operators. Fall back to an unrestricted search if
fewer than MIN_SITE_RESULTS results come back from the restricted query.
"""

from dataclasses import dataclass
import httpx
from app.config import get_settings

settings = get_settings()

SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"

# Preferred climbing route databases — checked before falling back to open web
CLIMBING_SITES: list[str] = [
    "thecrag.com",
    "bergsteigen.com",
    "mountainproject.com",
]

# If fewer than this many results come back from site-restricted search,
# run a second open-web search and merge the results.
MIN_SITE_RESULTS = 2


@dataclass
class SearchResult:
    title: str
    url: str
    description: str


async def _do_search(query: str, count: int) -> list[SearchResult]:
    """Execute a single Brave Search request and return parsed results."""
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": settings.brave_api_key,
    }
    params = {"q": query, "count": count, "safesearch": "moderate"}

    async with httpx.AsyncClient(timeout=8.0) as client:
        resp = await client.get(SEARCH_URL, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

    return [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            description=r.get("description", ""),
        )
        for r in data.get("web", {}).get("results", [])
    ]


async def web_search(
    query: str,
    count: int = 5,
    preferred_sites: list[str] | None = None,
) -> list[SearchResult]:
    """
    Search the web via Brave Search API.

    If ``preferred_sites`` is provided (defaults to CLIMBING_SITES when None is
    passed and no override is given), the search first tries a site:-restricted
    query.  If that yields fewer than MIN_SITE_RESULTS results, it falls back to
    an unrestricted search so the user always gets useful data.

    Returns an empty list if BRAVE_API_KEY is not configured.
    """
    if not settings.brave_api_key:
        return []

    sites = preferred_sites if preferred_sites is not None else CLIMBING_SITES

    if sites:
        site_filter = " OR ".join(f"site:{s}" for s in sites)
        restricted_query = f"{query} ({site_filter})"
        results = await _do_search(restricted_query, count)
        if len(results) >= MIN_SITE_RESULTS:
            return results
        # Not enough hits from preferred sites — fall back to open web
        # Keep any preferred-site results and top them up with open results
        open_results = await _do_search(query, count)
        # Deduplicate by URL, preferred-site results first
        seen: set[str] = {r.url for r in results}
        for r in open_results:
            if r.url not in seen:
                results.append(r)
                seen.add(r.url)
        return results[:count]

    return await _do_search(query, count)
