import os
from tavily import TavilyClient
import schemas
from llm import extract_candidates_from_search

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "tvly-mock-key")

def get_evidence_for_query(query: str, case_id: str) -> schemas.Evidence:
    sources_searched = 0
    search_results = []
    
    if TAVILY_API_KEY != "tvly-mock-key":
        client = TavilyClient(api_key=TAVILY_API_KEY)
        try:
            # We search for the query along with some company related keywords to get better results
            response = client.search(query=f"{query} company profile", search_depth="advanced", max_results=10)
            search_results = response.get("results", [])
            sources_searched = len(search_results)
        except Exception as e:
            print(f"Tavily search failed: {e}")
            
    # Use LLM to extract candidates and structure the output
    parsed_data = extract_candidates_from_search(query, search_results)
    
    candidates = []
    for c in parsed_data.get("candidates", []):
        candidates.append(schemas.EvidenceCandidate(
            name=c.get("name", "Unknown"),
            country=c.get("country", "Unknown"),
            confidence=float(c.get("confidence", 0.0)),
            sources=int(c.get("sources", 0))
        ))
        
    return schemas.Evidence(
        query=query,
        candidates=candidates,
        selected_candidate=None,  # Never auto-select the top match
        sources_searched=sources_searched,
        reliable_sources=parsed_data.get("reliable_sources", 0),
        negative_news_found=parsed_data.get("negative_news_found", False),
        overall_confidence=parsed_data.get("overall_confidence", "low")
    )
