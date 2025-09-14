"""Retrieve evidence node - fetches evidence for claims using the Search Abstraction Layer."""

import logging
from typing import Dict, List

from search import search
from claim_verifier.config import EVIDENCE_RETRIEVAL_CONFIG
from claim_verifier.schemas import ClaimVerifierState, Evidence

logger = logging.getLogger(__name__)

# Retrieval settings
RESULTS_PER_QUERY = EVIDENCE_RETRIEVAL_CONFIG["results_per_query"]


async def retrieve_evidence_node(
    state: ClaimVerifierState,
) -> Dict[str, List[Evidence]]:
    """Retrieve evidence for a claim using the search abstraction layer."""
    if not state.query:
        logger.warning("No search query to process")
        return {"evidence": []}

    # Use simple search function
    search_results = await search(state.query, max_results=RESULTS_PER_QUERY)
    
    # Convert SearchResult objects to Evidence format
    evidence = [
        Evidence(
            url=result.url,
            text=result.content,
            title=result.title
        )
        for result in search_results
    ]
    
    logger.info(f"Retrieved {len(evidence)} total evidence snippets")
    return {"evidence": [item.model_dump() for item in evidence]}