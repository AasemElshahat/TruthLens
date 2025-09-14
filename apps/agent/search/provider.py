"""Simple search provider implementation."""

import asyncio
import logging
import os
from typing import List

import aiohttp
from langchain_exa import ExaSearchRetriever
from langchain_tavily import TavilySearch

from search.models import SearchResult

logger = logging.getLogger(__name__)


def _validate_max_results(max_results: int) -> int:
    """Validate max_results parameter."""
    if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
        raise ValueError("max_results must be an integer between 1 and 20")
    return max_results


async def _retry_request(func, max_retries: int = 2):
    """Retry network requests with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt == max_retries:
                raise e
            wait_time = 0.5 * (2 ** attempt)  # Exponential backoff: 0.5s, 1s, 2s
            logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries + 1}), retrying in {wait_time}s: {e}")
            await asyncio.sleep(wait_time)


async def search(query: str, max_results: int = 3) -> List[SearchResult]:
    """Search using the configured provider."""
    # Input validation
    max_results = _validate_max_results(max_results)
    
    provider = os.getenv("SEARCH_PROVIDER", "brave").lower()
    logger.info(f"Searching with {provider}: '{query}'")
    
    try:
        if provider == "brave":
            results = await _search_brave(query, max_results)
        elif provider == "exa":
            results = await _search_exa(query, max_results)
        elif provider == "tavily":
            results = await _search_tavily(query, max_results)
        else:
            raise ValueError(f"Unknown search provider: {provider}")
        
        logger.info(f"Retrieved {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Search failed with {provider}: {e}")
        return []


async def _search_brave(query: str, max_results: int) -> List[SearchResult]:
    """Search using Brave Search API with retry logic."""
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        raise ValueError("BRAVE_API_KEY not found in environment")
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"X-Subscription-Token": api_key}
    params = {
        "q": query,
        "count": min(max_results, 20),
        "search_lang": "en",
        "country": "us"
    }
    
    async def make_request():
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=await response.text()
                    )
                
                data = await response.json()
                web_results = data.get("web", {}).get("results", [])
                
                return [
                    SearchResult(
                        url=item.get("url", ""),
                        title=item.get("title", ""),
                        content=item.get("description", "")
                    )
                    for item in web_results[:max_results]
                ]
    
    return await _retry_request(make_request)


async def _search_exa(query: str, max_results: int) -> List[SearchResult]:
    """Search using Exa AI Search."""
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        raise ValueError("EXA_API_KEY not found in environment")
    
    retriever = ExaSearchRetriever(
        k=max_results,
        text_contents_options={"max_characters": 2000},
        type="neural",
        api_key=api_key
    )
    
    documents = await retriever.ainvoke(query)
    
    return [
        SearchResult(
            url=doc.metadata.get("url", ""),
            title=doc.metadata.get("title", ""),
            content=doc.page_content[:2000]
        )
        for doc in documents
    ]


async def _search_tavily(query: str, max_results: int) -> List[SearchResult]:
    """Search using Tavily Search API."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY not found in environment")
    
    search_client = TavilySearch(
        api_key=api_key,
        max_results=max_results,
        topic="general",
        include_raw_content="markdown"
    )
    
    raw_results = await search_client.ainvoke(query)
    
    # Handle different result formats from Tavily
    results = []
    if isinstance(raw_results, dict) and "results" in raw_results:
        search_results = raw_results["results"]
        if isinstance(search_results, list):
            for item in search_results[:max_results]:
                if isinstance(item, dict):
                    results.append(SearchResult(
                        url=item.get("url", ""),
                        title=item.get("title", ""),
                        content=item.get("raw_content") or item.get("content", "")
                    ))
    elif isinstance(raw_results, str):
        results.append(SearchResult(
            url="",
            title="Tavily Search Result",
            content=raw_results
        ))
    
    return results